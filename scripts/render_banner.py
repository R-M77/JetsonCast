"""Render the compact banner from approved artwork (requires Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, json, argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True, help='directory for rendered previews')
parser.add_argument('--font-dir', type=Path, default=Path('C:/Windows/Fonts'), help='directory containing Segoe UI fonts')
args = parser.parse_args()
OUT = args.output
OUT.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[1]
ASSETS = REPO / 'assets'
S = 2
W, H = 840, 360
BG, FG, MINT, MUTED = '#09151d', '#f4f3ec', '#9de4ce', '#b4c3cb'

def font(size, bold=False):
    return ImageFont.truetype(str(args.font_dir / ('seguisb.ttf' if bold else 'segoeui.ttf')), round(size*S))

def rect(d, box, fill, radius=0, outline=None, width=1):
    d.rounded_rectangle(tuple(round(v*S) for v in box), radius*S, fill=fill, outline=outline, width=width*S)

def line(d, pts, fill, width=1):
    d.line([(round(x*S), round(y*S)) for x,y in pts],fill=fill,width=width*S)

def text(d, xy, value, size, fill=FG, bold=False):
    d.text((xy[0]*S,xy[1]*S),value,font=font(size,bold),fill=fill,spacing=7*S)

def cast(d, x, y, color=MINT):
    line(d,[(x,y+5),(x,y),(x+17,y),(x+17,y+13),(x+9,y+13)],color,1)
    for r in (4,8,12):
        d.arc(((x-r)*S,(y+14-r)*S,(x+r)*S,(y+14+r)*S),270,360,fill=color,width=2)
    rect(d,(x,y+12,x+2,y+14),color,1)

def art(name):
    return Image.open(ASSETS / name).convert('RGB').resize((390*S,219*S),Image.Resampling.LANCZOS)

coast = art('golden-coast.gif')
meadow = art('moonlit-meadow.gif')
sprites = [Image.open(ASSETS / n).convert('RGBA') for n in ('jet-open.png','jet-blink.png')]

def frame(t):
    phase = min(2,int(t/1.6))
    im=Image.new('RGB',(W*S,H*S),BG); d=ImageDraw.Draw(im)
    rect(d,(.5,.5,839,359),BG,14,'#2b3c48')
    text(d,(28,47),'Block YouTube',34,bold=True)
    text(d,(28,88),'ads on your TV.',34,bold=True)
    line(d,[(30,140),(99,140)],MINT,3)
    text(d,(28,161),'Upgrade an old TV with\na spare Linux computer.',21)
    texts=[('01  Connect via HDMI','Keep the TV you already have.'),
           ('02  Cast from YouTube','Your phone controls. No mirroring.'),
           ('03  Optional fun mode','Jet walks and peeks while idle.')]
    text(d,(28,274),texts[phase][0],19,MINT,True)
    text(d,(28,304),texts[phase][1],14,MUTED)
    # Small step marks; title and layout stay stationary.
    for i in range(3): rect(d,(28+i*23,339,43+i*23,341),MINT if i==phase else '#344652',1)
    # TV + spare PC: consistent silhouette and explicit HDMI connection.
    line(d,[(728,290),(728,302),(751,302),(751,313)],MINT,2)
    text(d,(746,289),'HDMI',10,MUTED)
    rect(d,(674,313,790,343),'#172731',6,'#70858f')
    text(d,(687,317),'Linux PC',16,bold=True)
    rect(d,(779,328,783,332),MINT,2)
    rect(d,(383,57,789,290),'#26343e',8,'#70858f',2)
    line(d,[(452,290),(443,304)],'#70858f',3)
    line(d,[(725,290),(734,304)],'#70858f',3)
    screen=coast.copy()
    if phase==1:
        sd=ImageDraw.Draw(screen)
        rect(sd,(13,200,377,204),'#26343e',2)
        rect(sd,(13,200,90+40*(t-1.6),204),MINT,2)
    if phase==2:
        screen=meadow.copy(); sd=ImageDraw.Draw(screen)
        # Fictional time, no account or live desktop data.
        text(sd,(285,12),'10:08',30)
        text(sd,(18,171),'Jetson Cast',18,bold=True)
        text(sd,(18,195),'Open YouTube on your phone · Tap Cast',10)
        u=min(1,max(0,(t-3.35)/.65)); ease=u*u*(3-2*u)
        sprite=sprites[1 if 4.15<=t<4.3 else 0]
        sw,sh=49*S,67*S
        sprite=sprite.resize((sw,sh),Image.Resampling.LANCZOS)
        screen.paste(sprite,(round(220*S),round((224-56*ease)*S)),sprite)
        if t<3.4: screen=Image.blend(coast,screen,max(0,(t-3.2)/.2))
    im.paste(screen,(391*S,65*S))
    # Simplified illustrated app controls: no duplicate video or private UI.
    rect(d,(349,174,426,335),'#13212b',12,'#9eb0b8',2)
    rect(d,(355,182,420,327),'#edf0ec',8)
    rect(d,(377,179,399,182),'#9eb0b8',1)
    rect(d,(361,197,373,205),'#ce3f37',3)
    d.polygon([(365*S,199*S),(365*S,203*S),(369*S,201*S)],fill='white')
    text(d,(376,194),'YouTube',9,'#18242c',True)
    color='#226f60' if phase==1 else '#526770'
    cast(d,390,215,color)
    if phase==1 and t<2.1:
        r=15+5*math.sin((t-1.6)*math.pi/.5)
        d.ellipse(((398-r)*S,(222-r)*S,(398+r)*S,(222+r)*S),outline='#4d9b86',width=2)
    text(d,(361,239),'TV playback',9,'#344852',True)
    rect(d,(370,260,375,274),'#344852',1)
    rect(d,(380,260,385,274),'#344852',1)
    d.polygon([(398*S,261*S),(398*S,274*S),(406*S,267*S)],fill='#344852')
    for y in (291,305):
        rect(d,(361,y,372,y+8),'#b7c9c9',2)
        rect(d,(377,y+1,411,y+3),'#78928e',1)
        rect(d,(377,y+6,400,y+7),'#b7c9c9',1)
    # Final state labels fun mode explicitly, rather than implying it is default.
    if phase==2:
        rect(d,(451,314,484,334),MINT,10)
        d.ellipse((467*S,317*S,481*S,331*S),fill=BG)
        text(d,(492,313),'Jet is optional',15,MINT,True)
    else:
        text(d,(451,315),'TV plays. Phone controls.',13,MUTED)
    return im.resize((W,H),Image.Resampling.LANCZOS)

frames=[frame(i/20) for i in range(96)]
# A shared palette avoids palette shifts/flicker. Static scenery compresses well.
palette_sheet=Image.new('RGB',(W,H*3))
for i,n in enumerate((0,40,95)): palette_sheet.paste(frames[n],(0,H*i))
palette=palette_sheet.quantize(colors=240,method=Image.Quantize.MEDIANCUT)
indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
indexed[0].save(OUT/'banner.gif',save_all=True,append_images=indexed[1:],duration=50,loop=0,optimize=True,disposal=1)
frames[95].save(OUT/'banner-poster.png')
for n in (0,40,95): frames[n].save(OUT/f'beat-{n:02}.png')
palette_sheet.save(OUT/'storyboard.png')
frames[95].resize((320,137),Image.Resampling.LANCZOS).save(OUT/'mobile-check.png')
gif=Image.open(OUT/'banner.gif')
duration=0
for i in range(gif.n_frames): gif.seek(i); duration+=gif.info.get('duration',0)
metadata={'size':gif.size,'duration_ms':duration,'encoded_frames':gif.n_frames,'loop':gif.info.get('loop','absent: play once'),'bytes':(OUT/'banner.gif').stat().st_size}
(OUT/'validation.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps(metadata))
