"""Umay ile Zıpzıp, 2. Bölüm: "Şekil Avı" (≈10 dk). Tam senaryo.

Hikâye: Anneanne Umay'a bir şekil kutusu getirir; kutunun üç deliği var: DAİRE, KARE, ÜÇGEN. Parçalar bahçeye
saçılır. Umay ile Zıpzıp her şeklin parçasını ararken o şekildeki şeyleri keşfeder. Her blok aynı şekilde kalır
(4-5 örnek, sayma, tekerleme), parça bulununca kutudaki deliğine "tık" diye oturur, sonra diğer şekle geçilir.
Karşıtlık (komik an): Zıpzıp kare parçayı yuvarlak deliğe sokmaya çalışır, olmaz; "kare, kare deliğe!"
Final: üç şekil birleşip bir resim olur: kare ev + üçgen çatı + daire güneş.

Sıra: Açılış → DAİRE → KARE → ÜÇGEN → Final.
Satır biçimi: (kimlik, konuşan, metin, bekleme_sn). bekleme_sn > 0: çocuğun cevabı için sessizlik (seslendirilmez).
Zıpzıp yalnızca havlama kütüphanesindeki sesleri kullanır (zipzip_barks.py).
"""

A, U, Z = "anlatici", "umay", "zipzip"

BOLUMLER = [
    {
        "kod": "acilis", "baslik": "Açılış", "sekil": None, "sure": ("0:00", "1:20"),
        "sahneler": [
            ("A1", "0:00–0:15", "Tema müziği, başlık belirir.", [
                ("A01", A, "Umay ile Zıpzıp!", 0),
                ("A02", A, "Bugünkü macera... Şekil Avı!", 0),
            ]),
            ("A2", "0:15–0:50", "Anneanne kapıda elinde renkli bir şekil kutusuyla çıkar. Kutunun üç deliği var.", [
                ("A03", U, "Günaydın anneanne!", 0),
                ("A04", Z, "Hav hav!", 0),
                ("A05", A, "Anneanne Umay'a bir kutu getirdi. Bu bir şekil kutusu!", 0),
                ("A06", A, "Bak, kutunun üç deliği var.", 0),
                ("A07", U, "Ooo! Delikler!", 0),
            ]),
            ("A3", "0:50–1:20", "Zıpzıp heyecanla zıplar, kutuya çarpar; parçalar havaya uçar, bahçeye saçılır.", [
                ("A08", Z, "Hav?", 0),
                ("A09", A, "Eyvah! Zıpzıp kutuya çarptı. Parçalar bahçeye düştü!", 0),
                ("A10", U, "Parçaları bulalım!", 0),
                ("A11", A, "Hadi şekil avına çıkalım! Sen de bize yardım eder misin?", 0),
            ]),
        ],
    },
    {
        "kod": "daire", "baslik": "DAİRE", "sekil": "daire", "sure": ("1:20", "4:00"),
        "sahneler": [
            ("D1", "1:20–1:50", "Yolda sarı, yuvarlak bir parça yuvarlanıp kaçar. Zıpzıp peşinden koşar.", [
                ("D01", A, "Bak! Bir parça yuvarlanıyor!", 0),
                ("D02", U, "Dur! Kaçma!", 0),
                ("D03", A, "Bu parça yuvarlak. Bunun adı... daire!", 0),
                ("D04", U, "Daire!", 0),
                ("D05", A, "Daire yuvarlanır. Hadi, başka daireler bulalım!", 0),
            ]),
            ("D2", "1:50–2:15", "Kamera yukarı bakar: güneş. Güneşin etrafında bir daire çizilir.", [
                ("D06", A, "Yukarı bak! Güneş ne şekil?", 3),
                ("D07", A, "Daire! Güneş yuvarlak, güneş bir daire!", 0),
                ("D08", U, "Güneş daire!", 0),
            ]),
            ("D3", "2:15–2:40", "Çalının yanında Zıpzıp'ın topu. Zıpzıp topu burnuyla yuvarlar.", [
                ("D09", A, "Zıpzıp'ın topu da yuvarlak.", 0),
                ("D10", A, "Top ne şekil?", 3),
                ("D11", A, "Daire!", 0),
                ("D12", Z, "Hav hav!", 0),
            ]),
            ("D4", "2:40–3:10", "Anneannenin piknik örtüsünde üç yuvarlak kurabiye. Her sayışta biri parlar.", [
                ("D13", A, "Anneanne kurabiye yaptı. Kurabiyeler de daire!", 0),
                ("D14", A, "Hadi sayalım! Bir... iki... üç!", 0),
                ("D15", U, "Üç daire kurabiye!", 0),
                ("D16", Z, "Hıh hıh!", 0),
                ("D17", A, "Zıpzıp kurabiyeleri kokluyor.", 0),
            ]),
            ("D5", "3:10–3:30", "Sarı daire parça bir tekerleğin yanında durur. Umay alır, kutudaki yuvarlak deliğe koyar: tık!", [
                ("D18", A, "İşte daire parça! Tekerleğin yanında!", 0),
                ("D19", A, "Tekerlek de daire. Döner, döner!", 0),
                ("D20", U, "Daire, daire deliğe!", 0),
                ("D21", A, "Tık! Oldu! Aferin!", 0),
            ]),
            ("D6", "3:30–4:00", "Daire tekerlemesi: söylenen her şey ekranda parlar, daireler dans eder.", [
                ("D22", A, "Daire, daire, yuvarlak daire.", 0),
                ("D23", A, "Güneş daire, top da daire.", 0),
                ("D24", A, "Kurabiye daire, tekerlek daire.", 0),
                ("D25", A, "Dön dön dön, yuvarlan!", 0),
                ("D26", A, "Sen de etrafına bak. Yuvarlak bir şey bulabilir misin?", 4),
            ]),
        ],
    },
    {
        "kod": "kare", "baslik": "KARE", "sekil": "kare", "sure": ("4:00", "6:40"),
        "sahneler": [
            ("K1", "4:00–4:30", "Çiçeklerin arasında mavi, köşeli bir parça. Umay parmağıyla kenarlarını sayar.", [
                ("K01", A, "Bak! Çiçeklerin arasında bir parça var!", 0),
                ("K02", A, "Bu parça yuvarlak değil. Köşeleri var. Bunun adı... kare!", 0),
                ("K03", U, "Kare!", 0),
                ("K04", A, "Karenin kenarlarını sayalım! Bir... iki... üç... dört!", 0),
                ("K05", A, "Karenin dört kenarı var.", 0),
            ]),
            ("K2", "4:30–5:00", "Komik an: Zıpzıp kare parçayı ağzıyla alıp yuvarlak deliğe sokmaya çalışır, olmaz. Parça seker.", [
                ("K06", A, "Zıpzıp kareyi daire deliğe koyuyor...", 0),
                ("K07", Z, "Hav?", 0),
                ("K08", A, "Olmadı! Kare, daire deliğe girmez.", 0),
                ("K09", U, "Kare, kare deliğe!", 0),
                ("K10", A, "Tık! Oldu! Aferin Umay!", 0),
            ]),
            ("K3", "5:00–5:20", "Evin penceresi kare. Pencerenin etrafında bir kare çizilir; anneanne el sallar.", [
                ("K11", A, "Başka kare var mı? Evin penceresine bak!", 0),
                ("K12", A, "Pencere ne şekil?", 3),
                ("K13", A, "Kare! Pencere de kare!", 0),
                ("K14", U, "Pencere kare!", 0),
            ]),
            ("K4", "5:20–5:45", "Çalının dibinde kurdeleli bir hediye kutusu. Umay açar, içinden Zıpzıp'ın kemiği çıkar.", [
                ("K15", A, "Bu ne? Bir hediye kutusu!", 0),
                ("K16", A, "Kutu da kare.", 0),
                ("K17", U, "Zıpzıp, bu senin!", 0),
                ("K18", Z, "Hav hav hav!", 0),
            ]),
            ("K5", "5:45–6:05", "Piknik örtüsü karelerle dolu. Umay üç kareye basar, her biri parlar.", [
                ("K19", A, "Piknik örtüsünde kareler var!", 0),
                ("K20", A, "Hadi sayalım! Bir... iki... üç!", 0),
                ("K21", U, "Üç kare!", 0),
            ]),
            ("K6", "6:05–6:40", "Kare tekerlemesi: her şey sırayla parlar, kareler zıplar.", [
                ("K22", A, "Kare, kare, köşeli kare.", 0),
                ("K23", A, "Pencere kare, kutu da kare.", 0),
                ("K24", A, "Dört kenar, dört köşe.", 0),
                ("K25", A, "Hop hop hop, kare zıpla!", 0),
                ("K26", A, "Sen de etrafına bak. Kare bir şey bulabilir misin?", 4),
            ]),
        ],
    },
    {
        "kod": "ucgen", "baslik": "ÜÇGEN", "sekil": "ucgen", "sure": ("6:40", "9:10"),
        "sahneler": [
            ("T1", "6:40–7:10", "Gölün kıyısında kırmızı, sivri bir parça. Umay kenarlarını sayar.", [
                ("T01", A, "Son parça nerede? Gölün kıyısında!", 0),
                ("T02", A, "Bu parçanın üç kenarı var. Bunun adı... üçgen!", 0),
                ("T03", U, "Üçgen!", 0),
                ("T04", A, "Kenarlarını sayalım! Bir... iki... üç!", 0),
                ("T05", A, "Üç kenar, üçgen!", 0),
            ]),
            ("T2", "7:10–7:30", "Gölde kâğıttan bir gemi yüzer; yelkeni üçgen. Rüzgâr eser, gemi süzülür.", [
                ("T06", A, "Gölde bir gemi var. Geminin yelkenine bak!", 0),
                ("T07", A, "Yelken ne şekil?", 3),
                ("T08", A, "Üçgen! Yelken üçgen!", 0),
                ("T09", U, "Yelken üçgen!", 0),
            ]),
            ("T3", "7:30–7:55", "Anneanne bir dilim karpuz uzatır. Umay ısırır, Zıpzıp hapşırır (karpuz suyu burnuna kaçar).", [
                ("T10", A, "Anneanne karpuz kesti. Karpuz dilimi de üçgen!", 0),
                ("T11", U, "Ham! Mmm, tatlı!", 0),
                ("T12", Z, "Hap... hap... hapşuuu!", 0),
                ("T13", U, "Hi hi! Çok yaşa Zıpzıp!", 0),
            ]),
            ("T4", "7:55–8:20", "Evin çatısı üçgen. Çatının etrafında bir üçgen çizilir. Umay üçgen parçayı kutudaki deliğe koyar: tık!", [
                ("T14", A, "Evin çatısına bak! Çatı ne şekil?", 3),
                ("T15", A, "Üçgen! Çatı da üçgen!", 0),
                ("T16", U, "Üçgen, üçgen deliğe!", 0),
                ("T17", A, "Tık! Oldu! Bütün parçaları bulduk!", 0),
                ("T18", Z, "Hav hav!", 0),
            ]),
            ("T5", "8:20–9:10", "Üçgen tekerlemesi: her şey sırayla parlar, üçgen flamalar sallanır.", [
                ("T19", A, "Üçgen, üçgen, sivri üçgen.", 0),
                ("T20", A, "Yelken üçgen, çatı üçgen.", 0),
                ("T21", A, "Karpuz dilimi üçgen.", 0),
                ("T22", A, "Bir, iki, üç, üç kenar!", 0),
                ("T23", A, "Sen de etrafına bak. Üçgen bir şey bulabilir misin?", 4),
            ]),
        ],
    },
    {
        "kod": "final", "baslik": "Final: Şekillerden Resim", "sekil": None, "sure": ("9:10", "10:30"),
        "sahneler": [
            ("F1", "9:10–9:40", "Kutudaki üç parça parlar. Anlatıcı sorar, sorulan parça zıplar.", [
                ("F01", A, "Şimdi sen söyle! Daire hangisi?", 3),
                ("F02", A, "İşte daire!", 0),
                ("F03", A, "Kare hangisi?", 3),
                ("F04", A, "İşte kare!", 0),
                ("F05", A, "Peki üçgen hangisi?", 3),
                ("F06", A, "İşte üçgen! Aferin sana!", 0),
            ]),
            ("F2", "9:40–10:10", "Parçalar kutudan uçar, gökyüzünde birleşir: kare bir ev, üçgen çatı, daire güneş.", [
                ("F07", A, "Bak! Şekiller bir resim yaptı!", 0),
                ("F08", A, "Kare bir ev, üçgen bir çatı, daire bir güneş!", 0),
                ("F09", U, "Ev! Bizim ev!", 0),
                ("F10", Z, "Hav hav hav!", 0),
            ]),
            ("F3", "10:10–10:30", "Kapanış kartı: Umay el sallar, Zıpzıp zıplar, şekiller uçuşur.", [
                ("F11", A, "Bugün üç şekil öğrendik: daire, kare, üçgen!", 0),
                ("F12", U, "Hoşça kalın! Yine görüşelim!", 0),
                ("F13", Z, "Hav hav!", 0),
            ]),
        ],
    },
]

AD = {A: "Anlatıcı", U: "Umay", Z: "Zıpzıp"}
SEKIL = {"daire": "DAİRE", "kare": "KARE", "ucgen": "ÜÇGEN"}


def satirlar(konusan=None, bolumler=None):
    for b in BOLUMLER:
        if bolumler and b["kod"] not in bolumler:
            continue
        for _, _, _, lines in b["sahneler"]:
            for ln in lines:
                if konusan is None or ln[1] == konusan:
                    yield ln


def belge():
    out = ["# Umay ile Zıpzıp, 2. Bölüm: \"Şekil Avı\" (≈10 dk)", "",
           "**Öğrenme hedefi:** Daire, kare, üçgen. Her şekil kendi bölümünde kalır (4-5 örnek, kenar sayma, tekerleme); "
           "şeklin parçası bulununca kutudaki deliğine oturur, sonra diğer şekle geçilir.", "",
           "**Hikâye:** Anneannenin şekil kutusunun parçaları bahçeye saçılır; Umay ile Zıpzıp şekil avına çıkar. "
           "Komik an: Zıpzıp kareyi yuvarlak deliğe sokmaya çalışır, olmaz. Finalde şekiller birleşip bir ev resmi olur.", "",
           "**Sessiz bekleme:** ⏸ işaretli yerlerde anlatıcı soru sorar ve çocuğun cevabı için 3–4 saniye bekler.", ""]
    for b in BOLUMLER:
        out += [f"## {b['baslik']}  ({b['sure'][0]}–{b['sure'][1]})", ""]
        for kod, zaman, aciklama, lines in b["sahneler"]:
            out += [f"### Sahne {kod} · {zaman}", f"*{aciklama}*", ""]
            for cid, who, txt, wait in lines:
                out.append(f"- `{cid}` **{AD[who]}:** {txt}" + (f"  ⏸ *{wait} sn bekle*" if wait else ""))
            out.append("")
    n = {w: sum(1 for _ in satirlar(w)) for w in (A, U, Z)}
    out.insert(6, f"**Toplam:** {sum(n.values())} satır (anlatıcı {n[A]}, Umay {n[U]}, Zıpzıp {n[Z]}).")
    out.insert(7, "")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    import os
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "06_bolum2_sekil_avi.md")
    open(p, "w").write(belge())
    print(p)
