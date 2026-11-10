"""Supersampled native UI battery icons, pre-rendered for fast RGB565 blits."""
from PIL import Image,ImageDraw
from pathlib import Path
import json,zlib,base64
P=Path(__file__).parent;S=4;W=64;H=40
sprites={}
for key in ['unplugged','charging','paused','ready','finished','offline','unknown']+[str(i) for i in range(101)]:
 im=Image.new('RGB',(W*S,H*S),(7,55,47));d=ImageDraw.Draw(im)
 def box(coords,fill,outline=None,r=4,width=1):d.rounded_rectangle(tuple(int(v*S) for v in coords),radius=r*S,fill=fill,outline=outline,width=width*S)
 def line(points,fill,width=2):d.line([(int(x*S),int(y*S)) for x,y in points],fill=fill,width=width*S)
 def ellipse(coords,fill):d.ellipse(tuple(int(v*S) for v in coords),fill=fill)
 numeric=key.isdigit();accent='#f8d578'
 box((6,7,58,35),'#03251f',r=7)
 box((56,14,62,25),'#d6a342','#ffebac',r=2)
 box((3,4,57,33),'#c69336','#ffe8a0',r=6,width=1)
 # Metallic gold body highlights, rendered at 4x for clean small edges.
 for yy in range(7,31):
  light=1-abs(yy-13)/23
  c=tuple(int(v) for v in (146+100*light,98+108*light,29+74*light))
  line([(6,yy),(54,yy)],c,1)
 box((7,8,53,29),'#191c1a','#8e6b2c',r=3,width=1)
 line([(10,10),(49,10)],'#46463a',1)

 if numeric:
  n=int(key);fillw=42*n/100
  if n>0:
   color='#d58d36' if n<=20 else '#e6bd53'
   box((9,10,9+max(1,fillw),27),color,r=min(2,max(0,int(fillw/2))))
   line([(10,11),(9+max(1,fillw)-1,11)],'#ffedb0',1)
 elif key=='charging':
  d.polygon([(34*S,9*S),(23*S,21*S),(30*S,21*S),(26*S,29*S),(40*S,16*S),(32*S,16*S)],fill='#ffe08a')
 elif key=='paused':
  box((24,12,28,26),accent,r=1);box((33,12,37,26),accent,r=1)
 elif key=='finished':line([(20,20),(27,26),(41,12)],accent,3)
 elif key=='unplugged':
  # Friendly resting battery with eyes and an unplugged cable cue.
  ellipse((21,15,24,18),'#ffda7c');ellipse((35,15,38,18),'#ffda7c')
  d.arc((25*S,18*S,35*S,24*S),0,180,fill='#ffda7c',width=S)
  line([(9,35),(18,35)],'#ddb65e',1);box((18,32,24,38),'#ddb65e',r=1)
  line([(25,33),(28,33)],'#ddb65e',1);line([(25,37),(28,37)],'#ddb65e',1)
 elif key=='offline':line([(24,13),(37,26)],'#e69f7c',2);line([(37,13),(24,26)],'#e69f7c',2)
 elif key=='ready':
  box((25,15,36,24),accent,r=2);line([(27,10),(27,15)],accent,2);line([(34,10),(34,15)],accent,2);line([(30,24),(30,29)],accent,2)
 else:
  for x in (22,30,38):ellipse((x,18,x+2,20),accent)
 line([(10,7),(49,7)],'#fff1bf',1)
 # Double the artwork, trimming only empty outer padding to fit the card.
 im=im.resize((128,80),Image.LANCZOS).crop((0,8,128,78))
 raw=b''.join((((r>>3)<<11)|((g>>2)<<5)|(b>>3)).to_bytes(2,'big') for r,g,b in im.getdata())
 sprites[key]=base64.b64encode(zlib.compress(raw)).decode()
 if key in ('unplugged','charging','paused','78'):im.resize((256,160)).save(P/('battery-preview-'+key+'.png'))
(P/'batteries.json').write_text(json.dumps(sprites))
