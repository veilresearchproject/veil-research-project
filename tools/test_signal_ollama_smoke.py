import unittest
from unittest.mock import patch
import signal_ollama_smoke as s

class TestSmoke(unittest.TestCase):
    def test_valid(self):
        self.assertIsNone(s.inspect_response({'response':'Okay','done': True}))
    def test_missing(self):
        self.assertIsNotNone(s.inspect_response({'response':'','done': True}))
    def test_incomplete(self):
        self.assertIsNotNone(s.inspect_response({'response':'Hi','done': False}))
    def test_list_only(self):
        with patch.object(s, 'request_json', return_value={'models':[{'name':'llama3.2:3b'}]}) as fn:
            output=s.run('llama3.2:3b',20,evaluate=False)
        self.assertTrue(output['ok'])
        self.assertEqual(fn.call_count,1)
    def test_not_installed(self):
        with patch.object(s,'request_json',return_value={'models':[]}):
            self.assertFalse(s.run('llama3.2:3b',20)['ok'])
    def test_three_prompts(self):
        with patch.object(s,'request_json',side_effect=[{'models':[{'name':'llama3.2:3b'}]}]+[{'response':'Measured answer','done':True}]*3) as fn:
            output=s.run('llama3.2:3b',20)
        self.assertTrue(output['ok'])
        self.assertEqual(len(output['test_results']),3)
        self.assertEqual(fn.call_count,4)

if __name__=='__main__': unittest.main()
