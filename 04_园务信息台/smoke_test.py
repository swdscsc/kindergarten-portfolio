# -*- coding: utf-8 -*-
"""轻量冒烟测试：python 04_园务信息台/smoke_test.py"""
import sqlite3
import tempfile
from pathlib import Path
import app as campus

def run():
    with tempfile.TemporaryDirectory() as tmp:
        campus.DB = Path(tmp) / "test.db"
        campus.init_db()
        campus.app.config.update(TESTING=True)
        client = campus.app.test_client()

        for path in ["/", "/assets", "/inspections", "/tickets", "/media", "/health", "/audit", "/data-tools"]:
            response = client.get(path)
            assert response.status_code == 200, (path, response.status_code)

        response = client.post("/assets", data={
            "asset_code":"TEST-PC-999", "name":"测试电脑", "category":"办公终端",
            "location":"测试室", "owner":"测试员", "status":"在用", "last_check":"2026-11-02"
        }, follow_redirects=True)
        assert response.status_code == 200 and "测试电脑" in response.get_data(as_text=True)

        with sqlite3.connect(campus.DB) as conn:
            asset_id = conn.execute("SELECT id FROM assets WHERE asset_code='TEST-PC-999'").fetchone()[0]

        response = client.post("/inspections", data={
            "asset_id":str(asset_id), "check_date":"2026-11-02", "result":"正常",
            "checker":"测试员", "issue":"", "action":"测试通过"
        }, follow_redirects=True)
        assert response.status_code == 200 and "测试通过" in response.get_data(as_text=True)

        response = client.post("/tickets", data={
            "department":"测试部门", "contact":"虚构联系人", "device":"测试打印机",
            "priority":"普通", "description":"冒烟测试报修"
        }, follow_redirects=True)
        assert response.status_code == 200 and "冒烟测试报修" in response.get_data(as_text=True)

        with sqlite3.connect(campus.DB) as conn:
            ticket_id = conn.execute("SELECT id FROM tickets WHERE description='冒烟测试报修'").fetchone()[0]
        response = client.get(f"/tickets?update={ticket_id}&status=已完成&assignee=测试员&resolution=测试修复")
        assert response.status_code == 302

        response = client.post("/media", data={
            "event_date":"2026-11-02", "event_name":"测试归档（虚构）",
            "material_type":"图文", "count":"2", "permission_status":"仅内部演示",
            "archive_path":"test/demo/", "reviewer":"测试员", "note":"无真实个人信息"
        }, follow_redirects=True)
        assert response.status_code == 200 and "测试归档" in response.get_data(as_text=True)

        print("PASS：6 个页面/健康检查路由")
        print("PASS：设备新增、巡检登记、工单创建与完成、素材归档")
        response = client.get("/assets?q=TEST-PC-999")
        assert response.status_code == 200 and "测试电脑" in response.get_data(as_text=True)
        for path in ["/export/assets", "/export/inspections", "/export/tickets", "/export/media", "/export/audit_logs"]:
            exported = client.get(path)
            assert exported.status_code == 200 and "text/csv" in exported.headers.get("Content-Type", "")
        backup = client.get("/backup")
        assert backup.status_code == 200 and backup.data[:16] == b"SQLite format 3\\x00"
        with sqlite3.connect(campus.DB) as conn:
            assert conn.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0] >= 4
        print("PASS：搜索、5 类 CSV 导出、SQLite 备份、操作记录")
        print("PASS：使用临时 SQLite 数据库，未修改真实演示数据")
        print("园务信息台冒烟测试全部通过。")

if __name__ == "__main__":
    run()
