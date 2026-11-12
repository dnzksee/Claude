# Kroniknâme — indirilebilir videolar

Her konunun klasöründe: uzun video (1080p), Short, YouTube kapak resmi, başlık/açıklama/etiketler, altyazı.
İndirmek için dosyaya tıklayın, sağ üstteki **indir (Download raw file)** düğmesine basın.

- `emu/` — Büyük Emu Savaşı 1932 (4:52) + 3 Short — uzun video Git LFS ile saklanır
- `lagari/` — Lagari Hasan Çelebi 1633 (4:40) + 3 Short — uzun video Git LFS ile saklanır
- `dans/` — Dans Vebası 1518 (5:34) + 3 Short — uzun video Git LFS ile saklanır
- `preveze/` — Preveze Deniz Savaşı 1538 (7:30) + 3 Short — uzun video Git LFS ile saklanır
- `fetih/` — İstanbul'un Fethi 1453 (8:30) + Short — uzun video Git LFS ile saklanır
- `mumya/` — Avrupalılar Mumya Yedi: İlaç Diye (3:14)
- `kanal/` — profil resimleri, kanal kapakları (A: ilk sürüm, B: zaman çizelgeli), kanal açıklaması

## Seslendirme ayarı (tüm videolar)
Gemini TTS, ses **Kore**, Türkçe. Ton talimatı (kanalın seçtiği ton, mumya ses örneği 4):
`Çok heyecanlı, enerjik ve şaşkınlık dolu, sesini canlı tutan bir belgesel anlatıcısı gibi, akıcı Türkçe ile oku:`
Ses asla hızlandırılmaz ya da yavaşlatılmaz. Yeni videolar Google Drive'a yüklenir.

## Video yapısı (bundan sonraki tüm videolar)
1. **Kanca (5-8 sn):** Videonun en çarpıcı 2-3 sahnesi hızlı kesmelerle, ekranda büyük merak sorusu, tek cümlelik anlatım, geçişlerde davul vuruşu.
2. **Başlık kartı (3 sn):** Kancadan hemen sonra.
3. **Hikâye:** Bölümler hâlinde, orta tempo. Yaklaşık 1:30'da "Abone ol" butonu.
4. **Kapanış:** Yoruma davet eden soru ve kanal kartı.
Shorts: ilk 1-2 saniyede ekranda büyük soru ya da şaşırtıcı cümle.
Her uzun videodan 3 Short: her biri tek bir şaşırtıcı ayrıntı, "bunu bilmiyordum" dedirten başlık, ekrandaki yazılar düz (eğik değil).
Short süresi en fazla 25-30 saniye (daha uzunu izleyiciyi sıkıyor).
Short kanca yazısı somut olur ve olayın kendisini söyler ("ORDU KUŞLARA YENİLDİ!", "ROKETLE UÇTU!"); bağlamsız alıntı kullanılmaz.
Short'un ilk karesi, kanca yazısının anlattığını gösteren en hareketli sahne olur (sakin sahneyle açılmaz). Dans Short'u (15 B) böyleydi; Lagari Short'u (21) değildi.
Short'lar günde en fazla 1 tane yüklenir; uzun videoyla aynı gün yüklenmez.
Her video bitince (sorulmadan) uzun video ve 3 Short için başlık, açıklama (uzun videoda bölüm zamanlarıyla) ve etiketler verilir; etiketler hem virgüllü hem # ile. Ayrıca `<konu>/yayin/youtube.md` dosyasına yazılır.
Short başlıkları 80-100 karakter (#shorts dahil, YouTube sınırı 100): olayı merak uyandıran tek bir cümleyle anlatır, sonunda bir emoji + #shorts.
Evliya Çelebi gibi kaynakların doğruluğu videoda tartışılmaz; hikâye kaynağın anlattığı gibi aktarılır ("Evliya Çelebi'ye göre").
Videolarda fotoğraf kullanılmaz (küçük çözünürlük TV'de bulanık görünüyor); her sahne Veo videosu olur, eksik sahne için yeniden video istenir.
Kapaklarda sağ alt köşe boş kalır (YouTube süre etiketi oraya gelir).
Uzun video hedefi: 8-10 dakika.
