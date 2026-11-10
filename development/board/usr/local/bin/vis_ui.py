"""Scrollable read-only module pages, independent of the LCD transport."""
import time,datetime,math
from vis_battery import presentation
class UI:
 def __init__(self,text,batteries=None):
  self.batteries=batteries
  self.text=text;self.module=0;self.offset=0;self.tab='Status';self.start=None;self.last=None;self.moved=False;self.rows=[];self.home_offset=0;self.modules=[{'id':1},{'id':2}]
 def event(self,point):
  if point==(-1,-1):
   if self.start and not self.moved:self.tap(*self.start)
   self.start=None;self.last=None;return
  if self.start is None:self.start=point;self.last=point;self.moved=False
  else:
   if abs(point[1]-self.start[1])+abs(point[0]-self.start[0])>12:self.moved=True
   if self.module and self.moved:
    self.offset=max(0,min(max(0,len(self.rows)*37-150),self.offset+self.last[1]-point[1]))
   if not self.module and self.moved:
    self.home_offset=max(0,min(self.home_max(),self.home_offset+self.last[1]-point[1]))
   self.last=point
 def tap(self,x,y):
  if not self.module:
   if 48<=y<198:
    position=y-48+self.home_offset;index=position//78
    if position%78<70 and index<len(self.modules):
     self.module=self.modules[index]['id'];self.tab='Status';self.offset=0
   return
  if y<38 and x<78:self.module=0;self.offset=0;return
  if 38<=y<72:
   self.tab=('Status','Specs','Options')[min(2,x//107)];self.offset=0
 def set_modules(self,modules):
  self.modules=sorted(modules,key=lambda item:item['id'])
  self.home_offset=min(self.home_offset,self.home_max())
  if self.module and not any(m['id']==self.module for m in self.modules):self.module=0
 def home_max(self):return max(0,len(self.modules)*78-6-150)
 def home(self,background,data,statuses,everest):
  f=bytearray(background);self.rect(f,0,48,320,150,(2,28,24))
  for i,m in enumerate(self.modules):
   y=48+i*78-self.home_offset
   if y+70<=48 or y>=198:continue
   n=m['id'];state=statuses.get(n,'WAITING DATA')
   self.rect(f,9,y,302,70,(7,55,47))
   self.text(f,64,y+6,m.get('name',f'ACDC #{n}'),13)
   self.text(f,18,y+8,{'Ethernet':'ETH'}.get(m.get('connection'),m.get('connection','NEW')),11)
   color=(115,245,87) if state=='LIVE' else (255,194,83)
   label={'WAITING DATA':'Waiting','SETUP NEEDED':'Setup needed','SERVICE OFF':'Service off'}.get(state,state)
   self.text(f,18,y+30,'Bridge: '+label,13,color)
   entry=data.get(n,{});evstate=self.session_state(entry,state)
   label={'ChargingPausedEV':'Paused by vehicle','ChargingPausedEVSE':'Paused by charger','State unavailable':'State unavailable'}.get(evstate,evstate)
   self.text(f,18,y+50,label,11)
   if self.batteries:
    key,percent=presentation(evstate,self.fresh(entry.get('ev_info')))
    self.batteries.draw(f,182,y,key)
    if percent:self.text(f,222,y+28,percent,13,(255,255,230))
  # Fixed header/footer clip scrolling cards and retain the original logo.
  f[:48*640]=background[:48*640];f[198*640:]=background[198*640:]
  self.text(f,12,204,'EVerest: '+('RUNNING' if everest else 'OFFLINE'),11)
  self.rect(f,0,221,320,19,(3,30,25))
  self.text(f,12,225,f'{len(self.modules)} modules | '+('Swipe to browse' if self.home_max() else 'Tap a module'),11)
  if self.home_max():
   h=max(10,150*150//(len(self.modules)*78-6));pos=48+(150-h)*self.home_offset//self.home_max()
   self.rect(f,315,48,3,150,(15,65,49));self.rect(f,315,pos,3,h,(112,219,102))
  return f
 def rect(self,f,x,y,w,h,color):
  r,g,b=color;p=(((r>>3)<<11)|((g>>2)<<5)|(b>>3)).to_bytes(2,'big')
  for yy in range(max(0,y),min(240,y+h)):
   a=(yy*320+x)*2;f[a:a+w*2]=p*w
 def fresh(self,entry,seconds=30):
  if not entry:return {}
  data,received,retained=entry
  if retained or time.monotonic()-received>seconds:return {}
  if 'timestamp' in data:
   try:
    age=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(data['timestamp'].replace('Z','+00:00'))).total_seconds()
    if not 0<=age<60:return {}
   except (ValueError,TypeError):return {}
  return data
 def session_state(self,data,status):
  if status!='LIVE':return 'Offline'
  heartbeat=data.get('heartbeat')
  if not heartbeat or heartbeat[2] or time.monotonic()-heartbeat[1]>100:return 'State unavailable'
  entry=data.get('session_info')
  if not entry or data.get('_state_reset'):return 'Waiting for state'
  state,received,retained=entry
  # State is event-driven; age since a transition is not measurement staleness.
  # Retained startup state is accepted only from the current EVerest run.
  try:
   stamp=datetime.datetime.fromisoformat(state['timestamp'].replace('Z','+00:00')).timestamp()
   epoch=data.get('_everest_epoch')
   if epoch is None or stamp<epoch:return 'Waiting for state'
  except (KeyError,ValueError,TypeError):return 'State unavailable'
  value=state.get('state')
  return value if isinstance(value,str) and value else 'Unknown'
 def number(self,v,unit):
  return f'{v:.2f} {unit}' if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) else 'Unavailable'
 def build_rows(self,n,data,status):
  d=data.get(n,{});session=self.fresh(d.get('session_info'));meter=self.fresh(d.get('powermeter'));limits=self.fresh(d.get('enforced_limits'),15).get('limits_root_side',{})
  caps=self.fresh(d.get('hw_capabilities'),120)
  if status!='LIVE':session={};meter={};limits={}
  if self.tab=='Options':return [('Future selections','Not enabled yet'),('Charging controls','Coming later'),('Current limit selection','Coming later'),('Module settings','Coming later'),('This page','Monitoring only')]
  if self.tab=='Specs':
   m=next((m for m in self.modules if m['id']==n),{})
   return [('Module',m.get('model','Not configured')),('ChargeBridge',m.get('chargebridge_model','Not configured')),('Connection',m.get('connection','Not configured')),('IP address',m.get('ip','Not configured')),('EVerest connector',m.get('connector',f'vis_acdc{n}')),('Reported max current',self.number(caps.get('max_current_A_import'),'A')),('Reported phases',str(caps.get('max_phase_count_import','Unavailable'))),('Connector type',str(caps.get('connector_type','Unavailable'))),('Ratings note','Reported config; not board rating')]

  current=meter.get('current_A',{});voltage=meter.get('voltage_V',{});power=meter.get('power_W',{})
  return [('ChargeBridge',status),('Charging state',self.session_state(d,status)),('Charging current L1',self.number(current.get('L1'),'A')),('Charging current L2',self.number(current.get('L2'),'A')),('Charging current L3',self.number(current.get('L3'),'A')),('Voltage L1',self.number(voltage.get('L1'),'V')),('Voltage L2',self.number(voltage.get('L2'),'V')),('Voltage L3',self.number(voltage.get('L3'),'V')),('Charging power',self.number(power.get('total',session.get('latest_total_w')),'W')),('Session energy',self.number(session.get('charged_energy_wh'),'Wh')),('Session duration',self.number(session.get('session_duration_s'),'s')),('Configured current limit',self.number(limits.get('ac_max_current_A',{}).get('value'),'A')),('Configured power limit',self.number(limits.get('total_power_W',{}).get('value'),'W')),('Data quality','Missing / old values stay unavailable')]
 def render(self,data,status):
  f=bytearray(b'\x01\x06'*320*240)
  self.rect(f,0,0,320,37,(5,55,43));self.text(f,10,11,'< Back',13);self.text(f,103,11,f'ACDC #{self.module}',13)
  for i,tab in enumerate(('Status','Specs','Options')):
   self.rect(f,i*107,39,106,31,(27,103,66) if tab==self.tab else (12,51,42));self.text(f,i*107+22,47,tab,13)
  self.rows=self.build_rows(self.module,data,status)
  self.offset=min(self.offset,max(0,len(self.rows)*37-150))
  for i,(label,value) in enumerate(self.rows):
   y=75+i*37-self.offset
   if y<54 or y>=222:continue
   self.text(f,12,y,label,11,(139,187,165));self.text(f,12,y+15,value,13)
  # Cover clipped rows with the fixed header and footer.
  self.rect(f,0,0,320,37,(5,55,43));self.text(f,10,11,'< Back',13);self.text(f,103,11,f'ACDC #{self.module}',13)
  for i,tab in enumerate(('Status','Specs','Options')):
   self.rect(f,i*107,38,106,34,(27,103,66) if tab==self.tab else (12,51,42));self.text(f,i*107+22,47,tab,13)
  self.rect(f,0,224,320,16,(3,30,25));self.text(f,12,226,'Swipe up/down to scroll',11,(139,187,165))
  total=max(150,len(self.rows)*37);h=max(12,int(145*150/total));pos=75+int((145-h)*self.offset/max(1,total-150))
  self.rect(f,314,75,3,145,(15,65,49));self.rect(f,314,pos,3,h,(112,219,102))
  return f
