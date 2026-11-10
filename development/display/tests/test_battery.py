import unittest
from vis_battery import presentation
from vis_ui import UI
class Tests(unittest.TestCase):
 def test_unplugged_no_percent(self):self.assertEqual(presentation('Unplugged',{'soc':78}),('unplugged',''))
 def test_real_soc(self):self.assertEqual(presentation('Charging',{'soc':78}),('78','78%'))
 def test_missing_invalid_soc(self):
  for v in (None,-1,101,float('nan'),True,'78'):
   self.assertEqual(presentation('Charging',{'soc':v}),('charging',''))
 def test_noncharging(self):
  self.assertEqual(presentation('ChargingPausedEV',{}),('paused',''))
  self.assertEqual(presentation('Finished',{}),('finished',''))
  self.assertEqual(presentation('Offline',{'soc':50}),('offline',''))
 def test_stale_soc(self):
  self.assertEqual(presentation('Charging',UI(None).fresh(({'soc':78},0,False))),('charging',''))
if __name__=='__main__':unittest.main()
