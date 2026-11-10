import base64,json,zlib,math
from pathlib import Path
from functools import lru_cache
class Batteries:
 def __init__(self,path):self.sprites=json.loads(Path(path).read_text())
 @lru_cache(maxsize=108)
 def sprite(self,key):return zlib.decompress(base64.b64decode(self.sprites[key]))
 def draw(self,frame,x,y,key):
  raw=self.sprite(key)
  for row in range(70):
   yy=y+row
   if 0<=yy<240:
    start=(yy*320+x)*2;frame[start:start+256]=raw[row*256:(row+1)*256]
def presentation(state,info):
 """Never imply an SoC from charge state, charging current or connectivity."""
 if state=='Unplugged':return 'unplugged',''
 if state in ('Offline','Disabled','Faulted'):return 'offline',''
 connected=state in ('Preparing','AuthRequired','AuthTimeout','Charging','ChargingPausedEV','ChargingPausedEVSE','Finished','FinishedEV','FinishedEVSE')
 soc=info.get('soc') if connected else None
 if isinstance(soc,(int,float)) and not isinstance(soc,bool) and math.isfinite(soc) and 0<=soc<=100:
  n=round(soc);return str(n),f'{n}%'
 if state=='Charging':return 'charging',''
 if state in ('ChargingPausedEV','ChargingPausedEVSE'):return 'paused',''
 if state in ('Finished','FinishedEV','FinishedEVSE'):return 'finished',''
 if state in ('Preparing','AuthRequired','AuthTimeout','Reserved'):return 'ready',''
 return 'unknown',''
