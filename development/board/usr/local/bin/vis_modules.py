"""Configured modules plus live EVerest discovery; stale retained topics never add devices."""
import json,re
class Modules:
 def __init__(self,path):
  self.items={}
  for item in json.loads(path.read_text()):
   n=item['id']
   if not isinstance(n,int) or isinstance(n,bool) or n<1 or n>9999 or n in self.items:raise ValueError('Invalid or duplicate module ID')
   self.items[n]=dict(item)
 def accept(self,topic,payload,retained):
  match=re.fullmatch(r'everest_api/1/evse_manager_consumer/(vis_acdc([1-9][0-9]{0,3}))/e2m/(session_info|hw_capabilities|powermeter|enforced_limits|heartbeat|ev_info)',topic)
  if not match:return None
  if match.group(3)=='heartbeat':
   return (int(match.group(2)),'heartbeat') if int(match.group(2)) in self.items and isinstance(payload,(int,float)) else None
  if not isinstance(payload,dict):return None
  connector,n,kind=match.group(1),int(match.group(2)),match.group(3)
  if n not in self.items:
   if retained or kind not in ('session_info','hw_capabilities'):return None
   if kind=='session_info' and 'state' not in payload:return None
   if kind=='hw_capabilities' and 'connector_type' not in payload:return None
   self.items[n]={'id':n,'name':f'ACDC #{n}','connector':connector,'discovered':True}
  return n,kind
 def snapshot(self):return [dict(self.items[n]) for n in sorted(self.items)]
