# -*- coding: utf-8 -*-
"""
作品集验收测试脚本（真实执行，不做任何模拟断言）
用法: python run_tests.py            # 运行全部测试
      python run_tests.py --json     # 追加输出 JSON 结果
覆盖: 文件完整性 / 图片规格 / 封面规格 / 视频元数据 / 文档可读性 / 图文字数
"""
import os, sys, json, subprocess, wave, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 作品集根目录
results = []

def check(case_id, name, expect, actual_ok, detail):
    results.append({"id": case_id, "case": name, "expect": expect,
                    "result": "通过" if actual_ok else "不通过", "detail": detail})

def p(rel):
    return os.path.join(BASE, rel)

# ---------- T1 文件完整性 ----------
PHOTOS = ["IMG_2401_活动拱门与主题横幅", "IMG_2402_操场场地布置全景", "IMG_2403_主题宣传海报",
          "IMG_2404_交通安全体验区", "IMG_2405_消防安全体验区", "IMG_2406_防拐骗情景演练道具",
          "IMG_2407_安全小卫士签到板", "IMG_2408_安全知识四大展板", "IMG_2409_活动物资准备平铺",
          "IMG_2410_教师示范避险动作", "IMG_2411_秋日校园氛围", "IMG_2412_活动流程指示牌",
          "IMG_2413_安全小卫士打卡墙"]
missing = [f for f in PHOTOS if not os.path.isfile(p(f"01_原图照片/{f}.jpg"))]
check("T1-1", "13 张活动照片齐全", "13/13 存在", not missing,
      "缺失: " + (", ".join(missing) if missing else "无"))

CONTRAST = [f"{n}_{s}" for n in ["IMG_2401_活动拱门与主题横幅", "IMG_2404_交通安全体验区", "IMG_2411_秋日校园氛围"]
            for s in ["调整前", "调整后", "前后对比"]]
missing = [f for f in CONTRAST if not os.path.isfile(p(f"02_修图对比/{f}.jpg"))]
check("T1-2", "3 组修图对比齐全（9 个文件）", "9/9 存在", not missing,
      "缺失: " + (", ".join(missing) if missing else "无"))

must = ["README.md", "03_宣传视频/秋季安全教育主题活动_宣传视频_41秒.mp4",
        "03_宣传视频/视频分镜脚本_剪映制作对照表.md",
        "04_封面图/公众号头条封面_900x383.png", "04_封面图/公众号次条封面_200x200.png",
        "05_公众号图文稿/公众号图文稿_秋季安全教育主题活动.md",
        "05_公众号图文稿/公众号图文稿_秋季安全教育主题活动.docx",
        "06_素材清单/素材清单与文件夹说明.md",
        "07_操作流程文档/从拍摄到发布_全流程操作文档.md",
        "07_操作流程文档/从拍摄到发布_全流程操作文档.docx",
        "07_操作流程文档/真实幼儿园公众号推文拆解笔记.md",
        "08_设计文档/设计文档.md", "10_面试准备/面试问题及回答准备.md",
        "docs/index.html"]
missing = [f for f in must if not os.path.isfile(p(f))]
check("T1-3", "核心交付文件齐全", "14/14 存在", not missing,
      "缺失: " + (", ".join(missing) if missing else "无"))

# ---------- T2 图片规格 ----------
try:
    from PIL import Image
    ok, details = True, []
    for f in PHOTOS:
        im = Image.open(p(f"01_原图照片/{f}.jpg"))
        if im.size != (1600, 1200):
            ok = False; details.append(f"{f}: {im.size}")
    check("T2-1", "活动照片尺寸统一 1600×1200 JPG", "13 张全部符合", ok,
          "异常: " + (", ".join(details) if details else "无"))
    c1 = Image.open(p("04_封面图/公众号头条封面_900x383.png"))
    c2 = Image.open(p("04_封面图/公众号次条封面_200x200.png"))
    ok = c1.size == (900, 383) and c2.size == (200, 200)
    check("T2-2", "公众号封面规格（头条 900×383 / 次条 200×200）", "符合微信官方比例",
          ok, f"头条 {c1.size}，次条 {c2.size}")
except ImportError:
    check("T2-1", "图片规格", "PIL 可用", False, "未安装 Pillow，无法校验")

# ---------- T3 视频元数据 ----------
V = p("03_宣传视频/秋季安全教育主题活动_宣传视频_41秒.mp4")
try:
    r = subprocess.run(["ffmpeg", "-i", V], capture_output=True, text=True)
    info = r.stderr
    import re
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    res = re.search(r"(\d{3,4})x(\d{3,4})", info)
    fps = re.search(r"([\d.]+) fps", info)
    has_audio = "Audio:" in info
    seconds = int(dur.group(1))*3600 + int(dur.group(2))*60 + float(dur.group(3))
    ok = 30 <= seconds <= 60 and res and res.group(1) == "1280" and has_audio
    check("T3-1", "视频时长 30–60 秒、720P、含音轨",
          "30–60s / 1280x720 / 有音轨", ok,
          f"实际 {seconds:.1f}s / {res.group(1)}x{res.group(2) if res else '?'} / 音轨{'有' if has_audio else '无'} / {fps.group(1) if fps else '?'}fps")
except FileNotFoundError:
    check("T3-1", "视频元数据", "ffmpeg 可用", False, "未安装 ffmpeg，无法校验")

# ---------- T4 文档可读性 ----------
try:
    import docx as docxlib
    a = docxlib.Document(p("05_公众号图文稿/公众号图文稿_秋季安全教育主题活动.docx"))
    b = docxlib.Document(p("07_操作流程文档/从拍摄到发布_全流程操作文档.docx"))
    ok = len(a.paragraphs) > 10 and len(b.paragraphs) > 10
    check("T4-1", "两份 Word 文档可正常解析", "段落结构完整", ok,
          f"图文稿 {len(a.paragraphs)} 段 / 流程文档 {len(b.paragraphs)} 段")
except Exception as e:
    check("T4-1", "Word 文档可读性", "可解析", False, str(e))

# ---------- T5 图文稿字数 ----------
try:
    txt = open(p("05_公众号图文稿/公众号图文稿_秋季安全教育主题活动.md"), encoding="utf-8").read()
    body = txt.split("**【导语】**")[1].split("## 排版说明")[0]
    cn = sum(1 for ch in body if '\u4e00' <= ch <= '\u9fff')
    check("T5-1", "正文汉字数 600–800", "600–800 字", 600 <= cn <= 800, f"实际 {cn} 字")
except Exception as e:
    check("T5-1", "图文字数", "600–800 字", False, str(e))

# ---------- T6 README 基本项 ----------
try:
    rd = open(p("README.md"), encoding="utf-8").read()
    items = ["安装", "运行", "目录结构", "成果", "技术难点"]
    miss = [k for k in items if k not in rd]
    check("T6-1", "README 含安装/运行/目录/成果/难点章节", "5/5 章节齐备", not miss,
          "缺失章节: " + (", ".join(miss) if miss else "无"))
except Exception as e:
    check("T6-1", "README", "存在且含关键章节", False, str(e))

# ---------- 汇总 ----------
passed = sum(1 for r in results if r["result"] == "通过")
report = {"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          "passed": passed, "total": len(results), "results": results}
print("=" * 62)
print(f"作品集验收测试  {report['time']}")
print("=" * 62)
for r in results:
    mark = "PASS" if r["result"] == "通过" else "FAIL"
    print(f"[{mark}] {r['id']} {r['case']}")
    print(f"       期望: {r['expect']} ｜ 实际: {r['detail']}")
print("-" * 62)
print(f"结果: {passed}/{len(results)} 通过")
if "--json" in sys.argv:
    with open(os.path.join(BASE, "09_验收测试", "last_run.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("JSON 已写入 09_验收测试/last_run.json")
sys.exit(0 if passed == len(results) else 1)
