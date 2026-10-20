"""Umay ile Zıpzıp, 1. Bölüm: "Renkli Kelebekler" (≈20 dk). Tam senaryo.

Tek kaynak: hem okunabilir senaryo belgesi (docs/05_...) hem seslendirme paketi bu veriden üretilir;
ileride animasyonun zamanlaması da buradan okunacak.

Renk kuralı: her renk kendi bölümünde uzun süre kalır (6 örnek + tekerleme), sonra diğerine geçilir.
Sıra: MAVİ → KIRMIZI → SARI → hepsi birlikte (final).

Satır biçimi: (kimlik, konuşan, metin, bekleme_sn)
  bekleme_sn > 0 ise satırdan sonra çocuğun cevap vermesi için o kadar sessizlik bırakılır (seslendirilmez).
"""

A, U, Z = "anlatici", "umay", "zipzip"

BOLUMLER = [
    {
        "kod": "acilis", "baslik": "Açılış", "renk": None, "sure": ("0:00", "1:40"),
        "sahneler": [
            ("A1", "0:00–0:30", "Tema müziği. Kamera gökyüzünden çayıra iner, kâğıttan bulutlar süzülür. Başlık belirir.", [
                ("A01", A, "Umay ile Zıpzıp!", 0),
                ("A02", A, "Bugünkü macera... Renkli Kelebekler!", 0),
            ]),
            ("A2", "0:30–1:10", "Evin kapısı açılır, Umay çıkar. Zıpzıp kapının önünde zıplar. Anneanne pencereden el sallar.", [
                ("A03", A, "Günaydın! Bu, Umay.", 0),
                ("A04", U, "Günaydın!", 0),
                ("A05", A, "Bu da Umay'ın en iyi arkadaşı... Zıpzıp!", 0),
                ("A06", Z, "Hav hav!", 0),
                ("A07", U, "Günaydın Zıpzıp!", 0),
                ("A08", Z, "Hav!", 0),
            ]),
            ("A3", "1:10–1:40", "Bahçe kapısında dururlar, rengârenk çayıra bakarlar.", [
                ("A09", A, "Bugün çok güzel bir gün.", 0),
                ("A10", A, "Umay ile Zıpzıp bugün renkleri arayacak.", 0),
                ("A11", U, "Renkleri arayalım!", 0),
                ("A12", A, "Sen de bize yardım eder misin? Hadi gel!", 0),
            ]),
        ],
    },
    {
        "kod": "mavi", "baslik": "MAVİ", "renk": "mavi", "sure": ("1:40", "7:10"),
        "sahneler": [
            ("M1", "1:40–2:30", "Mavi bir kelebek süzülerek gelir, Umay'ın etrafında döner.", [
                ("M01", A, "Bak! Bir kelebek geliyor!", 0),
                ("M02", U, "Kelebek! Kelebek!", 0),
                ("M03", A, "Kelebek ne renk?", 3),
                ("M04", A, "Mavi! Evet, mavi!", 0),
                ("M05", U, "Mavi kelebek!", 0),
                ("M06", Z, "Hav hav!", 0),
                ("M07", A, "Mavi kelebek bize mavi şeyleri gösterecek. Hadi, takip edelim!", 0),
            ]),
            ("M2", "2:30–3:15", "Kelebek yukarı uçar, kamera gökyüzüne bakar.", [
                ("M08", A, "Kelebek yukarı uçtu. Yukarı bak!", 0),
                ("M09", A, "Gökyüzü ne renk?", 3),
                ("M10", A, "Mavi! Gökyüzü de mavi!", 0),
                ("M11", U, "Gökyüzü mavi!", 0),
            ]),
            ("M3", "3:15–4:10", "Kelebek üç mavi çiçeğe konar. Her sayışta bir çiçek parlar.", [
                ("M12", A, "Kelebek nereye kondu? Mavi çiçeklere!", 0),
                ("M13", A, "Hadi sayalım! Bir... iki... üç!", 0),
                ("M14", U, "Üç mavi çiçek!", 0),
                ("M15", Z, "Hıh hıh!", 0),
                ("M16", A, "Zıpzıp çiçekleri kokluyor.", 0),
            ]),
            ("M4", "4:10–5:00", "Masmavi küçük bir göl. Zıpzıp patisini suya sokar, su sıçrar.", [
                ("M17", A, "Bak, bir göl! Ne güzel bir göl.", 0),
                ("M18", A, "Su ne renk?", 3),
                ("M19", A, "Mavi!", 0),
                ("M20", Z, "Hav!", 0),
                ("M21", U, "Hi hi! Zıpzıp ıslandı!", 0),
            ]),
            ("M5", "5:00–5:45", "Ağaç dalında mavi bir kuş, Cik-Cik. Şakır şakır öter.", [
                ("M22", A, "Ağaçta kim var? Bir kuş!", 0),
                ("M23", U, "Merhaba kuşçuk!", 0),
                ("M24", A, "Bu Cik-Cik. Cik-Cik de mavi!", 0),
                ("M25", A, "Cik-Cik ne der? Cik cik cik!", 0),
            ]),
            ("M6", "5:45–6:30", "Çalının altında mavi bir top. Umay atar, Zıpzıp koşup getirir.", [
                ("M26", A, "Çalının altında ne var?", 0),
                ("M27", U, "Top! Mavi top!", 0),
                ("M28", U, "Zıpzıp, yakala!", 0),
                ("M29", Z, "Hav hav!", 0),
                ("M30", A, "Aferin Zıpzıp!", 0),
            ]),
            ("M7", "6:30–7:10", "Mavi tekerlemesi: söylenen her şey ekranda sırayla parlar. Sonra kelebek el sallar gibi uçar gider.", [
                ("M31", A, "Mavi, mavi, gökyüzü mavi.", 0),
                ("M32", A, "Mavi çiçek, mavi su.", 0),
                ("M33", A, "Mavi kuş, mavi top.", 0),
                ("M34", A, "Mavi kelebek, uç uç uç!", 0),
                ("M35", A, "Sen de etrafına bak. Bir mavi şey bulabilir misin?", 4),
                ("M36", U, "Hoşça kal mavi kelebek!", 0),
            ]),
        ],
    },
    {
        "kod": "kirmizi", "baslik": "KIRMIZI", "renk": "kırmızı", "sure": ("7:10", "12:40"),
        "sahneler": [
            ("K1", "7:10–7:55", "Kırmızı bir kelebek gelir.", [
                ("K01", A, "Aaa! Bir kelebek daha geldi!", 0),
                ("K02", A, "Bu kelebek ne renk?", 3),
                ("K03", A, "Kırmızı! Evet, kırmızı!", 0),
                ("K04", U, "Kırmızı kelebek!", 0),
                ("K05", A, "Kırmızı kelebek bize kırmızı şeyleri gösterecek.", 0),
            ]),
            ("K2", "7:55–8:50", "Elma ağacı. Kelebek bir elmaya konar, elma düşer, Umay yakalar.", [
                ("K06", A, "Ağaçta ne var? Elmalar!", 0),
                ("K07", A, "Elma ne renk?", 3),
                ("K08", A, "Kırmızı!", 0),
                ("K09", U, "Kırmızı elma! Mmm, nefis!", 0),
            ]),
            ("K3", "8:50–9:40", "Kelebek Zıpzıp'ın tasmasına konar. Zıpzıp gururla göğsünü kabartır.", [
                ("K10", A, "Kelebek nereye kondu?", 0),
                ("K11", A, "Zıpzıp'ın tasmasına!", 0),
                ("K12", A, "Zıpzıp'ın tasması ne renk?", 3),
                ("K13", A, "Kırmızı!", 0),
                ("K14", Z, "Hav hav!", 0),
            ]),
            ("K4", "9:40–10:40", "Yaprakta minicik bir uğur böceği. Sayarken her benek parlar.", [
                ("K15", U, "Bak! Minicik bir böcek!", 0),
                ("K16", A, "Bu bir uğur böceği. Uğur böceği de kırmızı!", 0),
                ("K17", A, "Üstünde siyah benekler var. Hadi sayalım!", 0),
                ("K18", A, "Bir... iki... üç... dört!", 0),
                ("K19", U, "Dört benek!", 0),
            ]),
            ("K5", "10:40–11:30", "Yerde kırmızı çilekler. Zıpzıp koklarken burnu çileğe değer, kıpkırmızı olur.", [
                ("K20", A, "Yerde küçük, kırmızı meyveler var.", 0),
                ("K21", U, "Çilek!", 0),
                ("K22", A, "Evet! Kırmızı çilekler.", 0),
                ("K23", Z, "Hıh hıh!", 0),
                ("K24", U, "Hi hi! Zıpzıp'ın burnu kırmızı oldu!", 0),
            ]),
            ("K6", "11:30–12:00", "Kelebek eve doğru uçar, kırmızı çatının üstünde döner.", [
                ("K25", A, "Kelebek eve doğru uçtu.", 0),
                ("K26", A, "Umay'ın evinin çatısı ne renk?", 3),
                ("K27", A, "Kırmızı!", 0),
            ]),
            ("K7", "12:00–12:40", "Kırmızı tekerlemesi, her şey sırayla parlar. Kelebek uçar gider.", [
                ("K28", A, "Kırmızı, kırmızı, elma kırmızı.", 0),
                ("K29", A, "Kırmızı çilek, kırmızı tasma.", 0),
                ("K30", A, "Kırmızı böcek, kırmızı çatı.", 0),
                ("K31", A, "Kırmızı kelebek, uç uç uç!", 0),
                ("K32", A, "Sen de bir kırmızı şey bulabilir misin?", 4),
                ("K33", U, "Hoşça kal kırmızı kelebek!", 0),
            ]),
        ],
    },
    {
        "kod": "sari", "baslik": "SARI", "renk": "sarı", "sure": ("12:40", "18:10"),
        "sahneler": [
            ("S1", "12:40–13:25", "Sarı bir kelebek gelir.", [
                ("S01", A, "Bir kelebek daha! Bu kelebek ne renk?", 3),
                ("S02", A, "Sarı! Evet, sarı!", 0),
                ("S03", U, "Sarı kelebek!", 0),
                ("S04", Z, "Hav hav!", 0),
                ("S05", A, "Sarı kelebek bize sarı şeyleri gösterecek.", 0),
            ]),
            ("S2", "13:25–14:10", "Kamera güneşe bakar, kâğıttan güneş ışınları döner.", [
                ("S06", A, "Gökyüzünde kocaman, sıcacık bir şey var.", 0),
                ("S07", U, "Güneş!", 0),
                ("S08", A, "Güneş ne renk?", 3),
                ("S09", A, "Sarı!", 0),
            ]),
            ("S3", "14:10–15:00", "Kelebek Umay'ın sarı kurdelesine konar.", [
                ("S10", A, "Kelebek nereye kondu?", 0),
                ("S11", A, "Umay'ın kurdelesine!", 0),
                ("S12", U, "Benim kurdelem sarı!", 0),
                ("S13", Z, "Hav!", 0),
            ]),
            ("S4", "15:00–15:50", "Kocaman bir ayçiçeği. Zıpzıp koklar, polenler burnunu gıdıklar, hapşırır.", [
                ("S14", A, "Bak! Kocaman bir çiçek. Bu bir ayçiçeği.", 0),
                ("S15", A, "Ayçiçeği ne renk?", 3),
                ("S16", A, "Sarı!", 0),
                ("S17", A, "Zıpzıp ayçiçeğini kokluyor...", 0),
                ("S18", Z, "Hap... hap... hapşuuu!", 0),
                ("S19", U, "Hi hi hi! Çok yaşa Zıpzıp!", 0),
            ]),
            ("S5", "15:50–16:40", "Ayçiçeğinin arkasından minik bir civciv çıkar. Zıpzıp şaşkınlıkla başını yana eğer.", [
                ("S20", A, "Çiçeğin arkasından kim çıktı?", 0),
                ("S21", U, "Civciv!", 0),
                ("S22", A, "Civciv ne renk?", 3),
                ("S23", A, "Sarı!", 0),
                ("S24", A, "Civciv ne der? Civ civ civ!", 0),
                ("S25", Z, "Hav?", 0),
            ]),
            ("S6", "16:40–17:30", "Piknik sepetinde bir limon. Umay ısırır, yüzünü buruşturur.", [
                ("S26", A, "Sepette sarı bir meyve var. Bu bir limon.", 0),
                ("S27", U, "Limon sarı!", 0),
                ("S28", U, "Ham! Iyy, ekşi!", 0),
                ("S29", A, "Limon çok ekşi!", 0),
            ]),
            ("S7", "17:30–18:10", "Sarı tekerlemesi, her şey sırayla parlar. Kelebek uçar gider.", [
                ("S30", A, "Sarı, sarı, güneş sarı.", 0),
                ("S31", A, "Sarı kurdele, sarı civciv.", 0),
                ("S32", A, "Sarı çiçek, sarı limon.", 0),
                ("S33", A, "Sarı kelebek, uç uç uç!", 0),
                ("S34", A, "Sen de bir sarı şey bulabilir misin?", 4),
                ("S35", U, "Hoşça kal sarı kelebek!", 0),
            ]),
        ],
    },
    {
        "kod": "final", "baslik": "Final: Hepsi Birlikte", "renk": None, "sure": ("18:10", "20:00"),
        "sahneler": [
            ("F1", "18:10–19:00", "Üç kelebek birlikte geri gelir, Umay'ın etrafında dans eder. Soru sorulan kelebek parlar.", [
                ("F01", A, "Bakın! Bütün kelebekler geri geldi!", 0),
                ("F02", U, "Mavi! Kırmızı! Sarı!", 0),
                ("F03", A, "Mavi kelebek hangisi? Göster bakalım!", 3),
                ("F04", A, "İşte mavi kelebek!", 0),
                ("F05", A, "Kırmızı kelebek hangisi?", 3),
                ("F06", A, "İşte kırmızı kelebek!", 0),
                ("F07", A, "Peki sarı kelebek hangisi?", 3),
                ("F08", A, "İşte sarı kelebek! Aferin sana!", 0),
            ]),
            ("F2", "19:00–19:35", "Gökyüzünde kâğıttan bir gökkuşağı açılır. Umay ile Zıpzıp sarılır, kalpler yükselir.", [
                ("F09", A, "Bugün üç renk öğrendik.", 0),
                ("F10", U, "Mavi, kırmızı, sarı!", 0),
                ("F11", Z, "Hav hav hav!", 0),
                ("F12", A, "Umay ile Zıpzıp... en iyi iki arkadaş!", 0),
            ]),
            ("F3", "19:35–20:00", "Kapanış kartı: Umay kameraya el sallar, Zıpzıp zıplar, üç kelebek uçuşur.", [
                ("F13", U, "Hoşça kalın! Yine görüşelim!", 0),
                ("F14", Z, "Hav hav!", 0),
            ]),
        ],
    },
]

# Seslendirme: AI Studio ayarları
SESLER = {
    A: ("Aoede", "Say in a sweet, warm, smiling preschool cartoon storyteller voice, lively, playful and expressive. "
                 "Leave a clear pause between each line."),
    U: ("Leda", "Say slowly and sweetly, like a cute three-year-old toddler girl in a cartoon: sing-song, soft and breathy, "
                "a tiny bit lispy, full of wonder, with little giggles. Leave a clear pause between each line."),
    Z: ("Laomedeia", "Make the sounds of a tiny, cute, playful cartoon puppy, high and happy. "
                     "Leave a clear pause between each line."),
}
AD = {A: "Anlatıcı", U: "Umay", Z: "Zıpzıp"}

# Ses dosyaları: anlatıcı her bölüm için ayrı (uzunluk sınırı), Umay ve Zıpzıp tek dosya
DOSYALAR = [(f"anlatici_{i + 1}_{b['kod']}", A, [b["kod"]]) for i, b in enumerate(BOLUMLER)] + [
    ("umay_tum", U, [b["kod"] for b in BOLUMLER]),
    ("zipzip_tum", Z, [b["kod"] for b in BOLUMLER]),
]


def satirlar(konusan=None, bolumler=None):
    for b in BOLUMLER:
        if bolumler and b["kod"] not in bolumler:
            continue
        for _, _, _, lines in b["sahneler"]:
            for ln in lines:
                if konusan is None or ln[1] == konusan:
                    yield ln


def belge():
    out = ["# Umay ile Zıpzıp, 1. Bölüm: \"Renkli Kelebekler\" (≈20 dk)", "",
           "**Öğrenme hedefi:** Mavi, kırmızı ve sarı renkleri. Her renk kendi bölümünde uzun süre kalır "
           "(6 örnek, sayma, tekerleme) ve çocuk o rengi pekiştirmeden diğerine geçilmez.", "",
           "**Akış:** Açılış → MAVİ (5,5 dk) → KIRMIZI (5,5 dk) → SARI (5,5 dk) → Final: üç renk birlikte", "",
           "**Sessiz bekleme:** ⏸ işaretli yerlerde anlatıcı soru sorar ve çocuğun cevap vermesi için 3–4 saniye bekler. "
           "Bu süre seslendirilmez, montajda eklenir.", ""]
    total = 0
    for b in BOLUMLER:
        renk = f" 🦋 {b['renk']} kelebek" if b["renk"] else ""
        out += [f"## {b['baslik']}  ({b['sure'][0]}–{b['sure'][1]}){renk}", ""]
        for kod, zaman, aciklama, lines in b["sahneler"]:
            out += [f"### Sahne {kod} · {zaman}", f"*{aciklama}*", ""]
            for cid, who, txt, wait in lines:
                total += 1
                out.append(f"- `{cid}` **{AD[who]}:** {txt}" + (f"  ⏸ *{wait} sn bekle*" if wait else ""))
            out.append("")
    out += ["---", "", "# Seslendirme Paketi (Google AI Studio)", "",
            "**aistudio.google.com → Generate speech** · Model: **gemini-2.5-flash-preview-tts** · Mod: **Single speaker**", "",
            "Her kutu için sesi seçin, **Style instructions** kutusuna yönergeyi, metin kutusuna metni yapıştırın, **Run**'a basın ve indirin. "
            "Dosyayı başlıktaki adla kaydedip sohbete yükleyin. Cümleleri ben ayırıp kontrol edeceğim.", "",
            f"Toplam **{len(DOSYALAR)} dosya**. Anlatıcı her bölüm için ayrı kaydedilir, çünkü tek seferde çok uzun metin okutmak sorun çıkarabilir.", ""]
    for i, (ad, who, bols) in enumerate(DOSYALAR, 1):
        voice, style = SESLER[who]
        lines = [t for _, _, t, _ in satirlar(who, bols)]
        style = style.replace("Leave a clear pause between each line.",
                              f"Leave a long, two-second silent pause between each line. Read ALL {len(lines)} lines, in order, without skipping any line.")
        out += [f"## {i}) `{ad}`: {AD[who]} · Ses: **{voice}** · {len(lines)} cümle", "",
                "Style instructions:", "```", style, "```", "Metin:", "```", *lines, "```", ""]
    out.insert(6, f"**Toplam:** {total} cümle (anlatıcı {sum(1 for _ in satirlar(A))}, Umay {sum(1 for _ in satirlar(U))}, "
                  f"Zıpzıp {sum(1 for _ in satirlar(Z))}).")
    out.insert(7, "")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    import os
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "05_bolum1_renkli_kelebekler_20dk.md")
    open(p, "w").write(belge())
    print(p)
