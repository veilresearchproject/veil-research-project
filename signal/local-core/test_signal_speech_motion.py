"""HTTP asset and privacy regressions for new mouth-motion frames, no Windows needed."""
import unittest
import signal_desktop

class MotionTest(unittest.TestCase):
    def test_frames_serve_through_same_local_allowlist(self):
        """Assets are intentionally static and no media endpoint opens WAVs."""
        server,state=signal_desktop.make_server(signal_desktop.DemoModel())
        try:
            self.assertEqual(len(signal_desktop.SPEECH_POSES),4)
            for name in signal_desktop.SPEECH_POSES:
                path,mime=signal_desktop.STATIC['/face_assets/'+name+'.webp']
                self.assertEqual(mime,'image/webp')
                self.assertTrue(path.is_file())
                self.assertTrue(path.read_bytes().startswith(b'RIFF'))
            self.assertNotIn('/api/wav',signal_desktop.STATIC)
            self.assertEqual(state.listener.status()['state'],'idle')
            self.assertFalse(state.bot.voice.enabled)
        finally:
            server.server_close()

    def test_existing_expressions_unchanged(self):
        self.assertEqual(signal_desktop.FACES,('neutral','focused','amused','excited','concentrating','reassuring'))
        self.assertFalse(any('/face_assets/' in x and not x.endswith('.webp') for x in signal_desktop.STATIC))

if __name__=='__main__': unittest.main()
