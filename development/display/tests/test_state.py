import unittest,time,datetime
from vis_ui import UI
class Tests(unittest.TestCase):
 def data(self):
  return {'heartbeat':(10,time.monotonic(),False),'session_info':({'state':'Unplugged','timestamp':'2026-10-25T23:12:29Z'},time.monotonic(),True),'_everest_epoch':datetime.datetime(2026,10,25,23,12,12,tzinfo=datetime.timezone.utc).timestamp()}
 def test_old_transition_current_run(self):
  self.assertEqual(UI(None).session_state(self.data(),'LIVE'),'Unplugged')
 def test_prior_run_rejected(self):
  d=self.data();d['_everest_epoch']+=60;self.assertEqual(UI(None).session_state(d,'LIVE'),'Waiting for state')
 def test_lost_heartbeat(self):
  d=self.data();d['heartbeat']=(10,time.monotonic()-110,False);self.assertEqual(UI(None).session_state(d,'LIVE'),'State unavailable')
 def test_offline_and_api_reset(self):
  d=self.data();self.assertEqual(UI(None).session_state(d,'NO LINK'),'Offline');d['_state_reset']=True;self.assertEqual(UI(None).session_state(d,'LIVE'),'Waiting for state')
 def test_meter_still_expires(self):
  d=self.data();self.assertEqual(UI(None).fresh(d['session_info']),{})
if __name__=='__main__':unittest.main()
