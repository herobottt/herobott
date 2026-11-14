"""Talabalar ro'yxati (students.json — PDF'dan olingan): email bo'yicha ism-familya va Student ID topish."""
import json
import os
import re
import unicodedata

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.json")
_DATA = {}
try:
    with open(_PATH, encoding="utf-8") as f:
        _DATA = json.load(f)
except Exception:
    _DATA = {}


def norm_email(email):
    """Kichik harf, diakritiksiz, apostrofsiz — g'/gʻ/g‘/g` kabi yozuv farqlari bir xil deb olinadi."""
    e = unicodedata.normalize("NFKD", (email or "").strip().lower())
    e = "".join(ch for ch in e if not unicodedata.combining(ch))
    e = re.sub(r"[ʻʼ‘’`´'′\"]", "", e)
    return re.sub(r"\s+", "", e)


def lookup(email):
    """-> {'full_name', 'student_id', 'ambiguous'} yoki None.
    Bir xil email bir necha talabaga to'g'ri kelsa (ro'yxatda 75 ta shunday email bor), ismlar ' / ' bilan
    birlashtiriladi va ambiguous=True bo'ladi — qaysi biri ekanini aniq bilib bo'lmaydi."""
    rows = _DATA.get(norm_email(email))
    if not rows:
        return None
    names = [f"{r['first']} {r['last']}".strip() for r in rows]
    ids = [r["id"] for r in rows]
    return {"full_name": " / ".join(names), "student_id": " / ".join(ids), "ambiguous": len(rows) > 1}


def count():
    return sum(len(v) for v in _DATA.values())


def classify(email, student_id=None, today=None):
    """Email va Student ID bo'yicha jins hamda kurs.
    Jins: emailda '@' dan oldingi harf 'a' bo'lsa — qiz (familiya -ova/-eva), aks holda — o'g'il bola.
    Kurs: Student ID dastlabki 2 raqami = qabul yili (23 → 2023-yil sentabr). O'quv yili 1-sentabrdan boshlanadi:
    kurs = (joriy yil - qabul yili) + (sentabr va undan keyin bo'lsa 1). Ro'yxatdagi 1423 ta talabada qoida familiyaga 100% mos tushdi.
    -> {'gender': 'f'|'m'|None, 'year': 2023|None, 'course': int|None}"""
    from datetime import datetime, timedelta
    local = (email or "").split("@")[0].strip().lower().rstrip("0123456789")
    gender = None
    if local:
        gender = "f" if local[-1] == "a" else "m"
    m = re.match(r"\s*(\d{2})", str(student_id or ""))
    year = course = None
    if m:
        year = 2000 + int(m.group(1))
        now = today or (datetime.utcnow() + timedelta(hours=5))   # Toshkent vaqti
        course = now.year - year + (1 if now.month >= 9 else 0)
        if course < 1: year = course = None   # kelajak yili — ID noto'g'ri
    return {"gender": gender, "year": year, "course": course}
