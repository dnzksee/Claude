"""Göbeklitepe — Veo prompt listesi (promptlar.md üretir). Hollywood sinema dili: her sahne ayrı kamera tekniği."""
STYLE = ("Style: premium hand-drawn 2D animated feature film, thick clean black outlines, rich painterly colors with "
         "soft cel shading, expressive faces, richly detailed painted backgrounds. Hollywood blockbuster "
         "cinematography: anamorphic widescreen look, subtle film grain, gentle anamorphic lens flares, dramatic "
         "motivated lighting (golden hour, torchlight, moonlight), volumetric light rays and dust in the air, deep "
         "foreground-midground-background layering, shallow depth of field where noted, smooth professional camera "
         "movement like a crane, Steadicam or dolly on a big film set. Real-world scale: stones and people keep their "
         "true size, grandeur comes from the camera. Smooth natural character animation, people never glide or "
         "slide, one continuous shot with no scene cuts, the place never changes, 16:9. Family-friendly and "
         "respectful: no blood, no violence. No text, no subtitles, no dialogue, no speech, no logos, no flags.")
ANTIK = ("Southeastern Anatolia around 9600 BC, Stone Age: hunter-gatherer people in animal-hide and woven-fiber "
         "clothing with bone and shell ornaments, flint tools only; absolutely no metal, no wheels, no pottery, no "
         "horses, no buildings except the stone circles.")
TEPE = ("A gentle limestone hill overlooking the wide fertile Harran plain near Şanlıurfa, Turkey, dry golden grass, "
        "a single lone mulberry tree on top.")
SUTUN = ("massive T-shaped limestone pillars about 5 meters tall arranged in large stone circles with low stone walls "
         "between them, two even taller pillars facing each other in the center, the pillars carved in low relief "
         "with arms, hands with long fingers and belts on their sides, and animals: foxes, wild boars, snakes, "
         "scorpions, cranes and vultures")
ARKEOLOG = ("a friendly German archaeologist in his forties with a short beard, glasses, a wide-brimmed hat and a "
            "khaki field shirt")
MODERN = {5, 6, 7, 9, 10, 11, 12, 13, 14, 23, 29, 36, 37, 39, 40, 42, 46, 47, 48}
B = []


def k(cumle, ozet, p, ses, kamera, yer=ANTIK):
    if cumle in MODERN:
        B.append((cumle, ozet, "IMPORTANT: hand-drawn 2D cartoon animation, NOT photorealistic, NOT live action, all "
                               f"people are cartoon characters. {p} Camera: {kamera} Sound: {ses}. {STYLE}"))
    else:
        B.append((cumle, ozet, f"{p} {yer} Camera: {kamera} Sound: {ses}. {STYLE}"))


# KANCA (iki klip: kanca + başlık kartı arkası)
k(0, "KANCA: yıldızlar altında meşalelerle aydınlanan dev sütunlar",
  f"Night, under a breathtaking sky full of stars and the Milky Way: {SUTUN}, lit by flickering torches held by a few Stone Age people standing in awe between them.",
  "crackling torches, deep cinematic drone, wind",
  "epic slow aerial crane descending from the Milky Way down into the stone circle, ending on the two central pillars.")
k(0, "KANCA 2: toprak sütunların üstünü örtüyor (zaman atlamalı)",
  f"Time-lapse over thousands of years: the stone circle of {SUTUN} is slowly covered by soil and rocks, grass grows over it, until only a smooth hill with a lone tree remains; stars and the sun streak across the sky.",
  "rising orchestral swell, rushing wind", "locked-off wide shot, then a very slow push-in as the hill forms.")
# Giriş
k(1, "Şanlıurfa yakınlarında, ovaya bakan tepe",
  f"Golden hour: {TEPE} Endless plain glowing below, shepherds' tiny silhouettes far away.",
  "wind over grass, distant sheep bells", "majestic IMAX-style aerial drone sweep over the plain, rising up the slope to reveal the hill.", yer="Present day.")
k(2, "Tarlalar ve tek bir dut ağacı",
  f"{TEPE} Wheat fields around it sway in the wind; the lone mulberry tree stands against a warm sunset sky.",
  "wind, birds", "slow low-angle dolly toward the tree, sun flare peeking through its branches.", yer="Present day.")
k(3, "Ayakların altında ne var? Toprağın içine inen kamera",
  "A cross-section view: from the grassy surface of the hill, the camera sinks down through layers of soil and stones, revealing in the darkness below the top of a giant carved T-shaped stone pillar.",
  "deep rumble, mysterious music", "vertical crane-down through the ground in one continuous move.", yer="")
k(4, "Toprak altında uyuyan tapınak",
  f"Underground in darkness, faint shafts of light fall through cracks onto buried {SUTUN}, dust floating; the stones look like sleeping giants.",
  "low choir hum, dripping", "slow Steadicam glide between the buried pillars, shallow depth of field.", yer="")
# Keşif
k(5, "1963: araştırmacılar tepeye uğruyor",
  "1963: a small team of researchers in 1960s field clothes with notebooks and an old camera walk up the dry hill under the hot sun, wiping their foreheads.",
  "wind, footsteps on gravel", "tracking shot from behind, then crane up to reveal the vast plain.")
k(6, "Yerde kırık kireçtaşı parçaları",
  "Close-up: a researcher's hand in the 1960s picks up a broken flat piece of limestone from the dry ground, turning it over; more broken stones scattered around.",
  "gravel crunch", "macro close-up with shallow depth of field, slow rack focus from the stone to the researcher's face.")
k(7, "Mezarlık sanıp gidiyorlar",
  "The 1960s researchers shrug, write a short note, and walk away down the hill; the camera stays on the lonely hill and the mulberry tree as they become small.",
  "fading footsteps, wind", "static wide shot, then a slow push-in on the hill as they leave.")
k(8, "Otuz yıl bekleyiş: mevsimler değişiyor",
  f"Time-lapse: {TEPE} Seasons pass rapidly over the hill: snow, spring flowers, golden summer, autumn, again and again; clouds race above.",
  "ticking clock, wind", "locked-off wide shot, time-lapse.", yer="")
k(9, "Çiftçinin sabanı taşa takılıyor",
  "1990s: a Turkish farmer with a mustache and a flat cap plows a field on the hill; suddenly the plow jerks and stops with a clang against a large buried stone; he kneels and brushes the soil away, revealing the carved edge of a big limestone block.",
  "plow scraping, sudden thud, birds", "ground-level shot beside the plow blade in slow motion, then rising up to the farmer's surprised face.")
k(10, "1994: arkeolog tepeye geliyor",
  f"1994: {ARKEOLOG} walks up the hill with a local guide, the sun behind him creating a heroic silhouette.",
  "wind, rising music", "low-angle hero shot, Steadicam following, lens flare.")
k(11, "Taşa dokunuyor: bunlar sıradan değil",
  f"{ARKEOLOG} kneels and gently touches a half-buried carved limestone block, his eyes widen behind his glasses.",
  "heartbeat-like drum", "slow dolly-zoom (vertigo effect) onto his face.")
k(12, "İlk dakikada anladı",
  f"{ARKEOLOG} stands up slowly on top of the hill and looks around at the whole hill with wonder, the wind moving his shirt, the sunset behind him.",
  "wind, emotional music", "slow 360-degree orbit around him.")
k(13, "Kalmayı seçiyor: kazı kampı kuruluyor",
  f"{ARKEOLOG} drives a wooden stake into the ground and smiles; behind him, a team sets up white tents and tools at sunrise.",
  "hammer tap, morning birds", "crane pull-back revealing the camp being set up.")
# Taşlar Konuşuyor
k(14, "Kazı: toprak altından dev sütun çıkıyor",
  "Archaeologists with brushes and trowels carefully uncover the top of a huge carved T-shaped limestone pillar emerging from the earth.",
  "brushes, soft music", "slow top-down crane shot rotating down to eye level.")
k(16, "Daireler halinde dizilmiş sütunlar, ortada iki dev",
  f"Midday: a grand stone circle of {SUTUN}.",
  "wind, epic music", "high aerial top-down shot slowly rotating, then descending between the two central pillars.")
k(17, "Yakından bakınca...",
  f"Inside the stone circle, a curious Stone Age woman holding a torch walks slowly toward one of the central pillars and raises the torch.",
  "torch crackle, suspense music", "Steadicam following behind her, slow push-in toward the pillar.")
k(18, "Sütunlarda kollar, eller, kemer",
  "Extreme close-up on the side of a T-shaped limestone pillar: carved arms bend around it and long-fingered hands meet above a carved belt, lit by moving torchlight.",
  "torch crackle", "slow vertical tilt down along the carved arm, shallow depth of field, rack focus to the hands.")
k(19, "Taştan devler",
  f"Low angle at night: the two central T-shaped pillars tower like giant stone figures, their T-tops like heads, torchlight making their carved arms seem alive; tiny people below.",
  "deep choir, wind", "extreme low-angle slow dolly-in with a slight dolly-zoom for scale.")
k(20, "Hayvan kabartmaları: tilki, domuz, yılan, akbaba",
  "Torchlight moves across carved reliefs on limestone pillars: a leaping fox, a wild boar, snakes running down the stone, a scorpion, cranes and a vulture with spread wings; shadows make them seem to move.",
  "crackling fire, mysterious music", "slow lateral macro tracking shot across the carvings, rack focus from one animal to the next.")
k(21, "11 bin yıldır orada duran figürler",
  "Close-up of a carved vulture on a pillar; the image slowly transitions from glowing torchlight in the past to the same weathered carving in today's daylight, with the same composition.",
  "time whoosh, soft music", "locked-off close-up, very slow push-in.")
# Kimler Yaptı?
k(22, "Peki kimler yaptı? Silüetler",
  "Silhouettes of Stone Age people standing on the hill against a giant orange sunrise, holding spears and baskets, looking at the stone circle below.",
  "wind, haunting flute", "wide silhouette shot, slow lateral dolly.")
k(23, "Bilim insanları yaşı hesaplıyor",
  "Modern lab: a scientist in a white coat places a tiny sample under a microscope; on a screen, a glowing timeline (no readable text) zooms back through millennia.",
  "lab hum, electronic pulse", "slow push-in from the microscope to the screen, shallow depth of field.")
k(25, "Yazı yok, tekerlek yok, metal yok",
  "A Stone Age camp at dusk: people sit around a fire making flint blades by knapping stone, weaving baskets and scraping hides; no metal, no wheels, no pottery anywhere.",
  "fire crackle, stone knapping clicks", "slow 360-degree orbit around the fire.")
k(26, "Tarım bile yok: yabani tahıl toplama",
  "Hunter-gatherers walk through a field of wild grasses and wild wheat, gathering grain by hand into woven baskets, gazelles running in the distance.",
  "wind in grass, birds", "low tracking shot through the tall grass, sun flare.")
k(27, "Avcı-toplayıcılar",
  "A group of Stone Age hunters with flint-tipped spears crouches silently in tall grass watching a herd of gazelles on the plain at sunrise.",
  "breathing, wind, distant hooves", "over-the-shoulder shot from behind a hunter, rack focus to the herd.")
# Nasıl Yaptılar?
k(28, "On tonluk taş nasıl taşındı?",
  "A giant T-shaped limestone pillar lies on the ground; a single Stone Age man stands next to it, tiny in comparison, scratching his head.",
  "wind, comic-curious music", "crane shot rising from the man to reveal the pillar's full length.")
k(29, "Taş ocağında yarım kalmış dev sütun (bugün)",
  "Present day: in a limestone bedrock quarry on a hillside, an enormous unfinished T-shaped pillar about 7 meters long lies still attached to the rock; a few visitors stand beside it for scale.",
  "wind, soft music", "slow aerial drone pass along the full length of the unfinished pillar.")
k(31, "Çakmaktaşı aletlerle kayaya oyma",
  "Stone Age workers chip at the limestone bedrock with sharp flint tools and hammerstones, carving a channel around a huge pillar shape; dust flies in the golden light.",
  "rhythmic stone tapping, chipping", "close-up on flint striking stone in slow motion, then pull back to reveal many workers.")
k(32, "Yüzlerce insan iplerle ve kütüklerle taşı çekiyor",
  "Epic scene: hundreds of Stone Age people pull thick plant-fiber ropes, dragging a giant T-shaped limestone pillar over wooden logs up the hill, others place logs in front; a leader raises his arm.",
  "rhythmic chanting without words, creaking ropes, drums", "massive crane shot rising high over the crowd to reveal the whole procession, like a historical epic.")
k(33, "Birlikte çalışmak ve beslenmek: büyük şölen",
  "Evening feast after the work: many Stone Age people share roasted meat and grain around big fires near the stone circle, laughing together, children running.",
  "fire, laughter, drums", "slow Steadicam weaving through the crowd, warm firelight.")
# Kayıp Tapınak
k(34, "Gizemli bir şey oldu",
  f"Dusk: an empty stone circle of {SUTUN}; storm clouds gather, wind blows dust between the pillars, the torches go out one by one.",
  "thunder, wind, suspense", "slow push-in from outside the circle, lightning flash.")
k(35, "Yapıların içi taş ve toprakla doluyor",
  f"Time-lapse over centuries: soil, rubble and stones gradually fill the inside of a stone circle of {SUTUN} until only the tops of the pillars show.",
  "deep rumble, time whoosh", "locked-off high angle time-lapse.")
k(36, "Bilerek mi gömüldü? (araştırmacılar tartışıyor)",
  "Modern archaeologists stand in an excavation trench beside a half-uncovered pillar, pointing at layers of soil in the trench wall and discussing thoughtfully.",
  "soft discussion murmur, wind", "slow lateral dolly along the trench wall layers to the archaeologists.")
k(37, "Yamaçtan kayan toprak",
  "Animated reconstruction: heavy rain on the hill, mud and rocks slide slowly down the slope into a stone circle.",
  "rain, sliding mud", "wide side view, slow push-in.")
k(38, "Binlerce yıl toprağın altında: yıldızlar dönüyor",
  "Night time-lapse: the smooth grassy hill with a lone tree under star trails swirling around the sky for thousands of years.",
  "ethereal music", "locked-off wide time-lapse, very slow push-in.", yer="")
k(39, "Korunmuş taşlar: kazıda ortaya çıkan pırıl pırıl kabartma",
  "Present day: a brush sweeps the last soil away from a carved fox relief on a pillar, revealing it crisp and perfectly preserved; the archaeologist's face lights up.",
  "brush strokes, soft triumphant music", "macro close-up, rack focus from the carving to the smiling archaeologist.", yer="")
# Önce Tapınak
k(40, "Tarihi sarstı: bilim insanları şaşkın",
  "Modern lecture hall: surprised scholars lean forward in their seats as a projector beam lights up a picture of the stone pillars (no readable text).",
  "gasp, murmurs", "slow dolly along the rows of amazed faces.")
k(41, "Eski fikir: önce tarım, sonra köy, sonra tapınak",
  "A quick animated sequence on one continuous landscape: a farmer plants seeds, a small village of mud-brick houses grows, then a small temple appears on top.",
  "light whimsical music", "slow lateral pan across the growing landscape.", yer="A stylized ancient Near East landscape.")
k(42, "Önce tapınak geldi, sonra şehir",
  f"{ARKEOLOG} stands among the excavated pillars at sunset, looking up at a central pillar with a thoughtful smile.",
  "wind, emotional music", "slow crane up and around him to the top of the pillar, sun flare.")
k(43, "Taşları dikmek için bir araya gelen insanlar",
  "Many Stone Age groups arrive from different directions across the plain, walking toward the hill with the stone circle, carrying baskets and tools.",
  "drums, wind, rising music", "epic high aerial shot of groups converging toward the hill.")
k(44, "Karacadağ'ın yamaçlarında yabani buğday",
  "Golden wild einkorn wheat waving on the slopes of a wide dark volcanic mountain at sunset; a Stone Age woman gently strokes the wheat heads with her hand.",
  "wind in wheat, soft music", "low-angle macro tracking shot through wheat heads, rack focus to the woman and the mountain.")
# Bugün
k(46, "Karahantepe ve kazılar sürüyor",
  "Present day: a nearby rocky hill excavation with many archaeologists working on carved stone pillars and a carved stone human head emerging from bedrock, under a sunny sky.",
  "tools tapping, wind", "slow aerial descent over the excavation.")
k(47, "Sadece küçük bir bölümü kazıldı",
  "Present day: a large modern curved protective roof over the excavated stone circles; the camera rises to show that the rest of the big hill around it is still untouched grass.",
  "wind, soft music", "crane up from under the roof to a high aerial view of the whole hill.")
k(48, "Toprağın altında bekleyen sırlar",
  "Present day at dusk: a child visitor kneels at the edge of the hill and touches the ground; under the soil (in a cross-section view) more unexcavated pillars glow faintly.",
  "mysterious music", "slow tilt down from the child through the ground.")
k(49, "İlk mesaj: yıldızlara yükselen final",
  f"Night: torchlit {SUTUN} with Stone Age people standing quietly among them looking up at the Milky Way; the carved animals glow in the firelight.",
  "epic orchestral finale, wind", "slow majestic crane rising from the pillars up into the stars.")

CIZIM = {15: "kart: 5 m / 10 ton", 24: "kart: zaman çizelgesi (Göbeklitepe → Stonehenge → Piramitler)",
         30: "kart: 7 metre", 45: "kart: UNESCO 2018"}

if __name__ == "__main__":
    out = ["# Göbeklitepe — Veo prompt'ları (Hollywood sinema çekimi)\n",
           "Her klip **ayrı yeni video**, **16:9 yatay**. Dosyaları numarasıyla yükle (`G01.mp4`, `G02.mp4`…).",
           f"Cümle {', '.join(map(str, CIZIM))} için klip gerekmiyor; kartları ben çiziyorum. Fotoğraf değil, hepsi video olsun.\n"]
    for n, (c, oz, p) in enumerate(B, 1):
        out.append(f"## G{n:02d} · {'kanca' if c == 0 else 'cümle ' + str(c)} — {oz}\n```\n{p}\n```\n")
    open("promptlar.md", "w").write("\n".join(out))
    eksik = [i for i in range(1, 50) if i not in {c for c, _, _ in B} | set(CIZIM)]
    print(len(B), "klip, eksik:", eksik)
