"""Combine 1:1 phone-size render crops and measure the authored mint cue."""
import json
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont

directory=Path(sys.argv[1])
report=Path(sys.argv[2])
out=Image.new('RGB',(960,732),'#18252d')
draw=ImageDraw.Draw(out)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=lambda size: ImageFont.truetype(font_path,size)
draw.text((32,26),'W3C  /  SWING TARGET',font=font(30),fill='#e9e5d6')
draw.text((33,65),'Three distances · 402 × 874 source frames · no bloom',font=font(16),fill='#a0b1b4')
draw.text((178,102),'REST',font=font(16),fill='#e9e5d6')
draw.text((575,102),'IMPACT  /  0.183 s',font=font(16),fill='#70e4c1')
counts={}
for i,d in enumerate((25,50,75)):
    row=136+i*184
    draw.text((34,row+60),f'{d} m',font=font(22),fill='#e9e5d6')
    for k,f in enumerate((0,11)):
        raw=Image.open(directory/f'w3c-target-{d}m-{f}.png').convert('RGB')
        assert raw.size==(402,874)
        clip=raw.crop((145,400,257,505))
        hits=sum(1 for r,g,b in clip.get_flattened_data() if g-r>25 and b-r>15 and g>125) if hasattr(clip,'get_flattened_data') else sum(
            1 for r,g,b in clip.getdata() if g-r>25 and b-r>15 and g>125)
        counts.setdefault(d,[]).append(hits)
        x=(176,572)[k]
        out.paste(raw.crop((119,398,283,480)).resize((328,164),Image.Resampling.NEAREST),(x,row))
        draw.rectangle((x-1,row-1,x+328,row+164),outline='#45555d')
draw.text((32,702),'2× crops for comparison. Counts are pixel measurements, not a phone playtest.',font=font(15),fill='#a0b1b4')
assert all(a==0 and b>=15 for a,b in counts.values()),counts
out.save(directory/'w3c-target-impact-review.png')
q=json.loads(report.read_text());q['mintPixelsIdleImpact']=counts;q['reviewResolution']=[402,874]
report.write_text(json.dumps(q,indent=2)+'\n')
