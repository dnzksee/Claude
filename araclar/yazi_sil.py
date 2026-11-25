"""Türkçe kapaktan yazıları sildirip yazısız arka plan üretir (gemini-3.1-flash-image), 1280x720.
python3 yazi_sil.py <konu>/kapak.png <konu>/dil_kaynak/kapak_arka.png"""
import base64, io, os, sys
import requests
from PIL import Image

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image:generateContent"
ISTEK = ("Remove all the text and lettering from this image. Fill the areas where the text was with the "
         "matching background so it looks natural. Keep everything else exactly the same: same characters, "
         "same composition, same colors, same art style.")

if __name__ == "__main__":
    giris, cikti = sys.argv[1:3]
    veri = base64.b64encode(open(giris, "rb").read()).decode()
    body = {"contents": [{"parts": [{"text": ISTEK}, {"inlineData": {"mimeType": "image/png", "data": veri}}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]}}
    r = requests.post(URL, json=body, headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"].replace("buraya_yeni_anahtar", "").strip().strip("'\"=").strip()}, timeout=300)
    r.raise_for_status()
    for p in r.json()["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            im = Image.open(io.BytesIO(base64.b64decode(p["inlineData"]["data"]))).convert("RGB")
            im.resize((1280, 720), Image.LANCZOS).save(cikti)
            print("tamam:", cikti, im.size)
            break
    else:
        sys.exit("yanıtta görsel yok")
