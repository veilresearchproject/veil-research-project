import unittest
import synthetic_evidence as s

class IntakeTests(unittest.TestCase):
    def test_unknown_schema(self):
        with self.assertRaises(ValueError):
            s.inspect_synthetic(b'example', 'unsupported')

if __name__ == '__main__':
    unittest.main()
