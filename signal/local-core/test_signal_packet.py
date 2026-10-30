"""Read-only MTC review export tests: provenance, integrity and no acoustic claims."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import signal_annotations
import signal_packet


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.session = {
            'session_id': 'MTC_20261027_215040_70c105', 'recorded_seconds': 5400.021,
            'outcome': 'complete', 'events': 800, 'segments_declared': 2,
            'file_integrity': {'session_metadata.json': True, 'events.jsonl': True},
        }
        self.fixed = datetime(2026, 10, 30, 14, 0, tzinfo=timezone.utc)

    def packet(self, scanner=None):
        return signal_packet.build_packet(self.session, scanner, self.root, created=self.fixed)

    def test_missing_session_does_not_create_note_folder(self):
        with self.assertRaises(signal_packet.PacketError):
            signal_packet.build_packet(None, None, self.root, created=self.fixed)
        self.assertFalse(self.root.joinpath('MTC_20261027_215040_70c105.jsonl').exists())

    def test_empty_packet_still_discloses_limits(self):
        p = self.packet()
        self.assertEqual(p['note_count'], 0)
        self.assertIsNone(p['scanner_review'])
        self.assertTrue(signal_packet.verify_packet_fingerprint(p))
        page = signal_packet.html_bytes(p).decode()
        self.assertIn('No scanner report loaded', page)
        self.assertIn('No investigator notes recorded', page)
        self.assertIn('No raw WAV recordings were opened', page)
        self.assertNotIn('<script>', page)

    def test_all_notes_preserved_not_just_last_hundred(self):
        for i in range(105):
            signal_annotations.append_note(self.root, self.session, float(i),
                                           'needs_review', 'Sound ' + str(i))
        self.assertEqual(len(signal_annotations.list_notes(self.root, self.session)), 100)
        p = self.packet()
        self.assertEqual(p['note_count'], 105)
        self.assertEqual(p['investigator_notes'][0]['note'], 'Sound 0')
        self.assertEqual(p['investigator_notes'][-1]['note'], 'Sound 104')
        original = (self.root / (self.session['session_id'] + '.jsonl')).read_bytes()
        signal_packet.json_bytes(p)
        signal_packet.html_bytes(p)
        self.assertEqual(original, (self.root / (self.session['session_id'] + '.jsonl')).read_bytes())

    def test_scanner_matching_and_boundaries(self):
        report = {'session_id': self.session['session_id'], 'raw_candidates': 2,
                  'review_windows': 1, 'report_sha256': 'a'*64,
                  'groups': [{'review_id':'R-001','start':31.5,'end':34.0,'count':2,'score':5.4}],
                  'warnings': []}
        p = self.packet(report)
        self.assertEqual(p['scanner_review']['report_sha256'], 'a'*64)
        self.assertIn('R-001', signal_packet.html_bytes(p).decode())
        report['session_id'] = 'MTC_DIFFERENT'
        with self.assertRaises(signal_packet.PacketError):
            self.packet(report)

    def test_hash_tracks_content_changes_not_authentication(self):
        p = self.packet()
        self.assertTrue(signal_packet.verify_packet_fingerprint(p))
        self.assertEqual(json.loads(signal_packet.json_bytes(p))['packet_content_sha256'],
                         p['packet_content_sha256'])
        altered = dict(p, note_count=7)
        self.assertFalse(signal_packet.verify_packet_fingerprint(altered))
        signal_annotations.append_note(self.root,self.session,31.5,'known_source','Door closed')
        updated = self.packet()
        self.assertNotEqual(p['packet_content_sha256'],updated['packet_content_sha256'])
        self.assertIn('not a WAV hash or authenticity signature', updated['hash_scope'])

    def test_html_escapes_untrusted_notes_no_placeholder_recursion(self):
        bad = '<script>alert("x")</script> __FINGERPRINT__ & <b>strange</b>'
        signal_annotations.append_note(self.root,self.session,14,'needs_review',bad)
        p = self.packet()
        text = signal_packet.html_bytes(p).decode()
        self.assertNotIn('<script>',text)
        self.assertNotIn('<b>strange</b>',text)
        self.assertIn('&lt;script&gt;',text)
        self.assertIn('__FINGERPRINT__',text)
        self.assertIn('&amp;',text)

    def test_rejects_timestamp_without_timezone(self):
        with self.assertRaises(signal_packet.PacketError):
            signal_packet.build_packet(self.session,None,self.root,created=datetime(2026,1,1))

    def test_unsafe_notes_file_does_not_succeed(self):
        (self.root/(self.session['session_id']+'.jsonl')).write_text('garbage', encoding='utf-8')
        with self.assertRaises(signal_annotations.ReviewError):self.packet()

if __name__ == '__main__':unittest.main()
