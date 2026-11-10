# Gemini (Veo) için örnek prompt: Umay ile Zıpzıp, Pixar tarzı

Gemini uygulaması → **Video** (Veo). Gemini'de bir video **8 saniye**; 10 saniye için iki klip yapılıp art arda eklenebilir
(aşağıda 2. klip de var). Prompt İngilizce yazıldı: Veo İngilizce tarifleri daha iyi anlıyor. Konuşmalar Türkçe kalır.

## Klip 1 (8 sn): Mavi kelebek

```
A heartwarming 3D animated short in the style of a modern Pixar feature film. Soft global illumination, warm golden
morning sunlight, gentle depth of field, rich saturated pastel colors, smooth expressive character animation, 24 fps.

Characters (keep exactly the same design in every shot):
- UMAY: a cute 3-year-old Turkish girl, big round sparkling brown eyes, rosy cheeks, small button nose, chestnut-brown
  hair in two puffy pigtails tied with little yellow flower hair ties and a short fringe. She wears a coral-red
  short-sleeved dress with a round white Peter Pan collar and a small yellow heart on the chest, and orange shoes.
- ZIPZIP: her small, playful puppy. Cream-white fluffy fur with caramel-brown patches, one big floppy caramel ear,
  a brown patch around one eye, shiny black button nose, red collar with a round golden tag, always-wagging tail.

Setting: a bright flower meadow with a winding sandy path, round green trees, a small cream cottage with a red roof
in the background, a few soft white clouds in a clear blue sky.

Action (8 seconds):
0–3 s: Slow dolly-in. Umay walks happily along the path, Zıpzıp trotting beside her, tail wagging.
3–6 s: A glowing blue butterfly flutters down and lands softly on Umay's nose. Umay goes cross-eyed looking at it,
       then giggles with delight. Zıpzıp tilts his head curiously.
6–8 s: Umay points at the butterfly and says in Turkish, in a sweet toddler voice: "Mavi kelebek!"
       Zıpzıp bounces up and gives one happy little "Hav!" The butterfly flies up toward the sky.

Audio: gentle cheerful ukulele and glockenspiel music, birds chirping softly, the girl's giggle, one cute puppy bark.
Child-friendly, calm, no text on screen, no scary elements.
```

## Klip 2 (8 sn): Devamı, iki klip art arda ≈ 10–16 sn

```
Same characters, same design and same Pixar-style 3D look as before: UMAY (3-year-old girl, chestnut pigtails with
yellow flower hair ties, coral-red dress with white collar and yellow heart, orange shoes) and her puppy ZIPZIP
(cream fur with caramel patches, one floppy caramel ear, red collar with golden tag). Same sunny flower meadow.

0–4 s: The blue butterfly flies in a playful loop; Zıpzıp jumps after it, misses, and rolls softly in the grass.
4–8 s: Umay laughs, kneels and hugs Zıpzıp. Camera slowly rises to the blue sky. Umay says in Turkish, sweetly:
       "Hadi Zıpzıp, başka mavi şeyler bulalım!"

Audio: same cheerful ukulele music, soft grass rustle, girl's laugh, happy puppy panting. No text on screen.
```

## İpuçları

- **Karakter tutarlılığı:** Gemini'de bir görsel yükleyip "bu karakterleri kullan" diyebilirsin. Bunun için
  `kanal/profil_logo_800.png` ya da `kanal/kapak_bolum1_renkli_kelebekler_1280x720.jpg` iyi bir başlangıç.
  Görsel yüklenince prompt'a ekle: *"Use the girl and the puppy from the attached image as the characters,
  but render them in Pixar-style 3D."*
- **Türkçe konuşma:** Veo kısa Türkçe cümleleri genelde söyler ama aksan kayabilir. Olmazsa
  *"no dialogue, only giggles and a bark"* yazıp sesi bizim seslendirmeyle sonradan ekleyebiliriz.
- **"2D" ve "3D" farkı:** Pixar 3D çalışır. Daha düz bir görüntü istersen "3D" yerine şunu yaz:
  *"2D hand-drawn cartoon with soft Pixar-like lighting and shading"*.
- **Uyarı:** Yapay zekâ videosunda karakterlerin yüzü ve kıyafeti klipten klibe biraz değişebilir. Bu yüzden 10 dakikalık
  bölümlerde kendi çizim motorumuzu kullanıyoruz. Ama kısa tanıtım ve Shorts için Veo klipleri çok güzel olabilir.
