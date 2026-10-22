"""Konu: Malazgirt 1071 — ağır zırh ile hızlı okun savaşı.

Kanal kuralı: Bizans her zaman SOLDA, Türkler her zaman SAĞDA (sağdan gelir, sağdan akın eder).

Yeni bir konu için bu dosyayı kopyalayın: BASLIK/ALT_BASLIK, ACILIS/KAPANIS metni, KARAKTERLER ve
SAHNELER listesini değiştirin. Her sahne: başlık, arka plan, geçiş, cümle listesi (her öğe tek
cümle, . ! ? ile biter) ve kurgu fonksiyonu. Kurguda s.c(i) i. cümlenin başladığı an,
s.c(i, 0.5) cümlenin ortasıdır; bütün oyunculuk bu anlara bağlanır.
"""

import math

BASLIK = "Malazgirt 1071"
ALT_BASLIK = "Ağır zırh ile hızlı okun savaşı"
KANAL = "KRONİKNÂME"
LOGO = "kilic"
KAPANIS_YAZI = "Anadolu'nun kapısı açıldı"
KART_RENK = {"ust": (0.55, 0.16, 0.14), "alt": (0.25, 0.06, 0.06)}
YOUTUBE = dict(
    baslik="Malazgirt 1071: Ağır Zırh Hızlı Oka Nasıl Yenildi? | Animasyonlu Anlatım",
    kanca="1071 yazında Doğu Anadolu'da iki dünya karşı karşıya geldi: ağır zırhlı Bizans ordusu ile hafif ve "
          "hızlı Selçuklu atlıları.",
    ozet="Sultan Alparslan ile İmparator Romen Diyojen'in Malazgirt'te karşılaşmasını haritalar ve çizgi film "
         "sahneleriyle anlatıyoruz: iki ordunun savaş anlayışı, savaştan önce bölünen Bizans ordusu, hilal tuzağı ve "
         "sahte ricat, imparatorun esir düşüşü ve Anadolu'nun Türklere açılan kapısı.",
    etiketler=["Malazgirt", "Malazgirt Savaşı", "Malazgirt 1071", "Alparslan", "Romen Diyojen", "Romanos Diogenes",
               "Selçuklu", "Büyük Selçuklu", "Bizans", "Anadolu Selçuklu", "Süleyman Şah", "1071",
               "Türk tarihi", "Anadolu'nun fethi", "hilal taktiği", "sahte ricat", "atlı okçu"],
    hashtagler=["#Malazgirt", "#Alparslan", "#tarih", "#Kroniknâme"],
)

ACILIS = [
    "Bin yetmiş bir yılının yazında, Doğu Anadolu'da iki dünya karşı karşıya geldi.",
    "Bir yanda ağır ve kalabalık bir imparatorluk ordusu, öbür yanda hafif ve hızlı bozkır atlıları.",
]
KAPANIS = [
    "Ağır zırh hızlı oka yenilmişti, ama bu zaferi asıl belirleyen bölünmüş bir ordu ve bozulan güvendi.",
    "Bir sonraki büyük savaşta görüşmek üzere!",
]

BIZANS = (0.5, 0.2, 0.55)
SELCUK = (0.1, 0.52, 0.48)
ALTIN = (0.98, 0.78, 0.25)

KARAKTERLER = {
    "Romen": dict(govde=BIZANS, sapka="tac", sakal=(0.42, 0.27, 0.14), sac_renk=(0.42, 0.27, 0.14), etek=True,
                  kemer=ALTIN, pantolon=(0.3, 0.15, 0.3)),
    "Alparslan": dict(govde=SELCUK, sapka="bork", sakal=(0.12, 0.08, 0.06), sac_renk=(0.12, 0.08, 0.06), etek=True,
                      kemer=ALTIN, pantolon=(0.2, 0.25, 0.3), yon=-1),
    "Asker": dict(govde=(0.55, 0.58, 0.66), sapka="migfer", elde={"L": ("kalkan", {}), "R": "kilic"},
                  pantolon=(0.3, 0.2, 0.35)),
    "Akıncı": dict(govde=(0.12, 0.58, 0.55), sapka="bork", sapka_renk=(0.2, 0.35, 0.6), elde={"R": ("yay", {"ok": 1})},
                   pantolon=(0.35, 0.25, 0.15), yon=-1),
    "Dukas": dict(govde=(0.62, 0.15, 0.2), sac="kivircik", sac_renk=(0.3, 0.2, 0.1), sakal=(0.3, 0.2, 0.1), etek=True),
    "Tarkaniyotis": dict(govde=(0.4, 0.32, 0.55), sapka="migfer", sakal=(0.55, 0.55, 0.55),
                         elde={"R": ("sancak", {"renk": BIZANS})}),
    "Varang": dict(govde=(0.68, 0.2, 0.16), sapka="migfer", sakal=(0.85, 0.65, 0.3), sac_renk=(0.85, 0.65, 0.3),
                   elde={"L": ("kalkan", {"renk": (0.68, 0.2, 0.16)}), "R": "kilic"}, pantolon=(0.3, 0.2, 0.2)),
    "Süleyman Şah": dict(govde=(0.15, 0.45, 0.6), sapka="bork", sapka_renk=(0.15, 0.3, 0.55), sakal=(0.2, 0.12, 0.08),
                         sac_renk=(0.2, 0.12, 0.08), etek=True, kemer=ALTIN, yon=-1),
    "Tuğrul": dict(govde=(0.12, 0.45, 0.4), sapka="bork", sapka_renk=(0.15, 0.45, 0.3), sakal=(0.15, 0.1, 0.08),
                   sac_renk=(0.15, 0.1, 0.08), etek=True, kemer=ALTIN, yon=-1),
    "Çağrı": dict(govde=(0.2, 0.38, 0.55), sapka="bork", sapka_renk=(0.55, 0.3, 0.15), sakal=(0.3, 0.2, 0.1),
                  sac_renk=(0.3, 0.2, 0.1), etek=True, kemer=ALTIN, yon=-1),
    "Mesud": dict(govde=(0.85, 0.48, 0.12), sapka="sarik", sakal=(0.12, 0.08, 0.06), sac_renk=(0.12, 0.08, 0.06),
                  etek=True, kemer=ALTIN, yon=-1),
    "Basileios": dict(govde=(0.45, 0.18, 0.5), sapka="tac", sakal=(0.92, 0.92, 0.9), sac_renk=(0.92, 0.92, 0.9),
                      etek=True, kemer=ALTIN),
    "İmparator": dict(govde=(0.6, 0.35, 0.65), sapka="tac", sakal=(0.5, 0.35, 0.2), sac_renk=(0.5, 0.35, 0.2),
                      etek=True),
    "Evdokia": dict(govde=(0.7, 0.35, 0.7), sac="topuz", sac_renk=(0.35, 0.2, 0.1), sapka="tac", etek=True,
                    kemer=ALTIN, pantolon=(0.5, 0.25, 0.5)),
    "Yuhanna Dukas": dict(govde=(0.62, 0.15, 0.2), sac="kel", sakal=(0.75, 0.75, 0.72), etek=True),
    "Ebu Nasr": dict(govde=(0.92, 0.9, 0.82), sapka="sarik", sakal=(0.95, 0.95, 0.92), sac_renk=(0.9, 0.9, 0.88),
                     etek=True, yon=-1),
    "Melikşah": dict(govde=(0.15, 0.4, 0.65), sapka="bork", sapka_renk=(0.85, 0.2, 0.15), sac_renk=(0.12, 0.08, 0.06),
                     etek=True, kemer=ALTIN, yon=-1),
    "Esir komutan": dict(govde=(0.45, 0.42, 0.4), sapka="sarik", sapka_renk=(0.6, 0.55, 0.5), sakal=(0.2, 0.15, 0.1)),
    "Uz": dict(govde=(0.6, 0.45, 0.25), sapka="bork", sapka_renk=(0.35, 0.25, 0.15), pantolon=(0.3, 0.25, 0.2)),
}

# Bölge sınırları (yaklaşık, 1071 öncesi) — tarih_video/projeler/malazgirt_v2 ile aynı
BIZANS_1071 = [(19.3, 42.3), (19.5, 44.6), (22.5, 44.7), (25, 43.7), (28.0, 44.2), (29.7, 45.3), (31, 45),
               (31, 42.5), (36, 42.5), (41.5, 41.6), (42.5, 41.2), (42.6, 40.2), (42.0, 39.4), (41.2, 38.6),
               (40.2, 37.8), (39.5, 36.8), (38.0, 36.2), (36.6, 35.6), (35.6, 35.2), (34.6, 34.4), (32, 34.4),
               (26, 34.7), (22.5, 36.2), (20, 38.3), (19.2, 40.4)]
SELCUKLU_1071 = [(42.6, 41.4), (44.6, 41.6), (46.5, 41.9), (49.5, 41.6), (50, 40), (54, 38), (56, 39.5),
                 (60, 40.5), (63, 40.5), (66, 39), (67, 37.3), (65, 35), (62, 32), (61, 29), (58, 26), (52, 27.5),
                 (48.5, 30), (46.5, 31.5), (44.5, 33), (42.8, 34.2), (41, 34.6), (39.6, 36.0), (40.2, 37.8),
                 (41.2, 38.6), (42.0, 39.4), (42.6, 40.2), (42.5, 41.2)]
MALAZGIRT, AHLAT = (42.54, 39.14), (42.49, 38.75)


def isim(s, metin, x, y, t, renk=(1, 1, 1), boyut=38):
    return s.nesne("yazi", x, y, metin=metin, boyut=boyut, renk=renk, olcek=1.0).belir(t, ses="tik")


# ------------------------------------------------------------------ 1
def iki_hukumdar(s):
    s.kamera.ayarla(s.t0, zoom=1.0)
    romen = s.karakter("Romen", x=300, y=600, olcek=0.85, ifade="kararli", poz="eller_belde").belir(s.c(0, 0.25))
    isim(s, "Romen Diyojen", 300, 300, s.c(0, 0.35))
    for k, (x, y) in enumerate(((760, 330), (690, 420), (800, 470))):  # Türk akınları: sağdan sola oklar
        s.nesne("ok", x, y, olcek=0.6, aci=180, renk=SELCUK).belir(s.c(1, 0.2 + k * 0.15), ses="whoosh")
    romen.ifade(s.c(1, 0.5), "kizgin").poz(s.c(1, 0.5), "dur_isareti")

    alp = s.karakter("Alparslan", x=1090, y=600, olcek=0.85, ifade="gururlu").belir(s.c(2, 0.3))
    isim(s, "Sultan Alparslan", 1090, 300, s.c(2, 0.4))
    s.kamera.git(s.c(2), s.c(2) + 1, x=760, zoom=1.08)

    dus = s.nesne("dusunce", 1050, 150, metin="Mısır'daki Fatımiler...", boyut=34, azami=330, olcek=1.0,
                  kuyruk=1).belir(s.c(3, 0.45))
    alp.ifade(s.c(3, 0.3), "dusunceli").poz(s.c(3, 0.3), "dusun")
    dus.kaybol(s.c(4, 0.35))
    alp.ifade(s.c(4, 0.35), "saskin").ifade(s.c(4, 0.65), "kararli").poz(s.c(4, 0.65), "eller_belde")
    s.kamera.punch(s.c(4, 0.35), 0.1)
    s.kamera.git(s.c(4, 0.6), s.c(4, 0.6) + 1, x=640, zoom=1.0)
    x, y = s.yer(*MALAZGIRT)
    s.nesne("pin", x, y, metin="Malazgirt", nabiz=1, olcek=1.0).belir(s.c(4, 0.7))
    s.nesne("patlama", x, y - 120, metin="!", boyut=60, olcek=0.6).belir(s.c(4, 0.8), ses="punch")


# ------------------------------------------------------------------ 2
def fil_ile_ari(s):
    asker = s.karakter("Asker", x=330, olcek=1.0, ifade="kararli").belir(s.c(0, 0.2))
    akinci = s.karakter("Akıncı", x=950, olcek=0.9, ifade="kararli").belir(s.c(0, 0.45))
    asker.kaybol(s.c(1) - 0.2)
    akinci.kaybol(s.c(1) - 0.1)

    fil = s.nesne("fil", 360, 470, olcek=1.4, yuru=1.0).belir(s.c(1, 0.05), ses="punch")
    fil.git(s.c(1), s.bitis(4), x=430)
    s.kamera.git(s.c(1), s.c(1) + 1.2, x=480, zoom=1.15)
    s.nesne("levha", 330, 230, metin="AĞIR", boyut=40, olcek=1.0).belir(s.c(1, 0.4))
    fil.ayarla(s.c(1, 0.85), ter=1.0, sure=0.1)
    s.nesne("saat", 520, 230, olcek=0.6, hiz=0.4).belir(s.c(1, 0.85))

    for k, ad in enumerate(("Ermeni", "Frank", "Varang", "Peçenek")):
        s.nesne("sancak", 150 + k * 150, 470, renk=BIZANS if k != 3 else (0.6, 0.45, 0.25),
                olcek=0.8).belir(s.c(2, 0.3 + k * 0.15))
        isim(s, ad, 190 + k * 150, 545 + (k % 2) * 36, s.c(2, 0.3 + k * 0.15) + 0.1, renk=ALTIN, boyut=32)

    s.kamera.git(s.c(3), s.c(3) + 1.2, x=640, zoom=1.0)
    ari = s.nesne("ari_suru", 960, 360, olcek=1.3, adet=16, hucum=0.0, hedef_x=-330).belir(s.c(3, 0.15),
                                                                                           ses="swoosh_yukari")
    s.nesne("levha", 980, 200, metin="HIZLI", boyut=40, olcek=1.0).belir(s.c(3, 0.5))

    ari.ayarla(s.c(4, 0.1), hucum=1.0, sure=0.5)
    s.nesne("ok_yagmuru", 700, 330, olcek=1.0, yon=-1, genislik=560, adet=16).belir(s.c(4, 0.3), ses="whoosh")
    s.kamera.sars(s.c(4, 0.45), 0.6, 0.6)
    ari.ayarla(s.c(4, 0.85), hucum=0.0, sure=0.6)


# ------------------------------------------------------------------ 3
def bolunen_ordu(s):
    romen = s.karakter("Romen", x=180, y=640, olcek=0.75, ifade="kararli", poz="eller_belde").belir(s.c(0, 0.2))
    mx, my = s.yer(*MALAZGIRT)
    ax, ay = s.yer(*AHLAT)
    s.nesne("pin", mx, my, metin="Malazgirt", olcek=0.9, yazi_dx=-80, yazi_dy=-60).belir(s.c(0, 0.3))
    s.nesne("pin", ax, ay, metin="Ahlat", olcek=0.9, yazi_dy=34, renk=(0.95, 0.6, 0.2)).belir(s.c(1, 0.4))
    terazi = s.nesne("terazi", 1010, 300, olcek=0.8, egim=-1.0, sol="Bizans", sag="Selçuklu").belir(s.c(0, 0.55))

    tark = s.karakter("Tarkaniyotis", x=300, y=640, olcek=0.65, ifade="kararli").belir(s.c(1, 0.3))
    tark.git(s.c(1, 0.55), s.c(1, 0.55) + 2.2, x=ax, y=ay + 120)
    terazi.ayarla(s.c(1, 0.8), egim=-0.45, sure=0.8, egri="elastik")
    tark.kaybol(s.c(2, 0.3))
    s.nesne("carpi", ax + 70, ay - 30, olcek=0.6).belir(s.c(2, 0.4), ses="bzzt")
    romen.ifade(s.c(2, 0.4), "uzgun")

    for k in range(3):
        uz = s.karakter("Uz", x=260 + k * 50, y=650 + k * 12, olcek=0.5, ifade="mutlu")
        uz.belir(s.c(3, 0.35) + k * 0.12).git(s.c(3, 0.55), s.c(3, 0.55) + 1.6, x=1180 + k * 40, kos=True)
    s.sfx("whoosh", s.c(3, 0.55))
    isim(s, "Uz ve Peçenekler saf değiştirdi", 640, 120, s.c(3, 0.6), renk=(1, 0.75, 0.6)).kaybol(s.c(4))
    terazi.ayarla(s.c(3, 0.8), egim=0.3, sure=0.8, egri="elastik")

    terazi.ayarla(s.c(4, 0.3), egim=0.9, sure=1.0, egri="elastik")
    s.kamera.git(s.c(4, 0.2), s.c(4, 0.2) + 0.6, x=1000, y=330, zoom=1.35, egri="geri_tepme")
    romen.ifade(s.c(4, 0.4), "panik")


# ------------------------------------------------------------------ 4
def hilal_tuzagi(s):
    """Kuş bakışı savaş alanı: diziliş, ok akınları, sahte ricat, dönüş kargaşası, Dukas'ın çekilmesi, kuşatma."""
    c, b = s.c, s.bitis
    s.nesne("kale_ust", 70, 360, olcek=0.6, metin="Malazgirt").goster(s.t0)
    s.nesne("yazi", 640, 64, metin="26 Ağustos 1071 · Cuma", boyut=40, renk=ALTIN, olcek=1.0).belir(c(0, 0.05)) \
        .kaybol(c(1))
    s.kamera.ayarla(s.t0, x=640, y=360, zoom=1.0)
    # Bizans (solda): iki kanat, merkez, arkada ihtiyat
    sol = s.birlik("bizans", "piyade", 330, 160, sira=4, kol=7, ad="Briyennios", tohum=1)
    mer = s.birlik("bizans", "agir", 420, 360, sira=3, kol=5, ad="Romen Diyojen", tohum=2)
    sag = s.birlik("bizans", "piyade", 330, 565, sira=4, kol=7, ad="Alyates", tohum=3)
    iht = s.birlik("bizans", "piyade", 185, 360, sira=3, kol=6, ad="Dukas (ihtiyat)", tohum=4)
    for k, u in enumerate((mer, sol, sag, iht)):
        u.belir(c(0, 0.1) + k * 0.25)
    # Selçuklu (sağda): hilal biçiminde atlı okçular, arkada sultan, tepelerin ardında pusu
    hilal = []
    for k, aci in enumerate((-60, -30, 0, 30, 60)):
        r = math.radians(aci)
        x, y = 1180 - 250 * math.cos(r), 360 + 275 * math.sin(r)
        u = s.birlik("selcuklu", "atli_okcu", x, y, sira=2, kol=4, aci=180, tohum=10 + k)
        hilal.append(u.belir(c(0, 0.45) + abs(k - 2) * 0.2))
    sultan = s.birlik("selcuklu", "agir", 1200, 360, sira=2, kol=4, aci=180, ad="Alparslan", tohum=20)
    sultan.belir(c(0, 0.5))
    pusu_ust = s.birlik("selcuklu", "suvari", 1150, 70, sira=3, kol=5, aci=180, tohum=21)
    pusu_alt = s.birlik("selcuklu", "suvari", 1150, 655, sira=3, kol=5, aci=180, tohum=22)
    alp = s.yakin_plan("Alparslan", c(0, 0.3), b(0) + 1.8, konum="sag_alt", baslik="Alparslan",
                       govde=(0.97, 0.96, 0.92), ifade="kararli", elde={"R": "kilic"})
    alp.poz(c(0, 0.6), "kutlama")

    # 1: hilal düzeni ve ok akınları (yaklaş - ok at - çekil, iki dalga)
    hedefler = [sol, sol, mer, sag, sag]
    for k, (u, h) in enumerate(zip(hilal, hedefler)):
        x0, y0 = u.merkez(c(1))
        t = c(1, 0.15) + k * 0.12
        u.git(t, t + 1.1, x=x0 - 190)
        s.ok_akini(u, h, t + 1.0, t + 2.8, yogunluk=9, tohum=k, ses=(k == 2))
        u.git(t + 2.8, t + 3.7, x=x0)
        u.git(t + 3.9, t + 4.9, x=x0 - 210)
        s.ok_akini(u, h, t + 4.8, t + 6.2, yogunluk=9, tohum=k + 5, ses=(k == 2))
        u.git(t + 6.2, t + 7.0, x=x0)
    for u in (sol, mer, sag):
        u.titre(c(1, 0.4), c(1, 0.4) + 6.0, 0.6)
    s.nesne("yazi", 640, 64, metin="Yaklaş · ok at · çekil", boyut=36, renk=(1, 1, 1), olcek=1.0) \
        .belir(c(1, 0.4)).kaybol(c(2))

    # 2: sahte ricat ve kovalama (akşama kadar)
    from motor.birlikler import Karartma
    s.ekle(Karartma(c(2), b(3), renk=(0.95, 0.45, 0.2), azami=0.3))
    for k, u in enumerate(hilal):
        x0, y0 = u.merkez(c(2))
        u.git(c(2, 0.1), c(2, 0.1) + 4.5, x=x0 + 260, y=360 + (y0 - 360) * 1.15)
    sultan.git(c(2, 0.1), c(2, 0.1) + 4.5, x=1330)
    for u, dx in ((sol, 380), (mer, 380), (sag, 380), (iht, 200)):
        x0, y0 = u.merkez(c(2))
        u.git(c(2, 0.25), c(2, 0.25) + 4.3, x=x0 + dx)
    s.kamera.git(c(2, 0.2), c(2, 0.2) + 4.2, x=760, zoom=1.0)
    s.nesne("yazi", 760, 64, metin="Sahte ricat!", boyut=40, renk=(1, 0.75, 0.6), olcek=1.0).belir(c(2, 0.15)) \
        .kaybol(c(3))
    rom = s.yakin_plan("Romen", c(2, 0.45), b(2) + 2.6, konum="sol_alt", baslik="Romen Diyojen",
                       zemin=(0.85, 0.7, 0.95), ifade="kizgin")
    rom.ifade(c(2, 0.8), "yorgun")

    # 3: dönüş emri, saflar karışır, Dukas çekilir
    for u in (sol, mer, sag):
        u.don(c(3, 0.1), 180, sure=1.2).titre(c(3, 0.1), c(3, 0.1) + 3.5, 1.2)
    iht.don(c(3, 0.35), 180, sure=0.6)
    iht.git(c(3, 0.45), c(3, 0.45) + 3.0, x=-200, egri="hizlan")
    s.nesne("konusma", 300, 250, metin="İmparator yenildi!", boyut=34, olcek=1.0, kuyruk=-1) \
        .belir(c(3, 0.45)).kaybol(c(3, 0.45) + 3.0)
    s.kamera.git(c(3, 0.3), c(3, 0.3) + 1.5, x=560)
    duk = s.yakin_plan("Dukas", c(3, 0.5), b(3) + 2.0, konum="sag_alt", baslik="Andronikos Dukas",
                       zemin=(0.9, 0.6, 0.55), ifade="kizgin", poz="isaret")
    duk.don(c(3, 0.7), -1)

    # 4: tepelerden iki yandan saldırı, hilal kapanır, kanatlar dağılır, imparator esir
    s.kamera.git(c(4), c(4) + 1.2, x=760, zoom=1.0)
    for u in (pusu_ust, pusu_alt):
        u.belir(c(4, 0.05), 0.4)
    pusu_ust.git(c(4, 0.1), c(4, 0.1) + 2.0, x=720, y=110, aci=150)
    pusu_alt.git(c(4, 0.1), c(4, 0.1) + 2.0, x=720, y=610, aci=210)
    halka = [(930, 240), (960, 360), (930, 480), (800, 210), (800, 510)]
    for u, (x, y) in zip(hilal, halka):
        u.git(c(4, 0.15), c(4, 0.15) + 2.0, x=x, y=y)
    sultan.git(c(4, 0.2), c(4, 0.2) + 2.5, x=1090)
    sol.dagil(c(4, 0.45), 2.0)
    sag.dagil(c(4, 0.5), 2.0)
    mer.titre(c(4, 0.3), b(4) + 3, 1.5).git(c(4, 0.3), c(4, 0.3) + 2, yayilma=0.75)
    for k in range(3):
        t = c(4, 0.35) + k * 0.6
        s.nesne("patlama", 760 + (k - 1) * 70, 300 + (k % 2) * 110, metin="ÇAT!", boyut=34, olcek=0.6, tohum=k) \
            .belir(t, ses="kilic_sesi").kaybol(t + 0.6)
    s.kamera.sars(c(4, 0.4), 1.0, 0.6)
    s.nesne("damga", 780, 270, metin="ESİR", boyut=56, olcek=1.4).belir(c(4, 0.85), ses="punch")
    s.kamera.git(c(4, 0.7), c(4, 0.7) + 1.5, x=780, y=360, zoom=1.35)
    s.kamera.punch(c(4, 0.85), 0.1)


# ------------------------------------------------------------------ 5: savaş anı
def savas_ani(s):
    s.sfx("kalabalik", s.t0 + 0.3, 0.8)
    s.kamera.ayarla(s.t0, zoom=1.25, x=520, y=380).git(s.c(0), s.c(0) + 2.5, zoom=1.0, x=640, y=360)
    romen = s.karakter("Romen", x=360, olcek=0.95, ifade="kararli", poz="sunum", elde={"R": "kilic"}).belir(s.c(0, 0.2))
    # 1: dört bir yandan akın + ok yağmuru (sağdan)
    akincilar = []
    for k in range(4):
        a = s.karakter("Akıncı", x=1400, y=600 + k * 14, olcek=0.7, ifade="kararli")
        a.gir(s.c(1, 0.05) + k * 0.25, "sag", x=860 + k * 95, sure=0.8, kos=True)
        akincilar.append(a)
    s.nesne("ok_yagmuru", 620, 300, olcek=1.2, yon=-1, genislik=700, adet=26, hiz=1.1).belir(s.c(1, 0.4), ses=None) \
        .kaybol(s.c(4, 0.2))
    for k in range(5):
        s.sfx("ok", s.c(1, 0.4) + k * 0.35, 0.8)
    s.kamera.sars(s.c(1, 0.5), 1.0, 0.5)
    # 2: kenetlenen kalkanlar, durmayan oklar
    kalkanlar = [s.nesne("kalkan", 130 + k * 70, 560 - (k % 2) * 30, olcek=0.55, renk=BIZANS).belir(s.c(2, 0.1) + k * 0.12)
                 for k in range(4)]
    for k in range(4):
        s.sfx("ok", s.c(2, 0.5) + k * 0.4, 0.7)
    for n in kalkanlar:
        n.salla(s.c(2, 0.6), s.c(2, 0.6) + 1.2).kaybol(s.c(3) - 0.2)
    # 3: Varang muhafızları imparatorun çevresinde
    varang = [s.karakter("Varang", x=x, y=y, olcek=0.75, ifade="kizgin").belir(s.c(3, 0.2) + k * 0.15)
              for k, (x, y) in enumerate(((190, 620), (520, 630), (270, 655)))]
    isim(s, "Varang muhafızları", 360, 160, s.c(3, 0.4), renk=(1, 0.8, 0.6)).kaybol(s.c(4))
    for v in varang:
        v.poz(s.c(3, 0.5), "sunum")
    # 4: kılıç kılıca
    for k, a in enumerate(akincilar[:2]):
        a.git(s.c(4, 0.1), s.c(4, 0.1) + 0.6, x=620 + k * 110, kos=True)
    for k, t in enumerate((s.c(4, 0.3), s.c(4, 0.55), s.c(4, 0.8))):
        s.nesne("patlama", 560 + k * 40, 380 - k * 30, metin="ÇAT!", boyut=44, olcek=0.7, tohum=k,
                aci=(-10, 8, -4)[k]).belir(t, ses="kilic_sesi").kaybol(t + 0.6)
        s.kamera.punch(t, 0.05)
    romen.ifade(s.c(4, 0.3), "kizgin").poz(s.c(4, 0.3), "isaret")
    for v in varang:
        v.titre(s.c(4, 0.3), s.c(4, 0.9), 0.6)
    # 5: muhafızlar birer birer düşer, halka daralır
    for k, v in enumerate(varang):
        v.ifade(s.c(5, 0.1), "yorgun").kaybol(s.c(5, 0.25) + k * 0.5)
    for k, a in enumerate(akincilar):
        a.git(s.c(5, 0.3), s.c(5, 0.3) + 1.5, x=600 + k * 70)
    s.sfx("kilic_sesi", s.c(5, 0.3), 0.6)
    # 6: atı öldürüldü, eli yaralandı
    isim(s, "Atı öldürüldü", 360, 160, s.c(6, 0.1), renk=(1, 0.6, 0.5)).kaybol(s.c(6, 0.55))
    romen.ifade(s.c(6, 0.15), "panik").zipla(s.c(6, 0.1), 30)
    isim(s, "Elinden yaralandı", 360, 160, s.c(6, 0.6), renk=(1, 0.6, 0.5)).kaybol(s.c(7, 0.1))
    romen.ifade(s.c(6, 0.6), "yorgun").poz(s.c(6, 0.6), "yorgun")
    # 7: tanınmadan esir
    s.kamera.git(s.c(7), s.c(7) + 2, x=520, y=400, zoom=1.25)
    yakalayan = akincilar[0]
    yakalayan.git(s.c(7, 0.1), s.c(7, 0.1) + 1.0, x=520).poz(s.c(7, 0.35), "isaret")
    s.nesne("damga", 330, 280, metin="ESİR", boyut=56, olcek=1.5).belir(s.c(7, 0.4), ses="punch")
    s.nesne("konusma", 640, 230, metin="Bu da kim?", boyut=38, olcek=1.0, kuyruk=1).belir(s.c(7, 0.7))
    yakalayan.ifade(s.c(7, 0.7), "saskin")


# ------------------------------------------------------------------ 6
def acilan_kapi(s):
    romen = s.karakter("Romen", x=380, olcek=0.95, ifade="uzgun", poz="yorgun").belir(s.c(0, 0.15))
    alp = s.karakter("Alparslan", x=920, olcek=0.95, ifade="kararli").belir(s.c(0, 0.25))
    b1 = s.nesne("konusma", 870, 230, metin="Beni esir alsaydın ne yapardın?", boyut=34, azami=360, olcek=1.0,
                 kuyruk=1).belir(s.c(0, 0.55))
    alp.poz(s.c(0, 0.55), "sunum")
    b1.kaybol(s.c(1))
    b2 = s.nesne("konusma", 430, 230, metin="Belki öldürür, belki teşhir ederdim.", boyut=34, azami=360,
                 olcek=1.0, kuyruk=-1).belir(s.c(1, 0.2))
    romen.ifade(s.c(1, 0.2), "utangac").bas_egim(s.c(1, 0.2), 8)
    b2.kaybol(s.c(2))
    s.nesne("konusma", 870, 230, metin="Seni affediyorum.", boyut=38, olcek=1.0, kuyruk=1).belir(s.c(2, 0.25)) \
        .kaybol(s.c(3) - 0.2)
    alp.ifade(s.c(2, 0.25), "mutlu").poz(s.c(2, 0.25), "el_salla")
    romen.ifade(s.c(2, 0.55), "saskin").bas_egim(s.c(2, 0.55), 0).poz(s.c(2, 0.55), "dur")
    romen.ifade(s.c(2, 0.8), "mutlu")
    s.nesne("isiltilar", 640, 330, olcek=1.4).belir(s.c(2, 0.6), ses=None)

    for k in (romen, alp):
        k.kaybol(s.c(3, 0.1))
    kapi = s.nesne("kapi", 640, 400, olcek=1.2, acik=0.0, metin="ANADOLU").belir(s.c(3, 0.15), ses="punch")
    kapi.ayarla(s.c(3, 0.6), acik=1.0, sure=1.6)
    s.sfx("swoosh_yukari", s.c(3, 0.6))
    s.sfx("ding", s.c(3, 0.9), 0.6)
    s.kamera.git(s.c(3, 0.5), s.bitis(3) + 1.0, y=380, zoom=1.25)


# ------------------------------------------------------------------ 7: sonrası
def yeni_yurt(s):
    romen = s.karakter("Romen", x=330, y=640, olcek=0.75, ifade="uzgun", poz="yorgun").belir(s.c(0, 0.3))
    ix, iy = s.yer(29.72, 40.43)
    mx, my = s.yer(*MALAZGIRT)
    s.nesne("pin", mx, my, metin="Malazgirt", olcek=0.8).belir(s.c(0, 0.2))
    s.nesne("damga", 330, 330, metin="TAHT GİTTİ", boyut=38, olcek=1.0).belir(s.c(1, 0.25), ses="punch") \
        .kaybol(s.c(2) - 0.2)
    romen.ifade(s.c(1, 0.5), "uzgun").bas_egim(s.c(1, 0.5), -10)
    romen.kaybol(s.c(2) - 0.2)
    for k in range(5):  # Türkmen boyları sağdan (doğudan) Anadolu içlerine
        t = s.c(2, 0.15) + k * 0.25
        s.nesne("ok", 1150 - k * 30, 360 + k * 40, olcek=0.7, aci=180, renk=SELCUK).belir(t, ses=None) \
            .git(t, t + 3.0, x=620 - k * 60).kaybol(s.c(4) - 0.3)
    s.sfx("whoosh", s.c(2, 0.2), 0.6)
    # 3: aileler, sürüler, çadırlarla göç
    for k in range(4):
        t = s.karakter("Uz", x=1400, y=640 + k * 12, olcek=0.55 if k != 3 else 0.4, ifade="mutlu",
                       elde={"R": ("sancak", {"renk": SELCUK})} if k == 0 else None)
        t.gir(s.c(3, 0.05) + k * 0.35, "sag", x=900 - k * 90, sure=3.0)
        t.kaybol(s.c(4) - 0.2)
    isim(s, "Yeni yurt arayışı", 900, 300, s.c(3, 0.5), renk=ALTIN).kaybol(s.c(4) - 0.2)
    # 4: Süleyman Şah ve İznik
    s.nesne("pin", ix, iy, metin="İznik", olcek=1.0, nabiz=1).belir(s.c(4, 0.45))
    sul = s.karakter("Süleyman Şah", x=ix + 120, y=iy + 250, olcek=0.7, ifade="gururlu").belir(s.c(4, 0.2))
    sul.poz(s.c(4, 0.55), "isaret")
    isim(s, "Süleyman Şah", ix + 120, iy - 40, s.c(4, 0.25))
    s.kamera.git(s.c(4), s.c(4) + 1.5, x=ix + 250, y=iy + 120, zoom=1.2)
    # 5: Anadolu Selçuklu Devleti
    s.nesne("levha", ix + 330, iy + 40, metin="Anadolu Selçuklu Devleti", boyut=32, olcek=1.0).belir(s.c(5, 0.2))
    s.nesne("isiltilar", ix + 120, iy + 120, olcek=1.4).belir(s.c(5, 0.3), ses=None)
    sul.poz(s.c(5, 0.3), "kutlama").ifade(s.c(5, 0.3), "mutlu")
    s.sfx("ding", s.c(5, 0.35), 0.4)
    # 6: "Turchia"
    s.kamera.git(s.c(6), s.c(6) + 2.0, x=640, y=360, zoom=1.0)
    s.nesne("levha", 1000, 330, metin="TURCHIA", boyut=46, olcek=1.2).belir(s.c(6, 0.6))
    # 7: kapanış cümlesi
    s.nesne("yazi", 640, 110, metin="1071: yeni bir yurdun ilk adımı", boyut=46, renk=ALTIN, olcek=1.0).belir(s.c(7, 0.3))


# ------------------------------------------------------------------ 0a: Selçukluların doğuşu
GAZNELI = [(56, 38), (61, 38.8), (66, 37.6), (71, 37.2), (72.5, 34.5), (71, 30.5), (67, 27.5), (62, 26), (58, 27.5),
           (56.5, 31), (55.5, 34.5)]
YER = {"Cend": (65.6, 44.8), "Merv": (61.83, 37.6), "Dandanakan": (62.2, 37.1), "Bağdat": (44.37, 33.31),
       "Gazne": (68.4, 33.55), "İstanbul": (28.98, 41.01), "Sivas": (37.02, 39.75), "Erzurum": (41.27, 39.9),
       "Halep": (37.15, 36.2), "Musul": (43.13, 36.34), "Hoy": (44.95, 38.55), "İznik": (29.72, 40.43)}


def bozkir_guc(s):
    c = s.c
    cx, cy = s.yer(*YER["Cend"])
    mx, my = s.yer(*YER["Merv"])
    dx_, dy_ = s.yer(*YER["Dandanakan"])
    bx, by = s.yer(*YER["Bağdat"])
    gx, gy = s.yer(*YER["Gazne"])
    s.kamera.ayarla(s.t0, x=cx, y=cy + 60, zoom=1.35).git(c(0, 0.3), c(0, 0.3) + 3, x=640, y=360, zoom=1.0)
    s.nesne("pin", cx, cy, metin="Cend", nabiz=1, olcek=1.0).belir(c(0, 0.3))
    tug = s.karakter("Tuğrul", x=cx - 30, y=cy + 200, olcek=0.55).belir(c(1, 0.35))
    cag = s.karakter("Çağrı", x=cx + 50, y=cy + 205, olcek=0.55).belir(c(1, 0.45))
    isim(s, "Tuğrul ve Çağrı", cx + 10, cy + 235, c(1, 0.5), boyut=30).kaybol(c(3))
    s.nesne("ok", (cx + mx) / 2, (cy + my) / 2, olcek=0.8, aci=math.degrees(math.atan2(my - cy, mx - cx)),
            renk=SELCUK).belir(c(1, 0.6), ses="whoosh")
    for k_, (kar, dx) in enumerate(((tug, -30), (cag, 40))):
        kar.git(c(1, 0.65), c(1, 0.65) + 2.5, x=mx + dx, y=my + 200)
    s.nesne("pin", mx, my, metin="Horasan", olcek=0.9, yazi_dy=-70).belir(c(1, 0.8))
    s.yakin_plan("Akıncı", c(2, 0.1), s.bitis(2) + 0.6, konum="sol_alt", baslik="Bozkır atlısı", ifade="mutlu",
                 poz="isaret", olcek=1.0)
    mes = s.karakter("Mesud", x=gx - 40, y=gy + 200, olcek=0.6, ifade="gururlu").belir(c(3, 0.2))
    gfil = s.nesne("fil", gx + 70, gy + 120, olcek=0.45, yuru=0.5, hac=0, ortu=(0.85, 0.48, 0.12))
    gfil.belir(c(3, 0.3), ses="punch").kaybol(c(4))
    isim(s, "Gazneli Mesud", gx - 40, gy + 235, c(3, 0.3), boyut=30).kaybol(c(5))
    s.nesne("yazi", 640, 70, metin="1040 · Dandanakan", boyut=48, renk=ALTIN, olcek=1.0).belir(c(4, 0.2)).kaybol(c(6))
    s.kamera.git(c(4), c(4) + 1.5, x=dx_, y=dy_ + 60, zoom=1.5)
    for kar, ddx in ((tug, -190), (cag, -120)):
        kar.git(c(4), c(4) + 1.5, x=dx_ + ddx, y=dy_ + 175)
    mes.git(c(4), c(4) + 1.5, x=dx_ + 120, y=dy_ + 175)
    fil = s.nesne("fil", dx_ + 200, dy_ + 95, olcek=0.4, yuru=1.0, hac=0, ortu=(0.85, 0.48, 0.12))
    fil.belir(c(4, 0.3), ses=None)
    ari = s.nesne("ari_suru", dx_ - 60, dy_ - 10, olcek=0.6, adet=14, hucum=0.0, hedef_x=220).belir(c(5, 0.05))
    ari.ayarla(c(5, 0.2), hucum=1.0, sure=0.5)
    fil.ayarla(c(5, 0.4), ter=1.0, sure=0.1)
    mes.ifade(c(5, 0.45), "panik").titre(c(5, 0.45), c(5, 0.9))
    s.nesne("carpi", dx_ + 120, dy_ + 20, olcek=0.6).belir(c(5, 0.85), ses="bzzt").kaybol(c(6))
    s.kamera.git(c(6), c(6) + 1.5, x=mx, y=my + 40, zoom=1.2)
    for n in (fil, ari):
        n.kaybol(c(6))
    mes.kaybol(c(6))
    for kar, ddx in ((tug, -30), (cag, 40)):
        kar.git(c(6), c(6) + 1.0, x=mx + ddx, y=my + 200)
    s.nesne("sancak", mx + 10, my + 80, renk=SELCUK, olcek=0.9).belir(c(6, 0.2))
    s.nesne("levha", mx + 10, my - 90, metin="Büyük Selçuklu Devleti", boyut=30, olcek=1.0).belir(c(6, 0.3))
    s.nesne("isiltilar", mx, my, olcek=1.2).belir(c(6, 0.35), ses="ding")
    s.kamera.git(c(7), c(7) + 2.0, x=(mx + bx) / 2, y=(my + by) / 2 + 60, zoom=1.0)
    tug.git(c(7, 0.1), c(7, 0.1) + 2.5, x=bx + 40, y=by + 180)
    cag.kaybol(c(7, 0.2))
    s.nesne("pin", bx, by, metin="Bağdat", nabiz=1, olcek=1.0).belir(c(7, 0.3))
    s.nesne("levha", bx + 30, by - 90, metin="1055", boyut=32, olcek=1.0).belir(c(7, 0.6))
    tug.kaybol(c(8, 0.05))
    alp = s.karakter("Alparslan", x=bx + 40, y=by + 180, olcek=0.6, ifade="kararli").belir(c(8, 0.15))
    alp.poz(c(8, 0.5), "isaret").don(c(8, 0.45), -1)
    isim(s, "Alparslan", bx + 40, by + 215, c(8, 0.25), boyut=30)
    s.nesne("ok", bx - 120, by - 10, olcek=1.0, aci=180, renk=SELCUK).belir(c(8, 0.55), ses="whoosh")
    s.kamera.git(c(8, 0.5), c(8, 0.5) + 2.0, x=bx - 80, y=by + 40, zoom=1.15)


# ------------------------------------------------------------------ 0b: Bizans'ın krizi
def bizans_krizi(s):
    c = s.c
    kalkan = s.nesne("kalkan", 640, 300, olcek=2.2).belir(c(0, 0.1), ses="punch")
    kalkan.salla(c(0, 0.5), c(0, 0.5) + 1.2).kaybol(c(1))
    bas = s.karakter("Basileios", x=640, olcek=0.95, ifade="gururlu").belir(c(1, 0.05))
    isim(s, "II. Basileios", 640, 230, c(1, 0.1)).kaybol(c(1, 0.45))
    bas.kaybol(c(1, 0.45))
    for k in range(3):
        t = c(1, 0.5) + k * 0.45
        imp = s.karakter("İmparator", x=380 + k * 260, olcek=0.75, ifade=("saskin", "uzgun", "panik")[k],
                         govde=((0.6, 0.35, 0.65), (0.5, 0.4, 0.6), (0.55, 0.3, 0.45))[k])
        imp.belir(t).kaybol(c(2) - 0.1)
    yuh = s.karakter("Yuhanna Dukas", x=330, olcek=0.9, ifade="kararli").belir(c(2, 0.05))
    ent = s.karakter("İmparator", x=950, olcek=0.9, ifade="saskin", yon=-1).belir(c(2, 0.1))
    s.nesne("konusma", 420, 240, metin="...", boyut=44, olcek=1.0, kuyruk=-1).belir(c(2, 0.2)).kaybol(c(2, 0.6))
    s.nesne("patlama", 820, 230, metin="DARBE!", boyut=48, olcek=0.9).belir(c(2, 0.6), ses="punch").kaybol(c(3))
    ent.ifade(c(2, 0.6), "panik").titre(c(2, 0.6), c(3)).kaybol(c(3))
    yuh.kaybol(c(3))
    askerler = [s.karakter("Asker", x=420 + k * 140, olcek=0.75, ifade="uzgun").belir(c(3, 0.05) + k * 0.1)
                for k in range(3)]
    for k, a in enumerate(askerler):
        a.cik(c(3, 0.45) + k * 0.15, "sol", sure=1.6)
    for k in range(4):
        s.nesne("para", 900 + (k % 2) * 80, 300 - k * 40, olcek=0.5, hiz=6.0).belir(c(3, 0.6) + k * 0.15) \
            .kaybol(c(4))
    for k, ad in enumerate(("Frank", "Varang", "Peçenek")):
        s.nesne("sancak", 760 + k * 150, 560, renk=BIZANS if k < 2 else (0.6, 0.45, 0.25), olcek=0.8) \
            .belir(c(3, 0.75) + k * 0.15).kaybol(c(4))
        isim(s, ad, 800 + k * 150, 600, c(3, 0.75) + k * 0.15, renk=ALTIN, boyut=28).kaybol(c(4))
    s.nesne("levha", 640, 300, metin="Sınır boş!", boyut=40, olcek=1.1).belir(c(4, 0.2)).kaybol(c(5))
    s.nesne("carpi", 790, 250, olcek=0.6).belir(c(4, 0.45), ses="bzzt").kaybol(c(5))
    ak = s.karakter("Akıncı", x=1400, olcek=0.8, ifade="kararli")
    ak.gir(c(5, 0.1), "sag", x=820, sure=1.0, kos=True)
    s.nesne("levha", 820, 230, metin="1067 · Kayseri", boyut=34, olcek=1.0).belir(c(5, 0.5)).kaybol(c(6))
    ak.kaybol(c(6))
    evd = s.karakter("Evdokia", x=520, olcek=0.9, ifade="kararli").belir(c(6, 0.2))
    rom = s.karakter("Romen", x=760, olcek=0.95, ifade="gururlu", yon=-1).belir(c(6, 0.4))
    isim(s, "Evdokia", 520, 230, c(6, 0.25), boyut=32)
    isim(s, "Romen Diyojen", 760, 230, c(6, 0.45), boyut=32)
    s.nesne("kalp", 640, 300, olcek=0.6).belir(c(6, 0.7))
    s.nesne("levha", 640, 120, metin="1068", boyut=36, olcek=1.0).belir(c(6, 0.6))
    yuh2 = s.karakter("Yuhanna Dukas", x=-150, olcek=0.9, ifade="kizgin")
    yuh2.gir(c(7, 0.05), "sol", x=230, sure=1.0)
    yuh2.poz(c(7, 0.5), "eller_belde")
    isim(s, "Dukas ailesi", 230, 230, c(7, 0.3), renk=(1, 0.7, 0.6), boyut=32)
    rom.bak(c(7, 0.5), -1).ifade(c(7, 0.5), "dusunceli")
    s.kamera.git(c(7), c(7) + 1.2, x=480, zoom=1.15)


# ------------------------------------------------------------------ 2b: sefer yolu
def sefer_yolu(s):
    c = s.c
    P = lambda ad: s.yer(*YER[ad])
    for ad in ("İstanbul", "Sivas", "Erzurum"):
        s.nesne("pin", *P(ad), metin=ad, olcek=0.8, renk=(0.6, 0.3, 0.65)).belir(
            c(0, 0.2) if ad == "İstanbul" else c(1, 0.2 if ad == "Sivas" else 0.6))
    ix, iy = P("İstanbul")
    ordu = s.birlik("bizans", "agir", ix + 30, iy + 40, sira=3, kol=5, olcek=1.0, ad="Romen Diyojen", tohum=31)
    ordu.belir(c(0, 0.3))
    ax, ay = s.yer(32.5, 39.8)
    ordu.git(c(0, 0.5), c(0, 0.5) + 2.5, x=ax, y=ay)
    s.nesne("levha", 640, 90, metin="1071 baharı", boyut=34, olcek=1.0).belir(c(0, 0.3)).kaybol(c(2))
    sx, sy = P("Sivas")
    ex, ey = P("Erzurum")
    ordu.git(c(1, 0.05), c(1, 0.5), x=sx, y=sy + 20)
    ordu.git(c(1, 0.55), c(1, 0.98), x=ex - 30, y=ey + 20)
    s.kamera.git(c(1), c(1) + 3, x=760, zoom=1.1)
    rom = s.yakin_plan("Romen", c(2, 0.1), s.bitis(2) + 0.4, konum="sol_alt", baslik="Romen Diyojen",
                       zemin=(0.85, 0.7, 0.95), ifade="kizgin", poz="dur_isareti")
    s.nesne("patlama", ex - 40, ey - 70, metin="Yağma!", boyut=34, olcek=0.7).belir(c(2, 0.4), ses="punch") \
        .kaybol(c(3))
    ordu.titre(c(2, 0.3), c(3))
    ordu.git(c(3, 0.2), c(3, 0.9), yayilma=1.25)
    mx, my = s.yer(*MALAZGIRT)
    ahx, ahy = s.yer(*AHLAT)
    s.nesne("pin", mx, my, metin="Malazgirt", nabiz=1, olcek=0.9).belir(c(4, 0.2))
    s.nesne("pin", ahx, ahy, metin="Ahlat", nabiz=1, olcek=0.8, yazi_dy=32, renk=(0.95, 0.6, 0.2)).belir(c(4, 0.35))
    s.nesne("ok", (ex + mx) / 2, (ey + my) / 2, olcek=0.6, aci=math.degrees(math.atan2(my - ey, mx - ex)),
            renk=BIZANS).belir(c(4, 0.5), ses=None)
    hx, hy = P("Halep")
    s.kamera.git(c(5), c(5) + 1.5, x=hx + 150, y=hy - 40, zoom=1.2)
    s.nesne("pin", hx, hy, metin="Halep", olcek=0.9, renk=SELCUK).belir(c(5, 0.15))
    turk = s.birlik("selcuklu", "atli_okcu", hx + 60, hy + 40, sira=2, kol=4, olcek=1.0, aci=0, ad="Alparslan",
                    tohum=32)
    turk.belir(c(5, 0.25))
    s.yakin_plan("Alparslan", c(5, 0.3), c(6, 0.3), konum="sag_alt", baslik="Alparslan", ifade="dusunceli")
    mux, muy = P("Musul")
    hox, hoy = P("Hoy")
    s.kamera.git(c(6, 0.1), c(6, 0.1) + 3.5, x=mx + 60, y=my + 20, zoom=1.1)
    turk.git(c(6, 0.1), c(6, 0.45), x=mux, y=muy, aci=-30)
    turk.git(c(6, 0.47), c(6, 0.75), x=hox, y=hoy, aci=-70)
    turk.git(c(6, 0.77), c(6, 1.0) + 0.6, x=mx + 90, y=my + 30, aci=180, yayilma=1.2)
    katil = s.birlik("notr", "suvari", mux + 40, muy + 50, sira=1, kol=4, olcek=0.9, aci=-40, tohum=33)
    katil.belir(c(6, 0.35)).git(c(6, 0.45), c(6, 0.75), x=hox + 40, y=hoy + 40)
    katil.git(c(6, 0.77), c(6, 1.0) + 0.6, x=mx + 140, y=my + 70, aci=180)
    isim(s, "Türkmen ve Kürt birlikleri", mux, muy + 90, c(6, 0.4), renk=ALTIN, boyut=26).kaybol(c(6, 0.8))


# ------------------------------------------------------------------ 3b: ilk kan (kuş bakışı)
def ilk_kan(s):
    c = s.c
    s.kamera.ayarla(s.t0, x=600, y=360, zoom=1.0)
    s.nesne("kale_ust", 330, 360, olcek=0.75, metin="Malazgirt").belir(c(0, 0.1))
    ordu = [s.birlik("bizans", tur, x, y, sira=3, kol=5, tohum=40 + k)
            for k, (tur, x, y) in enumerate((("piyade", 150, 200), ("agir", 130, 360), ("piyade", 150, 520)))]
    for k, u in enumerate(ordu):
        u.belir(c(0, 0.2) + k * 0.2)
    s.nesne("levha", 330, 230, metin="Teslim!", boyut=30, olcek=1.0).belir(c(0, 0.6)).kaybol(c(1, 0.3))
    s.nesne("yazi", 640, 64, metin="23–24 Ağustos 1071", boyut=40, renk=ALTIN, olcek=1.0).belir(c(0, 0.1)) \
        .kaybol(c(2))
    toplayici = [s.birlik("bizans", "piyade", 430, y, sira=2, kol=3, tohum=45 + k) for k, y in enumerate((210, 510))]
    for k, u in enumerate(toplayici):
        u.belir(c(1, 0.05)).git(c(1, 0.1), c(1, 0.6), x=700, y=(170, 550)[k], yayilma=1.6)
    onc = [s.birlik("selcuklu", "atli_okcu", 1350, y, sira=2, kol=3, aci=180, tohum=50 + k)
           for k, y in enumerate((170, 550))]
    for k, u in enumerate(onc):
        u.belir(c(1, 0.4)).git(c(1, 0.4), c(1, 0.85), x=930)
        s.ok_akini(u, toplayici[k], c(1, 0.8), c(1, 0.8) + 2.0, yogunluk=7, tohum=k, ses=(k == 0))
        toplayici[k].titre(c(1, 0.85), c(2, 0.3))
    vas = s.birlik("bizans", "suvari", 300, 360, sira=2, kol=4, ad="Vasilakis", tohum=55)
    vas.belir(c(2, 0.0)).git(c(2, 0.05), c(2, 0.45), x=800, egri="hizlan")
    pusu = [s.birlik("selcuklu", "suvari", 900, y, sira=2, kol=4, aci=(150, 210)[k], tohum=56 + k)
            for k, y in enumerate((40, 690))]
    for k, u in enumerate(pusu):
        u.belir(c(2, 0.35), 0.3).git(c(2, 0.4), c(2, 0.75), x=840, y=(270, 450)[k])
    vas.titre(c(2, 0.6), c(2, 1.0)).dagil(c(2, 0.85), 1.2)
    s.nesne("damga", 800, 300, metin="ESİR", boyut=46, olcek=1.1).belir(c(2, 0.9), ses="punch").kaybol(c(3, 0.3))
    s.kamera.punch(c(2, 0.9), 0.08)
    bri = s.birlik("bizans", "suvari", 300, 360, sira=2, kol=4, ad="Briyennios", tohum=60)
    bri.belir(c(3, 0.0)).git(c(3, 0.05), c(3, 0.4), x=680)
    bri.titre(c(3, 0.4), c(3, 0.7)).git(c(3, 0.6), c(3, 1.0), x=320, yayilma=0.7)
    for u in toplayici:
        u.dagil(c(3, 0.3), 1.2)
    sultan = s.birlik("selcuklu", "agir", 1350, 360, sira=3, kol=5, aci=180, ad="Alparslan", tohum=61)
    sultan.belir(c(4, 0.05)).git(c(4, 0.05), c(4, 0.6), x=1080)
    for u in onc + pusu:
        u.git(c(4, 0.1), c(4, 0.7), x=1000)
    s.nesne("konusma", 360, 210, metin="Sultanın ordusu!", boyut=34, olcek=1.0, kuyruk=-1).belir(c(4, 0.5)) \
        .kaybol(c(5))
    kitap = s.nesne("kitap", 1000, 300, olcek=0.6).belir(c(5, 0.15))
    kitap.git(c(5, 0.25), c(5, 0.9), x=480)
    isim(s, "Barış teklifi", 1000, 250, c(5, 0.2), renk=ALTIN, boyut=30).git(c(5, 0.25), c(5, 0.9), x=480) \
        .kaybol(c(6, 0.6))
    s.yakin_plan("Alparslan", c(5, 0.2), c(6), konum="sag_alt", baslik="Alparslan", ifade="kararli", poz="sunum")
    rom = s.yakin_plan("Romen", c(6, 0.05), s.bitis(6) + 1.0, konum="sol_alt", baslik="Romen Diyojen",
                       zemin=(0.85, 0.7, 0.95), ifade="kizgin", poz="dur_isareti")
    s.nesne("carpi", 480, 300, olcek=0.7).belir(c(6, 0.4), ses="bzzt")
    kitap.kaybol(c(6, 0.5))


# ------------------------------------------------------------------ 3c: savaştan önceki gece
def gece(s):
    c = s.c
    s.nesne("yazi", 640, 70, metin="25 Ağustos 1071 · Gece", boyut=44, renk=(0.85, 0.9, 1.0), olcek=1.0) \
        .belir(c(0, 0.1)).kaybol(c(2))
    s.kamera.ayarla(s.t0, x=500, zoom=1.1)
    askerler = [s.karakter("Asker", x=170 + k * 150, y=610 + (k % 2) * 10, olcek=0.75, ifade="yorgun",
                           poz="yorgun").belir(c(0, 0.2) + k * 0.15) for k in range(3)]
    s.nesne("ok_yagmuru", 380, 330, olcek=1.0, yon=-1, genislik=520, adet=10, hiz=0.7).belir(c(1, 0.1), ses=None) \
        .kaybol(c(2))
    for k in range(4):
        s.sfx("ok", c(1, 0.15) + k * 0.7, 0.6)
    for k, a in enumerate(askerler):
        a.ifade(c(1, 0.2) + k * 0.1, "panik").titre(c(1, 0.2), c(1, 0.9))
    uzlar = [s.karakter("Uz", x=260 + k * 90, y=640, olcek=0.55, ifade="kararli") for k in range(3)]
    for k, u in enumerate(uzlar):
        u.belir(c(2, 0.1) + k * 0.1).cik(c(2, 0.35) + k * 0.15, "sag", sure=2.0)
    for a in askerler:
        a.ifade(c(2, 0.4), "saskin").bak(c(2, 0.4), 1)
    for a in askerler:
        a.kaybol(c(3))
    rom = s.karakter("Romen", x=260, olcek=0.9, ifade="yorgun").belir(c(3, 0.05))
    duk = s.karakter("Dukas", x=480, olcek=0.85, ifade="kararli", yon=-1).belir(c(3, 0.2))
    isim(s, "Andronikos Dukas", 480, 250, c(3, 0.3), renk=(1, 0.7, 0.6), boyut=30).kaybol(c(4, 0.1))
    duk.don(c(3, 0.7), 1).bak(c(3, 0.7), 1, 0.3)
    rom.kaybol(c(4, 0.1))
    duk.kaybol(c(4, 0.1))
    s.kamera.git(c(4), c(4) + 2.0, x=900, zoom=1.1)
    alp = s.karakter("Alparslan", x=1080, olcek=0.9, ifade="dusunceli").belir(c(4, 0.1))
    imam = s.karakter("Ebu Nasr", x=860, olcek=0.88, ifade="notr", yon=1).belir(c(4, 0.3))
    isim(s, "Ebu Nasr el-Buhari", 860, 250, c(4, 0.4), boyut=30)
    s.nesne("konusma", 900, 170, metin="Cuma günü, dualar edilirken saldır.", boyut=32, azami=360, olcek=1.0,
            kuyruk=-1).belir(c(5, 0.15))
    imam.poz(c(5, 0.15), "sunum")
    s.nesne("yildiz", 1000, 110, olcek=0.4).belir(c(5, 0.6))
    alp.ifade(c(6, 0.1), "kararli").poz(c(6, 0.3), "eller_belde")
    s.kamera.punch(c(6, 0.3), 0.06)


# ------------------------------------------------------------------ 6b: sultanın sonu
def sultanin_sonu(s):
    c = s.c
    alp = s.karakter("Alparslan", x=760, olcek=1.0, ifade="gururlu", elde={"R": "kilic"}).belir(c(0, 0.1))
    s.nesne("sancak", 1000, 560, renk=SELCUK, olcek=1.0).belir(c(0, 0.2))
    s.nesne("yazi", 640, 80, metin="1072 · Maveraünnehir", boyut=42, renk=ALTIN, olcek=1.0).belir(c(1, 0.05)) \
        .kaybol(c(3))
    esir = s.karakter("Esir komutan", x=-150, olcek=0.85, ifade="kizgin")
    esir.gir(c(1, 0.05), "sol", x=420, sure=1.4)
    s.nesne("kilic", 560, 470, olcek=0.4, aci=-60).belir(c(1, 0.65), ses="kilic_sesi").kaybol(c(1, 0.65) + 0.8)
    alp.ifade(c(1, 0.7), "saskin").titre(c(1, 0.7), c(2))
    esir.kaybol(c(2))
    alp.ifade(c(2, 0.1), "yorgun").poz(c(2, 0.1), "yorgun")
    alp.kaybol(c(2, 0.6), 1.5)
    s.kamera.git(c(2), c(2) + 3, x=900, y=380, zoom=1.2)
    s.nesne("dusunce", 640, 230, metin="Güç insanı yanıltabilir...", boyut=36, azami=380, olcek=1.0) \
        .belir(c(3, 0.2)).kaybol(c(4))
    s.kamera.git(c(4), c(4) + 1.5, x=640, y=360, zoom=1.0)
    mel = s.karakter("Melikşah", x=640, olcek=1.0, ifade="gururlu").belir(c(4, 0.1))
    mel.poz(c(4, 0.5), "kutlama")
    isim(s, "Melikşah", 640, 230, c(4, 0.2))
    s.nesne("levha", 640, 120, metin="1072 – 1092", boyut=34, olcek=1.0).belir(c(4, 0.35))
    s.nesne("isiltilar", 640, 380, olcek=1.6).belir(c(4, 0.5), ses="ding")


# ------------------------------------------------------------------ 8: zaferin sırrı (özet)
def zaferin_sirri(s):
    c = s.c
    s.nesne("soru", 640, 280, olcek=1.3, boyut=170).belir(c(0, 0.2)).salla(c(0, 0.4), c(0, 0.4) + 1).kaybol(c(1))
    # 1: hız — fil ile arı
    s.nesne("yazi", 220, 120, metin="1 · HIZ", boyut=52, renk=ALTIN, olcek=1.0).belir(c(1, 0.05)).kaybol(c(2))
    fil = s.nesne("fil", 380, 470, olcek=0.9, yuru=0.6).belir(c(1, 0.15))
    ari = s.nesne("ari_suru", 900, 330, olcek=1.0, adet=14, hucum=0.0, hedef_x=-380).belir(c(1, 0.2))
    ari.ayarla(c(1, 0.45), hucum=1.0, sure=0.4)
    fil.ayarla(c(1, 0.6), ter=1.0, sure=0.1)
    for n in (fil, ari):
        n.kaybol(c(2) - 0.1)
    # 2: birlik — tek sancak etrafında kenetlenme / bölünen ordu
    s.nesne("yazi", 220, 120, metin="2 · BİRLİK", boyut=52, renk=ALTIN, olcek=1.0).belir(c(2, 0.05)).kaybol(c(3))
    s.nesne("sancak", 950, 560, renk=SELCUK, olcek=1.1).belir(c(2, 0.15)).kaybol(c(3))
    akincilar = [s.karakter("Akıncı", x=850 + k * 70, y=620 + (k % 2) * 12, olcek=0.6, ifade="kararli")
                 .belir(c(2, 0.2) + k * 0.08) for k in range(4)]
    askerler = [s.karakter("Asker", x=200 + k * 110, y=620 + (k % 2) * 12, olcek=0.6, ifade="uzgun")
                .belir(c(2, 0.45) + k * 0.08) for k in range(3)]
    askerler[0].cik(c(2, 0.75), "sol", sure=1.2)
    askerler[2].don(c(2, 0.8), -1).ifade(c(2, 0.8), "saskin")
    for k in akincilar + askerler:
        k.kaybol(c(3))
    # 3: sabır — doğru anı beklemek
    s.nesne("yazi", 220, 120, metin="3 · SABIR", boyut=52, renk=ALTIN, olcek=1.0).belir(c(3, 0.05)).kaybol(c(4))
    alp = s.karakter("Alparslan", x=640, olcek=0.95, ifade="dusunceli", poz="dusun").belir(c(3, 0.15))
    saat = s.nesne("saat", 860, 280, olcek=0.9, hiz=3.0).belir(c(3, 0.2))
    alp.ifade(c(3, 0.75), "kararli").poz(c(3, 0.75), "isaret")
    s.nesne("hilal", 1150, 380, olcek=0.7, kapan=0.0).belir(c(3, 0.6)).ayarla(c(3, 0.8), kapan=1.0, sure=0.8) \
        .kaybol(c(4))
    for n in (alp,):
        n.kaybol(c(4))
    saat.kaybol(c(4))
    # 4: saraydaki ihanet
    duk = s.karakter("Dukas", x=640, olcek=1.0, ifade="kararli").belir(c(4, 0.15))
    s.nesne("damga", 640, 250, metin="İHANET", boyut=52, olcek=1.2).belir(c(4, 0.55), ses="punch")
    duk.cik(c(4, 0.75), "sol", sure=1.5, kos=True)
    s.kamera.punch(c(4, 0.55), 0.08)


SAHNELER = [
    dict(baslik="Bozkırdan Doğan Güç", arkaplan="harita", gecis="punch", kurgu=bozkir_guc,
         arkaplan_p=dict(kapsam=(44.0, 76.0, 39.5), bolgeler=[((0.85, 0.48, 0.12), GAZNELI)],
                         etiketler=[("HORASAN", 58.5, 35.6, 32), ("GAZNELİLER", 66.5, 31.8, 30),
                                    ("Hazar Denizi", 51.0, 41.5, 26)]),
         aralar={4: 1.0, 5: 1.4},
         metin=[
             "Bu hikâye, Malazgirt'ten yaklaşık elli yıl önce, Aral Gölü'nün güneyindeki bozkırlarda başlar.",
             "Oğuzların Kınık boyundan Selçuk Bey'in torunları Tuğrul ve Çağrı, boylarını Horasan'a taşıdı.",
             "Bu bozkır atlıları daha çocukken ata binmeyi ve at üstünden ok atmayı öğreniyordu.",
             "Bölgenin hâkimi Gazneliler ise bu göçebeleri kolayca dağıtabileceklerini düşünüyordu.",
             "Ama bin kırk yılında Dandanakan'da işler tam tersine döndü.",
             "Filleri ve ağır ordusuyla gelen Sultan Mesud, susuzluk ve bitmeyen akınlarla yıpratıldı ve ağır bir "
             "yenilgi aldı.",
             "Bu zaferle Büyük Selçuklu Devleti kuruldu.",
             "On beş yıl sonra Tuğrul Bey Bağdat'a girdi ve İslam dünyasının en güçlü hükümdarı oldu.",
             "Tuğrul'un ölümünden sonra tahta yeğeni Alparslan geçti ve bakışlarını batıya, Anadolu'ya çevirdi.",
         ]),
    dict(baslik="Bizans'ın Krizi", arkaplan="cadir", gecis="whip", kurgu=bizans_krizi,
         arkaplan_p=dict(renk1=(0.45, 0.22, 0.5), renk2=(0.95, 0.86, 0.62)), metin=[
             "Aynı yıllarda Bizans İmparatorluğu ise içeriden çürüyordu.",
             "Güçlü imparator İkinci Basileios'un ölümünden sonra tahta birbiri ardına zayıf hükümdarlar geçti.",
             "Saraydaki entrikalar ve darbeler, devletin bütün enerjisini tüketti.",
             "Hazineyi korumak için sınırdaki yerli askerler terhis edildi; ordu giderek paralı askerlere bağımlı "
             "hâle geldi.",
             "Sınır kaleleri bakımsız kaldı ve doğu sınırı neredeyse savunmasız kaldı.",
             "Türkmen akıncıları Anadolu'nun içlerine kadar ilerliyor, Kayseri gibi şehirler yağmalanıyordu.",
             "Bin altmış sekizde imparatoriçe Evdokia, tecrübeli bir asker olan Romen Diyojen'le evlendi ve onu "
             "imparator yaptı.",
             "Ama güçlü Dukas ailesi bu evlilikten hiç hoşlanmamıştı.",
         ]),
    dict(baslik="İki Hükümdar", arkaplan="harita", gecis="punch", kurgu=iki_hukumdar,
         arkaplan_p=dict(kapsam=(24.0, 52.0, 38.6), bolgeler=[(BIZANS, BIZANS_1071), (SELCUK, SELCUKLU_1071)],
                         etiketler=[("BİZANS", 34.5, 40.3, 46), ("BÜYÜK SELÇUKLU", 45.2, 36.4, 34)]),
         metin=[
             "Bizans'ın başında, tahta yeni çıkmış asker imparator Romen Diyojen vardı.",
             "Amacı, yıllardır Anadolu'ya akın eden Türkleri bir daha dönmemek üzere durdurmaktı.",
             "Karşısında ise Büyük Selçuklu Sultanı Alparslan duruyordu.",
             "Sultan aslında bu savaşı istemiyordu; gözü güneyde, Mısır'daki Fatımilerdeydi.",
             "Ama imparatorun büyük bir orduyla geldiğini duyunca hemen kuzeye döndü.",
         ]),
    dict(baslik="Fil ile Arı", arkaplan="bozkir", gecis="whip", kurgu=fil_ile_ari, metin=[
        "İki ordu, iki farklı savaş anlayışını temsil ediyordu.",
        "Bizans ordusu bir fil gibiydi: ağır zırhlı, kalabalık ve güçlü, ama yavaş.",
        "Saflarında Bizanslıların yanında Ermeni, Frank, Varang ve Peçenek paralı askerler vardı.",
        "Selçuklu ordusu ise bir arı sürüsüne benziyordu: daha küçük, hafif ve son derece hareketli.",
        "Atlı okçular düşmana yaklaşır, ok yağdırır ve göğüs göğüse çarpışmadan geri çekilirdi.",
    ]),
    dict(baslik="Sefer Yolu", arkaplan="harita", gecis="whip", kurgu=sefer_yolu, aralar={1: 1.5, 6: 1.5},
         arkaplan_p=dict(kapsam=(26.0, 48.0, 38.8), bolgeler=[(BIZANS, BIZANS_1071), (SELCUK, SELCUKLU_1071)],
                         etiketler=[("ANADOLU", 33.5, 38.7, 40)]),
         metin=[
             "Bin yetmiş bir baharında Romen Diyojen büyük ordusuyla İstanbul'dan yola çıktı.",
             "Ordu Anadolu'yu boydan boya geçerek Sivas'a, oradan da Erzurum'a ulaştı.",
             "Yol boyunca disiplinsizlik ve paralı askerlerin yağmaları imparatoru uğraştırdı.",
             "İmparator ordusunu Erzurum'da toplayıp son hazırlıklarını yaptı.",
             "Hedefi, Van Gölü'nün kuzeyindeki Malazgirt ve Ahlat kalelerini geri almaktı.",
             "Alparslan o sırada Suriye'de, Halep önlerindeydi.",
             "Haberi alınca kuşatmayı kaldırdı ve hızla kuzeye yöneldi; yolda Türkmen ve Kürt birlikleri de "
             "ordusuna katıldı.",
         ]),
    dict(baslik="Bölünen Ordu", arkaplan="harita", gecis="iris", kurgu=bolunen_ordu,
         arkaplan_p=dict(kapsam=(36.0, 48.0, 39.3), bolgeler=[(BIZANS, BIZANS_1071), (SELCUK, SELCUKLU_1071)],
                         etiketler=[("Van Gölü", 43.2, 38.35, 28)]),
         metin=[
             "Romen Diyojen, ilk büyük hatasını savaştan önce yaptı.",
             "Ordusunun önemli bir kısmını general Tarkaniyotis ile Ahlat'a gönderdi.",
             "Bu birlikler savaşa hiç katılmadı.",
             "Üstelik ordudaki Uz ve Peçenek atlılarının bir kısmı, savaştan bir gün önce soydaşları "
             "Selçukluların safına geçti.",
             "Terazi yavaş yavaş Alparslan'dan yana dönüyordu.",
         ]),
    dict(baslik="İlk Kan", arkaplan="ova", gecis="iris", kurgu=ilk_kan,
         aralar={1: 2.0, 2: 2.2, 3: 1.0},
         arkaplan_p=dict(tepeler=[(900, 40, 140), (900, 690, 140), (1350, 360, 150)],
                         dereler=[[(-200, 620), (0, 660), (150, 760)]], yollar=[[(330, 360), (1500, 360)]],
                         agaclar=[(600, 640), (560, 90)], tohum=7),
         metin=[
             "Ordunun geri kalanıyla Malazgirt'e varan Romen, kaleyi kolayca teslim aldı.",
             "Ertesi gün ot ve erzak toplamak için dağılan Bizans birlikleri, Selçuklu öncüleriyle karşılaştı.",
             "Yardıma koşan general Vasilakis pusuya düştü ve esir alındı.",
             "Onu kurtarmaya giden Briyennios da ancak ağır kayıplarla geri dönebildi.",
             "Bizanslılar ilk kez, karşılarındaki ordunun sultanın kendi ordusu olduğunu anladı.",
             "Alparslan bu sırada imparatora elçiler gönderip barış teklif etti.",
             "Ama Romen teklifi reddetti; bunu sultanın zaman kazanma çabası olarak gördü.",
         ]),
    dict(baslik="Savaştan Önceki Gece", arkaplan="bozkir", gecis="whip", kurgu=gece,
         arkaplan_p=dict(gece=True), metin=[
             "Yirmi beş Ağustos gecesi iki ordugâhta da kimse rahat uyuyamadı.",
             "Bizans kampının çevresinde Selçuklu okçuları gece boyunca dolaşıp ok attı ve askerlerin uykusunu "
             "kaçırdı.",
             "Uz atlılarının bir kısmının karşı tarafa geçmesi, kamptaki güvensizliği daha da artırmıştı.",
             "Romen'in yanında, imparatora pek de bağlı olmayan Andronikos Dukas komuta ediyordu.",
             "Selçuklu karargâhında ise Alparslan, din âlimi Ebu Nasr el-Buhari ile konuşuyordu.",
             "Âlim, saldırının Cuma günü, bütün camilerde zafer için dua edilirken yapılmasını önerdi.",
             "Alparslan bu öneriyi kabul etti ve gözünü ertesi güne dikti.",
         ]),
    dict(baslik="Hilal Tuzağı", arkaplan="ova", gecis="whip", kurgu=hilal_tuzagi,
         aralar={0: 1.0, 1: 3.0, 2: 1.5, 3: 1.2, 4: 2.0},
         arkaplan_p=dict(tepeler=[(1150, 70, 150), (1150, 655, 150), (620, 30, 110), (1450, 360, 160)],
                         dereler=[[(-200, 600), (0, 640), (120, 720), (200, 820)]],
                         yollar=[[(70, 360), (500, 350), (900, 370), (1500, 350)]],
                         agaclar=[(560, 90), (700, 660), (-60, 150)]), metin=[
             "Yirmi altı Ağustos Cuma günü Alparslan, beyazlar giyerek askerlerinin önüne çıktı.",
             "Selçuklu atlıları hilal biçiminde dizildi ve Bizans ordusunu ok yağmuruna tuttu.",
             "Sonra geri çekilir gibi yaptılar; imparator onları akşama kadar boş yere kovaladı.",
             "Romen geri dönme emri verdiğinde saflar karıştı; arkadaki ihtiyat birliklerinin komutanı Andronikos "
             "Dukas, imparatorun yenildiği söylentisini yayarak savaş alanından çekildi.",
             "Tam o anda tepelerde bekleyen Selçuklu kuvvetleri iki yandan saldırdı ve imparator esir düştü.",
         ]),
    dict(baslik="Savaş Anı", arkaplan="bozkir", gecis="punch", kurgu=savas_ani, aralar={1: 1.5, 4: 1.5},
         arkaplan_p=dict(cadirlar=False, aksam=True), metin=[
             "Şimdi savaşın en sıcak anına, imparatorun etrafına yakından bakalım.",
             "Selçuklu atlıları dört bir yandan saldırırken gökyüzü oklarla karardı.",
             "Bizans saflarında kalkanlar birbirine kenetlendi, ama oklar durmak bilmiyordu.",
             "İmparatorun çevresinde yalnızca sadık Varang muhafızları kalmıştı.",
             "Romen Diyojen kılıcını bırakmadı ve askerleriyle birlikte sonuna kadar savaştı.",
             "Muhafızlar birer birer düştü ve imparatorun çevresindeki halka giderek daraldı.",
             "Ama atı öldürüldü, kendisi de elinden yaralandı.",
             "Akşam karanlığında bir Selçuklu askeri onu esir aldı; üstelik kim olduğunu bilmeden.",
         ]),
    dict(baslik="Açılan Kapı", arkaplan="cadir", gecis="whip", kurgu=acilan_kapi, metin=[
        "Esir imparator sultanın huzuruna getirildiğinde, Alparslan ona ne yapacağını sordu.",
        "Romen dürüstçe, belki onu öldüreceğini ya da teşhir edeceğini söyledi.",
        "Alparslan ise imparatoru affetti ve bir antlaşmayla serbest bıraktı.",
        "Ama asıl sonuç savaş alanının çok ötesindeydi: Anadolu'nun kapıları Türklere açılmıştı.",
    ]),
    dict(baslik="Sultanın Sonu", arkaplan="bozkir", gecis="iris", kurgu=sultanin_sonu,
         arkaplan_p=dict(aksam=True, cadirlar=True), metin=[
             "Malazgirt zaferinin sahibi Alparslan, bu zaferin tadını uzun süre çıkaramadı.",
             "Bir yıl sonra Orta Asya'daki bir seferde, esir alınan bir kale komutanı onu hançerle yaraladı.",
             "Büyük sultan, aldığı yaralarla birkaç gün sonra hayatını kaybetti.",
             "Kaynaklara göre son sözleri, gücüne güvenmenin bile insanı nasıl yanıltabileceğini anlatıyordu.",
             "Yerine oğlu Melikşah geçti ve Selçuklular onun döneminde en parlak çağlarını yaşadı.",
         ]),
    dict(baslik="Anadolu'nun Yeni Yüzü", arkaplan="harita", gecis="iris", kurgu=yeni_yurt,
         arkaplan_p=dict(kapsam=(25.0, 47.0, 39.2), bolgeler=[(BIZANS, BIZANS_1071), (SELCUK, SELCUKLU_1071)],
                         etiketler=[("ANADOLU", 36.0, 38.3, 44)]),
         metin=[
             "Malazgirt'ten sonra olaylar hızla gelişti.",
             "Romen Diyojen serbest kaldığında tahtını çoktan kaybetmişti; rakipleriyle savaştı, yenildi ve gözlerine "
             "mil çekildi.",
             "Bizans iç savaşlarla uğraşırken Türkmen boyları Anadolu'nun içlerine doğru ilerledi.",
             "Doğudan gelen bu boylar sürüleri, çadırları ve aileleriyle birlikte yeni bir yurt arıyordu.",
             "Bu göç dalgasının içinden Süleyman Şah çıktı ve İznik'i alarak yeni devletine merkez yaptı.",
             "Böylece Anadolu Selçuklu Devleti doğdu.",
             "Bir asır sonra Batılı kaynaklar bu topraklardan artık Türkiye diye söz etmeye başlayacaktı.",
             "Malazgirt, Anadolu'nun Türkler için yeni bir yurda dönüşmesinin ilk adımı oldu.",
         ]),
    dict(baslik="Zaferin Sırrı", arkaplan="sahne", gecis="punch", kurgu=zaferin_sirri,
         aralar={1: 0.8, 2: 0.8, 3: 0.8}, metin=[
        "Peki küçük bir ordu, nasıl olup da koca bir imparatorluk ordusunu yendi?",
        "Birinci sebep hızdı: Selçuklu atlıları vurup kaçarak ağır Bizans ordusunu saatlerce yordu.",
        "İkinci sebep birlikti: Selçuklu ordusu tek bir sultanın etrafında kenetlenmişti, Bizans ordusu ise kendi "
        "içinde bölünmüştü.",
        "Üçüncü sebep sabırdı: Alparslan doğru anı bekledi ve tuzağını ancak düşman yorulunca kapattı.",
        "Ve Bizans'ın en büyük düşmanı, belki de kendi sarayındaki ihanetti.",
    ]),
]
