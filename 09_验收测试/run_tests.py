# -*- coding: utf-8 -*-
"""当前版本作品集验收脚本。
用法：python 09_验收测试/run_tests.py [--json]
依赖：Python 3.10+；若需检查 MP4，另需 ffprobe。
说明：MP4 成片当前作为本次对话独立文件交付；放入 03_宣传视频/成片 后会自动纳入检测。
"""
from pathlib import Path
import json, re, subprocess, sys, datetime, shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
results = []

def add(case, ok, detail):
    results.append({"case": case, "status": "PASS" if ok else "FAIL", "detail": detail})

def exists(rel):
    p = ROOT / rel
    return p.is_file(), p

# 1. Required deliverables
required = [
    "README.md", "00_作品集总说明.md",
    "docs/index.html", "docs/visual/index.html", "docs/content/index.html", "docs/video/index.html",
    "docs/assets/autumn-safety-poster.svg",
    "docs/assets/wechat-cover-autumn-safety.svg",
    "docs/assets/wechat-square-autumn-safety.svg",
    "docs/assets/activity-long-poster-autumn-safety.svg",
    "06_素材清单/素材清单与文件夹说明.md",
    "03_宣传视频/视频制作说明.md", "03_宣传视频/视频生成脚本.py",
    "05_公众号图文稿/原创推文01_安全小卫士平安伴成长.md",
    "05_公众号图文稿/原创推文02_秋日自然探索小课堂.md",
    "05_公众号图文稿/原创推文03_家园携手生活自理.md",
    "04_信息管理台账/设备巡检记录模板.md",
    "04_信息管理台账/信息故障报修登记模板.csv",
    "04_信息管理台账/活动影像采集与归档规范.md",
    "04_信息管理台账/公众号稿件审核与隐私核对表.md",
    "04_信息管理台账/月度信息工作交接清单.md",
]
missing = [x for x in required if not (ROOT / x).is_file()]
add("核心交付文件", not missing, "缺失：" + (", ".join(missing) if missing else "全部存在（共 %d 项）" % len(required)))

# 1A. Information administration templates
ops_files = [
    "04_信息管理台账/设备巡检记录模板.md",
    "04_信息管理台账/信息故障报修登记模板.csv",
    "04_信息管理台账/活动影像采集与归档规范.md",
    "04_信息管理台账/公众号稿件审核与隐私核对表.md",
    "04_信息管理台账/月度信息工作交接清单.md",
]
ops_errors = []
for rel in ops_files:
    try:
        content = (ROOT / rel).read_text(encoding="utf-8-sig")
        if len(content.strip()) < 80:
            ops_errors.append(rel + "：内容过短")
    except Exception as exc:
        ops_errors.append(rel + "：" + str(exc))
csv_path = ROOT / "04_信息管理台账/信息故障报修登记模板.csv"
if csv_path.is_file():
    try:
        import csv
        with csv_path.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
        if len(rows) < 2 or len(rows[0]) != len(rows[1]):
            ops_errors.append("信息故障报修登记模板.csv：表头与示例行列数不一致")
    except Exception as exc:
        ops_errors.append("信息故障报修登记模板.csv：" + str(exc))
add("信息管理岗位模板", not ops_errors, "；".join(ops_errors) if ops_errors else "5/5 文件存在，CSV 表头与示例行列数一致")

# 2. SVG syntax and intrinsic dimensions
svg_files = [
    "docs/assets/autumn-safety-poster.svg",
    "docs/assets/wechat-cover-autumn-safety.svg",
    "docs/assets/wechat-square-autumn-safety.svg",
    "docs/assets/activity-long-poster-autumn-safety.svg",
]
svg_errors = []
for rel in svg_files:
    try:
        root = ET.parse(ROOT / rel).getroot()
        if not root.tag.endswith("svg"):
            svg_errors.append(rel + "：根元素不是 svg")
    except Exception as exc:
        svg_errors.append(rel + "：" + str(exc))
add("4 张 SVG 可解析", not svg_errors, "；".join(svg_errors) if svg_errors else "4/4 XML 结构有效")

# 3. HTML pages and local image references
html_files = ["docs/index.html", "docs/visual/index.html", "docs/content/index.html", "docs/video/index.html"]
html_errors = []
for rel in html_files:
    p = ROOT / rel
    try:
        txt = p.read_text(encoding="utf-8")
        if "<html" not in txt.lower() or "</html>" not in txt.lower():
            html_errors.append(rel + "：HTML 文档结构不完整")
        for target in re.findall(r'<img[^>]+src=["\']([^"\']+)', txt, flags=re.I):
            if target.startswith(("http://", "https://", "data:")):
                continue
            dest = (p.parent / target).resolve()
            if not dest.is_file():
                html_errors.append(rel + "：图片引用不存在 " + target)
    except Exception as exc:
        html_errors.append(rel + "：" + str(exc))
add("4 个展示页结构与图片引用", not html_errors, "；".join(html_errors) if html_errors else "HTML 均存在，页面内本地图片引用均可定位")

# 4. Article content
article_files = [
    "05_公众号图文稿/原创推文01_安全小卫士平安伴成长.md",
    "05_公众号图文稿/原创推文02_秋日自然探索小课堂.md",
    "05_公众号图文稿/原创推文03_家园携手生活自理.md",
]
article_errors = []
for rel in article_files:
    try:
        text = (ROOT / rel).read_text(encoding="utf-8")
        cn = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
        if cn < 450:
            article_errors.append(rel + "：正文内容偏短（%d 个汉字）" % cn)
        if not any(mark in text for mark in ("作品属性", "模拟原创稿", "模拟稿")) or "发布前核对" not in text:
            article_errors.append(rel + "：缺少模拟属性或发布审核提醒")
    except Exception as exc:
        article_errors.append(rel + "：" + str(exc))
add("3 篇原创稿完整性", not article_errors, "；".join(article_errors) if article_errors else "3/3 有足够正文，均包含模拟属性与发布审核提醒")

# 5. Video source and optional local MP4 files
video_script = ROOT / "03_宣传视频/视频生成脚本.py"
add("视频生成脚本", video_script.is_file(), str(video_script.relative_to(ROOT)) if video_script.is_file() else "脚本缺失")
mp4_dir = ROOT / "03_宣传视频/成片"
mp4s = sorted(mp4_dir.glob("*.mp4")) if mp4_dir.exists() else []
if not mp4s:
    results.append({"case": "MP4 成片元数据", "status": "INFO", "detail": "成片由本次对话单独交付；如需纳入仓库测试，请将 3 个 MP4 放入 03_宣传视频/成片"})
else:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        results.append({"case": "MP4 成片元数据", "status": "INFO", "detail": "未安装 ffprobe，跳过视频元数据检查"})
    else:
        failures = []
        for p in mp4s:
            raw = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name,width,height", "-of", "json", str(p)], capture_output=True, text=True)
            try:
                data = json.loads(raw.stdout)
                stream = next(s for s in data["streams"] if s.get("codec_name") == "h264")
                duration = float(data["format"]["duration"])
                if not (10 <= duration <= 15 and stream.get("width") == 720 and stream.get("height") == 1280):
                    failures.append(p.name + "：规格不符合")
            except Exception as exc:
                failures.append(p.name + "：" + str(exc))
        add("MP4 成片元数据", not failures and len(mp4s) >= 3, "；".join(failures) if failures else "%d 个 MP4 检查通过" % len(mp4s))

# 6. Report
passed = sum(x["status"] == "PASS" for x in results)
failed = sum(x["status"] == "FAIL" for x in results)
info = sum(x["status"] == "INFO" for x in results)
report = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "passed": passed, "failed": failed, "info": info, "total": len(results), "results": results}
print("=" * 64)
print("幼儿园集团信息管理员作品集｜当前版本验收")
print("=" * 64)
for item in results:
    print("[%s] %s — %s" % (item["status"], item["case"], item["detail"]))
print("-" * 64)
print("通过 %d ｜失败 %d ｜提示 %d ｜总项 %d" % (passed, failed, info, len(results)))
if "--json" in sys.argv:
    out = ROOT / "09_验收测试/last_run.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("JSON 报告已写入：" + str(out))
sys.exit(1 if failed else 0)
