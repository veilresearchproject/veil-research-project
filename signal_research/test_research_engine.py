import sqlite3,unittest
from research_engine import normalize_url,prepare_results,save_ledger,citation_brief
ROW=dict(url="https://example.org/photo",title="Archive",excerpt="Claimed 2014 image",observed_utc="2026-11-17T16:00:00Z")
class Tests(unittest.TestCase):
 def test_citation(self):
  x=prepare_results([ROW])[0];self.assertEqual(x["citation_id"],"R001");self.assertEqual(len(x["record_sha256"]),64);self.assertIn("unverified",citation_brief([x]))
 def test_dedupe(self):self.assertEqual(len(prepare_results([ROW,ROW])),1)
 def test_limit(self):
  with self.assertRaises(ValueError):prepare_results([ROW]*21)
 def test_fields(self):
  with self.assertRaises(ValueError):prepare_results([{**ROW,"verified":True}])
 def test_date(self):
  with self.assertRaises(ValueError):prepare_results([{**ROW,"observed_utc":"yesterday"}])
 def test_title(self):
  with self.assertRaises(ValueError):prepare_results([{**ROW,"title":"x"*181}])
 def test_urls(self):
  for url in ("http://example.org","https://localhost/a","https://127.0.0.1/","https://10.0.0.2/","https://user:pass@example.org/","https://example.org:8080/"):
   with self.subTest(url=url),self.assertRaises(ValueError):normalize_url(url)
 def test_sqlite(self):
  with sqlite3.connect(":memory:") as db:
   self.assertEqual(save_ledger(db,[ROW]),1);self.assertEqual(db.execute("SELECT count(*) FROM research_sources").fetchone()[0],1)
 def test_no_network(self):
  import inspect,research_engine
  s=inspect.getsource(research_engine);self.assertNotIn("urlopen(",s);self.assertNotIn("requests.get(",s)
if __name__=="__main__":unittest.main()
