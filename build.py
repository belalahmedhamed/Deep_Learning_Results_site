#!/usr/bin/env python3
"""تحويل ملف الإكسل إلى ملفات بيانات مشفّرة (ملف لكل طالب) داخل docs/data
الاستخدام:  python build.py الملف.xlsx            (الدخول بالكود فقط)
            python build.py الملف.xlsx --nid      (الدخول بالكود + الرقم القومي)"""
import sys, re, json, base64, hashlib, secrets, shutil, argparse
from pathlib import Path
import openpyxl
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITER = 100_000
DOCS = Path(__file__).parent / "docs"
AR = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
norm = lambda s: re.sub(r"\s+", "", str(s).translate(AR)).lower()
b64 = lambda b: base64.b64encode(b).decode()

def num(v):
    try: return None if v is None or str(v).strip() == "" else float(v)
    except ValueError: return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("xlsx"); ap.add_argument("--nid", action="store_true")
    a = ap.parse_args()
    ws = openpyxl.load_workbook(a.xlsx, data_only=True).active
    course = str(ws["A1"].value or "").strip()
    head = [c.value or "" for c in ws[2]]
    cols = []
    for i in range(3, 8):
        m = re.search(r"\(([\d.]+)\)", head[i])
        cols.append((i, re.sub(r"\s*\(.*?\)", "", head[i]).strip(), float(m.group(1)) if m else None))

    cfg_file = DOCS / "config.json"
    salt = base64.b64decode(json.loads(cfg_file.read_text())["salt"]) if cfg_file.exists() else secrets.token_bytes(16)
    data = DOCS / "data"; shutil.rmtree(data, ignore_errors=True); data.mkdir(parents=True)

    n = graded = 0; seen = set()
    for r in ws.iter_rows(min_row=3, values_only=True):
        if not r[0]: continue
        code = norm(r[0])
        if code in seen: print("⚠ كود مكرر:", r[0]); continue
        seen.add(code)
        comps = [{"label": l, "max": m, "value": num(r[i])} for i, l, m in cols]
        total = num(r[8])
        if total is None and any(c["value"] is not None for c in comps):
            total = sum(c["value"] or 0 for c in comps)
        status = r[10] if r[10] not in (None, 0, "0", "") else ""
        payload = {"name": str(r[1]).strip(), "code": str(r[0]).strip(), "course": course, "comps": comps,
                   "total": total, "max": sum(m or 0 for _, _, m in cols), "grade": str(r[9] or "").strip(),
                   "status": str(status), "prev": str(r[11] or "").strip()}
        secret = code + "|" + norm(int(r[2]) if isinstance(r[2], (int, float)) else r[2]) if a.nid else code
        d = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt, ITER, 64)
        iv = secrets.token_bytes(12)
        ct = AESGCM(d[:32]).encrypt(iv, json.dumps(payload, ensure_ascii=False).encode(), None)
        (data / f"{d[32:48].hex()}.json").write_text(json.dumps({"iv": b64(iv), "ct": b64(ct)}))
        n += 1; graded += total is not None
    cfg_file.write_text(json.dumps({"salt": b64(salt), "iter": ITER, "needNid": a.nid, "course": course}, ensure_ascii=False))
    (DOCS / ".nojekyll").touch()
    print(f"✓ تم إنشاء {n} ملف طالب ({graded} لديهم درجات) — الدخول: {'كود + رقم قومي' if a.nid else 'كود فقط'}")

main()
