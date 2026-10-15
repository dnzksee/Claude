"""Türkçe metni Microsoft Edge neural ses ile seslendirir, .mp3 + .srt üretir.

Kullanım: python3 seslendir.py metin.txt cikti_adi [--ses tr-TR-AhmetNeural] [--hiz +0%]
"""
import argparse, asyncio, os, ssl
import edge_tts
from edge_tts import communicate

# Proxy/özel CA ortamlarında sistem CA dosyasını kullan
_ca = os.environ.get("SSL_CERT_FILE")
if _ca and os.path.exists(_ca):
    communicate._SSL_CTX = ssl.create_default_context(cafile=_ca)


async def main(metin, cikti, ses, hiz):
    c = edge_tts.Communicate(metin, ses, rate=hiz, boundary="SentenceBoundary")
    alt = edge_tts.SubMaker()
    with open(cikti + ".mp3", "wb") as f:
        async for parca in c.stream():
            if parca["type"] == "audio":
                f.write(parca["data"])
            elif parca["type"] in ("WordBoundary", "SentenceBoundary"):
                alt.feed(parca)
    with open(cikti + ".srt", "w", encoding="utf-8") as f:
        f.write(alt.get_srt())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("metin_dosyasi")
    p.add_argument("cikti")
    p.add_argument("--ses", default="tr-TR-AhmetNeural")
    p.add_argument("--hiz", default="+0%")
    a = p.parse_args()
    asyncio.run(main(open(a.metin_dosyasi, encoding="utf-8").read(), a.cikti, a.ses, a.hiz))
