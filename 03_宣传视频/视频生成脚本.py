from PIL import Image, ImageDraw, ImageFont
import os, subprocess

# Original motion-graphics generator. No stock characters, generated child portraits,
# or claims that the illustrated scenes are real kindergarten activities.
W, H, FPS, DURATION = 720, 1280, 24, 12
OUT = os.path.join(os.path.dirname(__file__), "成片")

def first_existing(paths):
    for path in paths:
        if os.path.isfile(path):
            return path
    return None

SANS = first_existing([
    "C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/simhei.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
])
REG = first_existing([
    "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
])
SERIF = first_existing([
    "C:/Windows/Fonts/simsun.ttc", "C:/Windows/Fonts/STSONG.TTF",
    "/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf"
]) or REG or SANS

PAPER=(243,240,232); INK=(29,48,41); GREEN=(29,73,56)
RED=(180,59,46); MUTED=(83,99,90); LINE=(201,200,189); PALE=(231,227,216)

def font(size, kind="sans"):
    path={"sans":SANS,"reg":REG,"serif":SERIF}[kind]
    return ImageFont.truetype(path,size) if path else ImageFont.load_default()

def txt(draw,xy,text,size,color=INK,kind="sans",anchor=None):
    draw.text(xy,text,font=font(size,kind),fill=color,anchor=anchor)

def smooth(x):
    return x*x*(3-2*x)

SCENES=[
 [('安全小卫士','平安伴成长','认识标识 / 学习规则 / 知道求助','从熟悉的日常开始'),('先看懂提示','认识安全出口与方向标识','观察图形，听成人解释','01 / 看见'),('再练习动作','排队慢行，不推挤、不追逐','把提醒变成能做到的动作','02 / 练习'),('遇到问题会求助','告诉身边可信赖的成人','安全教育不止于一次主题活动','03 / 求助')],
 [('把安全做成日常','三个小步骤，一起练习','看见 / 听懂 / 做到','安全主题内容提案'),('第一步：看见','找到身边的安全标识','先观察，再理解方向','01 / 观察'),('第二步：听懂','听从成人清楚的指引','规则要具体，孩子才知道怎么做','02 / 理解'),('第三步：做到','慢行、有序，及时求助','把安全提醒放进每天的生活','03 / 行动')],
 [('一份安全小约定','看见 · 记住 · 做到','给孩子清楚、适龄的提醒','家园共育主题'),('看见','留意公共区域的安全提示','先停下来观察，不急着跑过去','01 / 看见'),('记住','听从老师和成人的指引','不推挤、不逗留、不擅自离队','02 / 记住'),('做到','需要帮助时主动说出来','知道可以求助，也知道向谁求助','03 / 做到')]
]

def base(style,scene,local):
    im=Image.new("RGB",(W,H),PAPER if style!=1 else (239,238,228))
    d=ImageDraw.Draw(im)
    d.rectangle((32,32,W-32,H-32),outline=LINE,width=2)
    txt(d,(64,68),"园务编辑部  /  安全主题提案",18,RED)
    txt(d,(W-64,68),f"{scene+1:02d} / 04",18,MUTED,anchor="ra")
    d.line((64,112,W-64,112),fill=INK,width=2)
    title,sub,detail,tag=SCENES[style][scene]
    lift=int(24*(1-smooth(min(1,local*2))))
    if scene==0:
        txt(d,(64,220-lift),"AUTUMN / SAFETY",18,RED)
        txt(d,(64,360-lift),title,58,INK,"serif")
        txt(d,(64,455-lift),sub,62,GREEN,"serif")
        d.rectangle((64,515,64+int(210*smooth(min(1,local*2))),523),fill=RED)
        txt(d,(64,600),detail,24,MUTED,"reg")
        cx,cy=360,850
        d.ellipse((cx-155,cy-155,cx+155,cy+155),outline=RED,width=3)
        pts=[(cx,cy-112),(cx+84,cy-82),(cx+84,cy+8),(cx,cy+118),(cx-84,cy+8),(cx-84,cy-82)]
        d.polygon(pts,fill=GREEN)
        d.line((cx-38,cy+5,cx-8,cy+36,cx+46,cy-35),fill=PAPER,width=14)
        txt(d,(64,1080),tag,20,RED)
    else:
        txt(d,(64,210),f"{scene:02d}",148,PALE,"serif")
        txt(d,(66,410-lift),tag,18,RED)
        txt(d,(64,520-lift),title,48,INK,"serif")
        d.line((64,590,656,590),fill=RED,width=4)
        txt(d,(64,670),sub,27,GREEN)
        txt(d,(64,735),detail,21,MUTED,"reg")
        if style==1:
            y=965; xs=[120,360,600]
            d.line((xs[0],y,xs[2],y),fill=LINE,width=8)
            prog=xs[0]+(xs[2]-xs[0])*smooth(min(1,local*1.5))
            d.line((xs[0],y,prog,y),fill=RED,width=8)
            for i,x in enumerate(xs):
                fill=RED if i<=scene-1 else GREEN if i==scene else PAPER
                d.ellipse((x-28,y-28,x+28,y+28),fill=fill,outline=INK,width=2)
                txt(d,(x,y+65),["看见","听懂","做到"][i],18,INK,anchor="mm")
        elif style==2:
            for i,label in enumerate(["先观察","听从指引","及时求助"]):
                y=900+i*74
                d.rounded_rectangle((68,y,108,y+40),radius=5,outline=GREEN,width=3)
                if i<=scene-1:
                    d.line((76,y+20,88,y+32,101,y+9),fill=RED,width=5)
                txt(d,(132,y+20),label,23,INK,anchor="lm")
        else:
            d.rectangle((90,900,630,1060),fill=PALE)
            d.rectangle((120,930,600,1030),outline=INK,width=2)
            txt(d,(360,980),f"{scene:02d}   /   {tag.split(' / ')[-1]}",25,RED,anchor="mm")
    d.line((64,1155,656,1155),fill=LINE,width=2)
    txt(d,(64,1182),"模拟动态图形 / 非真实园所活动记录",15,MUTED,"reg")
    d.rectangle((64,1218,656,1225),fill=LINE)
    d.rectangle((64,1218,64+int(592*((scene+local)/4)),1225),fill=RED)
    return im

def render(style,t):
    scene=min(3,int(t/3)); local=(t-scene*3)/3
    im=base(style,scene,local)
    if scene<3 and local>0.88:
        nxt=base(style,scene+1,0)
        im=Image.blend(im,nxt,smooth((local-0.88)/0.12)*0.18)
    return im

def main():
    os.makedirs(OUT,exist_ok=True)
    names=["01_编辑部纪实风.mp4","02_路径信息图风.mp4","03_清单排版风.mp4"]
    for style,name in enumerate(names):
        path=os.path.join(OUT,name)
        cmd=["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","slow","-crf","20","-pix_fmt","yuv420p","-movflags","+faststart",path]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for frame in range(FPS*DURATION):
            proc.stdin.write(render(style,frame/FPS).tobytes())
        proc.stdin.close()
        if proc.wait()!=0:
            raise RuntimeError("FFmpeg failed: "+name)
        print("Generated:",path)

if __name__=="__main__":
    main()
