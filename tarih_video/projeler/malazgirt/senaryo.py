"""Malazgirt Meydan Muharebesi (26 Ağustos 1071) — DEMO bölümü (~1,5 dk).

Tam bölüm aynı kalıpla 20-30 dakikaya genişletilir: önce arka plan / sebepler
(illüstrasyon sahneleri), sonra bu taktik animasyon, en sonda sonuçlar.
"""
from motor.harita import arka_plan_uret
from motor.sahne import (Birlik, Komutan, HareketOku, OkYagmuru, EtiketBalonu,
                         BaslikKarti, BolumEtiketi, Lejant, taraf_tanimla)

taraf_tanimla("bizans", (0.46, 0.17, 0.52), vurgu=(0.97, 0.83, 0.45))
taraf_tanimla("selcuklu", (0.05, 0.50, 0.55), vurgu=(0.93, 0.96, 0.90))

BOLUMLER = [
    {"id": "giris", "bolum": "Giriş",
     "metin": "26 Ağustos 1071. Malazgirt Ovası. Bir yanda Bizans İmparatoru Romen Diyojen, "
              "diğer yanda Büyük Selçuklu Sultanı Alparslan. Bu savaşın sonucu, "
              "Anadolu'nun kaderini yüzyıllar boyunca değiştirecekti.", "ek_sure": 1.0},
    {"id": "bizans", "bolum": "Bizans Ordusu",
     "metin": "Romen Diyojen ordusunu geniş bir hat halinde dizdi. Merkezde bizzat kendisi vardı. "
              "Sol kanadı Nikeforos Briyennios, sağ kanadı Teodor Alyates yönetiyordu. "
              "Arkada ise ihtiyat kuvvetleriyle Andronikos Dukas bekliyordu."},
    {"id": "selcuklu", "bolum": "Selçuklu Ordusu",
     "metin": "Alparslan ise ordusunu hilal biçiminde yaydı. Atlı okçular öndeydi. "
              "Ana kuvvetler ise tepelerin ardında, görünmeden bekliyordu."},
    {"id": "ilerleme", "bolum": "Sahte Ricat",
     "metin": "Bizans ordusu ilerlemeye başladı. Selçuklu atlı okçuları ok yağdırıyor, "
              "sonra göğüs göğüse çarpışmaya girmeden geri çekiliyordu. "
              "Saatler geçtikçe Bizans hatları uzadı, askerler yoruldu.", "ek_sure": 1.5},
    {"id": "donus", "bolum": "Kritik An",
     "metin": "Akşam yaklaşırken Romen Diyojen karargâha dönme emri verdi. Ancak bu emir yanlış anlaşıldı. "
              "Arkadaki Andronikos Dukas, imparatorun öldüğü söylentisini yayarak "
              "birlikleriyle savaş alanını terk etti."},
    {"id": "kusatma", "bolum": "Kuşatma",
     "metin": "İşte Alparslan'ın beklediği an buydu. Selçuklu kuvvetleri tepelerden inip "
              "iki yandan saldırdı. Bizans kanatları dağıldı, merkez kuşatıldı. "
              "Ve Bizans imparatoru Romen Diyojen, savaş meydanında esir düştü.", "ek_sure": 1.5},
    {"id": "sonuc", "bolum": "Sonuç",
     "metin": "Malazgirt, Anadolu'nun kapılarını Türklere açan zafer olarak tarihe geçti.",
     "ek_sure": 2.5},
]


def arka_plan():
    return arka_plan_uret(
        zemin="bozkir",
        tepeler=[(260, 170, 300, 0.9), (1660, 160, 320, 0.95), (960, 60, 260, 0.55),
                 (80, 620, 200, 0.4), (1850, 640, 220, 0.45)],
        nehirler=[[(-20, 760), (90, 820), (160, 940), (120, 1100)]],
        yollar=[[(230, 1000), (520, 960), (900, 1010), (1300, 990), (1940, 1030)]],
        yerlesimler=[(250, 990, "Malazgirt")],
        etiketler=[(1380, 965, "Malazgirt Ovası", 40)],
        tohum=1071,
    )


def kur(v, T):
    s = {k: a for k, (a, b) in T.items()}   # bölüm başlangıçları
    e = {k: b for k, (a, b) in T.items()}   # bölüm bitişleri

    # ---------------- birlikler
    bz = {
        "sol_s": Birlik("bizans", "suvari", 400, 800, 130, 44),
        "sol_p": Birlik("bizans", "piyade", 610, 800, 250, 48),
        "mer_a": Birlik("bizans", "agir_suvari", 960, 770, 300, 54),
        "mer_p": Birlik("bizans", "piyade", 960, 836, 300, 44),
        "sag_p": Birlik("bizans", "piyade", 1310, 800, 250, 48),
        "sag_s": Birlik("bizans", "suvari", 1520, 800, 130, 44),
        "ihtiyat": Birlik("bizans", "piyade", 960, 960, 380, 46),
    }
    okcular = [Birlik("selcuklu", "atli_okcu", x, y, 160, 70)
               for x, y in ((500, 480), (730, 430), (960, 410), (1190, 430), (1420, 480))]
    sol_ana = Birlik("selcuklu", "suvari", 300, 230, 220, 56)
    sag_ana = Birlik("selcuklu", "suvari", 1620, 230, 220, 56)
    sultan = Birlik("selcuklu", "agir_suvari", 960, 200, 240, 54)
    v.ekle(*bz.values(), *okcular, sol_ana, sag_ana, sultan)

    romen = Komutan("Romen Diyojen", "bizans", bz["mer_a"], ofset=(0, -118), unvan="İmparator")
    bri = Komutan("Briyennios", "bizans", bz["sol_p"], ofset=(0, -105))
    aly = Komutan("Alyates", "bizans", bz["sag_p"], ofset=(0, -105))
    dukas = Komutan("Andronikos Dukas", "bizans", bz["ihtiyat"], ofset=(300, -30))
    alp = Komutan("Alparslan", "selcuklu", sultan, ofset=(0, -112), unvan="Sultan")
    v.ekle(romen, bri, aly, dukas, alp)

    # ---------------- 1) giriş
    v.acilis(0, 1.2)
    v.kamera.ekle(0, {"x": 960, "y": 540, "zoom": 1.12})
    v.kamera_git(0, e["giris"], zoom=1.0)
    v.ekle(BaslikKarti("BÜYÜK SAVAŞLAR", "MALAZGİRT", "26 Ağustos 1071", 0.6, e["giris"]))

    # ---------------- 2) Bizans dizilişi
    t = s["bizans"]
    v.ekle(BolumEtiketi("Bizans Ordusu", t, e["selcuklu"], alt="Romen Diyojen komutasında"))
    v.kamera_git(t, t + 2.5, x=960, y=800, zoom=1.35)
    for i, k in enumerate(("mer_a", "mer_p")):
        bz[k].belir(t + 0.5 + i * 0.3)
    romen.belir(t + 1.2)
    for i, k in enumerate(("sol_p", "sol_s")):
        bz[k].belir(t + 5.5 + i * 0.3)
    bri.belir(t + 6)
    for i, k in enumerate(("sag_p", "sag_s")):
        bz[k].belir(t + 8.5 + i * 0.3)
    aly.belir(t + 9)
    bz["ihtiyat"].belir(t + 12)
    dukas.belir(t + 12.5)
    v.kamera_git(t + 11, t + 13, y=840)
    v.ekle(Lejant([("bizans", "Bizans"), ("selcuklu", "Büyük Selçuklu")], t + 3, e["sonuc"]))

    # ---------------- 3) Selçuklu dizilişi
    t = s["selcuklu"]
    v.kamera_git(t, t + 2.5, x=960, y=330, zoom=1.2)
    for i, o in enumerate(okcular):
        o.belir(t + 1 + abs(i - 2) * 0.35)
    for b in (sol_ana, sag_ana, sultan):
        b.git(t + 5, t + 6.5, alfa=0.45)   # yarı saydam = gizli/pusuda
    alp.belir(t + 5.5)
    v.ekle(EtiketBalonu("Pusu", t + 6, e["selcuklu"] + 0.5, birlik=sol_ana, ofset=(0, 80)),
           EtiketBalonu("Pusu", t + 6, e["selcuklu"] + 0.5, birlik=sag_ana, ofset=(0, 80)))

    # ---------------- 4) ilerleme + sahte ricat
    t, te = s["ilerleme"], e["ilerleme"]
    v.ekle(BolumEtiketi("Sahte Ricat", t, te, alt="Bozkır savaş taktiği"))
    v.kamera_git(t, t + 2.5, x=960, y=560, zoom=1.0)
    yayilma = {"sol_s": -90, "sol_p": -50, "sag_p": 50, "sag_s": 90}
    for k, b in bz.items():
        x, y = b.merkez(t)
        dy = -120 if k == "ihtiyat" else -230
        b.git(t + 1, te - 1, x=x + yayilma.get(k, 0), y=y + dy)
    for i, o in enumerate(okcular):
        x, y = o.merkez(t)
        o.git(t + 3, te - 1, y=y - 150)
        hedef = [bz["sol_p"], bz["sol_p"], bz["mer_a"], bz["sag_p"], bz["sag_p"]][i]
        v.ekle(OkYagmuru(o, hedef, t + 1.5, te - 1.5, yogunluk=9, tohum=i))
    for x in (610, 960, 1310):
        v.ekle(HareketOku("bizans", [(x, 720), (x, 520)], t + 1, t + 3.5, t_son=t + 7, kalinlik=22))
    v.ekle(EtiketBalonu("Sahte ricat!", t + 5, te, birlik=okcular[2], ofset=(0, 85)))

    # ---------------- 5) dönüş emri ve Dukas'ın çekilmesi
    t, te = s["donus"], e["donus"]
    v.ekle(BolumEtiketi("Kritik An", t, te, alt="Dönüş emri yanlış anlaşılıyor"))
    v.kamera_git(t, t + 2.5, x=960, y=700, zoom=1.15)
    for k in ("sol_s", "sol_p", "mer_a", "mer_p", "sag_p", "sag_s"):
        bz[k].git(t + 1, t + 3, aci=180)              # cephe geriye döner
    bz["sol_p"].git(t + 3, t + 7, y=bz["sol_p"].merkez(t)[1] + 60)
    bz["mer_a"].git(t + 3, t + 7, y=bz["mer_a"].merkez(t)[1] + 50)
    bz["mer_p"].git(t + 3, t + 7, y=bz["mer_p"].merkez(t)[1] + 50)
    bz["sag_s"].git(t + 3, t + 7, x=bz["sag_s"].merkez(t)[0] + 40)   # sağ kanat karışıyor
    v.ekle(EtiketBalonu("Karargâha dönün!", t + 2, t + 6, birlik=bz["mer_a"], ofset=(0, -190)))
    td = t + 7.5
    v.ekle(EtiketBalonu("“İmparator öldü!”", td - 0.5, te + 0.5, birlik=bz["ihtiyat"], ofset=(0, -80),
                        renk=(1, 0.75, 0.6)))
    bz["ihtiyat"].git(td, td + 1, aci=180)
    bz["ihtiyat"].git(td + 1.5, te + 2, y=1180)
    bz["ihtiyat"].kaybol(te + 0.5, 1.5)
    dukas.kaybol(te, 1.0)
    v.ekle(HareketOku("bizans", [(960, 900), (960, 1060)], td + 1, td + 3, t_son=te + 1, kalinlik=22,
                      renk=(0.55, 0.45, 0.55)))
    v.kamera_git(td, td + 3, y=780)

    # ---------------- 6) kuşatma
    t, te = s["kusatma"], e["kusatma"]
    v.ekle(BolumEtiketi("Kuşatma", t, te, alt="Selçuklu ana kuvvetleri saldırıyor"))
    v.kamera_git(t, t + 2.5, x=960, y=540, zoom=1.0)
    for b in (sol_ana, sag_ana, sultan):
        b.git(t + 0.5, t + 1.5, alfa=1)
    v.ekle(HareketOku("selcuklu", [(300, 290), (230, 560), (420, 820), (640, 800)], t + 2, t + 6, t_son=te - 1),
           HareketOku("selcuklu", [(1620, 290), (1690, 560), (1500, 820), (1280, 800)], t + 2, t + 6, t_son=te - 1),
           HareketOku("selcuklu", [(960, 270), (960, 420)], t + 3, t + 6, t_son=te - 1, kalinlik=22))
    sol_ana.git(t + 2, t + 7, x=560, y=760, aci=60)
    sag_ana.git(t + 2, t + 7, x=1360, y=760, aci=-60)
    sultan.git(t + 3, t + 8, y=320)
    halka = [(640, 560), (790, 450), (960, 420), (1130, 450), (1280, 560)]
    for o, (x, y) in zip(okcular, halka):
        o.git(t + 2, t + 7, x=x, y=y)
    for k in ("sol_s", "sol_p", "mer_a", "mer_p", "sag_p", "sag_s"):
        bz[k].savas(t + 6, te)
    # kanatlar dağılır
    for k, dx in (("sol_s", -120), ("sol_p", -60), ("sag_p", 60), ("sag_s", 120)):
        x, y = bz[k].merkez(t + 7)
        bz[k].git(t + 8, t + 12, x=x + dx, y=y + 90, g=150, alfa=0.0)
    bri.kaybol(t + 10)
    aly.kaybol(t + 10)
    # merkez sıkışır
    bz["mer_a"].git(t + 8, t + 12, g=220)
    bz["mer_p"].git(t + 8, t + 12, g=220)
    v.kamera_git(t + 9, t + 13, x=960, y=600, zoom=1.35)
    romen.esir(te - 3)

    # ---------------- 7) sonuç
    t, te = s["sonuc"], e["sonuc"]
    v.kamera_git(t, te, zoom=1.0, y=540)
    v.ekle(BaslikKarti("BÜYÜK SELÇUKLU ZAFERİ", "MALAZGİRT", "Anadolu'nun kapıları açıldı", t + 1.5, te + 1.5))
    v.kapanis(te + 0.3, 1.2)
