import json,tempfile,time,unittest
from pathlib import Path
from vis_modules import Modules
from vis_ui import UI
class Tests(unittest.TestCase):
 def test_two_fit(self):
  u=UI(lambda *a:None);self.assertEqual(u.home_max(),0)
  u.event((100,180));u.event((100,60));u.event((-1,-1));self.assertEqual(u.home_offset,0);self.assertEqual(u.module,0)
 def test_many_and_back(self):
  u=UI(lambda *a:None);u.set_modules([{'id':n} for n in (1,2,4,7,10)])
  u.event((100,180));u.event((100,24));u.event((-1,-1))
  self.assertEqual(u.home_offset,156);self.assertEqual(u.module,0)
  u.event((100,80));u.event((-1,-1));self.assertEqual(u.module,4)
  u.event((20,20));u.event((-1,-1));self.assertEqual(u.module,0);self.assertEqual(u.home_offset,156)
  u.set_modules([{'id':1},{'id':2}]);self.assertEqual(u.home_offset,0)
 def test_all_cards_accessible(self):
  u=UI(lambda *a:None);u.set_modules([{'id':n} for n in range(1,21)])
  u.home_offset=u.home_max();u.tap(100,170);self.assertEqual(u.module,20)
  u.module=0;frame=u.home(bytes(153600),{}, {},False);self.assertEqual(len(frame),153600)
 def test_discovery(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'m.json';p.write_text('[{"id":1},{"id":2}]');m=Modules(p)
   topic='everest_api/1/evse_manager_consumer/vis_acdc3/e2m/hw_capabilities'
   self.assertIsNone(m.accept(topic,{'connector_type':'Test'},True))
   self.assertIsNone(m.accept(topic,{},False))
   self.assertEqual(m.accept(topic,{'connector_type':'Test'},False),(3,'hw_capabilities'))
   self.assertEqual([x['id'] for x in m.snapshot()],[1,2,3])
   self.assertNotIn('ip',m.items[3]);self.assertNotIn('chargebridge_model',m.items[3])
if __name__=='__main__':unittest.main()
