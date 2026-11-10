"""GT911 polling input; only acknowledges touch status, no configuration flash writes."""
import ctypes,os,time
class Msg(ctypes.Structure):
 _fields_=[('addr',ctypes.c_uint16),('flags',ctypes.c_uint16),('len',ctypes.c_uint16),('buf',ctypes.c_void_p)]
class Transfer(ctypes.Structure):
 _fields_=[('msgs',ctypes.POINTER(Msg)),('nmsgs',ctypes.c_uint32)]
class Touch:
 def __init__(self):
  self.fd=os.open('/dev/i2c-2',os.O_RDWR);self.addr=0x14
  self.lib=ctypes.CDLL(None,use_errno=True)
  try:
   for addr in (0x14,0x5d):
    self.addr=addr
    try:
     if self.read(0x8140,4).startswith(b'911'):break
    except OSError:pass
   else:raise OSError('GT911 missing')
   r=self.read(0x8048,4);self.width=int.from_bytes(r[:2],'little');self.height=int.from_bytes(r[2:],'little')
   if not self.width or not self.height:raise OSError('GT911 configuration not loaded')
  except Exception:os.close(self.fd);raise
 def transfer(self,parts):
  buffers=[ctypes.create_string_buffer(data) if not isinstance(data,int) else ctypes.create_string_buffer(data) for flag,data in parts]
  msgs=(Msg*len(parts))(*(Msg(self.addr,flag,len(data) if isinstance(data,bytes) else data,ctypes.addressof(buf)) for (flag,data),buf in zip(parts,buffers)))
  req=Transfer(msgs,len(parts))
  if self.lib.ioctl(self.fd,0x0707,ctypes.byref(req))<0:raise OSError(ctypes.get_errno(),'I2C transfer')
  return buffers[-1].raw
 def read(self,reg,n):return self.transfer([(0,reg.to_bytes(2,'big')),(1,n)])
 def poll(self):
  status=self.read(0x814e,1)[0]
  if not status&128:return None
  point=None
  if 0<status&15<=5:
   d=self.read(0x8150,4);x=int.from_bytes(d[:2],'little');y=int.from_bytes(d[2:],'little')
   point=(min(319,x*320//self.width),min(239,y*240//self.height))
  self.transfer([(0,b'\x81\x4e\x00')])
  return point if point is not None else (-1,-1)
 def close(self):os.close(self.fd)
