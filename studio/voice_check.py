"""Bölünmüş seslendirme parçalarını tek istekte yazıya döktürüp senaryoyla karşılaştırır.
    python3 voice_check.py anlatici_2_mavi umay_tum ...
"""
import base64
import difflib
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voice_batch import OUT, DOSYALAR, satirlar

MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash"]


NUM = {"1": "bir", "2": "iki", "3": "üç", "4": "dört", "5": "beş", "6": "altı"}


def norm(s):
    for d, w in NUM.items():
        s = s.replace(d, w)
    s = s.lower().replace("ı", "i").replace("İ", "i")
    return re.sub(r"[^a-zçğöşü0-9]", "", s)


def check(ad):
    who, bols = next((w, b) for a, w, b in DOSYALAR if a == ad)
    lines = list(satirlar(who, bols))
    parts = []
    for i, (cid, _, _, _) in enumerate(lines):
        parts.append({"text": f"Parça {i + 1}:"})
        parts.append({"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(open(os.path.join(OUT, cid + ".wav"), "rb").read()).decode()}})
    parts.append({"text": f"Yukarıda {len(lines)} ayrı ses parçası var. Her parçada söylenenleri kelimesi kelimesine yaz. "
                          'Sadece JSON dizi döndür: ["parça 1 metni", "parça 2 metni", ...]'})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json"}}
    last = None
    for m in MODELS:
        try:
            req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                                         data=json.dumps(body).encode(),
                                         headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"})
            got = json.loads(json.load(urllib.request.urlopen(req, timeout=600))["candidates"][0]["content"]["parts"][0]["text"])
            break
        except Exception as e:
            last = e
    else:
        raise last
    bad = 0
    for (cid, _, txt, _), g in zip(lines, got):
        r = difflib.SequenceMatcher(None, norm(txt), norm(g)).ratio()
        flag = "" if r >= 0.6 else "   <-- UYUMSUZ"
        bad += bool(flag)
        print(f"  {cid:4} {r:4.2f} | {txt}  ⇢  {g}{flag}")
    print(f"{ad}: {len(lines) - bad}/{len(lines)} uyumlu")
    return bad


if __name__ == "__main__":
    sys.exit(sum(check(a) for a in sys.argv[1:]) > 0)
