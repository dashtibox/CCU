#!/usr/bin/env python3
"""Read-only live CCU display. Never publishes MQTT or operates charging outputs."""
from functools import lru_cache
import queue
from vis_touch import Touch
from vis_ui import UI
from vis_modules import Modules
from vis_battery import Batteries
import socket,json,subprocess,threading,time,datetime,fcntl,os,struct
from pathlib import Path
ROOT=Path('/usr/local/share/vis-display/status')
fonts=json.loads((ROOT/'fonts.json').read_text())
background=(ROOT/'background.rgb565').read_bytes()
seen={};sessions={};telemetry={};health={};lock=threading.Lock()
modules=Modules(ROOT/'modules.json')
events=queue.Queue(maxsize=256)
CHILD_ENV={k:v for k,v in os.environ.items() if k not in ('NOTIFY_SOCKET','WATCHDOG_USEC','WATCHDOG_PID')}
def notify(message):
 address=os.environ.get('NOTIFY_SOCKET')
 if address:
  with socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM) as sock:
   sock.connect('\0'+address[1:] if address.startswith('@') else address)
   sock.sendall(message.encode())
def monitor():
 while True:
  child=None
  try:
   child=subprocess.Popen(['docker','exec','everest-mosquitto','mosquitto_sub','-F','%j','-t','pionix/chargebridge/+/gpio/#','-t','everest_api/1/evse_manager_consumer/+/e2m/#'],stdout=subprocess.PIPE,text=True,env=CHILD_ENV)
   for line in child.stdout:
    try:
     m=json.loads(line);topic=m['topic'];payload=m['payload']
     with lock:
      for mdef in modules.snapshot():
       n=mdef['id'];key=mdef.get('bridge_key')
       if key and topic.startswith('pionix/chargebridge/'+key+'/') and not m.get('retain'):seen[n]=time.monotonic()
      if topic.startswith('everest_api/'):
       value=json.loads(payload);accepted=modules.accept(topic,value,m.get('retain',False))
       if accepted:
        n,kind=accepted
        values=telemetry.setdefault(n,{})
        if kind=='heartbeat' and not m.get('retain',False):
         previous=values.get('heartbeat')
         if previous and value<previous[0]:
          values.pop('session_info',None)
          values['_state_reset']=(True,time.monotonic(),False)
        if kind=='session_info' and not m.get('retain',False):values.pop('_state_reset',None)
        values[kind]=(value,time.monotonic(),m.get('retain',False))

    except (ValueError,KeyError,TypeError): pass
  except OSError as e: print('MQTT:',e,flush=True)
  finally:
   if child: child.terminate();child.wait()
  time.sleep(5)
@lru_cache(maxsize=65536)
def blend(old,a,color):
 bg=((old>>11)*255//31,((old>>5)&63)*255//63,(old&31)*255//31)
 r,g,b=[(color[k]*a+bg[k]*(255-a))//255 for k in range(3)]
 return (((r>>3)<<11)|((g>>2)<<5)|(b>>3)).to_bytes(2,'big')
def text(frame,x,y,s,size=11,color=(220,242,232)):
 for c in str(s):
  glyph=fonts[str(size)].get(c,fonts[str(size)]['?'])
  for dx,dy,a in glyph['pixels']:
   px=x+dx;py=y+dy
   if not (0<=px<320 and 0<=py<240): continue
   i=(py*320+px)*2;old=int.from_bytes(frame[i:i+2],'big')
   frame[i:i+2]=blend(old,a,color)
  x+=glyph['w']
  if x>303: break
def run(args):
 try: return subprocess.run(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=3,env=CHILD_ENV).returncode==0
 except (OSError,subprocess.TimeoutExpired): return False
def probe():
 while True:
  result={}
  with lock:definitions=modules.snapshot()
  for module in definitions:
   n=module['id'];ip=module.get('ip');unit=module.get('service')
   result[n]=(run(['ping','-c','1','-W','1',ip]) if ip else None,run(['systemctl','is-active','--quiet',unit]) if unit else None)
  result['everest']=run(['systemctl','is-active','--quiet','everest-chargebridge'])
  try:
   stamp=subprocess.check_output(['systemctl','show','everest-chargebridge','-p','ActiveEnterTimestamp','--value'],text=True,timeout=3,env=CHILD_ENV).strip()
   result['epoch']=datetime.datetime.strptime(stamp,'%a %Y-%m-%d %H:%M:%S %Z').replace(tzinfo=datetime.timezone.utc).timestamp()
  except (ValueError,subprocess.SubprocessError):result['epoch']=None
  with lock: health.update(result)
  time.sleep(5)
def touch_loop():
 while True:
  touch=None
  try:
   touch=Touch();print(f'Touch ready: {touch.width}x{touch.height}',flush=True)
   while True:
    point=touch.poll()
    if point is not None:
     try:events.put_nowait(point)
     except queue.Full:
      # Cancel the gesture if the consumer cannot keep up.
      while not events.empty():events.get_nowait()
      events.put_nowait((-1,-1))
    time.sleep(.02)
  except OSError as exc:print('Touch retry: '+str(exc),flush=True)
  finally:
   if touch:touch.close()
  time.sleep(5)
def status(n):
 with lock: reachable,active=health.get(n,(None,None));fresh=time.monotonic()-seen.get(n,-1e9)<20
 if reachable is None or active is None:return 'SETUP NEEDED'
 return 'LIVE' if reachable and active and fresh else ('NO LINK' if not reachable else ('SERVICE OFF' if not active else 'WAITING DATA'))

def main():
 splash=(ROOT/'splash.rgb565').read_bytes()
 assert len(background)==len(splash)==153600
 assert Path('/sys/class/gpio/gpiochip515/label').read_text().strip()=='4201000.gpio'
 def gpio(n):
  p=Path('/sys/class/gpio')/f'gpio{n}'
  if not p.exists(): Path('/sys/class/gpio/export').write_text(str(n))
  (p/'direction').write_text('high');return p/'value'
 reset=gpio(516);dc=gpio(517)
 fd=os.open('/dev/spidev0.0',os.O_WRONLY)
 def write(data):
  for i in range(0,len(data),4096):
   chunk=data[i:i+4096]
   if os.write(fd,chunk)!=len(chunk): raise IOError('Short SPI write')
 def cmd(c,data=b''):
  dc.write_text('0');write(bytes([c]))
  if data: dc.write_text('1');write(bytes(data))
 try:
  fcntl.ioctl(fd,0x40016b01,struct.pack('B',0));fcntl.ioctl(fd,0x40016b03,struct.pack('B',8));fcntl.ioctl(fd,0x40046b04,struct.pack('I',4000000))
  # GT911 shares LCD reset. Select address, then synchronize INT before releasing it.
  interrupt=gpio(518)
  reset.write_text('0');time.sleep(.02)
  interrupt.write_text('1');time.sleep(.002)
  reset.write_text('1');time.sleep(.006)
  interrupt.write_text('0');time.sleep(.05)
  (interrupt.parent/'direction').write_text('in');time.sleep(.1)
  cmd(1);time.sleep(.15);cmd(0x11);time.sleep(.12);cmd(0x3a,[0x55]);cmd(0x36,[0x60]);cmd(0x13)
  cmd(0x21) # Panel polarity: INVON; correct complemented colors after reset
  def show(frame,previous=None):
   started=time.monotonic();sent=0
   rows=[y for y in range(240) if previous is None or frame[y*640:(y+1)*640]!=previous[y*640:(y+1)*640]]
   spans=[]
   for y in rows:
    if spans and y-spans[-1][1]<=4:spans[-1][1]=y
    else:spans.append([y,y])
   for first,last in spans:
    cmd(0x2a,[0,0,1,0x3f]);cmd(0x2b,[0,first,0,last]);cmd(0x2c)
    dc.write_text('1');write(frame[first*640:(last+1)*640]);sent+=(last-first+1)*640
   Path('/run/vis-display-perf.json').write_text(json.dumps({'transfer_ms':round((time.monotonic()-started)*1000,1),'bytes':sent,'spi_hz':4000000}))
   cmd(0x29)
   Path('/run/vis-display-status.rgb565').write_bytes(frame)
  show(splash)
  print('VIS logo splash displayed',flush=True)
  notify('READY=1')
  for target in (monitor,probe,touch_loop):threading.Thread(target=target,daemon=True).start()
  time.sleep(4)
  previous=splash;ui=UI(text,Batteries(ROOT/'batteries.json'));last_render=0
  while True:
   with lock: definitions=modules.snapshot()
   changed=definitions!=ui.modules
   ui.set_modules(definitions)
   while not events.empty():
    point=events.get_nowait();before=(ui.module,ui.tab,ui.offset,ui.home_offset)
    ui.event(point)
    if before!=(ui.module,ui.tab,ui.offset,ui.home_offset):changed=True
   if changed or time.monotonic()-last_render>=5:
    with lock:
     data={n:dict(v) for n,v in telemetry.items()}
     for values in data.values():values['_everest_epoch']=health.get('epoch')
    with lock:ev=health.get('everest',False)
    frame=ui.render(data,status(ui.module)) if ui.module else ui.home(background,data,{m['id']:status(m['id']) for m in definitions},ev)
    if frame!=previous:show(frame,previous);previous=frame
    Path('/run/vis-display-page.json').write_text(json.dumps({'module':ui.module,'tab':ui.tab,'scroll':ui.offset,'home_scroll':ui.home_offset,'modules':[m['id'] for m in definitions]}))
    last_render=time.monotonic()
   notify('WATCHDOG=1');time.sleep(.02)
 finally: os.close(fd)
if __name__=='__main__': main()
