"""YouTube Shorts: Malazgirt'i kazandıran tuzak (dikey 9:16, ~50 sn).

Dikey tuval 720×1280 (çıktı 1080×1920). Zemin y≈870; üst bölge (y 150-520) iri yazılar ve eşyalar için,
altyazı y≈1024'te (Shorts arayüzünün üstünde). Kanal kuralı burada da geçerli: Bizans solda, Türkler sağda.
"""
FORMAT = "dikey"
BASLIK = "Malazgirt'i Kazandıran Tuzak"
ALT_BASLIK = "26 Ağustos 1071"
KANAL = "KRONİKNÂME"
LOGO = "kilic"
KAPANIS_YAZI = "Tamamı Kroniknâme'de!"
KAPANIS_GECIS = "punch"
KART_RENK = {"ust": (0.55, 0.16, 0.14), "alt": (0.25, 0.06, 0.06)}
YOUTUBE = dict(
    baslik="Küçük Ordu Dev İmparatorluğu Tek Numarayla Yendi! Malazgirt 1071",
    kanca="Sahte ricat ve hilal tuzağı: Malazgirt'i kazandıran taktik 40 saniyede.",
    ozet="Selçuklu atlıları kaçıyormuş gibi yaptı, İmparator Romen Diyojen peşlerine düştü ve hilal kapandı.",
    etiketler=["Malazgirt", "Malazgirt 1071", "Alparslan", "Romen Diyojen", "Selçuklu", "Bizans", "sahte ricat",
               "hilal taktiği", "tarih shorts"],
    hashtagler=["#Malazgirt", "#tarih", "#Kroniknâme"],
)
BOLUM_ETIKETI = False
ALTYAZI_BOYUT = 44
ALTYAZI_AZAMI = 44
TEMPO = dict(BOSLUK=0.3, ONCE={"acilis": 1.0, "sahne": 0.5, "kapanis": 0.4},
             SONRA={"acilis": 0.5, "sahne": 0.6, "kapanis": 2.2})

ACILIS = ["Bin yetmiş birde küçük bir ordu, dev bir imparatorluğu tek bir numarayla yendi."]
KAPANIS = ["Malazgirt'in tamamı Kroniknâme'de!"]

BIZANS = (0.5, 0.2, 0.55)
SELCUK = (0.1, 0.52, 0.48)
ALTIN = (0.98, 0.78, 0.25)
ZEMIN = 870

KARAKTERLER = {
    "Romen": dict(govde=BIZANS, sapka="tac", sakal=(0.42, 0.27, 0.14), sac_renk=(0.42, 0.27, 0.14), etek=True,
                  kemer=ALTIN, pantolon=(0.3, 0.15, 0.3)),
    "Alparslan": dict(govde=(0.97, 0.96, 0.92), sapka="bork", sakal=(0.12, 0.08, 0.06), sac_renk=(0.12, 0.08, 0.06),
                      etek=True, kemer=ALTIN, pantolon=(0.2, 0.25, 0.3), yon=-1, elde={"R": "kilic"}),
    "Asker": dict(govde=(0.55, 0.58, 0.66), sapka="migfer", elde={"L": ("kalkan", {}), "R": "kilic"},
                  pantolon=(0.3, 0.2, 0.35)),
    "Akıncı": dict(govde=(0.12, 0.58, 0.55), sapka="bork", sapka_renk=(0.2, 0.35, 0.6), elde={"R": ("yay", {"ok": 1})},
                   pantolon=(0.35, 0.25, 0.15), yon=-1),
}


def iri(s, metin, y, t, renk=(1, 1, 1), boyut=64):
    return s.nesne("yazi", 360, y, metin=metin, boyut=boyut, renk=renk, olcek=1.0).belir(t, ses="pop")


def tuzak(s):
    s.kamera.ayarla(s.t0, zoom=1.0)
    asker = s.karakter("Asker", x=180, y=ZEMIN, olcek=1.35, ifade="kararli").belir(s.c(0, 0.05))
    s.nesne("levha", 180, 400, metin="AĞIR", boyut=44, olcek=1.1).belir(s.c(0, 0.15)).kaybol(s.c(1))
    akinci = s.karakter("Akıncı", x=550, y=ZEMIN, olcek=1.2, ifade="kararli").belir(s.c(0, 0.5))
    s.nesne("levha", 550, 400, metin="HIZLI", boyut=44, olcek=1.1).belir(s.c(0, 0.6)).kaybol(s.c(1))

    s.nesne("ok_yagmuru", 360, 560, olcek=1.0, yon=-1, genislik=440, adet=16).belir(s.c(1, 0.05), ses="whoosh") \
        .kaybol(s.c(1, 0.6))
    for k in range(4):
        s.sfx("ok", s.c(1, 0.1) + k * 0.3, 0.7)
    asker.ifade(s.c(1, 0.2), "panik").titre(s.c(1, 0.2), s.c(1, 0.5))
    akinci.cik(s.c(1, 0.55), "sag", sure=0.8, kos=True)
    iri(s, "KAÇIYORLAR MI?", 290, s.c(1, 0.6), renk=ALTIN).kaybol(s.bitis(1))

    romen = s.karakter("Romen", x=-120, y=ZEMIN, olcek=1.3, ifade="kararli")
    romen.gir(s.c(2), "sol", x=300, sure=1.0)
    iri(s, "Romen Diyojen", 290, s.c(2, 0.2), boyut=52)
    romen.poz(s.c(2, 0.45), "isaret").ifade(s.c(2, 0.45), "kizgin")
    romen.git(s.c(2, 0.6), s.c(2, 0.6) + 1.6, x=500)
    asker.ifade(s.c(2, 0.5), "kararli").git(s.c(2, 0.6), s.c(2, 0.6) + 1.6, x=330)
    s.kamera.git(s.c(2, 0.5), s.c(2, 0.5) + 1.8, x=430, zoom=1.08)


def hilal(s):
    s.kamera.ayarla(s.t0, x=360, zoom=1.0)
    romen = s.karakter("Romen", x=240, y=ZEMIN, olcek=1.3, ifade="kararli")
    asker = s.karakter("Asker", x=95, y=ZEMIN + 14, olcek=1.1, ifade="kararli")
    h = s.nesne("hilal", 640, 640, olcek=1.1, kapan=0.0).belir(s.c(0, 0.15), ses=None)
    s.nesne("patlama", 360, 290, metin="TUZAK!", boyut=72, olcek=1.2).belir(s.c(0, 0.25), ses="punch") \
        .kaybol(s.c(1) - 0.1)
    s.kamera.punch(s.c(0, 0.25), 0.1)
    h.git(s.c(0, 0.55), s.c(0, 0.55) + 1.2, x=560).ayarla(s.c(0, 0.55), kapan=1.0, sure=1.2, egri="geri_tepme")
    s.sfx("kalabalik", s.c(0, 0.5), 0.6)
    romen.ifade(s.c(0, 0.6), "panik").poz(s.c(0, 0.6), "kollar_yukari").titre(s.c(0, 0.6), s.bitis(0))
    asker.ifade(s.c(0, 0.6), "panik")
    s.kamera.sars(s.c(0, 0.7), 0.6, 0.8)

    s.nesne("damga", 240, 470, metin="ESİR", boyut=60, olcek=1.5).belir(s.c(1, 0.2), ses="punch")
    s.kamera.punch(s.c(1, 0.2), 0.12)
    h.kaybol(s.c(1, 0.45))
    alp = s.karakter("Alparslan", x=860, y=ZEMIN, olcek=1.3, ifade="gururlu")
    alp.gir(s.c(1, 0.45), "sag", x=560, sure=1.0)
    iri(s, "26 Ağustos 1071", 290, s.c(1, 0.5), renk=ALTIN, boyut=56)
    romen.poz(s.c(1, 0.5), "yorgun").ifade(s.c(1, 0.5), "uzgun")


SAHNELER = [
    dict(baslik="Tuzak", arkaplan="bozkir", gecis="punch", kurgu=tuzak, arkaplan_p=dict(cadirlar=False), metin=[
        "Bizans ordusu ağır zırhlı ve kalabalıktı; Selçuklular ise hafif ve hızlıydı.",
        "Atlı okçular ok yağdırdı, sonra kaçıyormuş gibi geri çekildi.",
        "İmparator Romen Diyojen peşlerine düştü ve akşama kadar kovaladı.",
    ]),
    dict(baslik="Hilal Kapanıyor", arkaplan="bozkir", gecis="whip", kurgu=hilal,
         arkaplan_p=dict(cadirlar=False, aksam=True), metin=[
             "Ama bu bir tuzaktı: tepelerde bekleyen atlılar iki yandan saldırdı.",
             "Hilal kapandı ve bir Bizans imparatoru ilk kez bir Müslüman hükümdarın esiri oldu.",
         ]),
]
