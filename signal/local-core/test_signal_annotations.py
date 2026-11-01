"""Investigator note storage and validation, no MTC source changes."""
import json
from pathlib import Path
import tempfile
import unittest

import signal_annotations as sa

SESSION={'session_id':'20261027_215040_70c105','recorded_seconds':5400.021}

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'notes'

    def test_manual_known_door_notes_are_append_only(self):
        first=sa.append_note(self.root, SESSION,31.25,'known_source','Known: room door closed while exiting.')
        second=sa.append_note(self.root, SESSION,31.26,'needs_review','Same time frame; investigate duplicates.')
        self.assertEqual(first['seconds_from_start'],31.25)
        entries=sa.list_notes(self.root, SESSION)
        self.assertEqual(len(entries),2)
        self.assertEqual(entries[0]['note'],'Known: room door closed while exiting.')
        self.assertIn('Manual interpretation',entries[1]['provenance'])
        self.assertEqual(len(list(self.root.iterdir())),1)

    def test_empty_notebook(self):
        self.assertEqual(sa.list_notes(self.root,SESSION),[])

    def test_bad_time_label_notes_rejected(self):
        for t in [-1,5401,float('nan'),float('inf'),True,'17']:
            with self.subTest(time=t),self.assertRaises(sa.ReviewError):
                sa.append_note(self.root,SESSION,t,'known_source','Door')
        for label in ['paranormal','CONFIRMED_ENTITY','',None]:
            with self.subTest(label=label),self.assertRaises(sa.ReviewError):
                sa.append_note(self.root,SESSION,10,label,'Door')
        for note in ['','x'*401,'evidence\x00bad']:
            with self.subTest(note=repr(note)),self.assertRaises(sa.ReviewError):
                sa.append_note(self.root,SESSION,10,'needs_review',note)

    def test_path_traversal_blocked(self):
        with self.assertRaises(sa.ReviewError):
            sa.append_note(self.root,{'session_id':'../../evil','recorded_seconds':20},5,'known_source','x')

    def test_source_evidence_is_not_opened_or_edited(self):
        original=Path(self.tmp.name)/'session_result.json'
        original.write_bytes(b'untouchable evidence')
        sa.append_note(self.root,SESSION,4,'unexplained','Source not yet identified')
        self.assertEqual(original.read_bytes(),b'untouchable evidence')

    def test_corrupt_notebook_fails_closed(self):
        sa.append_note(self.root,SESSION,2,'known_source','door')
        with (self.root/(SESSION['session_id']+'.jsonl')).open('a') as f:f.write('broken\n')
        with self.assertRaisesRegex(sa.ReviewError,'Damaged notebook'):
            sa.list_notes(self.root,SESSION)

    def test_symlink_notebook_refused(self):
        self.root.mkdir()
        outer=Path(self.tmp.name)/'other'
        outer.write_text('protected')
        try: (self.root/(SESSION['session_id']+'.jsonl')).symlink_to(outer)
        except (OSError,NotImplementedError): self.skipTest('Symlink unavailable')
        with self.assertRaisesRegex(sa.ReviewError,'Unsafe notebook'):
            sa.append_note(self.root,SESSION,2,'known_source','door')
        self.assertEqual(outer.read_text(),'protected')

if __name__=='__main__':unittest.main()
