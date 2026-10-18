"""Wikimedia Commons'tan yalnızca KAMU MALI / CC0 görselleri indirir ve kaynak bilgisini kaydeder.

Kullanım: python3 commons_indir.py anahtar="File:...jpg" anahtar2="File:..." ...
Çıktı: varliklar/gorseller/<anahtar>.jpg|png + kaynaklar.json (lisans, sanatçı, adres)
"""
import json, os, sys, time, urllib.parse, urllib.request

KOK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "varliklar", "gorseller")
UA = {"User-Agent": "TarihVideo/1.0 (egitim amacli tarih videolari)"}
IZINLI = ("public domain", "pd", "cc0")


def api(**p):
    p.update(format="json")
    u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)
    for k in range(5):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))
        except Exception:
            time.sleep(4 * (k + 1))
    raise RuntimeError("Commons API yanıt vermedi")


def main():
    os.makedirs(KOK, exist_ok=True)
    kayit_yolu = os.path.join(KOK, "kaynaklar.json")
    kayit = json.load(open(kayit_yolu)) if os.path.exists(kayit_yolu) else {}
    for arg in sys.argv[1:]:
        anahtar, baslik = arg.split("=", 1)
        if anahtar in kayit:
            continue
        r = api(action="query", titles=baslik, prop="imageinfo", iiprop="url|extmetadata|size",
                iiurlwidth=1280, iiextmetadatafilter="LicenseShortName|Artist|DateTimeOriginal")
        sayfa = next(iter(r["query"]["pages"].values()))
        if "imageinfo" not in sayfa:
            print(f"YOK  {anahtar}: {baslik}")
            continue
        ii = sayfa["imageinfo"][0]
        md = ii.get("extmetadata", {})
        lisans = md.get("LicenseShortName", {}).get("value", "")
        if not lisans.lower().startswith(IZINLI):
            print(f"RED  {anahtar}: lisans '{lisans}' kamu malı değil")
            continue
        adres = ii.get("thumburl") or ii["url"]
        uzanti = os.path.splitext(urllib.parse.urlparse(adres).path)[1].lower() or ".jpg"
        if uzanti not in (".jpg", ".jpeg", ".png"):
            uzanti = ".png" if uzanti == ".webp" else ".jpg"
        hedef = os.path.join(KOK, anahtar + uzanti)
        veri = None
        for k in range(6):
            try:
                veri = urllib.request.urlopen(urllib.request.Request(adres, headers=UA), timeout=120).read()
                break
            except Exception as hata:
                print(f"  bekleniyor ({hata})", flush=True)
                time.sleep(60 * (k + 1))
        if not veri or veri[:3] not in (b"\xff\xd8\xff", b"\x89PN"):
            print(f"HATA {anahtar}: indirilemedi")
            continue
        open(hedef, "wb").write(veri)
        kayit[anahtar] = {"dosya": os.path.basename(hedef), "baslik": baslik, "lisans": lisans,
                          "sanatci": md.get("Artist", {}).get("value", ""),
                          "tarih": md.get("DateTimeOriginal", {}).get("value", ""),
                          "sayfa": ii.get("descriptionurl", "")}
        json.dump(kayit, open(kayit_yolu, "w"), ensure_ascii=False, indent=1)
        print(f"OK   {anahtar} [{lisans}] {len(veri) // 1024} KB")
        time.sleep(45)


if __name__ == "__main__":
    main()
