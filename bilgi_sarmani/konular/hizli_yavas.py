"""Konu: Hızlı Düşün, Yavaş Düşün — zihnimizin iki sistemi (Kahneman).

Yeni bir konu için bu dosyayı kopyalayın: BASLIK/ALT_BASLIK, ACILIS/KAPANIS metni, KARAKTERLER ve
SAHNELER listesini değiştirin. Her sahne: başlık, arka plan, geçiş, cümle listesi (her biri tek
cümle, . ! ? ile biter) ve kurgu fonksiyonu. Kurguda s.c(i) i. cümlenin başladığı an,
s.c(i, 0.5) cümlenin ortasıdır; bütün oyunculuk bu anlara bağlanır.
"""

BASLIK = "Hızlı Düşün, Yavaş Düşün"
ALT_BASLIK = "Zihnimizdeki iki karakter"
KAPANIS_YAZI = "Önemli anlarda yavaşla!"

ACILIS = [
    "Bir anda verdiğin kararlar mı daha doğru, yoksa uzun uzun düşündüklerin mi?",
    "Bugün zihnimizin iki farklı hızını tanıyacağız.",
]
KAPANIS = [
    "Hızlı düşünmek hayatı kolaylaştırır, ama önemli anlarda yavaşlamayı unutma.",
    "Bilgi Sarmanı'nda bir sonraki videoda görüşmek üzere!",
]

KARAKTERLER = {
    "Çabuk": dict(govde=(0.98, 0.52, 0.15), sac="diken", sac_renk=(0.35, 0.18, 0.08), pantolon=(0.25, 0.3, 0.45)),
    "Ağır": dict(govde=(0.25, 0.5, 0.92), sac="duz", sac_renk=(0.18, 0.13, 0.1), gozluk=True,
                 pantolon=(0.3, 0.28, 0.3)),
}

TURUNCU = (0.98, 0.52, 0.15)
MAVI = (0.25, 0.5, 0.92)


# ------------------------------------------------------------------ 1
def iki_surucu(s):
    beyin = s.nesne("beyin", 640, 300, olcek=2.2).belir(s.c(0) - 0.6)
    s.kamera.ayarla(s.t0, zoom=1.05).git(s.c(0), s.c(1), zoom=1.15, y=320)
    d1 = s.nesne("disli", 560, 290, olcek=0.7, renk=TURUNCU, hiz=6.0, katman=5).belir(s.c(0, 0.55))
    d2 = s.nesne("disli", 720, 300, olcek=0.8, renk=MAVI, hiz=-0.8, katman=5).belir(s.c(0, 0.75))
    for n in (beyin, d1, d2):
        n.ayarla(s.c(1) - 0.3, olcek=n.hedef_olcek * 0.45, sure=0.5)
    beyin.git(s.c(1) - 0.3, s.c(1) + 0.2, y=120)
    d1.git(s.c(1) - 0.3, s.c(1) + 0.2, x=605, y=115)
    d2.git(s.c(1) - 0.3, s.c(1) + 0.2, x=675, y=120)
    s.kamera.git(s.c(1) - 0.3, s.c(1) + 0.3, zoom=1.0, y=360)

    cabuk = s.karakter("Çabuk", ifade="mutlu").gir(s.c(1), "sol", x=380, sure=0.7, kos=True)
    cabuk.zipla(s.c(1) + 0.75).poz(s.c(1) + 0.8, "kollar_yukari").ifade(s.c(1) + 0.8, "kahkaha")
    s.sfx("whoosh", s.c(1), 0.6)
    s.sfx("boing", s.c(1) + 0.8)
    s.kamera.punch(s.c(1) + 0.8, 0.08)
    s.nesne("levha", 380, 250, metin="HIZLI", olcek=1.0).belir(s.c(1, 0.45))
    cabuk.poz(s.c(1, 0.7), "dur").ifade(s.c(1, 0.7), "mutlu")

    agir = s.karakter("Ağır", ifade="dusunceli", poz="dusun").gir(s.c(2) - 0.2, "sag", x=900, sure=2.6)
    s.nesne("levha", 900, 250, metin="YAVAŞ", olcek=1.0).belir(s.c(2, 0.5))
    agir.bak(s.c(2, 0.6), -1, 0)
    cabuk.bak(s.c(2, 0.3), 1, 0).ifade(s.c(2, 0.3), "saskin").ifade(s.c(2, 0.7), "notr")

    s.nesne("yazi", 380, 170, metin="ÇABUK", boyut=64, renk=TURUNCU, olcek=1.0).belir(s.c(3, 0.3))
    s.nesne("yazi", 900, 170, metin="AĞIR", boyut=64, renk=MAVI, olcek=1.0).belir(s.c(3, 0.55))
    cabuk.poz(s.c(3, 0.3), "el_salla").salla(s.c(3, 0.3), s.c(3, 0.3) + 2).ifade(s.c(3, 0.3), "kahkaha")
    agir.poz(s.c(3, 0.55), "sunum").ifade(s.c(3, 0.55), "gururlu")


# ------------------------------------------------------------------ 2
def otomatik_pilot(s):
    tahta = s.nesne("tahta", 640, 215, metin="2 + 2 = ?", boyut=76, olcek=1.0).belir(s.c(0) - 0.3)
    cabuk = s.karakter("Çabuk", x=330, ifade="notr")
    agir = s.karakter("Ağır", x=1010, ifade="notr", yon=-1)
    s.kamera.ayarla(s.t0, zoom=1.0)

    cabuk.poz(s.c(1, 0.1), "isaret").ifade(s.c(1, 0.1), "gururlu").zipla(s.c(1, 0.05), 40)
    s.nesne("patlama", 470, 300, metin="4!", boyut=80, olcek=0.9, aci=-8).belir(s.c(1, 0.15), ses="punch").kaybol(s.c(2))
    s.kamera.punch(s.c(1, 0.15), 0.1)
    tahta.degistir(s.c(1, 0.3), metin="2 + 2 = 4", ses="ding")

    cabuk.poz(s.c(2), "dur").ifade(s.c(2), "mutlu")
    for k, (tur, x) in enumerate((("kalp", 250), ("unlem", 340), ("onay", 430))):
        s.nesne(tur, x, 120, olcek=0.55, boyut=110).belir(s.c(2, 0.2 + 0.25 * k)).kaybol(s.c(3) - 0.2 + 0.08 * k)
    cabuk.zipla(s.c(2, 0.8), 45)

    tahta.degistir(s.c(3), metin="17 × 24 = ?", ses="tik")
    s.kamera.git(s.c(3), s.c(3) + 0.4, x=420, y=380, zoom=1.35, egri="geri_tepme")
    cabuk.ifade(s.c(3, 0.3), "panik").poz(s.c(3, 0.3), "kafa_kasi").titre(s.c(3, 0.3), s.c(4, 0.3))
    s.sfx("bzzt", s.c(3, 0.35), 0.6)

    s.kamera.git(s.c(4), s.c(4) + 1.2, x=700, y=360, zoom=1.08)
    cabuk.ifade(s.c(4, 0.2), "utangac").poz(s.c(4, 0.2), "dur").git(s.c(4, 0.2), s.c(4, 0.6), x=210)
    agir.ifade(s.c(4, 0.5), "kararli").git(s.c(4, 0.45), s.c(4, 0.45) + 1.6, x=820)

    agir.poz(s.c(5), "dusun").ifade(s.c(5), "dusunceli")
    disli = s.nesne("disli", 820, 270, olcek=0.6, renk=MAVI, hiz=1.2).belir(s.c(5, 0.1))
    s.nesne("disli", 880, 230, olcek=0.4, renk=MAVI, hiz=-1.8, dis=8).belir(s.c(5, 0.2))
    s.sfx("kayit", s.c(5, 0.2), 0.7)
    tahta.degistir(s.c(5, 0.82), metin="17 × 24 = 408", ses="ding")
    s.nesne("onay", 920, 140, olcek=0.8).belir(s.c(5, 0.85))
    agir.poz(s.c(5, 0.85), "kollar_yukari").ifade(s.c(5, 0.85), "mutlu")
    disli.ayarla(s.c(5, 0.85), hiz=0.2)
    s.kamera.punch(s.c(5, 0.85), 0.07)


# ------------------------------------------------------------------ 3
def kestirme_tuzagi(s):
    s.kamera.ayarla(s.t0, zoom=1.2, y=330).git(s.c(1), s.c(1) + 0.8, zoom=1.0, y=360)
    soru = s.nesne("soru", 640, 260, olcek=1.3, boyut=180).belir(s.c(0, 0.2))
    soru.salla(s.c(0, 0.3), s.c(0, 0.3) + 1.0)
    soru.kaybol(s.c(1) - 0.1)
    sopa = s.nesne("sopa", 470, 330, olcek=1.3).belir(s.c(1, 0.15))
    top = s.nesne("top", 800, 380, olcek=1.3).belir(s.c(1, 0.3))
    s.nesne("yazi", 640, 160, metin="Toplam: 1,10 ₺", boyut=58, olcek=1.0).belir(s.c(1, 0.6))
    s.nesne("yazi", 470, 470, metin="Sopa = Top + 1 ₺", boyut=40, renk=(1, 0.85, 0.4), olcek=1.0).belir(s.c(2, 0.3)) \
        .kaybol(s.c(4) - 0.2)
    sopa.salla(s.c(2, 0.3), s.c(2, 0.3) + 0.8)
    s.nesne("soru", 800, 270, olcek=0.7, boyut=120).belir(s.c(3, 0.2)).kaybol(s.c(4) - 0.2)
    top.ayarla(s.c(3), olcek=1.6, egri="geri_tepme")

    for n in (sopa, top):
        n.kaybol(s.c(4) - 0.2)
    cabuk = s.karakter("Çabuk", ifade="gururlu").gir(s.c(4) - 0.4, "sol", x=360, sure=0.6, kos=True)
    s.sfx("whoosh", s.c(4) - 0.4, 0.5)
    cabuk.poz(s.c(4, 0.15), "isaret")
    balon = s.nesne("konusma", 520, 250, metin="10 kuruş!", boyut=50, olcek=1.0, kuyruk=-1).belir(s.c(4, 0.15))

    s.nesne("carpi", 640, 330, olcek=1.6).belir(s.c(5, 0.15), ses="bzzt").kaybol(s.c(6) - 0.3)
    s.kamera.sars(s.c(5, 0.15), 0.5, 0.8)
    cabuk.ifade(s.c(5, 0.2), "utangac").poz(s.c(5, 0.2), "kafa_kasi")
    balon.kaybol(s.c(5, 0.1))
    s.nesne("yazi", 640, 520, metin="1,10 + 0,10 = 1,20 ₺", boyut=44, renk=(1, 0.55, 0.5), olcek=1.0).belir(s.c(5, 0.55)).kaybol(s.c(6) - 0.3)

    agir = s.karakter("Ağır", ifade="kararli", yon=-1).gir(s.c(6) - 0.5, "sag", x=930, sure=1.2)
    s.nesne("konusma", 820, 250, metin="5 kuruş.", boyut=50, olcek=1.0, kuyruk=1).belir(s.c(6, 0.3))
    s.nesne("onay", 980, 150, olcek=0.8).belir(s.c(6, 0.5), ses="ding")
    agir.poz(s.c(6, 0.3), "sunum")
    agir.ifade(s.c(7), "gururlu")
    cabuk.poz(s.c(7, 0.3), "omuz_silk").ifade(s.c(7, 0.3), "mutlu").bak(s.c(7, 0.3), 1, 0)


# ------------------------------------------------------------------ 4
def enerji_faturasi(s):
    cabuk = s.karakter("Çabuk", x=360, ifade="notr")
    agir = s.karakter("Ağır", x=920, ifade="notr", yon=-1)
    cabuk.poz(s.c(0, 0.3), "omuz_silk").ifade(s.c(0, 0.3), "saskin")
    s.nesne("soru", 640, 230, olcek=0.9, boyut=140).belir(s.c(0, 0.4)).kaybol(s.c(1) - 0.2)

    s.kamera.git(s.c(1), s.c(1) + 1.0, y=300, zoom=1.15)
    beyin = s.nesne("beyin", 640, 230, olcek=1.3).belir(s.c(1, 0.05))
    s.nesne("levha", 450, 300, metin="%2 ağırlık", boyut=34, olcek=1.0).belir(s.c(1, 0.32)).kaybol(s.c(2) - 0.3)
    s.nesne("levha", 830, 300, metin="%20 enerji", boyut=34, olcek=1.0).belir(s.c(1, 0.72)).kaybol(s.c(2) - 0.25)
    s.kamera.punch(s.c(1, 0.72), 0.07)
    beyin.salla(s.c(1, 0.72), s.c(1, 0.72) + 0.6)

    s.kamera.git(s.c(2) - 0.2, s.c(2) + 1.0, x=800, y=380, zoom=1.2)
    beyin.kaybol(s.c(2) - 0.3)
    pil = s.nesne("pil", 1070, 330, olcek=0.9, seviye=1.0).belir(s.c(2, 0.05))
    pil.ayarla(s.c(2, 0.95), sure=(s.bitis(2) - s.c(2)) * 0.85, seviye=0.08, egri="dogrusal")
    s.nesne("disli", 920, 270, olcek=0.55, renk=MAVI, hiz=3.0).belir(s.c(2, 0.05)).ayarla(s.c(2, 0.9), hiz=0.1,
                                                                                        sure=2.0)
    agir.poz(s.c(2, 0.1), "dusun").ifade(s.c(2, 0.1), "dusunceli")
    agir.ifade(s.c(2, 0.6), "yorgun").poz(s.c(2, 0.6), "yorgun")

    s.kamera.git(s.c(3) - 0.2, s.c(3) + 1.0, x=640, y=360, zoom=1.0)
    agir.ifade(s.c(3, 0.1), "uykulu").bas_egim(s.c(3, 0.1), -14)
    s.nesne("zzz", 960, 330, olcek=1.2).belir(s.c(3, 0.2), ses=None)
    cabuk.poz(s.c(3, 0.4), "kutlama").ifade(s.c(3, 0.4), "kahkaha").zipla(s.c(3, 0.4), 60)
    s.sfx("boing", s.c(3, 0.45))
    s.nesne("isiltilar", 360, 330, olcek=1.3, renk=(1, 0.8, 0.2)).belir(s.c(3, 0.45), ses=None)


# ------------------------------------------------------------------ 5
def takim(s):
    cabuk = s.karakter("Çabuk", x=420, ifade="mutlu")
    agir = s.karakter("Ağır", x=860, ifade="mutlu", yon=-1)
    s.kamera.ayarla(s.t0, zoom=1.1, y=380)
    s.nesne("kalp", 640, 330, olcek=0.9).belir(s.c(0, 0.4)).kaybol(s.c(1) - 0.1)
    cabuk.poz(s.c(0, 0.4), "el_salla")
    agir.poz(s.c(0, 0.4), "el_salla")

    s.kamera.git(s.c(1), s.c(1) + 1, zoom=1.0, y=360)
    terazi = s.nesne("terazi", 640, 260, olcek=1.0, egim=-1.0, sol="Hız", sag="Kontrol").belir(s.c(1, 0.05))
    cabuk.zipla(s.c(1, 0.1), 50).poz(s.c(1, 0.1), "isaret").ifade(s.c(1, 0.1), "kahkaha")
    s.sfx("whoosh", s.c(1, 0.1), 0.4)
    agir.poz(s.c(1, 0.55), "dur_isareti").ifade(s.c(1, 0.55), "kararli")
    s.sfx("tik", s.c(1, 0.55))
    terazi.ayarla(s.c(1, 0.6), sure=1.2, egim=0.0, egri="elastik")

    terazi.kaybol(s.c(2) - 0.2)
    s.kamera.git(s.c(2), s.c(2) + 1.5, zoom=1.25, y=300)
    s.nesne("dusunce", 640, 190, metin="Bu cevap fazla mı kolay geldi?", boyut=44, azami=420,
            olcek=1.0).belir(s.c(2, 0.55)).kaybol(s.c(3, 0.45))
    cabuk.ifade(s.c(2, 0.55), "dusunceli").poz(s.c(2, 0.55), "dusun")
    agir.ifade(s.c(2, 0.2), "uykulu")

    s.kamera.git(s.c(3), s.c(3) + 0.5, zoom=1.0, y=360)
    alarm = s.nesne("alarm", 980, 320, olcek=0.8, cal=0.0).belir(s.c(3, 0.05))
    alarm.ayarla(s.c(3, 0.2), cal=1.0, sure=0.1)
    s.sfx("zil", s.c(3, 0.2), 0.7)
    agir.ifade(s.c(3, 0.3), "saskin").zipla(s.c(3, 0.3), 70)
    agir.ifade(s.c(3, 0.6), "kararli").poz(s.c(3, 0.6), "kutlama")
    cabuk.poz(s.c(3, 0.6), "kutlama").ifade(s.c(3, 0.6), "kahkaha")
    alarm.ayarla(s.c(3, 0.6), cal=0.0, sure=0.1)
    s.kamera.punch(s.c(3, 0.6), 0.1)
    s.nesne("isiltilar", 640, 300, olcek=2.0).belir(s.c(3, 0.6), ses="alkis")


SAHNELER = [
    dict(baslik="İki Sürücü", arkaplan="beyin", gecis="punch", kurgu=iki_surucu, metin=[
        "Psikolog Daniel Kahneman'a göre zihnimiz iki ayrı sistemle çalışır.",
        "Birincisi hızlıdır: otomatik, zahmetsiz ve her an tetikte.",
        "İkincisi yavaştır: dikkatli, hesapçı ve biraz da tembel.",
        "Gelin onlara Çabuk ve Ağır diyelim.",
    ]),
    dict(baslik="Otomatik Pilot", arkaplan="sinif", gecis="whip", kurgu=otomatik_pilot, metin=[
        "İki artı iki kaç eder?",
        "Cevap, sen daha sormadan aklında belirdi bile.",
        "Bu, Çabuk'un işidir; yüzleri tanır, tehlikeyi sezer ve alışık olduğumuz işleri bizim yerimize yapar.",
        "Peki ya on yedi çarpı yirmi dört?",
        "İşte burada Çabuk susar ve sahneye Ağır çıkar.",
        "Ağır, adım adım hesaplar ve sonunda doğru cevabı bulur: dört yüz sekiz.",
    ]),
    dict(baslik="Kestirme Tuzağı", arkaplan="sahne", gecis="iris", kurgu=kestirme_tuzagi, metin=[
        "Şimdi küçük bir bilmece.",
        "Bir sopa ile bir top birlikte bir lira on kuruş.",
        "Sopa, toptan tam bir lira daha pahalı.",
        "Peki top kaç kuruş?",
        "Aklına hemen on kuruş geldiyse yalnız değilsin; bu, Çabuk'un cevabı.",
        "Ama o zaman sopa bir lira on kuruş olur ve toplam bir lira yirmiyi bulurdu.",
        "Doğru cevap beş kuruş.",
        "Ağır'ı uyandırmadan bunu bulmak neredeyse imkânsız.",
    ]),
    dict(baslik="Enerji Faturası", arkaplan="oda", gecis="whip", kurgu=enerji_faturasi, metin=[
        "Peki neden her kararı Ağır'a bırakmıyoruz?",
        "Çünkü beyin, vücut ağırlığımızın yalnızca yüzde ikisi kadardır ama enerjimizin yaklaşık beşte birini tüketir.",
        "Yoğun düşünmek yorucudur; Ağır çalıştıkça pil hızla azalır.",
        "Bu yüzden zihnimiz, işi çoğu zaman Çabuk'a bırakır.",
    ]),
    dict(baslik="Takım Çalışması", arkaplan="doga", gecis="punch", kurgu=takim, metin=[
        "Aslında ikisi rakip değil, bir takımdır.",
        "Çabuk hızla ilk tahmini yapar; Ağır ise gerektiğinde frene basar ve kontrol eder.",
        "Önemli bir karar vermeden önce kendine tek bir soru sor: Bu cevap fazla mı kolay geldi?",
        "Öyleyse Ağır'ı uyandırmanın tam zamanı.",
    ]),
]
