import tempfile,unittest
from pathlib import Path
from advanced_lab import parse_command,protocol,preflight,virtual_schedule,sensor_health,make_casebook,summarize,safe_artifact_name,verify_full_bundle,execute
class AdvancedTests(unittest.TestCase):
 def test_m07_allowlist(self):
  self.assertEqual(parse_command('lab status')['action'],'status')
  self.assertFalse(parse_command('run simulation')['authorized'])
  with self.assertRaises(ValueError):parse_command('delete everything')
 def test_m08_protocol(self):
  self.assertEqual(protocol()['mode'],'SYNTHETIC_ONLY')
  with self.assertRaises(ValueError):protocol(0)
 def test_m09_preflight(self):
  p=protocol();p['physical_outputs_enabled']=True
  self.assertFalse(preflight(p)['passed'])
 def test_m10_timing(self):
  self.assertEqual(virtual_schedule(protocol())[-1]['end_second'],610)
 def test_m11_health(self):
  r={'temperature_c':20,'humidity_pct':45,'sound_db':35}
  self.assertTrue(sensor_health([r]*3)['sensor_channels']['sound_db']['stuck_sensor_warning'])
 def test_m12_casebook(self):
  g={'id':'W-001','first_sample':0,'last_sample':1,'channels':['sound_db'],'flags':[]}
  self.assertEqual(make_casebook([g],'a'*64)['cases'][0]['source_sha256'],'a'*64)
 def test_m13_briefing(self):
  self.assertIn('No causal conclusions',summarize([{}],[],{'sensor_channels':{'sound_db':{}}}))
 def test_m14_paths(self):
  for name in ('../secret','.secret','bad/file'):
   with self.assertRaises(ValueError):safe_artifact_name(name)
 def test_m15_integrity(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);execute(d,operator_approved=True);self.assertTrue(verify_full_bundle(d))
   (d/'casebook.json').write_text('{}')
   self.assertFalse(verify_full_bundle(d))
 def test_m16_authorization(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t)
   with self.assertRaises(PermissionError):execute(d)
   self.assertEqual(execute(d,operator_approved=True)['cases'],2)
   first=(d/'casebook.json').read_bytes()
   execute(d,operator_approved=True)
   self.assertEqual(first,(d/'casebook.json').read_bytes())
if __name__=='__main__':unittest.main()
