import unittest,time
from vis_ui import UI
class Tests(unittest.TestCase):
 def test_navigation(self):
  u=UI(lambda *a:None);u.event((100,80));u.event((-1,-1));self.assertEqual(u.module,1)
  u.rows=[('x','y')]*14
  u.event((100,180));u.event((100,90));u.event((-1,-1));self.assertEqual(u.offset,90)
  u.event((150,50));u.event((-1,-1));self.assertEqual(u.tab,'Specs');self.assertEqual(u.offset,0)
  u.event((30,20));u.event((-1,-1));self.assertEqual(u.module,0)
 def test_measurement_vs_limit(self):
  u=UI(lambda *a:None);d={1:{'enforced_limits':({'limits_root_side':{'ac_max_current_A':{'value':8}}},time.monotonic(),False)}}
  rows=dict(u.build_rows(1,d,'LIVE'));self.assertEqual(rows['Charging current L1'],'Unavailable');self.assertEqual(rows['Configured current limit'],'8.00 A')
  rows=dict(u.build_rows(1,d,'NO LINK'));self.assertEqual(rows['Configured current limit'],'Unavailable')
 def test_stale_and_retained(self):
  u=UI(lambda *a:None)
  self.assertEqual(u.fresh(({'state':'Charging'},time.monotonic(),True)),{})
  self.assertEqual(u.fresh(({'state':'Charging'},time.monotonic()-100,False)),{})
 def test_bounds(self):
  u=UI(lambda *a:None);u.module=1;u.offset=100000
  self.assertEqual(len(u.render({},'NO LINK')),153600)
  self.assertLess(u.offset,1000)
if __name__=='__main__':unittest.main()
