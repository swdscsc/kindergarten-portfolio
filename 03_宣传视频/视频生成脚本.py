from PIL import Image, ImageDraw, ImageFont
import os, subprocess

# 原创动态图形视频生成器：三种视觉风格，共同主题，不使用真实人物影像。
W, H, FPS, DURATION = 720, 1280, 24, 12
def first_existing(paths):
    for item in paths:
        if os.path.isfile(item):
            return item
    return None

FONT = first_existing([
    "C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/simhei.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
])
REGULAR = first_existing([
    "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
])
OUT = os.path.join(os.path.dirname(__file__), "成片")
os.makedirs(OUT, exist_ok=True)

SCENES = [
    [("安全小卫士","平安伴成长","秋季安全教育主题活动"),("认识安全标识","看懂方向 · 记住提示","从身边的图形开始学习"),("学习安全规则","听从指引 · 不推不挤","把安全行为练在日常"),("共同守护成长","家园携手 · 安心相伴","创意模拟视频｜非真实活动记录")],
    [("今天的安全任务","发现身边的安全线索","观察 · 讨论 · 练习"),("任务 01","找到安全出口标识","认识图形，理解方向"),("任务 02","记住有序行动规则","不推挤、不逗留、不返回取物"),("任务完成","让安全成为日常习惯","创意模拟视频｜非真实活动记录")],
    [("一份安全小约定","从认识开始","看见标识，听从指引"),("看见","认识常见安全标识","观察身边的安全提示"),("记住","听从老师和成人指引","不推挤、不逗留"),("做到","把安全习惯带进生活","创意模拟视频｜非真实活动记录")]
]

def ft(size, bold=True):
    path = FONT if bold else REGULAR
    return ImageFont.truetype(path, size) if path else ImageFont.load_default()

def centered(draw, text, y, f, color):
    box = draw.textbbox((0,0), text, font=f)
    draw.text(((W-(box[2]-box[0]))/2, y), text, font=f, fill=color)

def render(style, scene, local):
    cream=(247,244,233); green=(38,76,57); sage=(220,232,216)
    orange=(212,119,78); ink=(32,62,49); muted=(95,116,101)
    title, sub, foot = SCENES[style][scene]
    im=Image.new("RGB",(W,H), cream if style != 1 else (238,243,232))
    d=ImageDraw.Draw(im)
    if style == 0:
        shift=int(local*30)
        d.ellipse((400-shift,70,870-shift,540),fill=(232,220,197))
        d.ellipse((-180+shift,800,430+shift,1410),fill=sage)
        d.rounded_rectangle((48,54,672,1226),radius=30,outline=(203,215,199),width=2)
        d.text((82,92),"AUTUMN / SAFETY",font=ft(20),fill=orange)
        centered(d,title,360,ft(57),ink); centered(d,sub,480,ft(28,False),muted)
        d.rounded_rectangle((160,590,560,596),radius=3,fill=orange)
        cx,cy=360,790
        d.polygon([(cx,cy-125),(cx+105,cy-88),(cx+105,cy+10),(cx,cy+150),(cx-105,cy+10),(cx-105,cy-88)],fill=green)
        d.line((cx-48,cy+2,cx-10,cy+42,cx+55,cy-38),fill=cream,width=17,joint="curve")
        centered(d,foot,1080,ft(20,False),muted)
    elif style == 1:
        d.ellipse((430,60,830,460),fill=(245,184,139))
        d.ellipse((-160,830,300,1290),fill=(194,218,190))
        for i in range(9):
            x=(i*97+int(local*28))%760-20; y=220+(i%3)*270
            d.ellipse((x,y,x+12,y+12),fill=orange)
        d.rounded_rectangle((52,220,668,1030),radius=42,fill=(255,253,246))
        d.rounded_rectangle((86,260,634,330),radius=25,fill=green)
        d.text((116,278),"SAFE PLAY / MISSION",font=ft(20),fill=cream)
        centered(d,title,430,ft(52),ink); centered(d,sub,545,ft(26,False),muted)
        d.line((160,770,560,770),fill=(205,216,202),width=13)
        for i,x in enumerate((170,360,550),1):
            d.ellipse((x-48,722,x+48,818),fill=orange if i==2 else green)
            d.text((x-13,737),str(i),font=ft(42),fill=cream)
        centered(d,foot,1100,ft(18,False),muted)
    else:
        d.rectangle((0,0,W,18),fill=green)
        d.text((70,82),"A SMALL SAFETY GUIDE",font=ft(18),fill=orange)
        d.text((70,180),f"{scene+1:02d}",font=ft(128),fill=sage)
        d.text((70,390),title,font=ft(52),fill=ink)
        d.rounded_rectangle((70,500,650,504),radius=2,fill=orange)
        d.text((70,560),sub,font=ft(27,False),fill=muted)
        d.rounded_rectangle((70,710,650,970),radius=22,fill=(255,253,246),outline=(215,222,210),width=2)
        for j,txt in enumerate(["先观察","再理解","记住并实践"]):
            y=755+j*68
            d.rounded_rectangle((104,y,140,y+36),radius=9,outline=green,width=3)
            d.line((112,y+18,122,y+28,136,y+9),fill=orange,width=4)
            d.text((165,y-2),txt,font=ft(25),fill=ink)
        d.text((70,1110),foot,font=ft(18,False),fill=muted)
    progress=(scene+local)/4
    d.rounded_rectangle((70,1190,650,1200),radius=5,fill=(220,226,216))
    d.rounded_rectangle((70,1190,70+580*progress,1200),radius=5,fill=orange)
    return im

def main():
    names=["01_Editorial_Cinematic.mp4","02_Playful_Geometric.mp4","03_Minimal_Checklist.mp4"]
    for style,name in enumerate(names):
        path=os.path.join(OUT,name)
        cmd=["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","medium","-crf","25","-pix_fmt","yuv420p","-movflags","+faststart",path]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for frame in range(FPS*DURATION):
            t=frame/FPS; scene=min(3,int(t/3)); local=(t-scene*3)/3
            frame_image=render(style,scene,local)
            fade=min(1,local*5,(1-local)*5)
            if fade < 1:
                frame_image=Image.blend(Image.new("RGB",(W,H),(247,244,233)),frame_image,max(0,fade))
            proc.stdin.write(frame_image.tobytes())
        proc.stdin.close()
        if proc.wait()!=0: raise RuntimeError(f"FFmpeg failed: {name}")
        print(f"Generated: {path}")

if __name__ == "__main__":
    main()
