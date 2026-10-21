"""Konu: Malazgirt 1071 — ağır zırh ile hızlı okun savaşı.

Kanal kuralı: Bizans her zaman SOLDA, Türkler her zaman SAĞDA (sağdan gelir, sağdan akın eder).

Yeni bir konu için bu dosyayı kopyalayın: BASLIK/ALT_BASLIK, ACILIS/KAPANIS metni, KARAKTERLER ve
SAHNELER listesini değiştirin. Her sahne: başlık, arka plan, geçiş, cümle listesi (her öğe tek
cümle, . ! ? ile biter) ve kurgu fonksiyonu. Kurguda s.c(i) i. cümlenin başladığı an,
s.c(i, 0.5) cümlenin ortasıdır; bütün oyunculuk bu anlara bağlanır.
"""

BASLIK = "Malazgirt 1071"
ALT_BASLIK = "Ağır zırh ile hızlı okun savaşı"
UST_YAZI = "26 AĞUSTOS 1071"
LOGO = "kilic"
KAPANIS_YAZI = "Anadolu'nun kapısı açıldı"
KART_RENK = {"ust": (0.55, 0.16, 0.14), "alt": (0.25, 0.06, 0.06)}

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
    s.nesne("yazi", 640, 80, metin="26 Ağustos 1071 · Cuma", boyut=44, renk=ALTIN, olcek=1.0).belir(s.c(0, 0.05))
    alp = s.karakter("Alparslan", govde=(0.97, 0.96, 0.92), x=1020, olcek=0.9, ifade="kararli",
                     elde={"R": "kilic"}).belir(s.c(0, 0.3))
    alp.poz(s.c(0, 0.6), "kutlama")
    s.nesne("isiltilar", 1020, 330, olcek=1.2, renk=(1, 1, 1)).belir(s.c(0, 0.6), ses=None)

    alp.git(s.c(1), s.c(1) + 0.8, x=1130).poz(s.c(1), "dur")
    hilal = s.nesne("hilal", 980, 400, olcek=1.0, kapan=0.0).belir(s.c(1, 0.2), ses="swoosh_yukari")
    askerler = [s.karakter("Asker", x=200 + k * 110, y=620 + (k % 2) * 14, olcek=0.6, ifade="kararli").belir(
        s.c(1, 0.25) + k * 0.1) for k in range(3)]
    romen = s.karakter("Romen", x=110, olcek=0.7, ifade="kararli").belir(s.c(1, 0.3))
    s.nesne("ok_yagmuru", 640, 380, olcek=1.0, yon=-1, genislik=520, adet=18).belir(s.c(1, 0.55), ses="whoosh") \
        .kaybol(s.c(2, 0.2))

    for k, a in enumerate(askerler):  # kovalama (sağa) — hilal geri çekilir
        a.git(s.c(2, 0.2), s.c(2, 0.2) + 2.5, x=420 + k * 110)
    romen.git(s.c(2, 0.2), s.c(2, 0.2) + 2.5, x=320)
    hilal.git(s.c(2, 0.15), s.c(2, 0.15) + 2.5, x=1080)
    s.kamera.git(s.c(2, 0.2), s.c(2, 0.2) + 2.5, x=700)

    romen.don(s.c(3), -1).poz(s.c(3), "isaret").ifade(s.c(3), "kizgin")
    s.nesne("konusma", 330, 300, metin="Geri dönün!", boyut=40, olcek=1.0, kuyruk=-1).belir(s.c(3, 0.05)) \
        .kaybol(s.c(3, 0.4))
    for a in askerler:
        a.ifade(s.c(3, 0.2), "panik").titre(s.c(3, 0.2), s.c(3, 0.45))
    dukas = s.karakter("Dukas", x=-80, olcek=0.65, ifade="kizgin")
    dukas.iz.ayarla(s.c(3, 0.4), dict(x=150))
    dukas.belir(s.c(3, 0.4))
    s.nesne("konusma", 260, 330, metin="İmparator yenildi!", boyut=36, olcek=1.0, kuyruk=-1).belir(s.c(3, 0.6)) \
        .kaybol(s.c(3, 0.92))
    dukas.cik(s.c(3, 0.85), "sol", sure=0.8, kos=True)
    s.kamera.git(s.c(3, 0.3), s.c(3, 0.3) + 1, x=620)

    s.kamera.git(s.c(4), s.c(4) + 0.6, x=640, zoom=1.0)
    hilal.git(s.c(4, 0.15), s.c(4, 0.15) + 1.0, x=780)
    hilal.ayarla(s.c(4, 0.15), kapan=1.0, sure=1.0, egri="geri_tepme")
    s.sfx("punch", s.c(4, 0.3))
    s.kamera.sars(s.c(4, 0.3), 0.6, 1.0)
    romen.ifade(s.c(4, 0.5), "panik").poz(s.c(4, 0.5), "kollar_yukari")
    s.nesne("damga", 330, 300, metin="ESİR", boyut=56, olcek=1.7).belir(s.c(4, 0.8), ses="punch")
    s.kamera.punch(s.c(4, 0.8), 0.12)


# ------------------------------------------------------------------ 5
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


SAHNELER = [
    dict(baslik="İki Hükümdar", arkaplan="harita", gecis="punch", kurgu=iki_hukumdar,
         arkaplan_p=dict(kapsam=(24.0, 52.0, 38.6), bolgeler=[(BIZANS, BIZANS_1071), (SELCUK, SELCUKLU_1071)],
                         etiketler=[("BİZANS", 34.5, 40.3, 46), ("BÜYÜK SELÇUKLU", 44.6, 35.0, 34)]),
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
    dict(baslik="Hilal Tuzağı", arkaplan="bozkir", gecis="whip", kurgu=hilal_tuzagi,
         arkaplan_p=dict(cadirlar=False), metin=[
             "Yirmi altı Ağustos Cuma günü Alparslan, beyazlar giyerek askerlerinin önüne çıktı.",
             "Selçuklu atlıları hilal biçiminde dizildi ve Bizans ordusunu ok yağmuruna tuttu.",
             "Sonra geri çekilir gibi yaptılar; imparator onları akşama kadar boş yere kovaladı.",
             "Romen geri dönme emri verdiğinde saflar karıştı; arkadaki ihtiyat birliklerinin komutanı Andronikos "
             "Dukas, imparatorun yenildiği söylentisini yayarak savaş alanından çekildi.",
             "Tam o anda tepelerde bekleyen Selçuklu kuvvetleri iki yandan saldırdı ve imparator esir düştü.",
         ]),
    dict(baslik="Açılan Kapı", arkaplan="cadir", gecis="punch", kurgu=acilan_kapi, metin=[
        "Esir imparator sultanın huzuruna getirildiğinde, Alparslan ona ne yapacağını sordu.",
        "Romen dürüstçe, belki onu öldüreceğini ya da teşhir edeceğini söyledi.",
        "Alparslan ise imparatoru affetti ve bir antlaşmayla serbest bıraktı.",
        "Ama asıl sonuç savaş alanının çok ötesindeydi: Anadolu'nun kapıları Türklere açılmıştı.",
    ]),
]
