# Umay ile Zıpzıp — Dizi Kitabı (Series Bible)

**Hedef kitle:** 2–5 yaş · **Dil:** Türkçe · **Format:** 25–30 dakikalık derleme bölümler (içinde 6–7 dakikalık mini hikâyeler + şarkılar)
**Tek cümleyle:** Dört yaşındaki meraklı Umay ve pamuk gibi beyaz köpeği Zıpzıp, evlerinin önündeki çayırda her gün küçük bir şey keşfeder. Her keşif bir renk, bir sayı ya da bir duygu öğretir.

---

## 1. Karakterler

### Umay (4 yaşında)
| Özellik | Tasarım kararı | Neden |
|---|---|---|
| Baş/gövde oranı | Baş, boyunun ~%40'ı | Bebeksi oran, küçük çocuklar büyük yüz ve gözlere daha çok bakar |
| Saç | Kestane, iki yanda top kuyruk, **sarı kurdele** | Siluet hemen tanınır; kuyruklar yürürken sallanır (ikincil hareket) |
| Elbise | **Mercan kırmızısı**, beyaz yaka, sarı kalp cep | Yeşil çayır üzerinde en yüksek kontrast: Umay her karede ilk fark edilen şey olur |
| Ayakkabı | Turuncu-sarı | Ayaklar görünür, yürüme ritmi okunur |
| Gözler | Büyük, koyu oval, iki parlama noktası | Canlılık ve sıcaklık; göz bebekleri baktığı nesneyi izler |
| Kişilik | Meraklı, cesur, paylaşımcı, çabuk heyecanlanır | Çocuk kendini onunla özdeşleştirir |
| Konuşma | En fazla 4–6 kelimelik cümleler | Dil gelişimine uygun, tekrar edilebilir |

### Zıpzıp (yavru köpek)
| Özellik | Tasarım kararı |
|---|---|
| Renk | Krem-beyaz, **karamel sarkık kulak** ve tek göz lekesi; kırmızı tasma, altın künye |
| Hareket | Paytak tırıs, sürekli sallanan kuyruk; heyecanlanınca zıplar |
| Ses | "Hav hav!", hapşırık, hıh-hıh koklama — **konuşmaz** (çocuklar hayvan seslerini taklit etmeyi sever) |
| Rolü | Komik an yaratıcısı; Umay'ın duygularını aynalar |

### Yan karakterler (ileriki bölümler)
- **Sarı Kelebek** — sessiz rehber; her bölümde bir şeyi "gösterir".
- **Mırmır** — tembel turuncu kedi (ayakta durmayı sevmez, hep uyur).
- **Cik-Cik** — mavi serçe, şarkıların başlatıcısı.
- **Anneanne** — evin penceresinden seslenir, kapanışta "Hadi eve!" der.

---

## 2. Görsel dil

**Renk paleti** (`studio/engine/characters.py` → `PAL`):

| Kullanım | Renk |
|---|---|
| Umay elbise | `#EE6A5E` |
| Umay saç | `#7A4426` |
| Kurdele / kalp | `#FFC93C` |
| Zıpzıp | `#F8EAD6` / karamel `#D9955A` |
| Gökyüzü | `#8EC5EC` → ufuk `#FFF1DA` |
| Çayır | `#A6D879` → `#6FB257` |
| Yol | `#F2DFB0` |

**Kurallar**
1. Karakterler sıcak renklerde, dekor serin/yeşil tonlarda: figür her zaman zeminden ayrılır.
2. Ekranda aynı anda en fazla 3 hareketli öğe. Küçük çocuğun dikkatini bölmeyiz.
3. Hızlı yanıp sönme yok (ışığa duyarlı epilepsi güvenliği; saniyede 3'ten fazla parlaklık değişimi kesinlikle yok).
4. Kamera yavaş: kesme veya kamera hareketi en az 4–6 saniyede bir. Yakın çekime geçişler yumuşak "dolly" ile yapılır.
5. Uzak katmanlar paralaks ile yavaş kayar; derinlik hissi verir ama göz yormaz.

---

## 3. Pedagojik ilkeler (her bölümde)

| İlke | Uygulama | Örnek kesitteki karşılığı |
|---|---|---|
| **Etkileşimli duraklama** | Anlatıcı soru sorar, **2,5–3 sn** bekler, sonra cevabı söyler | "Kelebek ne renk?" … "Sarı! Evet, sarı!" |
| **Tekrar** | Anahtar kelime en az 3 kez | sarı / kelebek / çiçek |
| **Tek öğrenme hedefi** | Her mini hikâyede bir kavram | Renkler: sarı, kırmızı, mavi |
| **Duygu modelleme** | Karakterin yüzü duyguyu net gösterir | Şaşırma (kaş kalkar), sevinç (kapalı gülen gözler) |
| **Güvenli komedi** | Fiziksel ama zararsız şakalar | Zıpzıp'ın hapşırığı |
| **Sıcak kapanış** | Her hikâye sarılma/vedalaşma ile biter | Umay–Zıpzıp sarılması, kalpler |
| **Ses** | Yumuşak tınılar, konuşma sırasında müzik kısılır | Kalimba, müzik kutusu, ksilofon |

---

## 4. Teknik seçimi — dört örnek

| | Suluboya | Kâğıt Kesme | Yumuşak 3B | Keçe El İşi |
|---|---|---|---|---|
| His | Masal kitabı, sakin, sanatsal | El yapımı, dokunsal, stop-motion | Parlak, oyuncak gibi, modern | Sıcacık, yumuşak, "anne eli değmiş" oyuncak |
| Ebeveyn algısı | "Kaliteli, sakin içerik" | "Yaratıcı, Montessori havası" | "Popüler YouTube çizgisi" | "Güvenli, sevimli, el emeği" |
| 2–3 yaş dikkat çekiciliği | Orta-yüksek | Yüksek (gölgeler derinlik verir) | En yüksek (parlak, kontrastlı) | Yüksek (dikişler ve tüylü doku göze takılır) |
| Ayırt edicilik (pazarda) | **Çok yüksek** — az rakip | Yüksek | Düşük — çok rakip | **Çok yüksek** — Türkçe içerikte neredeyse yok |
| Üretim maliyeti (bu altyapıda) | Yüksek işlem süresi | Düşük | Düşük | Yüksek işlem süresi |
| Ürün potansiyeli | Kitap | Boyama/etkinlik | Oyuncak | **Peluş ve keçe oyuncak, el işi seti** |

**Karar: Dizinin ana tekniği KÂĞIT KESME.** Katmanlı kâğıt ve yumuşak gölgeler derinlik verir. Saniyede 12 pozluk hafif stop-motion titreşimi el yapımı hissi taşır ve müzikle çok iyi uyum sağlar. Bu tarz boyama ve etkinlik ürünlerine de doğal olarak uyarlanabilir.
