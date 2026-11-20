"""Dil kapakları: yazısız arka plan + dilde 3 satır yazı (PIL + raqm: Arapça/Urduca sağdan sola ve bitişik).
python3 kapak_dil.py <arka.png> <cikti.png> <dil> "<satır1>" "<satır2>" "<satır3>" [x_merkez]
Arka plan yoksa Türkçe kapaktan yazıyı Gemini görsel modeliyle sildirip (gemini-3.1-flash-image) 1280x720'ye ölçekle.
Sağ alt köşe (süre etiketi) boş bırakılır."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = {"es": ("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", 0),
        "en": ("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", 0),
        "ru": ("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", 0),
        "ar": ("/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf", 0),
        "ur": ("/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf", 0),
        "ko": ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 1)}   # 1 = KR
YON = {"ar": "rtl", "ur": "rtl"}


def yaz(im, metin, cx, cy, boy, renk, dil, max_w=620):
    yol, idx = FONT[dil]
    kw = dict(direction=YON.get(dil, "ltr"), language=dil)
    while True:
        f = ImageFont.truetype(yol, boy, index=idx, layout_engine=ImageFont.Layout.RAQM)
        x0, y0, x1, y1 = ImageDraw.Draw(im).textbbox((0, 0), metin, font=f, **kw)
        if x1 - x0 <= max_w or boy < 30:
            break
        boy -= 4
    x, y = cx - (x1 - x0) / 2 - x0, cy - (y1 - y0) / 2 - y0
    st = max(5, boy // 9)
    golge = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(golge).text((x + boy * 0.06, y + boy * 0.07), metin, font=f, fill=(0, 0, 0, 180),
                               stroke_width=st, stroke_fill=(0, 0, 0, 180), **kw)
    im.alpha_composite(golge.filter(ImageFilter.GaussianBlur(boy * 0.05)))
    ImageDraw.Draw(im).text((x, y), metin, font=f, fill=renk, stroke_width=st, stroke_fill=(20, 16, 30), **kw)


if __name__ == "__main__":
    arka, cikti, dil, s1, s2, s3 = sys.argv[1:7]
    cx = float(sys.argv[7]) if len(sys.argv) > 7 else 950
    im = Image.open(arka).convert("RGBA").resize((1280, 720), Image.LANCZOS)
    # sağa doğru hafif koyulaşma (yazı okunurluğu)
    g = Image.new("L", (1280, 1), 0)
    for x in range(1280):
        g.putpixel((x, 0), int(max(0, min(1, (x - 560) / 720)) * 170))
    im.alpha_composite(Image.merge("RGBA", [Image.new("L", (1280, 720), c) for c in (8, 8, 20)] + [g.resize((1280, 720))]))
    yaz(im, s1, cx, 200, 84, (255, 255, 255), dil)
    yaz(im, s2, cx, 318, 118, (255, 200, 60), dil)
    yaz(im, s3, cx, 432, 50, (255, 122, 94), dil)
    im.convert("RGB").save(cikti)
    print("ok", cikti)
