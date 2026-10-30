"""v0.7 regression tests for stable, restrained mouth movement."""
import unittest
from pathlib import Path
import signal_desktop

ROOT=Path(__file__).resolve().parent

class MouthRefinementTest(unittest.TestCase):
    def test_neutral_frame_is_exact_original_file(self):
        root=ROOT/'face_assets'
        self.assertEqual((root/'speech_0.webp').read_bytes(), (root/'neutral.webp').read_bytes())

    def test_motion_frames_exist_and_have_webp_signature(self):
        root=ROOT/'face_assets'
        baseline=(root/'neutral.webp').read_bytes()
        for i in (1,2,3):
            with self.subTest(frame=i):
                blob=(root/f'speech_{i}.webp').read_bytes()
                self.assertTrue(blob.startswith(b'RIFF'))
                self.assertGreater(len(blob),len(baseline))
                self.assertLess(len(blob),500_000)

    def test_controls_allow_still_mode_and_reduced_motion(self):
        js=(ROOT/'signal_face.js').read_text(encoding='utf-8')
        html=(ROOT/'signal_face.html').read_text(encoding='utf-8')
        self.assertIn('motionEnabled = !motionEnabled',js)
        self.assertIn("const moving = speakingNow && motionAllowed && motionEnabled && name === 'neutral'",js)
        self.assertIn("speechTickTimer = window.setTimeout",js)
        self.assertIn("const motionAllowed = !window.matchMedia('(prefers-reduced-motion: reduce)').matches",js)
        self.assertNotIn('}, 180);',js)
        self.assertIn('id="motion-toggle"',html)
        self.assertIn('id="motion-preview" type="button" aria-pressed="false"',html)

    def test_existing_expressions_stay_registered_and_mic_off(self):
        self.assertEqual(len(signal_desktop.FACES),6)
        server,state=signal_desktop.make_server(signal_desktop.DemoModel())
        try:
            self.assertFalse(state.bot.voice.enabled)
            self.assertEqual(state.listener.status()['state'],'idle')
            self.assertEqual(len(signal_desktop.SPEECH_POSES),4)
        finally:
            server.server_close()

if __name__=='__main__':unittest.main()
