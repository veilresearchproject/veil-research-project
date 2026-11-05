import json
import tempfile
import threading
import unittest
from pathlib import Path
import memory_v34 as m

class MemoryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)/'approved'
  self.good={'approved':True,'kind':'equipment','note':'MTC recorder test unit has a test-tone setting','source':'Bench note, November 2026','approvedBy':'Operator'}
 def test_empty(self):self.assertEqual(m.load(self.root)['entries'],[])
 def test_explicit_approval(self):
  p={**self.good,'approved':False}
  with self.assertRaises(ValueError):m.add(self.root,p)
 def test_valid_add_persists(self):
  result=m.add(self.root,self.good)
  self.assertEqual(m.load(self.root)['entries'][0]['id'],result['id'])
 def test_no_automatic_model_use(self):self.assertNotIn('ollama',Path(m.__file__).read_text().lower())
 def test_approved_id_unique(self):
  a=m.add(self.root,self.good);b=m.add(self.root,self.good)
  self.assertNotEqual(a['id'],b['id'])
 def test_delete_requires_approval(self):
  a=m.add(self.root,self.good)
  with self.assertRaises(ValueError):m.remove(self.root,{'id':a['id']})
  self.assertTrue(m.remove(self.root,{'id':a['id'],'approved':True})['removed'])
 def test_invalid_category(self):
  with self.assertRaises(ValueError):m.add(self.root,{**self.good,'kind':'secrets'})
 def test_control_chars(self):
  with self.assertRaises(ValueError):m.add(self.root,{**self.good,'note':'secret\nsecond line'})
 def test_missing_operator(self):
  with self.assertRaises(ValueError):m.add(self.root,{**self.good,'approvedBy':''})
 def test_overlong_note(self):
  with self.assertRaises(ValueError):m.add(self.root,{**self.good,'note':'a'*501})
 def test_limit(self):
  for i in range(50):m.add(self.root,{**self.good,'note':f'Approved test note {i}'})
  with self.assertRaises(ValueError):m.add(self.root,self.good)
 def test_clear_requires_exact_confirmation(self):
  m.add(self.root,self.good)
  with self.assertRaises(ValueError):m.clear(self.root,{'approved':True,'confirmation':'DELETE'})
  self.assertEqual(len(m.load(self.root)['entries']),1)
 def test_clear_with_confirmation(self):
  m.add(self.root,self.good)
  self.assertEqual(m.clear(self.root,{'approved':True,'confirmation':'DELETE ALL APPROVED MEMORIES'})['removed'],1)
  self.assertEqual(m.load(self.root)['entries'],[])
 def test_malformed_json_does_not_get_overwritten(self):
  self.root.mkdir();p=self.root/'approved_memory_v34.json';p.write_text('{oops')
  with self.assertRaises(json.JSONDecodeError):m.load(self.root)
  self.assertEqual(p.read_text(),'{oops')
 def test_symlink_rejected(self):
  outside=Path(self.tmp.name)/'target';outside.write_text('{}')
  self.root.mkdir();(self.root/'approved_memory_v34.json').symlink_to(outside)
  with self.assertRaises(ValueError):m.load(self.root)
 def test_concurrent_adds(self):
  errors=[]
  def work(i):
   try:m.add(self.root,{**self.good,'note':f'Synthetic note {i}'})
   except Exception as e:errors.append(e)
  threads=[threading.Thread(target=work,args=(i,))for i in range(12)]
  for t in threads:t.start()
  for t in threads:t.join()
  self.assertFalse(errors)
  self.assertEqual(len(m.load(self.root)['entries']),12)

if __name__=='__main__':unittest.main(verbosity=2)
