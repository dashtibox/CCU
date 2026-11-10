from PIL import Image,ImageDraw,ImageFont
import math,json,pathlib
p=pathlib.Path(__file__).parent
im=Image.new('RGB',(320,240));d=ImageDraw.Draw(im)
for y in range(240):
 for x in range(320):
  glow=max(0,1-abs(y-(175+25*math.sin(x/70)))/65)
  d.point((x,y),fill=(2,int(23+25*glow),int(22+13*glow)))
for off in range(0,30,4):
 d.line([(x,int(185+off+20*math.sin(x/75))) for x in range(320)],fill=(3,65+off,52),width=1)
f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
b='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
# Render the supplied brand asset directly with high-quality downsampling.
logo=Image.open(p/'logo-original.png').convert('RGB')
small=logo.resize((110,39),Image.LANCZOS)
im.paste(small,(9,4))
d.text((132,7),'ChargeBridge',font=ImageFont.truetype(b,16),fill='white')
d.text((132,27),'Monitoring',font=ImageFont.truetype(f,12),fill='#a8daca')
for y in (48,126):
 d.rounded_rectangle((9,y,310,y+70),radius=9,fill='#07372f',outline='#22735c',width=1)
for y,n,link in [(54,1,'USB'),(132,2,'ETH')]:
 d.text((18,y),f'ACDC #{n}',font=ImageFont.truetype(b,15),fill='white')
 d.text((265,y+2),link,font=ImageFont.truetype(f,10),fill='#a8daca')
d.text((12,222),'VIS  |  ChargeBridge monitoring',font=ImageFont.truetype(f,9),fill='#a8daca')
def rgb565(im):
 return b''.join((((r>>3)<<11)|((g>>2)<<5)|(b>>3)).to_bytes(2,'big') for r,g,b in im.getdata())
(p/'background.rgb565').write_bytes(rgb565(im));im.save(p/'preview-background.png')
splash=Image.new('RGB',(320,240),'#fdfdfd')
large=logo.resize((304,107),Image.LANCZOS)
splash.paste(large,(8,54))
sd=ImageDraw.Draw(splash)
sd.text((63,187),'ChargeBridge Monitoring',font=ImageFont.truetype(b,13),fill='#30532a')
sd.text((104,210),'Starting CCU...',font=ImageFont.truetype(f,11),fill='#496745')
(p/'splash.rgb565').write_bytes(rgb565(splash));splash.save(p/'preview-splash.png')
fonts={}
for size in (11,13):
 font=ImageFont.truetype(b if size==13 else f,size);chars={}
 for c in map(chr,range(32,127)):
  a=Image.new('L',(20,20));ImageDraw.Draw(a).text((0,-2),c,font=font,fill=255)
  chars[c]={'w':round(font.getlength(c)), 'pixels':[(x,y,v) for y in range(20) for x in range(20) if (v:=a.getpixel((x,y)))>40]}
 fonts[str(size)]=chars
(p/'fonts.json').write_text(json.dumps(fonts))
