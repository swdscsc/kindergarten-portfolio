# -*- coding: utf-8 -*-
"""园务信息台｜本地演示版。仅供本机演示，勿直接部署公网。"""
from flask import Flask, request, redirect, url_for, render_template_string, flash
from pathlib import Path
import sqlite3
from datetime import datetime

BASE = Path(__file__).resolve().parent
DB = BASE / "data" / "campus_demo.db"
app = Flask(__name__)
app.secret_key = "local-demo-only-change-before-deployment"

SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
 id INTEGER PRIMARY KEY AUTOINCREMENT, asset_code TEXT UNIQUE NOT NULL,
 name TEXT NOT NULL, category TEXT NOT NULL, location TEXT DEFAULT '',
 owner TEXT DEFAULT '', status TEXT DEFAULT '在用', last_check TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS inspections (
 id INTEGER PRIMARY KEY AUTOINCREMENT, asset_id INTEGER, check_date TEXT NOT NULL,
 result TEXT NOT NULL, issue TEXT DEFAULT '', action TEXT DEFAULT '', checker TEXT DEFAULT '',
 FOREIGN KEY(asset_id) REFERENCES assets(id)
);
CREATE TABLE IF NOT EXISTS tickets (
 id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_no TEXT UNIQUE NOT NULL,
 created_at TEXT NOT NULL, department TEXT DEFAULT '', contact TEXT DEFAULT '',
 device TEXT NOT NULL, description TEXT NOT NULL, priority TEXT DEFAULT '普通',
 status TEXT DEFAULT '待受理', assignee TEXT DEFAULT '', resolution TEXT DEFAULT '',
 closed_at TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS media (
 id INTEGER PRIMARY KEY AUTOINCREMENT, event_date TEXT NOT NULL, event_name TEXT NOT NULL,
 material_type TEXT DEFAULT '照片', count INTEGER DEFAULT 0, permission_status TEXT DEFAULT '待核验',
 archive_path TEXT DEFAULT '', reviewer TEXT DEFAULT '', note TEXT DEFAULT ''
);
"""

def db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    with db() as c:
        c.executescript(SCHEMA)
        if c.execute("SELECT COUNT(*) FROM assets").fetchone()[0] == 0:
            c.executemany("""INSERT INTO assets(asset_code,name,category,location,owner,status,last_check)
            VALUES(?,?,?,?,?,?,?)""", [
                ("DEMO-PC-001","行政办公电脑","办公终端","行政办公室","行政组","在用","2026-11-01"),
                ("DEMO-AV-002","多媒体教学一体机","教学设备","大班活动室","信息管理员","在用","2026-10-30"),
                ("DEMO-PR-003","网络打印机","办公外设","资料室","行政组","维修中","2026-10-29"),
                ("DEMO-NET-004","无线接入设备","网络设备","一楼弱电箱","信息管理员","在用","2026-11-01"),
            ])
            c.executemany("""INSERT INTO tickets(ticket_no,created_at,department,contact,device,description,priority,status,assignee)
            VALUES(?,?,?,?,?,?,?,?,?)""", [
                ("DEMO-20261101-001","2026-11-01 09:20","行政办公室","演示联系人","网络打印机","打印任务无法正常输出（虚构案例）","普通","处理中","信息管理员"),
                ("DEMO-20261102-002","2026-11-02 10:05","大班活动室","演示联系人","教学一体机","开机后无信号，需检查输入源（虚构案例）","紧急","待受理",""),
            ])
            c.executemany("""INSERT INTO media(event_date,event_name,material_type,count,permission_status,archive_path,reviewer,note)
            VALUES(?,?,?,?,?,?,?,?)""", [
                ("2026-10-28","秋日自然观察（模拟）","照片",18,"仅内部演示","demo/2026/10/autumn/","待审核","虚构记录，不含真实儿童影像"),
                ("2026-11-01","安全主题图文（模拟）","图文",4,"已核验（模拟）","demo/2026/11/safety/","演示审核人","示例数据"),
            ])

LAYOUT = """
<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }} · 园务信息台</title><style>
:root{--ink:#24332f;--muted:#78847e;--line:#e6e9e3;--paper:#f7f8f4;--green:#456c59;--red:#b65343;--gold:#a77b39}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}
header{background:#fff;border-bottom:1px solid var(--line);padding:18px max(22px,calc((100vw - 1180px)/2));display:flex;justify-content:space-between;align-items:center;gap:20px}
.brand{font-weight:800;font-size:18px;letter-spacing:.04em}.brand small{display:block;color:var(--muted);font-size:11px;font-weight:500;letter-spacing:.14em}
nav{display:flex;gap:8px;flex-wrap:wrap}nav a{padding:8px 12px;border-radius:8px;color:#52625a;text-decoration:none;font-size:13px}nav a:hover,nav a.active{background:#edf2ec;color:var(--green)}
main{max-width:1180px;margin:30px auto;padding:0 22px}.eyebrow{color:var(--green);font-size:11px;letter-spacing:.16em;text-transform:uppercase;font-weight:700}
h1{font-size:28px;line-height:1.25;margin:7px 0 8px;letter-spacing:-.03em}h2{font-size:17px;margin:0 0 14px}.sub{color:var(--muted);margin:0 0 24px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.card{background:#fff;border:1px solid var(--line);border-radius:13px;padding:18px}.metric{font-size:30px;font-weight:750;letter-spacing:-.04em}.muted{color:var(--muted);font-size:13px}
.panel{background:#fff;border:1px solid var(--line);border-radius:13px;padding:20px;margin-top:18px}.panel-head{display:flex;justify-content:space-between;align-items:center;gap:12px}
.btn{display:inline-flex;border:0;background:var(--green);color:white;text-decoration:none;padding:9px 14px;border-radius:8px;font:inherit;font-size:13px;cursor:pointer}.btn.secondary{background:#eef2ed;color:var(--green)}.btn.danger{background:#f8ece9;color:var(--red)}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:12px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:600;background:#fbfcfa}tr:last-child td{border-bottom:0}
.pill{display:inline-block;padding:3px 8px;border-radius:30px;background:#edf2ed;color:var(--green);font-size:11px}.pill.warn{background:#fbf2e5;color:var(--gold)}.pill.bad{background:#f8ece9;color:var(--red)}
.formgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.field label{display:block;font-size:12px;color:var(--muted);margin-bottom:5px}.field input,.field select,.field textarea{width:100%;border:1px solid var(--line);background:#fff;border-radius:8px;padding:10px;font:inherit;color:var(--ink)}.field textarea{min-height:86px}.wide{grid-column:1/-1}.actions{display:flex;gap:9px;margin-top:18px}.notice{padding:12px 15px;background:#edf2ed;border-radius:9px;margin:0 0 14px;color:var(--green);font-size:13px}.warning{padding:12px 15px;background:#fbf2e5;border-radius:9px;color:#85652f;font-size:12px;margin:16px 0}
footer{max-width:1180px;margin:40px auto 0;padding:18px 22px 30px;color:var(--muted);font-size:12px;border-top:1px solid var(--line)}
@media(max-width:800px){header{align-items:flex-start;flex-direction:column}.grid{grid-template-columns:repeat(2,1fr)}.formgrid{grid-template-columns:1fr}.wide{grid-column:auto}main{margin-top:22px}h1{font-size:24px}.panel{overflow-x:auto}}
</style></head><body><header><div class="brand">园务信息台<small>CAMPUS INFORMATION DESK · DEMO</small></div>
<nav>{% for label,endpoint in nav %}<a class="{{ 'active' if request.endpoint==endpoint else '' }}" href="{{ url_for(endpoint) }}">{{label}}</a>{% endfor %}</nav></header>
<main>{% with messages=get_flashed_messages() %}{% if messages %}{% for m in messages %}<div class="notice">{{m}}</div>{% endfor %}{% endif %}{% endwith %}
<div class="eyebrow">INFORMATION OPERATIONS / 2026</div><h1>{{ title }}</h1><p class="sub">{{ subtitle }}</p>
<div class="warning">演示环境：页面内均为虚构数据。当前版本为本机单用户演示，不含登录、权限控制及生产级审计；请勿录入真实儿童、教职工或园所敏感信息，也不要直接部署到公网。</div>
{{ body|safe }}</main><footer>园务信息台 · Flask + SQLite · 本地演示作品 · 不代表真实园所运营记录</footer></body></html>
"""

NAV=[("总览","index"),("设备台账","assets"),("巡检记录","inspections"),("故障工单","tickets"),("素材归档","media")]

def page(title,subtitle,body):
    return render_template_string(LAYOUT,title=title,subtitle=subtitle,body=body,nav=NAV)

@app.get("/")
def index():
    with db() as c:
        stats={
          "assets":c.execute("SELECT COUNT(*) FROM assets").fetchone()[0],
          "issues":c.execute("SELECT COUNT(*) FROM assets WHERE status!='在用'").fetchone()[0],
          "open":c.execute("SELECT COUNT(*) FROM tickets WHERE status!='已完成'").fetchone()[0],
          "media":c.execute("SELECT COUNT(*) FROM media").fetchone()[0],
        }
        tickets=c.execute("SELECT * FROM tickets ORDER BY id DESC LIMIT 5").fetchall()
    body=render_template_string("""
    <div class="grid">
    {% for n,label,desc in [(s.assets,'设备资产','已登记设备'),(s.issues,'异常设备','状态非正常'),(s.open,'未完成工单','待受理或处理中'),(s.media,'素材归档','登记记录')] %}
    <div class="card"><div class="muted">{{label}}</div><div class="metric">{{n}}</div><div class="muted">{{desc}}</div></div>{% endfor %}</div>
    <section class="panel"><div class="panel-head"><h2>最近报修工单</h2><a class="btn secondary" href="{{url_for('tickets')}}">查看全部</a></div>
    <table><tr><th>工单编号</th><th>设备/系统</th><th>问题描述</th><th>优先级</th><th>状态</th></tr>
    {% for t in tickets %}<tr><td>{{t.ticket_no}}</td><td>{{t.device}}</td><td>{{t.description}}</td><td>{{t.priority}}</td><td><span class="pill {{'bad' if t.priority=='紧急' else 'warn' if t.status!='已完成' else ''}}">{{t.status}}</span></td></tr>{% else %}<tr><td colspan="5">暂无工单</td></tr>{% endfor %}</table></section>
    <section class="panel"><h2>工作闭环</h2><div class="grid" style="grid-template-columns:repeat(3,1fr)"><div><b>登记</b><p class="muted">设备建档、报修受理、素材登记</p></div><div><b>跟进</b><p class="muted">巡检记录、工单状态、授权核验</p></div><div><b>归档</b><p class="muted">处理结果、复核记录、资料留存</p></div></div></section>
    """,s=stats,tickets=tickets)
    return page("工作总览","把设备、巡检、报修和宣传素材放在同一个工作台。",body)

@app.route("/assets",methods=["GET","POST"])
def assets():
    with db() as c:
        if request.method=="POST":
            try:
                c.execute("INSERT INTO assets(asset_code,name,category,location,owner,status,last_check) VALUES(?,?,?,?,?,?,?)",
                (request.form["asset_code"].strip(),request.form["name"].strip(),request.form["category"],request.form.get("location",""),request.form.get("owner",""),request.form.get("status","在用"),request.form.get("last_check","")))
                c.commit(); flash("设备已登记。")
            except sqlite3.IntegrityError: flash("资产编号重复，请检查后重新提交。")
            return redirect(url_for("assets"))
        rows=c.execute("SELECT * FROM assets ORDER BY id DESC").fetchall()
    body=render_template_string("""
    <section class="panel"><h2>新增设备</h2><form method="post" class="formgrid">
    {% for name,label,ph in [('asset_code','资产编号','例如 DEMO-PC-005'),('name','设备名称','例如 办公电脑'),('category','设备类别','办公终端 / 教学设备 / 网络设备'),('location','所在位置','例如 行政办公室'),('owner','责任部门/人','例如 行政组'),('last_check','最近巡检日期','YYYY-MM-DD')] %}
    <div class="field"><label>{{label}}</label><input name="{{name}}" placeholder="{{ph}}" {{'required' if name in ['asset_code','name','category'] else ''}}></div>{% endfor %}
    <div class="field"><label>设备状态</label><select name="status"><option>在用</option><option>维修中</option><option>停用</option></select></div><div class="wide"><button class="btn">保存设备</button></div></form></section>
    <section class="panel"><h2>设备清单 · {{rows|length}} 项</h2><table><tr><th>编号</th><th>设备名称</th><th>类别</th><th>位置</th><th>责任人</th><th>状态</th><th>最近巡检</th></tr>{% for x in rows %}<tr><td>{{x.asset_code}}</td><td>{{x.name}}</td><td>{{x.category}}</td><td>{{x.location}}</td><td>{{x.owner}}</td><td><span class="pill {{'bad' if x.status!='在用' else ''}}">{{x.status}}</span></td><td>{{x.last_check or '—'}}</td></tr>{% endfor %}</table></section>
    """,rows=rows)
    return page("设备台账","统一记录资产编号、设备类别、位置、责任人和运行状态。",body)

@app.route("/inspections",methods=["GET","POST"])
def inspections():
    with db() as c:
        if request.method=="POST":
            aid=request.form.get("asset_id") or None
            c.execute("INSERT INTO inspections(asset_id,check_date,result,issue,action,checker) VALUES(?,?,?,?,?,?)",
            (aid,request.form["check_date"],request.form["result"],request.form.get("issue",""),request.form.get("action",""),request.form.get("checker","")))
            if aid: c.execute("UPDATE assets SET last_check=? WHERE id=?",(request.form["check_date"],aid))
            c.commit();flash("巡检记录已保存。");return redirect(url_for("inspections"))
        rows=c.execute("""SELECT i.*,a.name AS asset_name,a.asset_code FROM inspections i LEFT JOIN assets a ON i.asset_id=a.id ORDER BY i.id DESC""").fetchall()
        assets=c.execute("SELECT id,asset_code,name FROM assets ORDER BY name").fetchall()
    body=render_template_string("""
    <section class="panel"><h2>新增巡检记录</h2><form method="post" class="formgrid">
    <div class="field"><label>关联设备</label><select name="asset_id"><option value="">通用巡检/未关联</option>{% for a in assets %}<option value="{{a.id}}">{{a.asset_code}} · {{a.name}}</option>{% endfor %}</select></div>
    <div class="field"><label>巡检日期</label><input type="date" name="check_date" value="{{today}}" required></div>
    <div class="field"><label>检查结果</label><select name="result"><option>正常</option><option>异常</option><option>待复核</option></select></div>
    <div class="field"><label>巡检人</label><input name="checker" placeholder="演示人员"></div>
    <div class="field"><label>异常现象</label><input name="issue" placeholder="无异常可留空"></div>
    <div class="field"><label>处理措施/备注</label><input name="action"></div><div class="wide"><button class="btn">保存巡检</button></div></form></section>
    <section class="panel"><h2>巡检记录</h2><table><tr><th>日期</th><th>设备</th><th>结果</th><th>异常</th><th>处理措施</th><th>巡检人</th></tr>{% for x in rows %}<tr><td>{{x.check_date}}</td><td>{{x.asset_name or '通用巡检'}}</td><td><span class="pill {{'bad' if x.result=='异常' else 'warn' if x.result=='待复核' else ''}}">{{x.result}}</span></td><td>{{x.issue or '—'}}</td><td>{{x.action or '—'}}</td><td>{{x.checker or '—'}}</td></tr>{% else %}<tr><td colspan="6">还没有巡检记录，先新增一条试试。</td></tr>{% endfor %}</table></section>
    """,rows=rows,assets=assets,today=datetime.now().strftime("%Y-%m-%d"))
    return page("巡检记录","记录检查结果、异常现象和处理动作；关联设备后自动更新最近巡检日期。",body)

@app.route("/tickets",methods=["GET","POST"])
def tickets():
    with db() as c:
        if request.method=="POST":
            no="IT-"+datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:19]
            c.execute("INSERT INTO tickets(ticket_no,created_at,department,contact,device,description,priority,status) VALUES(?,?,?,?,?,?,?,'待受理')",
            (no,datetime.now().strftime("%Y-%m-%d %H:%M"),request.form.get("department",""),request.form.get("contact",""),request.form["device"],request.form["description"],request.form.get("priority","普通")))
            c.commit();flash("报修工单已创建："+no);return redirect(url_for("tickets"))
        if request.args.get("update"):
            tid=request.args.get("update"); status=request.args.get("status","处理中")
            c.execute("UPDATE tickets SET status=?,assignee=?,resolution=?,closed_at=? WHERE id=?",
            (status,request.args.get("assignee",""),request.args.get("resolution",""),datetime.now().strftime("%Y-%m-%d %H:%M") if status=="已完成" else "",tid))
            c.commit();flash("工单状态已更新。");return redirect(url_for("tickets"))
        rows=c.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()
    body=render_template_string("""
    <section class="panel"><h2>新建故障报修</h2><form method="post" class="formgrid">
    <div class="field"><label>报修部门</label><input name="department" placeholder="例如 行政办公室"></div><div class="field"><label>联系人（请勿填真实儿童信息）</label><input name="contact" placeholder="演示联系人"></div>
    <div class="field"><label>设备/系统</label><input name="device" required placeholder="例如 网络打印机"></div><div class="field"><label>紧急程度</label><select name="priority"><option>普通</option><option>紧急</option><option>低</option></select></div>
    <div class="field wide"><label>故障现象</label><textarea name="description" required placeholder="描述出现时间、现象和影响范围"></textarea></div><div class="wide"><button class="btn">提交报修</button></div></form></section>
    <section class="panel"><h2>工单跟踪 · {{rows|length}} 项</h2><table><tr><th>编号/时间</th><th>设备与故障</th><th>优先级</th><th>状态</th><th>处理更新</th></tr>{% for t in rows %}<tr><td>{{t.ticket_no}}<br><span class="muted">{{t.created_at}}</span></td><td><b>{{t.device}}</b><br>{{t.description}}</td><td>{{t.priority}}</td><td><span class="pill {{'bad' if t.priority=='紧急' else 'warn' if t.status!='已完成' else ''}}">{{t.status}}</span><br><span class="muted">{{t.assignee}}</span></td><td><form method="get" class="field"><input type="hidden" name="update" value="{{t.id}}"><select name="status"><option {{'selected' if t.status=='待受理' else ''}}>待受理</option><option {{'selected' if t.status=='处理中' else ''}}>处理中</option><option {{'selected' if t.status=='待复核' else ''}}>待复核</option><option {{'selected' if t.status=='已完成' else ''}}>已完成</option></select><input name="assignee" placeholder="处理人" value="{{t.assignee}}"><input name="resolution" placeholder="处理结果" value="{{t.resolution}}"><button class="btn secondary" style="margin-top:5px">更新状态</button></form></td></tr>{% endfor %}</table></section>
    """,rows=rows)
    return page("故障报修","从提交、受理、处理中到复核完成，保留工单状态和处理结果。",body)

@app.route("/media",methods=["GET","POST"])
def media():
    with db() as c:
        if request.method=="POST":
            c.execute("INSERT INTO media(event_date,event_name,material_type,count,permission_status,archive_path,reviewer,note) VALUES(?,?,?,?,?,?,?,?)",
            (request.form["event_date"],request.form["event_name"],request.form.get("material_type","照片"),int(request.form.get("count") or 0),request.form.get("permission_status","待核验"),request.form.get("archive_path",""),request.form.get("reviewer",""),request.form.get("note","")))
            c.commit();flash("素材归档登记已保存。");return redirect(url_for("media"))
        rows=c.execute("SELECT * FROM media ORDER BY id DESC").fetchall()
    body=render_template_string("""
    <section class="panel"><h2>新增素材归档登记</h2><form method="post" class="formgrid">
    <div class="field"><label>活动日期</label><input type="date" name="event_date" value="{{today}}" required></div><div class="field"><label>活动/事项名称</label><input name="event_name" required placeholder="请使用模拟事项或已授权内容"></div>
    <div class="field"><label>素材类型</label><select name="material_type"><option>照片</option><option>视频</option><option>图文</option><option>设计文件</option></select></div><div class="field"><label>素材数量</label><input type="number" name="count" min="0" value="0"></div>
    <div class="field"><label>授权状态</label><select name="permission_status"><option>待核验</option><option>已核验（模拟）</option><option>仅内部演示</option><option>不可发布</option></select></div><div class="field"><label>审核人</label><input name="reviewer" placeholder="演示审核人"></div>
    <div class="field"><label>归档路径</label><input name="archive_path" placeholder="demo/YYYY/MM/event/"></div><div class="field"><label>备注</label><input name="note" placeholder="不填写儿童姓名等个人信息"></div><div class="wide"><button class="btn">保存归档登记</button></div></form></section>
    <section class="panel"><h2>素材归档记录</h2><table><tr><th>日期</th><th>活动</th><th>类型/数量</th><th>授权状态</th><th>归档位置</th><th>审核/备注</th></tr>{% for m in rows %}<tr><td>{{m.event_date}}</td><td>{{m.event_name}}</td><td>{{m.material_type}} · {{m.count}}</td><td><span class="pill {{'warn' if m.permission_status=='待核验' else 'bad' if m.permission_status=='不可发布' else ''}}">{{m.permission_status}}</span></td><td>{{m.archive_path or '—'}}</td><td>{{m.reviewer or '—'}}<br><span class="muted">{{m.note}}</span></td></tr>{% endfor %}</table></section>
    """,rows=rows,today=datetime.now().strftime("%Y-%m-%d"))
    return page("素材归档","登记活动素材数量、类型、授权核验状态和归档位置，不上传真实影像。",body)

@app.get("/health")
def health():
    return {"status":"ok","app":"campus-information-desk","database":DB.name}

if __name__=="__main__":
    init_db()
    print("园务信息台已启动：http://127.0.0.1:5000")
    app.run(host="127.0.0.1",port=5000,debug=False)
