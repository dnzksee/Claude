"""MALAZGİRT 1071 — animasyon odaklı sürüm (v2).

Kurgu ilkesi: görüntü en geç 3-4 saniyede bir değişir; anlatıcı bir yer/kişi/olay söylediği anda
o şey ekranda olur (T.kelime ile kelime anına bağlanır). Yıllar, kişiler ve harita sahnelerindeki
şehir adları otomatik katmanla ayrıca canlandırılır.
"""
from motor.harita import arka_plan_uret
from motor.cografya import Harita, Bolge, Sehir, Rota
from motor.kartlar import koyu_arka_plan, KarakterKarti, ZamanCizelgesi, Karsilastirma, AlintiKarti, BuyukYazi
from motor.sahne import (Birlik, Komutan, HareketOku, OkYagmuru, EtiketBalonu, BaslikKarti, BolumEtiketi,
                         Lejant, taraf_tanimla)
from motor.figurler import Kafile
from motor.katmanlar import Ikon, Tablo, YilRozeti, oto_katman

taraf_tanimla("bizans", (0.46, 0.17, 0.52), vurgu=(0.97, 0.83, 0.45))
taraf_tanimla("selcuklu", (0.05, 0.50, 0.55), vurgu=(0.93, 0.96, 0.90))
taraf_tanimla("gazneli", (0.78, 0.45, 0.12), vurgu=(0.99, 0.92, 0.75))
taraf_tanimla("fatimi", (0.22, 0.52, 0.22), vurgu=(0.92, 0.95, 0.80))
taraf_tanimla("pecenek", (0.45, 0.42, 0.40), vurgu=(0.92, 0.90, 0.85))
taraf_tanimla("norman", (0.18, 0.32, 0.66), vurgu=(0.90, 0.92, 0.98))
taraf_tanimla("hacli", (0.72, 0.13, 0.10), vurgu=(0.98, 0.92, 0.85))
taraf_tanimla("notr", (0.55, 0.45, 0.25), vurgu=(0.95, 0.85, 0.6))

B = lambda i, m, **k: dict(id=i, metin=m, **k)  # noqa: E731

BOLUMLER = [
    # =============================================================== 1 GİRİŞ
    B("g1", "Yıl 1071, Ağustos ayının son haftası. Doğu Anadolu'da, Van Gölü'nün kuzeyinde, Malazgirt ile "
            "Ahlat arasında uzanan geniş bir ova.", bolum="Giriş"),
    B("g2", "Bir yanda, bin yıllık Roma mirasını taşıyan Bizans İmparatorluğu ve onun asker imparatoru Romen "
            "Diyojen. Diğer yanda, Orta Asya bozkırlarından çıkıp kısa sürede koca bir imparatorluk kuran Büyük "
            "Selçuklular ve onların sultanı Alparslan."),
    B("g3", "26 Ağustos günü bu ovada yaşanan savaş, yalnızca iki ordunun değil, iki dünyanın kaderini belirledi. "
            "Anadolu'nun kapıları Türklere açıldı. Bizans bir daha asla eski gücüne kavuşamadı. Ve bu savaşın "
            "yankıları, yirmi beş yıl sonra Haçlı Seferleri'ne kadar uzandı."),
    B("g4", "Peki, bozkırdan gelen bu atlılar, dünyanın en köklü imparatorluklarından birini nasıl dize getirdi? "
            "Bir imparator, savaş meydanında nasıl esir düştü? Bu hikâyeyi en başından anlatalım.", ek_sure=1.5),
    # =============================================================== 2 BOZKIR
    B("s1", "Hikâyemiz, Aral Gölü'nün doğusunda, Seyhun Nehri kıyılarında başlıyor. Onuncu yüzyılda burada, Oğuz "
            "boylarından biri olan Kınık boyunun başında, Selçuk Bey adında bir lider vardı.",
      bolum="Bozkırdan Doğan Güç"),
    B("s1b", "O dönemde Oğuzlar, Oğuz Yabgu Devleti adıyla bir siyasi birlik içinde yaşıyordu. Selçuk Bey, bu "
             "devletin ordusunda subaşı, yani komutandı. Ancak Yabgu ile anlaşmazlığa düşünce, boyunu alıp ayrıldı."),
    B("s2", "Selçuk Bey, boyuyla birlikte Seyhun kıyısındaki Cend şehri çevresine yerleşti ve İslamiyet'i kabul "
            "etti. Bu karar, Selçukluların kaderini belirleyecekti."),
    B("s2b", "Selçuk Bey'in oğulları ve torunları, sonraki yıllarda Karahanlılar, Samaniler ve Gazneliler arasındaki "
             "güç mücadelesinde ustaca saf değiştirerek güçlendiler. Bozkırın hızlı atlı okçuları, bölgedeki her "
             "devletin ilgisini çekiyordu."),
    B("s3", "Selçuk Bey'in torunları Tuğrul ve Çağrı Beyler, on birinci yüzyılın başında boylarını güneye, "
            "Horasan'a götürdüler. Ancak bu verimli topraklar, güçlü bir devletin, Gaznelilerin elindeydi."),
    B("s4", "Gazneli Sultan Mesud, bu göçebe Türkmenleri bir tehdit olarak görüyordu. Onları ezmek için fillerle "
            "desteklenen, ağır zırhlı büyük bir ordu topladı ve çöle yürüdü."),
    B("s5", "1040 yılında, Merv yakınlarındaki Dandanakan'da iki ordu karşılaştı. Selçuklular, Gazneli ordusunu "
            "günlerce yıprattı ve su kaynaklarından uzak tuttu. Susuz ve yorgun düşen Gazneliler, sonunda ağır bir "
            "yenilgiye uğradı."),
    B("s6", "Dandanakan zaferiyle Büyük Selçuklu Devleti resmen kuruldu. Tuğrul Bey sultan ilan edildi. Çağrı Bey "
            "ise doğuda, Horasan'ın yönetimini üstlendi."),
    B("s7", "Bundan sonrası bir fırtına gibiydi. Selçuklular Nişabur'u, Rey'i ve İsfahan'ı birer birer aldı. 1055 "
            "yılında Tuğrul Bey, Abbasi halifesinin daveti üzerine Bağdat'a girdi. Birkaç yıl sonra halife ona, "
            "Doğunun ve Batının Sultanı unvanını verdi."),
    B("s8", "Selçuklu yükselişi, Türkmen boylarını da harekete geçirmişti. Otlak ve ganimet arayan Türkmen "
            "akıncıları, giderek batıya, Bizans sınırlarına yöneldi. 1048 yılında Pasinler Ovası'nda, Selçuklular "
            "ile Bizans arasında ilk büyük savaş yaşandı ve zafer Selçukluların oldu."),
    B("s9", "Ama iki güç arasındaki asıl hesaplaşma, henüz başlamamıştı.", ek_sure=0.8),
    # =============================================================== 3 BİZANS
    B("b1", "Peki, o dönemde Bizans ne durumdaydı? Bunu anlamak için biraz geriye gitmemiz gerekiyor. 1025 "
            "yılında, Bizans'ın en güçlü imparatorlarından İkinci Basileios öldüğünde, imparatorluk batıda "
            "İtalya'dan doğuda Kafkaslara kadar uzanan muazzam bir güçtü.", bolum="Bizans'ın Krizi"),
    B("b2", "Basileios, Bulgarları ezdiği için Bulgar Avcısı lakabıyla anılıyordu. Ordusu disiplinli, hazinesi "
            "doluydu. Ama ardında, imparatorluğu yönetecek güçlü bir varis bırakmadı."),
    B("b3", "Basileios'un ölümünden sonra taht, saray entrikaları ve darbelerle sık sık el değiştirdi. Başkentteki "
            "sivil bürokratlar ordudan korkuyor, askeri harcamaları kısıyordu. Sınır boylarındaki köylü askerler, "
            "askerlik yerine vergi ödemeye başladı. Kaynaklara göre doğu sınırındaki koca bir ordu, tasarruf "
            "uğruna dağıtıldı."),
    B("b3b", "Bizans'ın gücü yüzyıllardır tema adı verilen askeri eyaletlere dayanıyordu. Bu sistemde köylüler toprak "
             "karşılığında askerlik yapar, sınırları kendi topraklarını korur gibi savunurlardı. On birinci yüzyılda "
             "bu sistem çözülmeye başladı. Büyük toprak sahipleri köylülerin topraklarını yuttu, köylü asker sınıfı "
             "zayıfladı."),
    B("b4", "Böylece imparatorluk, giderek yabancı paralı askerlere bağımlı hale geldi. Normanlar, Franklar, "
            "Peçenekler ve Uzlar. Bu askerler cesurdu, ama sadakatleri parayla ölçülüyordu."),
    B("b5", "Üstelik Bizans her cepheden sıkıştırılıyordu. Kuzeyde Peçenekler Tuna'yı aşıp Balkanlara akın "
            "ediyordu. Güney İtalya'da ise Normanlar, Bizans şehirlerini tek tek ele geçiriyordu."),
    B("b6", "Doğuda ise Türkmen akınları artık durdurulamaz hale gelmişti. 1064 yılında Ermenistan'ın görkemli "
            "başkenti Ani düştü. 1067'de Kayseri yağmalandı. Akıncılar Anadolu'nun içlerine kadar ilerliyor, "
            "Bizans ise etkili bir cevap veremiyordu."),
    B("b7", "Bizans'ın bu yorgun dönemi, tam da Selçukluların yükselişiyle aynı zamana denk geliyordu. Bir yanda "
            "hızla büyüyen genç bir güç, diğer yanda yorgun düşmüş köklü bir imparatorluk.", ek_sure=1.0),
    # =============================================================== 4 ALPARSLAN
    B("a1", "1063 yılında Tuğrul Bey çocuksuz olarak öldü. Taht için kısa ama sert bir mücadele yaşandı. Sonunda "
            "Çağrı Bey'in oğlu Alparslan, Büyük Selçuklu sultanı oldu.", bolum="Sultan Alparslan"),
    B("a2", "Alparslan, adının hakkını veren bir liderdi. Alp, yiğit demekti. Arslan ise aslan. Gençliğinden beri "
            "babasıyla birlikte savaşmış, Horasan'ı yönetmiş, tecrübeli bir komutandı."),
    B("a3", "Yanında ise tarihin en ünlü devlet adamlarından biri vardı: Veziri Nizamülmülk. Nizamülmülk devletin "
            "idaresini düzene soktu, medreseler kurdu. Alparslan ise seferlere odaklandı."),
    B("a3b", "Nizamülmülk'ün kaleme aldığı Siyasetname, devlet yönetimi üzerine yazılmış en ünlü eserlerden biridir "
             "ve bugün hâlâ okunur."),
    B("a4", "Sultan olduktan sadece bir yıl sonra, 1064'te Kafkasya'ya yürüdü. Yirmi beş günlük bir kuşatmanın "
            "ardından, uzun süredir alınamayan Ani'yi fethetti."),
    B("a5", "Ancak Alparslan'ın asıl hedefi Bizans değildi. Onun gözü güneyde, Mısır'daki Fatımi Devleti'ndeydi. "
            "Sünni İslam dünyasının lideri olarak, Fatımileri yıkmayı en büyük görevi sayıyordu."),
    B("a6", "Bizans sınırlarındaki Türkmen akınları ise çoğu zaman sultanın kontrolünde değildi. Ama Bizans için bu "
            "ayrım pek önemli değildi. Konstantinopolis'te, doğudaki tehdidi kökünden çözecek bir imparator "
            "aranıyordu.", ek_sure=0.5),
    # =============================================================== 5 ROMEN
    B("r1", "Bu imparator, Romen Diyojen olacaktı. Kapadokyalı köklü bir askeri aileden gelen Romen, cesaretiyle "
            "tanınan bir generaldi. Hatta bir ara darbe girişimiyle suçlanıp ölüme mahkûm edilmişti.",
      bolum="İmparator Romen Diyojen"),
    B("r2", "1067'de İmparator Konstantin Dukas öldüğünde, dul imparatoriçe Evdokia, devletin başına güçlü bir asker "
            "geçmesi gerektiğine karar verdi. Mahkûm generali affetti ve onunla evlenmeye karar verdi."),
    B("r3", "1068 yılının ilk gününde Evdokia, Romen Diyojen ile evlendi ve Romen imparator oldu. Ancak bu evlilik, "
            "sarayın en güçlü ailesi olan Dukasları çok kızdırmıştı. Özellikle Kaysar Yuhanna Dukas, yeni "
            "imparatoru bir gaspçı olarak görüyordu."),
    B("r4", "Romen, tahta çıkar çıkmaz doğuya seferler düzenledi. 1068'de Suriye'de Menbiç'i geri aldı. Ama Türkmen "
            "akıncıları her seferinde dağılıp başka bir yerden yeniden ortaya çıkıyordu."),
    B("r5", "Romen artık şuna inanıyordu: Bu sorunu çözmenin tek yolu, Selçuklu sultanını büyük bir meydan "
            "savaşında yenmekti. Ve bunun için, imparatorluğun toplayabildiği en büyük orduyu kuracaktı.",
      ek_sure=0.5),
    # =============================================================== 6 SEFER
    B("r5b", "Romen, ordusunu yeniden düzenlemek için büyük çaba harcadı. Dağınık birlikleri topladı, yeni askerler "
             "kaydetti ve paralı askerlerle ordusunu güçlendirdi. Ama zaman kısaydı ve bu yeni ordu, uyum içinde "
             "savaşmayı henüz öğrenmemişti.", ek_sure=0.5),
    B("k1", "1071 yılının baharında iki hükümdar da harekete geçti. Alparslan, bir yıl önce yol üzerindeki "
            "Malazgirt ve Erciş kalelerini almış, ardından güneye inerek Urfa'yı kuşatmıştı. Şimdi ise Halep "
            "önlerindeydi ve Fatımilere karşı sefere hazırlanıyordu.", bolum="1071 Seferi"),
    B("k2", "Tam bu sırada, Mart ayında, Romen Diyojen de devasa bir orduyla Konstantinopolis'ten yola çıktı. "
            "Bizans ordusu Anadolu'yu boydan boya geçti. Önce Sivas'a, Haziran'da da Erzurum'a ulaştı."),
    B("k2b", "Romen'in yolu, bir yıl önce bir Bizans ordusunun Türklere yenildiği Sivas'tan geçiyordu. Orada General "
             "Manuel Komnenos mağlup olmuş ve esir düşmüştü."),
    B("k3", "Ordunun ağırlık kervanı o kadar büyüktü ki, yol boyunca yavaş ilerliyordu. Bu arada Frank paralı "
            "askerleri yerel halkı yağmalayınca, Romen onların bir kısmını cezalandırıp ordudan gönderdi."),
    B("k4", "Bizans ordusunun yola çıktığı haberi Halep'teki Alparslan'a ulaştığında, sultan büyük bir karar verdi. "
            "Mısır seferini bıraktı ve hızla kuzeye döndü. Yol boyunca Halep ve Musul'dan gelen süvarileri ve "
            "müttefik Kürt birliklerini topladı."),
    B("k4b", "Alparslan'ın kuzeye dönüşü kolay olmadı. Ordusunun bir kısmı, ani dönüş kararıyla dağıldı. Sultan, "
             "seçkin birlikleriyle hızla ilerlerken, Azerbaycan ve Doğu Anadolu'daki Türkmen beylerine haber salarak "
             "onları da yanına çağırdı."),
    B("k5", "Alparslan'ın casusları Bizans ordusunun her adımını biliyordu. Romen ise, sultanın nerede olduğundan "
            "habersizdi."),
    B("k6", "Romen Diyojen, Erzurum'dan sonra kritik bir karar aldı ve ordusunu ikiye böldü. Generali Yusuf "
            "Tarkaniyotis'i; Varang, Peçenek ve Frank birlikleriyle Ahlat'a gönderdi. Kendisi ise geri kalan "
            "kuvvetlerle Malazgirt'e yürüdü."),
    B("k7", "23 Ağustos'ta Malazgirt'teki küçük Selçuklu garnizonu fazla direnemedi ve kale teslim oldu. Romen bu "
            "ilk başarıyla moral buldu."),
    B("k8", "Ancak Ahlat'a giden ordudan bir daha haber alınamayacaktı. Bu kuvvetler, savaşa hiç katılmadan "
            "bölgeden çekildi. Bizanslı tarihçi Attaleiates, Tarkaniyotis'in kaçtığını ima eder. Nedeni ne olursa "
            "olsun, Romen ordusunun neredeyse yarısını savaştan önce kaybetmişti.", ek_sure=0.5),
    # =============================================================== 7 ORDULAR
    B("o1", "Peki, Malazgirt'te karşı karşıya gelecek ordular nasıldı? Önce rakamlara bakalım. Ortaçağ kaynakları, "
            "Bizans ordusunun iki yüz bin, hatta bir milyon olduğunu yazar. Ancak modern tarihçiler bu sayıları "
            "abartılı bulur.", bolum="İki Ordu"),
    B("o1b", "Bu abartının bir nedeni vardı. Ortaçağ yazarları, zaferi ya da yenilgiyi daha etkileyici göstermek "
             "için rakamları büyütmeyi severdi. Bir milyonluk bir ordu, o dönemin yollarında ne yürüyebilir ne de "
             "beslenebilirdi."),
    B("o2", "Bugünkü tahminlere göre, sefere çıkan Bizans ordusu kırk bin ile yetmiş bin arasındaydı. Malazgirt'e "
            "ulaşan kısım ise bunun ancak yarısı kadardı."),
    B("o3", "Bu ordu rengârenk bir topluluktu. Zırhlı Bizans süvarileri, mızraklı piyadeler ve okçuların yanında; "
            "Ermeni birlikleri, Varang muhafızları, Frank ve Norman şövalyeleri, bozkır kökenli Uz ve Peçenek "
            "atlıları vardı."),
    B("o4", "Bu son grup çok önemliydi. Çünkü Uzlar da, tıpkı Selçuklular gibi, Oğuz kökenli Türklerdi. "
            "Karşılarında kendi soydaşlarını bulacaklardı."),
    B("o5", "Selçuklu ordusu ise daha küçüktü. Modern tahminler yirmi bin ile otuz bin arasında değişiyor. Ama bu "
            "ordunun büyük kısmı, bozkırın en korkulan silahından oluşuyordu: Atlı okçular."),
    B("o6", "Hafif zırhlı, son derece hızlı ve at üstündeyken her yöne ok atabilen savaşçılar. Düşmana yaklaşır, ok "
            "yağdırır, sonra hızla uzaklaşırlardı. Geri çekilirken bile dönüp ok atabiliyorlardı. Bunların yanında, "
            "sultanın seçkin muhafız süvarileri olan gulamlar bulunuyordu."),
    B("o7", "İki ordu, tamamen farklı iki savaş anlayışını temsil ediyordu. Bizans, sıkı düzen ve göğüs göğüse "
            "çarpışmaya güveniyordu. Selçuklular ise hız, hareket ve sabırla düşmanı yıpratmaya. Malazgirt, bu iki "
            "anlayışın sınavı olacaktı.", ek_sure=0.5),
    # =============================================================== 8 SAVAŞTAN ÖNCE
    B("p1", "24 Ağustos'ta, yiyecek toplamaya çıkan Bizans birlikleri, ovada Selçuklu ana kuvvetleriyle "
            "karşılaştı. Romen, Ermeni general Nikeforos Vasilakis'i süvarilerle yardıma gönderdi. Ama Vasilakis'in "
            "birliği pusuya düştü ve kendisi esir alındı.", bolum="Savaştan Önce"),
    B("p2", "Ardından gönderilen Briyennios da kuşatılmaktan son anda kurtuldu. Selçuklular geceyi yakındaki "
            "tepelerde geçirdi. Romen, karşısındakinin sıradan bir akıncı birliği değil, bizzat sultanın ordusu "
            "olduğunu ancak şimdi anlıyordu."),
    B("p3", "25 Ağustos'ta ise kötü bir haber geldi. Bizans ordusundaki Uz ve Peçenek atlılarının bir kısmı, gece "
            "karanlığında soydaşlarının safına geçti."),
    B("p4", "Aynı gün Alparslan, imparatora bir elçi gönderdi ve barış teklif etti. Bazı tarihçilere göre sultan, "
            "Fatımi seferine dönmek istiyordu. Ama Romen teklifi reddetti. Bu kadar büyük bir orduyu buraya kadar "
            "getirmişti. Kesin bir zafer olmadan geri dönmek, onun için siyasi bir intihar olurdu."),
    B("p4b", "Bizans karargâhında da tartışmalar vardı. Bazı komutanlar, barış teklifinin bir oyalama taktiği "
             "olduğunu düşünüyordu. Onlara göre sultan, takviye kuvvetler gelene kadar zaman kazanmaya "
             "çalışıyordu."),
    B("p5", "26 Ağustos 1071, bir Cuma günüydü. Rivayete göre Alparslan, o sabah askerleriyle birlikte Cuma namazını "
            "kıldı. Sonra beyaz bir elbise giydi ve atının kuyruğunu kendi eliyle bağladı. Ardından askerlerine "
            "döndü ve şöyle seslendi."),
    B("p6", "Eğer şehit düşersem, bu beyaz elbise kefenim olsun. Benimle gelmek isteyen gelsin, dönmek isteyen "
            "dönsün. Bugün burada ne emir veren bir sultan var, ne de emir alan bir asker. Ben de sizden biriyim.",
      ek_sure=1.0),
    B("p7", "Savaşa bizzat katılan Bizanslı tarihçi Mihail Attaleiates, o sabah Bizans ordusunun güçlü ve kendinden "
            "emin göründüğünü yazar. Ama Romen'in ordusunda sessiz bir tehlike vardı. Arka saflarda, imparatorun "
            "düşmanı Dukas ailesinden bir komutan bekliyordu: Andronikos Dukas."),
    # =============================================================== 9 MUHAREBE
    B("m1", "Bizans ordusu sabah saatlerinde savaş düzenine girdi. Romen Diyojen merkezde, bizzat birliklerinin "
            "başındaydı. Sol kanadı Nikeforos Briyennios, sağ kanadı Teodor Alyates yönetiyordu.",
      bolum="Malazgirt Muharebesi"),
    B("m2", "Arkada ise ihtiyat kuvvetleriyle Andronikos Dukas bekliyordu. Bu birlik, bir şeyler ters giderse "
            "ordunun geri çekilmesini koruyacaktı."),
    B("m3", "Alparslan ise ordusunu yaklaşık dört kilometre ötede, hilal biçiminde yaydı. Atlı okçular öndeydi. "
            "Ana kuvvetler ise tepelerin ardında, görünmeden bekliyordu."),
    B("m4", "Bizans ordusu ilerlemeye başladı. Selçuklu atlı okçuları yaklaşıyor, ok yağdırıyor, sonra göğüs "
            "göğüse çarpışmaya girmeden geri çekiliyordu. Hilalin merkezi geriledikçe, kanatları Bizans ordusunu "
            "yandan sarmaya başladı."),
    B("m4b", "Ağustos güneşinin altında, ağır zırhlar içindeki Bizans askerleri ilerledikçe, oklar kalkanlara ve "
             "zırhlara çarpıyordu. Zırhlı süvariler okçuları yakalamak için ileri atıldıkça, onlar bir sis gibi "
             "dağılıp kayboluyordu."),
    B("m5", "Bu, bozkırın asırlık taktiğiydi: Sahte ricat. Düşmanı peşinden sürükle, yor, dağıt ve doğru anda "
            "vur."),
    B("m6", "Öğleden sonra Bizanslılar Selçuklu kampına ulaştı. Ama kamp boştu. Atlı okçular sürekli ok atıyor, "
            "Bizans süvarileri onları yakalamaya çalıştıkça daha da uzaklaşıyorlardı.", ek_sure=0.5),
    B("m7", "Güneş batmaya yaklaşırken Bizans hatları uzamış, askerler susuz ve yorgun düşmüştü. Romen Diyojen, "
            "karanlıkta savunmasız kalmaktan korkarak ordusuna kampa dönme emri verdi. İmparatorluk sancağı geri "
            "döndü."),
    B("m8", "Ama bu emir, cephenin uzak kanatlarında yanlış anlaşıldı. Sağ kanattaki birlikler, imparatorun "
            "yenildiğini sanarak dağınık bir şekilde geri çekilmeye başladı."),
    B("m9", "Tam bu sırada, arka saflardaki Andronikos Dukas, geri çekilişi koruma emrini hiçe saydı. İmparatorun "
            "öldüğü söylentisini yaydı ve ihtiyat kuvvetleriyle birlikte Malazgirt'teki karargâha doğru savaş "
            "alanını terk etti.", ek_sure=1.0),
    B("m10", "İşte Alparslan'ın beklediği an buydu. Selçuklu kuvvetleri tepelerden inip iki yandan saldırdı. Sağ "
             "kanat bozguna uğradı. Sol kanattaki Briyennios ise ağır kayıplar vererek geri çekildi."),
    B("m11", "Romen Diyojen, merkezdeki birlikleri ve Varang muhafızlarıyla birlikte kuşatıldı. Kaçmayı reddetti ve "
             "sonuna kadar savaştı. Atı öldürüldü, elinden yaralandı. Ve sonunda, bir Bizans imparatoru savaş "
             "meydanında esir düştü.", ek_sure=1.5),
    B("m12", "Takip bütün gece sürdü. Sabah olduğunda, Bizans'ın profesyonel ordusunun çekirdeği yok olmuştu. "
             "Kayıplar konusunda kaynaklar farklı rakamlar verir. Ama asıl kayıp, kaybedilen askerlerden çok daha "
             "büyüktü: Bizans'ın prestiji.", ek_sure=1.0),
    # =============================================================== 10 ESİR
    B("m12b", "Bizans tarihçileri bu günü, imparatorluğun başına gelen en büyük felaketlerden biri olarak andı. "
              "Savaşın tanığı Attaleiates, gördüklerini derin bir yasla anlatır.", ek_sure=0.5),
    B("e1", "Ertesi gün yaralı imparator, Alparslan'ın huzuruna getirildi. Sultan başta, karşısındaki tozlu ve "
            "yorgun askerin imparator olduğuna inanmadı. Ancak esir Bizanslılar ve Vasilakis onu tanıyınca gerçek "
            "ortaya çıktı.", bolum="Esir İmparator"),
    B("e2", "Kaynaklara göre Alparslan, eski bir zafer geleneğine uyarak ayağını önce imparatorun boynuna koydu. "
            "Ama sonra onu yerden kaldırdı ve aralarında şöyle bir konuşma geçti."),
    B("e3", "Alparslan sordu: Eğer ben senin önüne esir olarak getirilseydim, ne yapardın?", ek_sure=0.8),
    B("e4", "Romen dürüstçe cevap verdi: Belki seni öldürürdüm. Belki de Konstantinopolis sokaklarında teşhir "
            "ederdim.", ek_sure=0.8),
    B("e5", "Alparslan'ın cevabı tarihe geçti: Benim cezam bundan çok daha ağır. Seni affediyor ve serbest "
            "bırakıyorum.", ek_sure=1.5),
    B("e6", "Alparslan, imparatora bir hafta boyunca büyük bir saygıyla davrandı ve onu kendi sofrasına oturttu. "
            "Fidye için önce on milyon altın istedi. Romen bunun çok fazla olduğunu söyleyince, bir buçuk milyon "
            "altın peşin ve her yıl üç yüz altmış bin altın üzerinde anlaşıldı."),
    B("e6b", "Bu davranış, hem Müslüman hem de Hristiyan kaynaklarda, Alparslan'ın cömertliğinin ve bilgeliğinin "
             "bir göstergesi olarak anlatılır."),
    B("e7", "Antlaşmaya göre Müslüman esirler serbest bırakılacak, Alparslan'ın oğlu ile Romen'in kızı "
            "evlenecekti. Bazı kaynaklar, Antakya, Urfa, Menbiç ve Malazgirt'in de Selçuklulara bırakılacağını "
            "yazar. Bir hafta sonra Romen Diyojen, iki emir ve yüz kişilik bir muhafız birliği eşliğinde ülkesine "
            "uğurlandı.", ek_sure=0.5),
    # =============================================================== 11 SONUÇLAR
    B("n1", "Ancak Romen'i Konstantinopolis'te bir zafer kutlaması beklemiyordu. Dukaslar, imparatorun esir "
            "düştüğünü duyar duymaz sarayda darbe yapmış ve Evdokia'nın oğlu Mihail Dukas'ı tahta çıkarmışlardı.",
      bolum="Sonuçlar"),
    B("n2", "Romen tahtını geri almak için savaştı, ama Dukas kuvvetlerine yenildi. Canının bağışlanacağına dair söz "
            "verilerek teslim oldu. Fakat bu söz tutulmadı. 1072 yazında gözlerine mil çekildi ve Kınalıada'ya "
            "sürgün edildi. Kısa süre sonra, aldığı yaraların etkisiyle öldü."),
    B("n3", "Rivayete göre Alparslan, imparatorun başına gelenleri duyunca çok öfkelendi ve antlaşmanın artık "
            "geçerli olmadığını ilan etti. Ama Alparslan da uzun yaşamadı. 1072 sonbaharında, Orta Asya'daki bir "
            "sefer sırasında, esir alınan bir kale komutanı tarafından hançerlenerek öldürüldü. Yerine oğlu Melikşah "
            "geçti."),
    B("n4", "Malazgirt'ten sonra Bizans'ın doğu sınırı fiilen çöktü. Yıllarca süren iç savaşlar, Türkmen boylarının "
            "Anadolu'ya akın akın gelmesinin önünü açtı. Sadece birkaç yıl içinde Türkler, Anadolu'nun içlerine, "
            "hatta Ege kıyılarına kadar ulaştı."),
    B("n5", "Kutalmışoğlu Süleyman Şah, 1075 civarında İznik'i ele geçirdi ve burayı başkent yaptı. Böylece Anadolu "
            "Selçuklu Devleti kuruldu. Konstantinopolis'in hemen karşısında, bir Türk devleti yükseliyordu."),
    # =============================================================== 11b BEYLİKLER
    B("t1", "Malazgirt'in ardından Anadolu'da sadece Selçuklular değil, birçok Türk beyliği kuruldu. Bunlara bugün "
            "ilk Türk beylikleri diyoruz.", bolum="Anadolu'nun Yeni Yüzü"),
    B("t2", "Sivas, Tokat ve Kayseri çevresinde Danişmendliler, Erzurum'da Saltuklular, Erzincan ve Divriği'de "
            "Mengücekliler hüküm sürdü. Biraz daha sonra, Mardin ve Hasankeyf çevresinde Artuklular ortaya çıktı."),
    B("t3", "Bu beylikler kendi aralarında rekabet etse de, Anadolu'ya kalıcı bir Türk kimliği kazandırdı. Camiler, "
            "kervansaraylar, köprüler ve medreseler inşa edildi. Göçebe Türkmenler zamanla şehirlere ve köylere "
            "yerleşti."),
    B("t4", "Ama bu dönüşüm bir anda olmadı. Bizans, Anadolu'nun kıyılarını ve batısını uzun süre elinde tuttu. "
            "Ve çok geçmeden, Batı'dan gelen yeni bir güç sahneye çıkacaktı.", ek_sure=0.5),
    B("n6", "Çaresiz kalan Bizans, Batı'dan yardım istedi. 1081'de tahta çıkan Aleksios Komnenos, Papa'ya elçiler "
            "gönderdi. 1095 yılında Papa İkinci Urbanus, Clermont'ta Haçlı Seferi çağrısını yaptı.",
      bolum="Haçlı Seferlerine Giden Yol"),
    B("n7", "Yani Malazgirt'in yankıları, Avrupa'dan Kudüs'e uzanan, iki yüz yıllık bir çatışma döneminin de "
            "başlangıcı oldu.", ek_sure=1.0),
    # =============================================================== 12 KAPANIŞ
    B("x1", "Malazgirt, bugün Türk tarihinin en önemli dönüm noktalarından biri olarak anılıyor. Öyle ki, sekiz yüz "
            "elli bir yıl sonra, 26 Ağustos 1922'de başlayan Büyük Taarruz da aynı güne denk geliyordu.",
      bolum="Kapanış"),
    B("x2", "Bir Ağustos günü başlayan bu hikâye, Anadolu'yu yurt edinen bir milletin hikâyesine dönüştü."),
    B("x3", "Bir sonraki büyük savaşta görüşmek üzere.", ek_sure=3.0),
]

# ---------------------------------------------------------------- kişiler (otomatik portre)
KISILER = {
    "Alparslan": dict(ad="Alparslan", unvan="Büyük Selçuklu Sultanı", yillar="1064 – 1072", taraf="selcuklu",
                      kultur="selcuklu"),
    "Romen": dict(ad="Romen Diyojen", unvan="Bizans İmparatoru", yillar="1068 – 1071", taraf="bizans",
                  kultur="bizans"),
    "Selçuk Bey": dict(ad="Selçuk Bey", unvan="Kınık Boyu Beyi", yillar="10. yüzyıl", taraf="selcuklu",
                       kultur="selcuklu"),
    "Tuğrul": dict(ad="Tuğrul Bey", unvan="Büyük Selçuklu Sultanı", yillar="1040 – 1063", taraf="selcuklu",
                   gorsel="tugrul", kirp=None, kultur="selcuklu"),
    "Çağrı": dict(ad="Çağrı Bey", unvan="Horasan Meliki", yillar="ö. 1060", taraf="selcuklu", kultur="selcuklu"),
    "Mesud": dict(ad="Gazneli Mesud", unvan="Gazneli Sultanı", yillar="1030 – 1040", taraf="gazneli",
                  kultur="selcuklu", konum="sag"),
    "Basileios": dict(ad="II. Basileios", unvan="Bizans İmparatoru", yillar="976 – 1025", taraf="bizans",
                      gorsel="basileios2", kirp=None, kultur="bizans"),
    "Nizamülmülk": dict(ad="Nizamülmülk", unvan="Selçuklu Veziri", yillar="1018 – 1092", taraf="selcuklu",
                        kultur="selcuklu"),
    "Konstantin": dict(ad="X. Konstantin Dukas", unvan="Bizans İmparatoru", yillar="1059 – 1067", taraf="bizans",
                       gorsel="konstantin10", kirp=None, kultur="bizans"),
    "Evdokia": dict(ad="Evdokia", unvan="Bizans İmparatoriçesi", yillar="ö. 1078 sonrası", taraf="bizans",
                    gorsel="evdokia", kirp=None, kultur="bizans", konum="sag"),
    "Yuhanna": dict(ad="Yuhanna Dukas", unvan="Kaysar", yillar="Dukas ailesi", taraf="bizans", kultur="bizans",
                    konum="sag"),
    "Tarkaniyotis": dict(ad="Yusuf Tarkaniyotis", unvan="Bizans Generali", yillar="1071", taraf="bizans",
                         kultur="bati"),
    "Attaleiates": dict(ad="Mihail Attaleiates", unvan="Bizanslı Tarihçi", yillar="Savaşın tanığı", taraf="notr",
                        kultur="bati", konum="sag"),
    "Vasilakis": dict(ad="Nikeforos Vasilakis", unvan="Bizans Generali", yillar="1071", taraf="bizans",
                      kultur="bati"),
    "Briyennios": dict(ad="Nikeforos Briyennios", unvan="Sol Kanat Komutanı", yillar="1071", taraf="bizans",
                       kultur="bati"),
    "Alyates": dict(ad="Teodor Alyates", unvan="Sağ Kanat Komutanı", yillar="1071", taraf="bizans", kultur="bati",
                    konum="sag"),
    "Andronikos": dict(ad="Andronikos Dukas", unvan="İhtiyat Komutanı", yillar="1071", taraf="bizans",
                       kultur="bati", konum="sag"),
    "Mihail Dukas": dict(ad="VII. Mihail Dukas", unvan="Bizans İmparatoru", yillar="1071 – 1078", taraf="bizans",
                         gorsel="mihail7", kirp=None, kultur="bizans", konum="sag"),
    "Melikşah": dict(ad="Melikşah", unvan="Büyük Selçuklu Sultanı", yillar="1072 – 1092", taraf="selcuklu",
                     gorsel="meliksah", kirp=None, kultur="selcuklu"),
    "Süleyman Şah": dict(ad="Süleyman Şah", unvan="Anadolu Selçuklu Kurucusu", yillar="ö. 1086", taraf="selcuklu",
                         kultur="selcuklu"),
    "Aleksios": dict(ad="Aleksios Komnenos", unvan="Bizans İmparatoru", yillar="1081 – 1118", taraf="bizans",
                     gorsel="aleksios", kirp=None, kultur="bizans", konum="sag"),
    "Urbanus": dict(ad="II. Urbanus", unvan="Papa", yillar="1088 – 1099", taraf="hacli", gorsel="clermont",
                    kirp=None, kultur="bati"),
}

KOORD = {
    "İstanbul": (28.98, 41.01), "Konstantinopolis": (28.98, 41.01), "Malazgirt": (42.54, 39.14),
    "Ahlat": (42.49, 38.75), "Erzurum": (41.27, 39.9), "Sivas": (37.02, 39.75), "Kayseri": (35.48, 38.72),
    "Ankara": (32.86, 39.93), "İzmit": (29.92, 40.77), "Ani": (43.57, 40.5), "Urfa": (38.79, 37.16),
    "Halep": (37.15, 36.2), "Musul": (43.13, 36.34), "Hoy": (44.95, 38.55), "Erciş": (43.36, 39.03),
    "Malatya": (38.31, 38.35), "Bağdat": (44.37, 33.31), "Kahire": (31.24, 30.04), "Cend": (65.6, 44.8),
    "Buhara": (64.42, 39.77), "Merv": (61.83, 37.6), "Dandanakan": (62.2, 37.1), "Rey": (51.43, 35.59),
    "İsfahan": (51.67, 32.65), "Nişabur": (58.8, 36.2), "Pasinler": (41.68, 39.98), "İznik": (29.72, 40.43),
    "Menbiç": (37.95, 36.53), "Antakya": (36.16, 36.2), "Kudüs": (35.21, 31.77), "Gazne": (68.42, 33.55),
    "Bari": (16.87, 41.12), "Clermont": (3.08, 45.78), "Kınalıada": (29.05, 40.91),
}
# otomatik şehir vurgusu (harita sahnelerinde anlatıcı söylediğinde)
OTO_YERLER = {k: v for k, v in KOORD.items() if k not in ("İstanbul", "Clermont")}

_DENIZ = [(34.5, 43.2, "Karadeniz", 34, "deniz"), (31.0, 34.2, "Akdeniz", 34, "deniz"),
          (50.6, 40.8, "Hazar Denizi", 30, "deniz")]
ANADOLU = Harita(25.5, 47.5, 38.6, etiketler=_DENIZ + [(33.5, 39.0, "Anadolu", 34, "bolge")], tohum=21,
                 dag_olcek=1.4)
DOGU = Harita(37.5, 47.5, 38.9, etiketler=[(43.2, 38.5, "Van Gölü", 26, "deniz")], tohum=25, dag_olcek=2.2)
ORTA = Harita(23.0, 58.0, 35.6, etiketler=_DENIZ + [(52.5, 33.5, "İran", 30, "bolge"),
                                                     (29.5, 26.8, "Mısır", 30, "bolge")], tohum=22)
GENIS = Harita(19.0, 73.0, 36.5, etiketler=_DENIZ + [(52.5, 32.0, "İran", 30, "bolge"),
                                                      (61.5, 35.0, "Horasan", 26, "bolge"),
                                                      (66.0, 41.5, "Maveraünnehir", 24, "bolge"),
                                                      (68.0, 46.2, "Oğuz Bozkırları", 24, "bolge")],
               tohum=23, dag_olcek=0.8)
AVRUPA = Harita(-6.0, 46.0, 44.0, etiketler=[(18.0, 35.5, "Akdeniz", 32, "deniz"), (34.5, 43.2, "Karadeniz", 30, "deniz")],
                tohum=26, dag_olcek=0.8)
BATI = Harita(11.0, 50.0, 39.6, etiketler=_DENIZ + [(26.0, 46.2, "Peçenek Bozkırları", 24, "bolge"),
                                                     (14.5, 43.5, "İtalya", 26, "bolge")], tohum=24)

BIZANS_1025 = [(19.3, 42.3), (19.5, 44.6), (22.5, 44.7), (25, 43.7), (28.0, 44.2), (29.7, 45.3), (31, 45),
               (31, 42.5), (36, 42.5), (41.5, 41.6), (43.5, 41.4), (44.6, 40.9), (44.5, 39.5), (43.5, 38.7),
               (42, 37.9), (40.5, 37.4), (39.5, 36.8), (38.0, 36.2), (36.6, 35.6), (35.6, 35.2), (34.6, 34.4),
               (32, 34.4), (26, 34.7), (22.5, 36.2), (20, 38.3), (19.2, 40.4)]
BIZANS_ITALYA = [(15.0, 41.9), (16.2, 41.9), (18.8, 40.3), (17.0, 38.6), (16.0, 37.8), (15.5, 38.3), (15.0, 40.0)]
BIZANS_1071 = [(19.3, 42.3), (19.5, 44.6), (22.5, 44.7), (25, 43.7), (28.0, 44.2), (29.7, 45.3), (31, 45),
               (31, 42.5), (36, 42.5), (41.5, 41.6), (42.5, 41.2), (42.6, 40.2), (42.0, 39.4), (41.2, 38.6),
               (40.2, 37.8), (39.5, 36.8), (38.0, 36.2), (36.6, 35.6), (35.6, 35.2), (34.6, 34.4), (32, 34.4),
               (26, 34.7), (22.5, 36.2), (20, 38.3), (19.2, 40.4)]
BIZANS_1080 = [(19.3, 42.3), (19.5, 44.6), (22.5, 44.7), (25, 43.7), (28.0, 44.2), (29.7, 45.3), (31, 45),
               (30.2, 41.3), (29.6, 40.9), (28.6, 40.4), (27.4, 40.4), (26.6, 39.6), (26.2, 37.8), (25.5, 36.8),
               (22.5, 36.2), (20, 38.3), (19.2, 40.4)]
BIZANS_KARADENIZ = [(31.5, 41.6), (36, 42.3), (41.6, 41.7), (41.4, 40.85), (36, 41.0), (31.5, 41.0)]
SELCUKLU_1040 = [(56, 38.6), (60, 39.8), (63.5, 39.2), (64, 36.5), (62, 34.5), (58.5, 34.5), (56, 35.5)]
SELCUKLU_1055 = [(44.5, 39.5), (48.5, 39.8), (53, 38.8), (56, 39.8), (60.5, 40.5), (64, 39.8), (65.5, 37.5),
                 (63.5, 34.5), (61, 31), (58, 27), (52, 27.8), (48.3, 30), (46.5, 31.5), (44.3, 33.2),
                 (42.5, 34.3), (41.5, 35.5), (42.8, 37.2), (44.2, 37.8)]
SELCUKLU_1071 = [(42.6, 41.4), (44.6, 41.6), (46.5, 41.9), (49.5, 41.6), (50, 40), (54, 38), (56, 39.5),
                 (60, 40.5), (63, 40.5), (66, 39), (67, 37.3), (65, 35), (62, 32), (61, 29), (58, 26), (52, 27.5),
                 (48.5, 30), (46.5, 31.5), (44.5, 33), (42.8, 34.2), (41, 34.6), (39.6, 36.0), (40.2, 37.8),
                 (41.2, 38.6), (42.0, 39.4), (42.6, 40.2), (42.5, 41.2)]
GAZNELI = [(56, 38), (61, 38.8), (66, 37.6), (71, 37.2), (72.5, 34.5), (71, 30.5), (67, 27.5), (62, 26),
           (58, 27.5), (56.5, 31), (55.5, 34.5)]
FATIMI = [(25, 31.8), (29, 31.2), (32, 31.3), (34.3, 31.3), (35, 32.8), (35.7, 34.3), (36.5, 34.2), (36.6, 33.2),
          (36.3, 31.5), (35.2, 29.5), (34.6, 28.2), (33.5, 27.8), (35.5, 24), (36.5, 22), (25, 22)]
TURKIYE_SELCUKLU = [(29.5, 40.8), (31, 40.6), (33, 40.9), (36, 40.9), (39, 40.3), (41, 40), (42.6, 40.2),
                    (42.0, 39.4), (41.2, 38.6), (40.2, 37.8), (37.5, 37.6), (35, 37.2), (33, 37.0), (31, 37.4),
                    (29.8, 38.2), (29.2, 39.5)]


# ================================================================= KURGU
def kur(v, T):
    ids = [b["id"] for b in BOLUMLER]
    s = {k: a for k, (a, b) in T.items()}
    e = {k: b for k, (a, b) in T.items()}
    K = T.kelime

    def aralik(ilk, son):
        t0 = 0.0 if ilk == ids[0] else s[ilk] - 0.4
        j = ids.index(son) + 1
        return t0, (s[ids[j]] - 0.4 if j < len(ids) else 1e9)

    def hsahne(ilk, son, h):
        return v.sahne(*aralik(ilk, son), h.yuzey, harita=h)

    def P(h, yer):
        return h.proj(*(KOORD[yer] if isinstance(yer, str) else yer))

    def kam(sc, h, t, yer, zoom, sure=2.5):
        x, y = P(h, yer)
        sc.kamera_git(t, t + sure, x=x, y=y, zoom=zoom)

    def kamA(sc, h, t, yer, zoom):
        x, y = P(h, yer)
        sc.kamera_ayarla(t, x=x, y=y, zoom=zoom)

    def ikon(sc, h, tur, yer, t, sure=4.5, olcek=1.0):
        sc.ekle(Ikon(tur, *P(h, yer), t, t + sure, olcek=olcek))

    def kafile(sc, h, taraf, yol, t0, sure, adet=6, tur="atli", ok=False, t_son=None, olcek=1.0, tohum=0):
        sc.ekle(Kafile(taraf, [P(h, y) for y in yol], t0, t0 + sure, tur=tur, adet=adet, ok=ok,
                       t_son=t_son, olcek=olcek, tohum=tohum))

    def balon(sc, h, metin, yer, t0, t1, renk=(0.98, 0.93, 0.8), dy=-60):
        x, y = P(h, yer)
        sc.ekle(EtiketBalonu(metin, t0, t1, x=x, y=y + dy, renk=renk))

    def sehir(sc, h, ad, t0, t1=1e9, **k):
        lon, lat = KOORD[ad]
        sc.ekle(Sehir(h, lon, lat, ad, t0, t1, **k))

    def tablo(ilk, son, anahtar, bas, son_, kaynak, kirp=None, yedek=None):
        from motor.katmanlar import gorsel_yukle
        if gorsel_yukle(anahtar, kirp) is None and yedek is not None:
            return yedek(ilk, son)
        sc = v.sahne(*aralik(ilk, son), KOYU, nefes=False)
        sc.ekle(Tablo(anahtar, s[ilk] - 0.4, e[son] + 0.4, bas, son_, kaynak, kirp))
        return sc

    KOYU = koyu_arka_plan(ANADOLU)
    v.acilis(0, 1.5)
    for b in BOLUMLER:
        if b.get("bolum") and b["id"] not in ("g1", "x1"):
            v.ekran(BolumEtiketi(b["bolum"], s[b["id"]] + 0.3, s[b["id"]] + 6.0))

    # ============================================================ 1 GİRİŞ
    h = ANADOLU
    sc = hsahne("g1", "g2", h)
    kamA(sc, h, 0, (36.5, 38.6), 1.0)
    kam(sc, h, 1.0, (42.3, 39.0), 2.6, sure=5)
    sc.ekle(Bolge(h, "bizans", BIZANS_1071, K("g2", "Bizans"), ad="Bizans", etiket_konum=(33.0, 39.6)),
            Bolge(h, "selcuklu", SELCUKLU_1071, K("g2", "Büyük"), ad="Büyük Selçuklu", etiket_konum=(45.8, 36.0)))
    sehir(sc, h, "Malazgirt", K("g1", "Malazgirt"), onemli=True, nabiz=True, yon="ust")
    sehir(sc, h, "Ahlat", K("g1", "Ahlat"), onemli=True, yon="sol")
    kafile(sc, h, "bizans", [(42.3, 39.5), (42.45, 39.1)], K("g1", "geniş") - 0.5, 3.5, adet=8, tur="piyade",
           olcek=0.9, t_son=e["g1"] + 0.5, tohum=1)
    kafile(sc, h, "selcuklu", [(42.9, 38.55), (42.6, 38.95)], K("g1", "geniş") - 0.2, 3.5, adet=8, olcek=0.9,
           t_son=e["g1"] + 0.5, tohum=2)
    kam(sc, h, K("g2", "Bizans") - 0.5, (33.0, 39.3), 1.25)
    kafile(sc, h, "bizans", ["İstanbul", "Ankara", (35.5, 39.4)], K("g2", "Bizans"), 6, adet=6, tur="piyade",
           olcek=1.2, t_son=e["g2"])
    kam(sc, h, K("g2", "Diğer") - 0.3, (42.5, 37.8), 1.4)
    kafile(sc, h, "selcuklu", [(46.5, 37.0), (44.0, 37.6), (42.8, 38.4)], K("g2", "Diğer"), 5, adet=8,
           olcek=1.2, t_son=e["g2"] + 0.5, tohum=3)

    tablo("g3", "g3", "malazgirt_minyatur1", (0.5, 0.45, 1.0), (0.45, 0.55, 1.35),
          "Malazgirt Savaşı — 15. yüzyıl Fransız minyatürü (kamu malı)")
    sc = v.sahne(*aralik("g4", "g4"), KOYU)
    sc.ekle(BuyukYazi("MALAZGİRT", s["g4"] + 0.4, e["g4"] + 0.4, ust="Büyük Savaşlar", alt="26 Ağustos 1071",
                      boyut=170))
    sc.ekle(Kafile("selcuklu", [(-100, 860), (2050, 860)], s["g4"], e["g4"] + 0.4, adet=12, olcek=1.8, tohum=5),
            Kafile("bizans", [(2050, 960), (-100, 960)], s["g4"] + 1, e["g4"] + 0.4, tur="piyade", adet=12,
                   olcek=1.6, tohum=6))

    # ============================================================ 2 BOZKIR
    h = GENIS
    sc = hsahne("s1", "s9", h)
    kamA(sc, h, s["s1"] - 1, (62.0, 44.5), 1.6)
    kam(sc, h, K("s1", "Seyhun") - 0.5, (65.0, 44.5), 2.3)
    sehir(sc, h, "Cend", K("s1", "Kınık"), e["s2"] + 1, onemli=True, nabiz=True)
    kafile(sc, h, "selcuklu", [(69.5, 46.5), (67.5, 45.6), (66.0, 45.0)], K("s1", "Oğuz"), 6, adet=7, olcek=1.1)
    kafile(sc, h, "notr", [(70.5, 44.0), (68.5, 43.6), (67.0, 44.0)], K("s1b", "Oğuz"), 5, adet=6, olcek=1.0,
           tohum=2)
    balon(sc, h, "Oğuz Yabgu Devleti", (69.0, 43.0), K("s1b", "Oğuz"), K("s1b", "Ancak"))
    kafile(sc, h, "selcuklu", [(67.0, 44.6), (66.0, 44.9)], K("s1b", "ayrıldı") - 0.5, 3, adet=7, olcek=1.1,
           tohum=4)
    ikon(sc, h, "yildiz", "Cend", K("s2", "İslamiyet"), 4)
    kam(sc, h, s["s2b"], (62.5, 41.0), 1.3, sure=3)
    for i, (yol, t) in enumerate((([(66, 44.6), (64.4, 41.5)], K("s2b", "Karahanlılar")),
                                   ([(66, 44.6), (63.0, 40.5)], K("s2b", "Samaniler")),
                                   ([(66, 44.6), (62.0, 39.0)], K("s2b", "Gazneliler")))):
        kafile(sc, h, "selcuklu", yol, t, 3.5, adet=4, olcek=1.0, tohum=10 + i, t_son=e["s2b"])
    t = s["s3"]
    kam(sc, h, t, (63.5, 39.0), 1.6, sure=3)
    kafile(sc, h, "selcuklu", ["Cend", "Buhara", "Merv"], K("s3", "Horasan") - 1.5, 6, adet=10, ok=True,
           olcek=1.1, t_son=e["s5"])
    gaz = sc.ekle(Bolge(h, "gazneli", GAZNELI, K("s3", "Gaznelilerin"), ad="Gazneliler", etiket_konum=(66.5, 33.0)))
    sehir(sc, h, "Gazne", K("s3", "Gaznelilerin") + 0.5)
    kam(sc, h, s["s4"], (65.0, 35.5), 1.4)
    kafile(sc, h, "gazneli", ["Gazne", (64.0, 35.5), (62.6, 36.9)], K("s4", "ordu") - 1, 7, adet=9,
           tur="piyade", olcek=1.1, t_son=e["s5"], tohum=7)
    kafile(sc, h, "gazneli", [(68.0, 33.2), (64.5, 35.2), (62.8, 36.7)], K("s4", "fillerle"), 6, adet=6,
           olcek=1.1, t_son=e["s5"], tohum=8)
    kam(sc, h, s["s5"], (62.2, 37.2), 2.6)
    sehir(sc, h, "Dandanakan", K("s5", "Dandanakan"), e["s6"], onemli=True, nabiz=True, yon="alt")
    for i in range(3):  # Gazneli ordusunun etrafında dönen atlı okçular
        x0, y0 = 62.2, 37.1
        halka = [(x0 + 0.9 * __import__("math").cos(a / 6 * 6.283 + i * 2.1),
                  y0 + 0.6 * __import__("math").sin(a / 6 * 6.283 + i * 2.1)) for a in range(7)]
        kafile(sc, h, "selcuklu", halka, K("s5", "yıprattı") - 1, 7, adet=4, tur="atli_okcu", olcek=0.9,
               tohum=20 + i, t_son=e["s5"])
    balon(sc, h, "Susuz kalan ordu", (62.2, 37.1), K("s5", "Susuz"), e["s5"], renk=(1, 0.75, 0.6), dy=70)
    ikon(sc, h, "kilic", (62.2, 37.1), K("s5", "ağır"), 4)
    gaz.kaybol(K("s6", "Büyük"))
    sc.ekle(Bolge(h, "selcuklu", SELCUKLU_1040, K("s6", "Büyük"), s["s7"] + 4, ad="Selçuklu",
                  etiket_konum=(59.5, 37.2), etiket_boyut=26))
    ikon(sc, h, "tac", (59.6, 36.6), K("s6", "sultan"), 4)
    t = s["s7"]
    kam(sc, h, t, (54.0, 35.5), 1.2, sure=3)
    kafile(sc, h, "selcuklu", ["Merv", "Nişabur", "Rey", "İsfahan"], K("s7", "Nişabur") - 1, 6, adet=8,
           ok=True, olcek=1.0, t_son=e["s7"])
    sc.ekle(Bolge(h, "selcuklu", SELCUKLU_1055, K("s7", "İsfahan"), ad="Büyük Selçuklu", etiket_konum=(54.5, 33.0)))
    kafile(sc, h, "selcuklu", ["Rey", (48.0, 34.6), "Bağdat"], K("s7", "Bağdat") - 2, 3.5, adet=6, olcek=1.0,
           t_son=e["s7"], tohum=9)
    ikon(sc, h, "tac", "Bağdat", K("s7", "unvanını"), 4.5)
    t = s["s8"]
    kam(sc, h, t, (42.0, 38.8), 1.8, sure=3)
    sc.ekle(Bolge(h, "bizans", BIZANS_1025, t + 0.5, ad="Bizans", etiket_konum=(32.5, 39.2)))
    for i, (yol, d) in enumerate(((((47, 37.5), (39.5, 39.5)), 0), ((((46, 39.5), (40.5, 40.6))), 0.6),
                                   ((((45.5, 36.5), (38.5, 38.0))), 1.2))):
        kafile(sc, h, "selcuklu", list(yol), K("s8", "akıncıları") + d, 5, adet=5, ok=True, olcek=1.0,
               tohum=30 + i, t_son=e["s8"])
    kafile(sc, h, "selcuklu", [(44.5, 39.4), "Pasinler"], K("s8", "Pasinler") - 0.8, 2.5, adet=8, olcek=1.1,
           t_son=e["s9"], tohum=33)
    kafile(sc, h, "bizans", [(38.8, 40.3), (41.2, 40.0)], K("s8", "Pasinler") - 0.8, 2.5, adet=7, tur="piyade",
           olcek=1.1, t_son=K("s8", "zafer"), tohum=34)
    ikon(sc, h, "kilic", "Pasinler", K("s8", "savaş"), 5)
    kam(sc, h, K("s8", "Pasinler") - 0.6, "Pasinler", 3.0, sure=1.6)
    kam(sc, h, s["s9"], (36.0, 39.5), 1.2, sure=3.5)

    # ============================================================ 3 BİZANS
    h = BATI
    sc = hsahne("b1", "b1", h)
    kamA(sc, h, s["b1"] - 1, (30.5, 39.6), 1.0)
    sc.ekle(Bolge(h, "bizans", BIZANS_1025, K("b1", "imparatorluk"), ad="Bizans İmparatorluğu",
                  etiket_konum=(32.0, 39.3)),
            Bolge(h, "bizans", BIZANS_ITALYA, K("b1", "İtalya")))
    sehir(sc, h, "İstanbul", s["b1"] + 1, onemli=True, nabiz=True)
    kam(sc, h, K("b1", "İtalya") - 0.3, (17.0, 40.5), 1.8, sure=1.8)
    kam(sc, h, K("b1", "Kafkaslara") - 0.3, (42.5, 40.8), 1.8, sure=2.0)
    def basileios_yedek(ilk, son):
        hb = BATI
        sb = hsahne(ilk, son, hb)
        kamA(sb, hb, s[ilk] - 0.5, (25.5, 42.5), 2.0)
        sb.ekle(Bolge(hb, "bizans", BIZANS_1025, s[ilk] - 0.5, alfa=0.3))
        kafile(sb, hb, "bizans", [(28.6, 41.2), (26.5, 42.2), (24.5, 42.8)], s[ilk], 4, adet=12, tur="piyade",
               olcek=1.2, t_son=e[son] + 0.5, tohum=55)
        kafile(sb, hb, "bizans", [(28.4, 41.0), (26.2, 41.9), (24.3, 42.5)], s[ilk] + 0.4, 4, adet=8, olcek=1.2,
               t_son=e[son] + 0.5, tohum=56)
        kafile(sb, hb, "pecenek", [(22.5, 43.4), (24.0, 42.9)], s[ilk], 2.5, adet=8, tur="piyade", olcek=1.1,
               t_son=K(son, "Ordusu"), tohum=57)
        ikon(sb, hb, "kilic", (24.2, 42.8), K(son, "Bulgarları"), 4)
        balon(sb, hb, "“Bulgar Avcısı”", (24.6, 42.8), K(son, "Bulgar"), K(son, "Ordusu"), dy=-80)
        ikon(sb, hb, "tac", (28.98, 41.01), K(son, "Ordusu"), 3.5)
        ikon(sb, hb, "parsomen", (29.4, 40.7), K(son, "hazinesi"), 3.5)
        kam(sb, hb, K(son, "Ama"), (28.98, 41.01), 2.6, sure=2.5)
        balon(sb, hb, "Varis yok", (28.98, 41.01), K(son, "varis") - 0.5, e[son] + 0.3, renk=(1, 0.75, 0.6), dy=-80)
        return sb

    tablo("b2", "b2", "basileios2", (0.5, 0.35, 1.0), (0.5, 0.25, 1.3),
          "II. Basileios — Basileios Mezmurları, 11. yüzyıl (kamu malı)", yedek=basileios_yedek)
    sc = hsahne("b3", "b5", h)
    kamA(sc, h, s["b3"], (29.0, 41.0), 2.0)
    sc.ekle(Bolge(h, "bizans", BIZANS_1025, s["b3"] - 1, ad="Bizans", etiket_konum=(32.0, 39.3)))
    ikon(sc, h, "tac", (28.6, 41.2), K("b3", "taht"), 3.5)
    balon(sc, h, "Saray entrikaları", (29.0, 41.0), K("b3", "entrikaları"), K("b3", "Başkentteki"))
    ikon(sc, h, "parsomen", (29.3, 40.8), K("b3", "bürokratlar"), 3.5)
    kam(sc, h, K("b3", "Sınır") - 0.3, (41.0, 40.0), 2.0, sure=2.5)
    kafile(sc, h, "bizans", [(42.5, 40.4), (39.5, 40.2)], K("b3", "dağıtıldı") - 1.5, 4, adet=7, tur="piyade",
           olcek=1.1, t_son=K("b3", "dağıtıldı") + 3)
    balon(sc, h, "Sınır ordusu dağıtıldı", (41.5, 40.4), K("b3", "Kaynaklara"), e["b3"] + 0.3, renk=(1, 0.75, 0.6))
    t = s["b3b"]
    kam(sc, h, t, (32.0, 39.6), 1.4, sure=3)
    for i, yer in enumerate([(27.5, 39.0), (31.0, 38.5), (35.0, 39.4), (38.5, 39.0), (33.0, 40.5)]):
        ikon(sc, h, "kale", yer, K("b3b", "tema") + i * 0.4, 6)
    for i, yer in enumerate([(31.0, 38.5), (35.0, 39.4)]):
        ikon(sc, h, "alev", yer, K("b3b", "çözülmeye") + i * 0.7, 4)
    t = s["b4"]
    kam(sc, h, t, (29.0, 41.5), 1.6, sure=2.5)
    sehir(sc, h, "İstanbul", t, e["b5"], onemli=True)
    kafile(sc, h, "norman", [(18.0, 44.0), (24.0, 42.6), (28.6, 41.2)], K("b4", "Normanlar") - 0.3, 3.5, adet=5,
           olcek=1.0, tohum=40, t_son=e["b4"])
    kafile(sc, h, "norman", [(20.0, 46.0), (25.0, 43.5), (28.6, 41.3)], K("b4", "Franklar") - 0.3, 3.5, adet=5,
           olcek=1.0, tohum=41, t_son=e["b4"])
    kafile(sc, h, "pecenek", [(33.0, 46.5), (30.0, 43.5), (28.9, 41.3)], K("b4", "Peçenekler") - 0.3, 3.5, adet=5,
           olcek=1.0, tohum=42, t_son=e["b4"])
    kafile(sc, h, "selcuklu", [(36.0, 44.0), (31.5, 42.4), (29.1, 41.2)], K("b4", "Uzlar") - 0.3, 3.5, adet=5,
           olcek=1.0, tohum=43, t_son=e["b4"])
    t = s["b5"]
    kam(sc, h, t, (24.0, 43.0), 1.1, sure=2.5)
    kafile(sc, h, "pecenek", [(31.0, 47.2), (28.5, 45.5), (26.5, 43.6)], K("b5", "Peçenekler") - 0.5, 4.5, adet=9,
           ok=True, olcek=1.0, t_son=e["b5"] + 0.3, tohum=44)
    kafile(sc, h, "norman", [(12.5, 43.3), (14.5, 42.0), (16.6, 41.1)], K("b5", "Normanlar") - 0.5, 4, adet=8,
           ok=True, olcek=1.0, t_son=e["b5"] + 0.3, tohum=45)
    ikon(sc, h, "kale", (16.87, 41.12), K("b5", "şehirlerini"), 4)
    h = ANADOLU
    sc = hsahne("b6", "b6", h)
    kamA(sc, h, s["b6"] - 1, (39.5, 39.3), 1.5)
    sc.ekle(Bolge(h, "bizans", BIZANS_1071, s["b6"] - 1, ad="Bizans", etiket_konum=(32.0, 39.4)),
            Bolge(h, "selcuklu", SELCUKLU_1071, s["b6"] - 1, ad="Selçuklu", etiket_konum=(45.5, 37.0)))
    kafile(sc, h, "selcuklu", [(46.0, 39.6), "Ani"], K("b6", "Ani") - 2.5, 2.5, adet=7, olcek=1.1, tohum=46,
           t_son=K("b6", "Kayseri"))
    ikon(sc, h, "alev", "Ani", K("b6", "düştü"), 5)
    kafile(sc, h, "selcuklu", [(44.0, 38.0), (39.0, 38.6), "Kayseri"], K("b6", "Kayseri") - 2.5, 3, adet=7,
           ok=True, olcek=1.1, tohum=47, t_son=e["b6"])
    ikon(sc, h, "alev", "Kayseri", K("b6", "yağmalandı"), 5)
    for i, (yol) in enumerate((((44.5, 38.2), (36.5, 38.9)), ((43.5, 37.2), (37.5, 38.0)), ((44.0, 40.0), (38.0, 40.0)))):
        kafile(sc, h, "selcuklu", list(yol), K("b6", "Akıncılar") + i * 0.5, 4, adet=4, olcek=1.0, tohum=48 + i,
               t_son=e["b6"] + 0.3)
    sc = v.sahne(*aralik("b7", "b7"), KOYU)
    t = s["b7"]
    sc.ekle(ZamanCizelgesi("Yükselen ve Yorulan", [
        (t + 0.5, "1025", "II. Basileios ölür", "bizans"), (t + 1.3, "1040", "Dandanakan Zaferi", "selcuklu"),
        (t + 2.1, "1048", "Pasinler Savaşı", "selcuklu"), (t + 2.9, "1055", "Tuğrul Bey Bağdat'ta", "selcuklu"),
        (t + 3.7, "1064", "Ani'nin fethi", "selcuklu"), (t + 4.5, "1067", "Kayseri yağmalanır", "selcuklu"),
    ], t, e["b7"] + 0.6))

    # ============================================================ 4 ALPARSLAN
    sc = v.sahne(*aralik("a1", "a3b"), KOYU)
    t = s["a1"]
    sc.ekle(KarakterKarti("Alparslan", "Büyük Selçuklu Sultanı", "Saltanatı: 1064 – 1072", "selcuklu", t + 0.3,
                          e["a3b"] + 0.5, monogram="A", gorsel=KISILER["Alparslan"].get("gorsel"),
                          kirp=KISILER["Alparslan"].get("kirp"), maddeler=[
                              (K("a1", "Çağrı"), "Çağrı Bey'in oğlu, Tuğrul Bey'in yeğeni"),
                              (K("a2", "Alp,"), "Alp: yiğit · Arslan: aslan"),
                              (K("a2", "Horasan'ı"), "Horasan'ın yöneticisi, usta bir komutan"),
                              (K("a3", "Nizamülmülk"), "Veziri: Nizamülmülk"),
                              (K("a3b", "Siyasetname"), "Siyasetname'nin yazarı Nizamülmülk"),
                          ]))
    h = ANADOLU
    sc = hsahne("a4", "a4", h)
    kamA(sc, h, s["a4"] - 1, (43.0, 40.3), 2.6)
    sc.ekle(Bolge(h, "selcuklu", SELCUKLU_1071, s["a4"] - 1, alfa=0.3))
    kafile(sc, h, "selcuklu", [(47.0, 40.0), (45.0, 40.4), (44.0, 40.45)], K("a4", "Kafkasya") - 0.5, 3, adet=9,
           ok=True, olcek=1.2, t_son=e["a4"], tohum=50)
    ikon(sc, h, "kale", "Ani", K("a4", "kuşatmanın"), 7)
    balon(sc, h, "25 gün kuşatma", "Ani", K("a4", "Yirmi"), K("a4", "fethetti"))
    ikon(sc, h, "tac", "Ani", K("a4", "fethetti"), 4)
    h = ORTA
    sc = hsahne("a5", "a6", h)
    kamA(sc, h, s["a5"] - 1, (42.0, 38.0), 1.6)
    sc.ekle(Bolge(h, "bizans", BIZANS_1071, s["a5"] - 1, ad="Bizans", etiket_konum=(32.0, 39.4)),
            Bolge(h, "selcuklu", SELCUKLU_1071, s["a5"] - 1, ad="Büyük Selçuklu", etiket_konum=(52.0, 34.8)))
    kam(sc, h, K("a5", "güneyde") - 0.3, (36.0, 32.5), 1.1, sure=3)
    sc.ekle(Bolge(h, "fatimi", FATIMI, K("a5", "Fatımi"), ad="Fatımiler", etiket_konum=(29.5, 28.5)))
    sehir(sc, h, "Kahire", K("a5", "Mısır"), onemli=True, nabiz=True)
    kafile(sc, h, "selcuklu", ["Bağdat", (40.0, 33.6), (35.5, 31.5), "Kahire"], K("a5", "yıkmayı") - 1, 5, adet=8,
           ok=True, olcek=1.0, t_son=e["a5"] + 0.3, tohum=51)
    kam(sc, h, s["a6"], (36.0, 38.8), 1.5)
    for i, (yol) in enumerate((((42.5, 38.0), (36.0, 39.0)), ((41.5, 37.0), (34.5, 37.8)))):
        kafile(sc, h, "selcuklu", list(yol), K("a6", "Türkmen") + i * 0.6, 4, adet=5, olcek=1.0, tohum=52 + i,
               t_son=e["a6"])
    balon(sc, h, "Kontrolsüz akınlar", (38.0, 38.6), K("a6", "kontrolünde"), K("a6", "Ama"))
    kam(sc, h, K("a6", "Konstantinopolis") - 0.5, "İstanbul", 2.6, sure=2.5)
    ikon(sc, h, "tac", "İstanbul", K("a6", "imparator"), 4)

    # ============================================================ 5 ROMEN
    sc = v.sahne(*aralik("r1", "r1"), KOYU)
    sc.ekle(KarakterKarti("Romen Diyojen", "Bizans İmparatoru", "Saltanatı: 1068 – 1071", "bizans", s["r1"] + 0.3,
                          e["r1"] + 0.5, monogram="R", gorsel=KISILER["Romen"].get("gorsel"), kirp=KISILER["Romen"].get("kirp"), dondur=KISILER["Romen"].get("dondur"),
                          maddeler=[(K("r1", "Kapadokyalı"), "Kapadokyalı askeri bir aileden"),
                                    (K("r1", "cesaretiyle"), "Cesur ve deneyimli bir general"),
                                    (K("r1", "ölüme"), "Darbe suçlamasıyla idama mahkûm edildi")]))
    sc = v.sahne(*aralik("r2", "r3"), KOYU)
    sc.ekle(BuyukYazi("Evdokia'nın Kararı", s["r2"] + 0.3, K("r2", "Mahkûm"), ust="1067", alt="Dul imparatoriçe",
                      boyut=110))
    sc.ekle(BuyukYazi("Affedildi", K("r2", "affetti"), e["r2"] + 0.2, ust="Mahkûm general", alt="ve evlilik kararı",
                      boyut=120))
    sc.ekle(BuyukYazi("Romen Diyojen İmparator", s["r3"] + 0.2, K("r3", "Ancak"), ust="1 Ocak 1068",
                      alt="Konstantinopolis", boyut=96))
    sc.ekle(BuyukYazi("Dukas Ailesi Öfkeli", K("r3", "Ancak"), e["r3"] + 0.3, ust="Saray",
                      alt="Kaysar Yuhanna Dukas: “Gaspçı!”", boyut=96))
    h = ORTA
    sc = hsahne("r4", "r5b", h)
    kamA(sc, h, s["r4"], (37.5, 36.8), 2.2)
    sc.ekle(Bolge(h, "bizans", BIZANS_1071, s["r4"] - 1, alfa=0.3))
    kafile(sc, h, "bizans", [(35.0, 38.5), (37.0, 37.3), "Menbiç"], K("r4", "Menbiç") - 2.5, 3, adet=9,
           tur="piyade", olcek=1.1, t_son=e["r4"], tohum=60)
    ikon(sc, h, "kale", "Menbiç", K("r4", "geri"), 4)
    for i, (a, b_) in enumerate((((39.0, 37.4), (41.0, 38.5)), ((38.4, 36.6), (40.5, 35.8)),
                                  ((40.5, 38.2), (38.6, 38.6)))):
        kafile(sc, h, "selcuklu", [a, b_], K("r4", "dağılıp") + i * 0.4, 3, adet=4, olcek=1.0, tohum=61 + i,
               t_son=e["r4"])
    kam(sc, h, s["r5"], "İstanbul", 2.0, sure=3)
    sehir(sc, h, "İstanbul", s["r5"], onemli=True)
    for i, yol in enumerate(([(24.0, 42.5), (28.9, 41.1)], [(26.5, 39.0), (28.9, 40.9)], [(32.5, 40.0), (29.2, 40.9)],
                             [(26.0, 41.8), (28.8, 41.1)])):
        kafile(sc, h, "bizans", yol, K("r5", "orduyu") - 1 + i * 0.5, 4, adet=6, tur="piyade" if i % 2 else "atli",
               olcek=1.0, tohum=63 + i, t_son=e["r5b"])
    balon(sc, h, "Yeni ordu toplanıyor", "İstanbul", K("r5b", "Dağınık"), K("r5b", "Ama"))
    balon(sc, h, "Uyumsuz ve deneyimsiz", "İstanbul", K("r5b", "Ama"), e["r5b"] + 0.3, renk=(1, 0.75, 0.6))

    # ============================================================ 6 SEFER
    h = ORTA
    sc = hsahne("k1", "k5", h)
    kamA(sc, h, s["k1"] - 1, (40.5, 37.8), 1.7)
    sc.ekle(Bolge(h, "bizans", BIZANS_1071, s["k1"] - 1, ad="Bizans", etiket_konum=(32.0, 39.4)),
            Bolge(h, "selcuklu", SELCUKLU_1071, s["k1"] - 1, ad="Büyük Selçuklu", etiket_konum=(52.0, 34.8)),
            Bolge(h, "fatimi", FATIMI, s["k1"] - 1, ad="Fatımiler", etiket_konum=(29.5, 28.5)))
    kafile(sc, h, "selcuklu", ["Hoy", "Erciş", "Malazgirt"], K("k1", "Malazgirt") - 1.5, 3, adet=8, ok=True,
           olcek=1.1, t_son=K("k1", "Halep") + 1, tohum=70)
    ikon(sc, h, "kale", "Malazgirt", K("k1", "Malazgirt") + 0.5, 4)
    ikon(sc, h, "kale", "Erciş", K("k1", "Erciş") + 0.5, 4)
    kafile(sc, h, "selcuklu", ["Malazgirt", (40.5, 38.3), "Urfa"], K("k1", "güneye") - 0.5, 3, adet=8, ok=True,
           olcek=1.1, t_son=K("k1", "Halep") + 1, tohum=71)
    ikon(sc, h, "kilic", "Urfa", K("k1", "kuşatmıştı"), 3.5)
    kafile(sc, h, "selcuklu", ["Urfa", "Halep"], K("k1", "Halep") - 0.5, 2.5, adet=8, olcek=1.1, t_son=s["k4"] + 2,
           tohum=72)
    kam(sc, h, s["k2"], (33.0, 39.6), 1.3, sure=3)
    kafile(sc, h, "bizans", ["İstanbul", "İzmit", "Ankara", "Sivas"], K("k2", "yola") - 0.5, 8, adet=12, ok=True,
           tur="piyade", olcek=1.1, t_son=1e9, tohum=73)
    kafile(sc, h, "bizans", ["İstanbul", "İzmit", "Ankara", "Sivas"], K("k2", "yola") + 0.5, 8, adet=6,
           olcek=1.1, t_son=1e9, tohum=74)
    kafile(sc, h, "bizans", ["Sivas", "Erzurum"], K("k2", "Haziran") - 1, 3, adet=12, tur="piyade", ok=True,
           olcek=1.1, t_son=1e9, tohum=75)
    t = s["k2b"]
    kam(sc, h, t, "Sivas", 2.6, sure=2.5)
    ikon(sc, h, "kilic", "Sivas", K("k2b", "yenildiği"), 4)
    balon(sc, h, "1070: Manuel Komnenos esir", "Sivas", K("k2b", "Manuel"), e["k2b"] + 0.2, renk=(1, 0.75, 0.6))
    t = s["k3"]
    kam(sc, h, t, (39.0, 39.8), 2.0, sure=2.5)
    kafile(sc, h, "notr", ["Sivas", (39.0, 39.85), "Erzurum"], t, e["k3"] - t, adet=9, tur="piyade", olcek=1.0,
           tohum=76)
    balon(sc, h, "Dev ağırlık kervanı", (39.0, 39.85), K("k3", "kervanı"), K("k3", "Bu"))
    ikon(sc, h, "alev", (38.4, 39.5), K("k3", "yağmalayınca"), 3.5)
    t = s["k4"]
    kam(sc, h, t, "Halep", 2.4, sure=2)
    balon(sc, h, "Mısır seferi iptal!", "Halep", K("k4", "Mısır"), K("k4", "Mısır") + 3.5, renk=(1, 0.75, 0.6))
    kam(sc, h, K("k4", "kuzeye") - 0.5, (41.5, 37.5), 1.5, sure=3)
    kafile(sc, h, "selcuklu", ["Halep", "Musul", "Hoy"], K("k4", "kuzeye") - 0.5, 7, adet=10, ok=True, olcek=1.1,
           t_son=1e9, tohum=77)
    kafile(sc, h, "selcuklu", [(45.0, 36.0), "Musul"], K("k4", "Musul") - 1, 3, adet=6, olcek=1.0,
           t_son=K("k4", "Musul") + 6, tohum=78)
    kafile(sc, h, "notr", [(46.5, 37.5), (44.5, 37.0)], K("k4", "Kürt") - 0.5, 3, adet=6, olcek=1.0,
           t_son=e["k4"] + 2, tohum=79)
    kafile(sc, h, "selcuklu", [(48.0, 39.0), "Hoy"], K("k4b", "Türkmen") - 0.5, 3, adet=7, olcek=1.0,
           t_son=e["k4b"] + 1, tohum=80)
    balon(sc, h, "Türkmen beyleri katılıyor", "Hoy", K("k4b", "Türkmen"), e["k4b"])
    t = s["k5"]
    kam(sc, h, t, (40.5, 39.0), 1.8, sure=2)
    kafile(sc, h, "selcuklu", [(44.0, 38.8), (41.5, 39.6), (40.5, 39.7)], t, 3.5, adet=2, olcek=0.9, tohum=81,
           t_son=e["k5"])
    balon(sc, h, "Casuslar", (41.6, 39.6), K("k5", "casusları"), K("k5", "Romen"), dy=-50)
    balon(sc, h, "Sultan nerede?", "Erzurum", K("k5", "habersizdi") - 1, e["k5"] + 0.3, renk=(1, 0.75, 0.6))

    h = DOGU
    sc = hsahne("k6", "k8", h)
    kamA(sc, h, s["k6"] - 1, (41.8, 39.3), 1.0)
    sehir(sc, h, "Erzurum", s["k6"] - 1, onemli=True)
    sehir(sc, h, "Malazgirt", s["k6"] - 1, onemli=True, yon="ust")
    sehir(sc, h, "Ahlat", s["k6"] - 1, onemli=True, yon="sol")
    ikon(sc, h, "kilic", (41.6, 39.6), K("k6", "ikiye"), 2.5, olcek=0.8)
    kafile(sc, h, "bizans", ["Erzurum", (41.6, 39.1), "Ahlat"], K("k6", "Ahlat") - 2, 4.5, adet=10, ok=True,
           olcek=1.2, t_son=K("k8", "çekildi") + 1, tohum=82)
    kafile(sc, h, "bizans", ["Erzurum", (41.9, 39.6), "Malazgirt"], K("k6", "Malazgirt") - 1, 4.5, adet=12,
           tur="piyade", ok=True, olcek=1.2, t_son=1e9, tohum=83)
    kam(sc, h, s["k7"], "Malazgirt", 2.2, sure=2.5)
    sc.ekle(YilRozeti("23 Ağustos", K("k7", "Ağustos") - 1.2))
    ikon(sc, h, "kale", "Malazgirt", K("k7", "teslim"), 5)
    balon(sc, h, "Kale teslim oldu", "Malazgirt", K("k7", "teslim") + 0.5, e["k7"] + 0.3, dy=-90)
    kam(sc, h, s["k8"], (41.0, 38.7), 1.4, sure=3)
    kafile(sc, h, "pecenek", ["Ahlat", (40.5, 38.6), "Malatya"], K("k8", "çekildi") - 1, 5, adet=10, ok=True,
           olcek=1.1, t_son=e["k8"], tohum=84)
    balon(sc, h, "Savaşmadan çekildi", (40.8, 38.6), K("k8", "çekildi"), K("k8", "Nedeni"), renk=(1, 0.75, 0.6))
    balon(sc, h, "Ordunun yarısı kayıp", "Malazgirt", K("k8", "yarısını") - 0.5, e["k8"] + 0.3, renk=(1, 0.75, 0.6),
          dy=-90)

    # ============================================================ 7 ORDULAR
    sc = v.sahne(*aralik("o1", "o2"), KOYU)
    sc.ekle(BuyukYazi("200.000?", s["o1"] + 2, K("o1", "Ancak"), ust="Ortaçağ kaynaklarına göre", alt="hatta 1.000.000",
                      boyut=150))
    sc.ekle(BuyukYazi("Abartı", K("o1", "Ancak"), e["o1b"] + 0.2, ust="Modern tarihçiler", alt="Bu orduyu ne yollar taşır ne erzak",
                      boyut=150))
    sc.ekle(Karsilastirma(
        {"taraf": "bizans", "baslik": "Bizans", "sayi": "40-70 bin", "alt": "sefere çıkan (tahmin)",
         "maddeler": [(K("o2", "Malazgirt'e"), "Malazgirt'e ulaşan: yaklaşık yarısı")]},
        {"taraf": "selcuklu", "baslik": "Büyük Selçuklu", "sayi": "?", "alt": "birazdan", "maddeler": []},
        s["o2"], e["o2"] + 0.4, baslik="Gerçek rakamlar"))
    sc = v.sahne(*aralik("o3", "o4"), arka_plan_uret(zemin="bozkir", tohum=12))
    for i, (tip, y_, adet, tohum) in enumerate((("agir_suvari", 360, 14, 1), ("piyade", 520, 18, 2),
                                                 ("okcu", 640, 14, 3))):
        b_ = sc.ekle(Birlik("bizans", tip, 760, y_, 520, 70, yon=1))
        b_.belir(s["o3"] + i * 0.8).git(s["o3"], e["o4"], x=1160)
    for i, (ad_, t_) in enumerate((("Ermeni", K("o3", "Ermeni")), ("Varang", K("o3", "Varang")),
                                    ("Frank", K("o3", "Frank")), ("Uz", K("o3", "Uz")))):
        bb = sc.ekle(Birlik("pecenek" if ad_ == "Uz" else ("norman" if ad_ in ("Frank", "Varang") else "bizans"),
                            "suvari" if ad_ in ("Frank", "Uz") else "piyade", 300 + i * 440, 860, 300, 60, yon=1))
        bb.belir(t_).git(t_, e["o4"], x=420 + i * 440)
        sc.ekle(EtiketBalonu(ad_ + " birlikleri", t_, e["o4"], birlik=bb, ofset=(0, -70)))
    sc.ekle(EtiketBalonu("Oğuz kökenli Türkler!", K("o4", "Oğuz"), e["o4"] + 0.3, x=1800 - 200, y=760,
                         renk=(1, 0.75, 0.6)))
    sc = v.sahne(*aralik("o5", "o7"), arka_plan_uret(zemin="bozkir", tohum=13))
    hedef = sc.ekle(Birlik("bizans", "piyade", 420, 560, 260, 120, aci=90, yon=1))
    hedef.belir(s["o5"] - 0.5)
    okcular = []
    for i in range(4):
        o_ = sc.ekle(Birlik("selcuklu", "atli_okcu", 1660, 260 + i * 190, 240, 110, aci=-90, yon=-1))
        o_.belir(s["o5"] + i * 0.4)
        okcular.append(o_)
    t0 = K("o6", "Düşmana")
    for i, o_ in enumerate(okcular):  # yaklaş - ok at - uzaklaş döngüsü
        o_.git(t0 - 0.5 + i * 0.3, t0 + 2 + i * 0.3, x=870)
        o_.git(t0 + 3.5 + i * 0.3, t0 + 6 + i * 0.3, x=1500)
        o_.git(t0 + 7 + i * 0.3, t0 + 9 + i * 0.3, x=870)
        o_.git(t0 + 10 + i * 0.3, t0 + 12 + i * 0.3, x=1420)
        sc.ekle(OkYagmuru(o_, hedef, t0 + 1.5, t0 + 11, yogunluk=6, tohum=i))
    hedef.savas(t0 + 2, t0 + 11)
    sc.ekle(EtiketBalonu("Yaklaş · ok at · uzaklaş", K("o6", "yağdırır"), K("o6", "Geri"), x=1160, y=170))
    sc.ekle(EtiketBalonu("Geri çekilirken bile ok!", K("o6", "Geri"), K("o6", "Bunların"), x=1160, y=170,
                         renk=(1, 0.75, 0.6)))
    gulam = sc.ekle(Birlik("selcuklu", "agir_suvari", 1660, 990, 380, 60, yon=-1))
    gulam.belir(K("o6", "gulamlar") - 0.5)
    sc.ekle(EtiketBalonu("Gulamlar: sultanın muhafızları", K("o6", "gulamlar"), e["o6"] + 0.3, birlik=gulam,
                         ofset=(0, -70)))
    sc.ekle(BuyukYazi("Düzen  ·  Hız", s["o7"] + 0.2, e["o7"] + 0.4, ust="İki savaş anlayışı",
                      alt="Malazgirt'te karşılaşacaklardı", boyut=120))

    # ============================================================ 8 SAVAŞTAN ÖNCE
    h = DOGU
    sc = hsahne("p1", "p4b", h)
    kamA(sc, h, s["p1"] - 1, (42.5, 39.0), 3.0)
    sehir(sc, h, "Malazgirt", s["p1"] - 1, onemli=True, yon="ust")
    sehir(sc, h, "Ahlat", s["p1"] - 1, onemli=True, yon="sol")
    sc.ekle(YilRozeti("24 Ağustos", s["p1"] + 0.2))
    kafile(sc, h, "bizans", ["Malazgirt", (42.45, 38.95)], K("p1", "yiyecek") - 0.5, 3, adet=5, tur="piyade",
           olcek=1.0, t_son=K("p1", "Romen") + 1, tohum=90)
    kafile(sc, h, "selcuklu", [(42.85, 38.85), (42.6, 38.94)], K("p1", "karşılaştı") - 1, 2, adet=8, olcek=1.0,
           t_son=K("p1", "Romen") + 1, tohum=91)
    kafile(sc, h, "bizans", ["Malazgirt", (42.5, 38.92)], K("p1", "Vasilakis") - 0.5, 2.5, adet=7, olcek=1.0,
           t_son=K("p1", "esir") + 1, tohum=92)
    for i, (a_, b_) in enumerate((((42.9, 38.8), (42.6, 38.88)), ((42.95, 39.02), (42.62, 38.96)))):
        kafile(sc, h, "selcuklu", [a_, b_], K("p1", "pusuya") - 0.5, 1.8, adet=6,
               olcek=1.0, t_son=e["p1"] + 1, tohum=93 + i)
    ikon(sc, h, "kilic", (42.5, 38.92), K("p1", "pusuya"), 3.5)
    balon(sc, h, "Vasilakis esir!", (42.5, 38.92), K("p1", "esir") - 0.3, e["p1"] + 0.3, renk=(1, 0.75, 0.6))
    kafile(sc, h, "bizans", ["Malazgirt", (42.62, 38.95), "Malazgirt"], s["p2"], 5, adet=8, olcek=1.0, tohum=95,
           t_son=s["p2"] + 6)
    ikon(sc, h, "kilic", (42.62, 38.95), K("p2", "kuşatılmaktan"), 3)
    for i, (y0_, y1_) in enumerate(((38.9, 38.8), (38.98, 39.05))):
        kafile(sc, h, "selcuklu", [(42.62, y0_), (42.92, y1_)], K("p2", "tepelerde") - 1, 3, adet=7, olcek=1.0,
               t_son=e["p2"] + 0.5, tohum=96 + i)
    balon(sc, h, "Sultanın ordusu!", "Malazgirt", K("p2", "sultanın"), e["p2"] + 0.3, renk=(1, 0.75, 0.6), dy=-90)
    sc.ekle(YilRozeti("25 Ağustos", s["p3"] + 0.2))
    kafile(sc, h, "pecenek", [(42.38, 39.1), (42.6, 38.98), (42.85, 38.9)], K("p3", "Uz") - 0.5, 4, adet=7,
           olcek=1.0, t_son=e["p3"] + 0.5, tohum=98)
    balon(sc, h, "Saf değiştirdiler", (42.7, 38.92), K("p3", "soydaşlarının"), e["p3"] + 0.3, renk=(1, 0.75, 0.6))
    kafile(sc, h, "selcuklu", [(42.85, 38.98), "Malazgirt"], K("p4", "elçi") - 0.5, 3, adet=2, olcek=1.0,
           t_son=K("p4", "reddetti") + 1.5, tohum=99)
    ikon(sc, h, "parsomen", "Malazgirt", K("p4", "barış"), 3)
    balon(sc, h, "Barış teklifi", "Malazgirt", K("p4", "barış"), K("p4", "reddetti"), dy=-90)
    balon(sc, h, "Reddedildi!", "Malazgirt", K("p4", "reddetti"), e["p4"] + 0.3, renk=(1, 0.75, 0.6), dy=-90)
    balon(sc, h, "Bir oyalama taktiği mi?", "Malazgirt", K("p4b", "oyalama"), e["p4b"] + 0.3, dy=-90)
    sc = v.sahne(*aralik("p5", "p6"), KOYU)
    sc.ekle(BuyukYazi("26 Ağustos 1071", s["p5"] + 0.3, e["p5"] + 0.2, ust="Cuma", alt="Malazgirt Ovası", boyut=120))
    sc.ekle(AlintiKarti("Eğer şehit düşersem, bu beyaz elbise kefenim olsun. Benimle gelmek isteyen gelsin, dönmek "
                        "isteyen dönsün. Bugün burada ne emir veren bir sultan var, ne de emir alan bir asker. Ben de "
                        "sizden biriyim.", "Alparslan (rivayet)", s["p6"], e["p6"] + 0.6, taraf="selcuklu"))
    sc.kamera_git(s["p5"], e["p6"], zoom=1.06)

    # ============================================================ 9 MUHAREBE (taktik)
    sc = v.sahne(*aralik("p7", "m12"), arka_plan_uret(
        zemin="bozkir", tepeler=[(1220, 90, 300, 0.9), (1220, 990, 320, 0.95), (1800, 540, 260, 0.55),
                                 (420, 40, 200, 0.4), (420, 1050, 220, 0.45)],
        nehirler=[[(-20, 180), (70, 260), (40, 420), (-20, 520)]],
        yollar=[[(140, 640), (420, 600), (800, 660), (1300, 620), (1940, 660)]],
        yerlesimler=[(130, 700, "Malazgirt")], etiketler=[(960, 1030, "Malazgirt Ovası", 40)], tohum=1071))
    _taktik(sc, v, s, e, K)

    tablo("m12b", "m12b", "malazgirt_minyatur2", (0.5, 0.5, 1.0), (0.55, 0.6, 1.4),
          "Malazgirt Savaşı — 15. yüzyıl minyatürü, Fransız el yazması (kamu malı)")

    # ============================================================ 10 ESİR
    sc = v.sahne(*aralik("e1", "e2"), KOYU)
    sc.kamera_ayarla(s["e1"] - 1, x=960, y=540, zoom=2.0)
    alp_ = sc.ekle(Komutan("Alparslan", "selcuklu", x=1230, y=500, unvan="Sultan"))
    alp_.belir(s["e1"])
    rom_ = sc.ekle(Komutan("Romen Diyojen", "bizans", x=-260, y=520, unvan="İmparator"))
    rom_.belir(K("e1", "imparator") - 0.4)
    rom_.iz.ekle(K("e1", "huzuruna") + 1.6, {"x": 700}, sure=2.2)
    rom_.esir(K("e1", "getirildi"))
    sc.ekle(EtiketBalonu("Bu mu imparator?", K("e1", "inanmadı") - 0.8, K("e1", "Ancak"), x=1230, y=380))
    sc.ekle(EtiketBalonu("Vasilakis onu tanıdı", K("e1", "Vasilakis") - 0.3, e["e1"] + 0.3, x=700, y=380,
                         renk=(1, 0.75, 0.6)))
    sc.ekle(Ikon("tac", 1230, 420, K("e2", "zafer") - 0.3, K("e2", "Ama"), olcek=1.2))
    sc.ekle(EtiketBalonu("Zafer geleneği", K("e2", "geleneğine") - 0.3, K("e2", "Ama"), x=960, y=380))
    alp_.iz.ekle(K("e2", "Ama") + 1.5, {"x": 1060}, sure=1.5)
    rom_.iz.ekle(K("e2", "kaldırdı") + 1.2, {"y": 470}, sure=1.2)
    sc.ekle(EtiketBalonu("Yerden kaldırdı", K("e2", "kaldırdı") - 0.3, e["e2"] + 0.3, x=880, y=380))
    sc = v.sahne(*aralik("e3", "e5"), KOYU)
    sc.kamera_git(s["e3"], e["e5"], zoom=1.05)
    sc.ekle(AlintiKarti("Eğer ben senin önüne esir olarak getirilseydim, ne yapardın?", "Alparslan", s["e3"],
                        e["e3"] + 0.3, taraf="selcuklu"),
            AlintiKarti("Belki seni öldürürdüm. Belki de Konstantinopolis sokaklarında teşhir ederdim.",
                        "Romen Diyojen", s["e4"], e["e4"] + 0.3, taraf="bizans"),
            AlintiKarti("Benim cezam bundan çok daha ağır. Seni affediyor ve serbest bırakıyorum.", "Alparslan",
                        s["e5"], e["e5"] + 0.3, taraf="selcuklu"))
    sc = v.sahne(*aralik("e6", "e7"), KOYU)
    sc.ekle(BuyukYazi("10.000.000", K("e6", "Fidye") - 0.2, K("e6", "Romen") + 0.3, ust="İlk fidye talebi",
                      alt="altın", boyut=150))
    sc.ekle(BuyukYazi("1.500.000", K("e6", "bir buçuk") - 0.2, K("e6", "her yıl"), ust="Peşin fidye", alt="altın",
                      boyut=150))
    sc.ekle(BuyukYazi("+ 360.000 / yıl", K("e6", "her yıl") - 0.1, e["e6b"] + 0.2, ust="Yıllık vergi",
                      alt="altın", boyut=130))
    sc.ekle(KarakterKarti("Antlaşma", "Malazgirt Sonrası", "Ağustos – Eylül 1071", "notr", s["e7"], e["e7"] + 0.5,
                          monogram="1071", maddeler=[
                              (K("e7", "Müslüman"), "Müslüman esirler serbest"),
                              (K("e7", "evlenecekti"), "Hanedanlar arası evlilik"),
                              (K("e7", "Antakya"), "Bazı sınır şehirleri (tartışmalı)"),
                              (K("e7", "emir"), "İmparator muhafızlarla uğurlandı"),
                          ]))

    # ============================================================ 11 SONUÇLAR
    sc = v.sahne(*aralik("n1", "n2"), KOYU)
    sc.ekle(KarakterKarti("Romen Diyojen", "Bir İmparatorun Sonu", "1071 – 1072", "bizans", s["n1"] + 0.3,
                          e["n2"] + 0.4, monogram="R", gorsel=KISILER["Romen"].get("gorsel"), kirp=KISILER["Romen"].get("kirp"), dondur=KISILER["Romen"].get("dondur"),
                          maddeler=[
                              (K("n1", "darbe"), "Dukaslar sarayda darbe yaptı"),
                              (K("n1", "Mihail"), "VII. Mihail Dukas tahta çıktı"),
                              (K("n2", "yenildi"), "Taht savaşını kaybetti"),
                              (K("n2", "söz"), "Söz verilerek teslim alındı"),
                              (K("n2", "mil"), "Gözlerine mil çekildi, Kınalıada'ya sürüldü"),
                          ]))
    sc = v.sahne(*aralik("n3", "n3"), KOYU)
    sc.ekle(KarakterKarti("Alparslan", "Bir Sultanın Sonu", "1072", "selcuklu", s["n3"] + 0.3, e["n3"] + 0.5,
                          monogram="A", gorsel=KISILER["Alparslan"].get("gorsel"), kirp=KISILER["Alparslan"].get("kirp"),
                          maddeler=[
                              (K("n3", "antlaşmanın"), "Antlaşmayı geçersiz saydı (rivayet)"),
                              (K("n3", "hançerlenerek"), "1072: Orta Asya seferinde hançerlendi"),
                              (K("n3", "Melikşah"), "Yerine oğlu Melikşah geçti"),
                          ]))
    h = ANADOLU
    sc = hsahne("n4", "n5", h)
    kamA(sc, h, s["n4"] - 1, (36.5, 38.6), 1.0)
    b71 = sc.ekle(Bolge(h, "bizans", BIZANS_1071, s["n4"] - 1, ad="Bizans", etiket_konum=(32.0, 39.4)))
    sc.ekle(Bolge(h, "selcuklu", SELCUKLU_1071, s["n4"] - 1, ad="Büyük Selçuklu", etiket_konum=(45.5, 36.6)))
    for i, (yol) in enumerate((((43, 38.5), (33.0, 39.5)), ((42, 37.5), (32.5, 37.6)), ((43, 40.0), (34.0, 40.6)),
                               ((40, 38.6), (28.0, 38.5)), ((41, 39.5), (30.0, 40.2)), ((44, 39.0), (36.0, 39.0)))):
        kafile(sc, h, "selcuklu", list(yol), K("n4", "Türkmen") - 1 + i * 0.6, 6, adet=6, ok=True, olcek=1.0,
               tohum=110 + i, t_son=e["n4"] + 0.3)
    ikon(sc, h, "yildiz", (27.0, 38.4), K("n4", "Ege"), 4)
    b71.kaybol(s["n5"])
    sc.ekle(Bolge(h, "bizans", BIZANS_1080, s["n5"], ad="Bizans", etiket_konum=(27.0, 41.6), etiket_boyut=28),
            Bolge(h, "bizans", BIZANS_KARADENIZ, s["n5"]),
            Bolge(h, "selcuklu", TURKIYE_SELCUKLU, K("n5", "Anadolu"), ad="Anadolu Selçuklu", etiket_konum=(34.8, 38.8)))
    kafile(sc, h, "selcuklu", [(33.0, 39.0), (30.5, 40.0), "İznik"], K("n5", "İznik") - 2, 2.5, adet=8, olcek=1.1,
           t_son=e["n5"], tohum=120)
    ikon(sc, h, "tac", "İznik", K("n5", "başkent"), 4.5)
    kam(sc, h, K("n5", "Konstantinopolis") - 0.5, (29.4, 40.7), 3.0, sure=2.5)
    sehir(sc, h, "İstanbul", K("n5", "Konstantinopolis"), onemli=True)

    # ============================================================ 11b BEYLİKLER
    h = ANADOLU
    sc = hsahne("t1", "t4", h)
    kamA(sc, h, s["t1"] - 1, (37.0, 39.0), 1.25)
    sc.ekle(Bolge(h, "selcuklu", TURKIYE_SELCUKLU, s["t1"] - 1, alfa=0.25))
    beylikler = [("Danişmendliler", (36.3, 40.0), "Danişmendliler"), ("Saltuklular", (41.27, 39.9), "Saltuklular"),
                 ("Mengücekliler", (39.5, 39.6), "Mengücekliler"), ("Artuklular", (41.0, 37.4), "Artuklular")]
    renkler = {"Danişmendliler": "gazneli", "Saltuklular": "fatimi", "Mengücekliler": "norman",
               "Artuklular": "hacli"}
    for ad_, yer, kel in beylikler:
        t_ = K("t2", kel)
        x, y = h.proj(*yer)
        sc.ekle(Ikon("kale", x, y, t_, e["t4"] + 0.3, olcek=1.2))
        sc.ekle(EtiketBalonu(ad_, t_ + 0.2, e["t4"] + 0.3, x=x, y=y - 70))
    for i, yer in enumerate([(33.5, 38.0), (35.5, 38.8), (37.5, 39.2), (31.5, 39.0)]):
        ikon(sc, h, "yildiz", yer, K("t3", "Camiler") + i * 0.5, 5, olcek=0.8)
    kam(sc, h, s["t4"], (31.0, 39.3), 1.0, sure=3)
    sc.ekle(Bolge(h, "bizans", BIZANS_1080, s["t4"], ad="Bizans", etiket_konum=(27.0, 41.6), etiket_boyut=28))
    kafile(sc, h, "hacli", [(25.6, 42.5), (28.0, 41.3), (29.5, 40.6)], K("t4", "Batı'dan") - 0.5, 4, adet=7,
           olcek=1.1, t_son=e["t4"] + 0.3, tohum=125)

    # ============================================================ HAÇLI
    def clermont_yedek(ilk, son):
        ha = AVRUPA
        sb = hsahne(ilk, son, ha)
        kamA(sb, ha, s[ilk] - 0.5, (29.0, 40.5), 1.6)
        sb.ekle(Bolge(ha, "bizans", BIZANS_1080, s[ilk] - 0.5, ad="Bizans", etiket_konum=(24.5, 41.8)))
        sehir(sb, ha, "İstanbul", s[ilk] - 0.5, onemli=True, nabiz=True)
        kafile(sb, ha, "bizans", ["İstanbul", (20.0, 43.5), (12.5, 41.9)], K(son, "elçiler") - 1, 4.5, adet=3,
               olcek=1.0, t_son=K(son, "1095") + 1, tohum=130)
        kam(sb, ha, K(son, "elçiler"), (13.0, 43.5), 1.2, sure=3)
        sehir(sb, ha, "Clermont", K(son, "Clermont") - 1, onemli=True, nabiz=True)
        ikon(sb, ha, "parsomen", (3.08, 45.78), K(son, "çağrısını") - 0.5, 5)
        kafile(sb, ha, "hacli", ["Clermont", (10.0, 46.5), (17.0, 45.0), (24.0, 43.0), "İstanbul"],
               K(son, "Haçlı") - 0.5, 7, adet=12, ok=True, olcek=1.0, t_son=e[son] + 1, tohum=131)
        return sb

    tablo("n6", "n6", "clermont", (0.5, 0.4, 1.0), (0.5, 0.35, 1.3),
          "Clermont Konsili — Passages d'outremer, 1474 civarı (kamu malı)", yedek=clermont_yedek)
    sc = v.sahne(*aralik("n7", "n7"), KOYU)
    t = s["n7"]
    sc.ekle(ZamanCizelgesi("Malazgirt'in Yankıları", [
        (t + 0.3, "1071", "Malazgirt Zaferi", "selcuklu"), (t + 1.0, "1072", "Romen ve Alparslan ölür", "notr"),
        (t + 1.7, "1075", "İznik başkent olur", "selcuklu"), (t + 2.4, "1081", "Aleksios Komnenos", "bizans"),
        (t + 3.1, "1095", "Haçlı Seferi çağrısı", "hacli"), (t + 3.8, "1096", "Birinci Haçlı Seferi", "hacli"),
    ], t, e["n7"] + 0.6))

    # ============================================================ KAPANIŞ
    h = ANADOLU
    sc = hsahne("x1", "x3", h)
    kamA(sc, h, s["x1"] - 1, (42.5, 39.1), 2.6)
    kam(sc, h, s["x1"] + 1, (35.5, 38.8), 1.0, sure=e["x1"] - s["x1"])
    sehir(sc, h, "Malazgirt", s["x1"] - 1, onemli=True, nabiz=True)
    sc.ekle(Bolge(h, "selcuklu", TURKIYE_SELCUKLU, K("x2", "Anadolu'yu"), alfa=0.35))
    v.ekran(BaslikKarti("BÜYÜK SAVAŞLAR", "MALAZGİRT", "26 Ağustos 1071", s["x3"] - 0.2, e["x3"] + 2))
    v.kapanis(e["x3"] + 0.5, 1.5)

    # ============================================================ OTOMATİK KATMAN
    oto_katman(v, T, KISILER, OTO_YERLER, haric_bolumler=("a1", "a2", "a3", "a3b", "r1", "n1", "n2", "n3",
                                                          "e3", "e4", "e5", "p6"))


# ---------------------------------------------------------------- taktik düzen dönüşümü
# Savaş kurgusu "mantıksal" düzende yazıldı (Bizans altta, Selçuklu üstte). Ekranda her zaman
# Bizans SOLDA, Türkler SAĞDA durur ve sağdan akın eder: mantıksal (x, y) -> ekran D(x, y).
SX, SY, YM = 1.55, 0.58, 560


def D(x, y):
    return 960 + (YM - y) * SX, 540 + (x - 960) * SY


def Dl(noktalar):
    return [D(x, y) for x, y in noktalar]


class DonukBirlik(Birlik):
    """Mantıksal düzende hareket eden, ekrana döndürülerek çizilen birlik."""

    def _ekran_deger(self, t):
        d = dict(self.iz.deger(t))
        d["x"], d["y"] = D(d["x"], d["y"])
        d["g"] = d["g"] * SY
        d["aci"] = d["aci"] + (270 if self.taraf == "selcuklu" else 90)
        return d

    def mantiksal(self, t):
        d = self.iz.deger(t)
        return d["x"], d["y"]


def _taktik(sc, v, s, e, K):
    bz = {
        "sol_s": DonukBirlik("bizans", "suvari", 400, 800, 150, 56, yon=1),
        "sol_p": DonukBirlik("bizans", "piyade", 620, 800, 260, 60, yon=1),
        "mer_a": DonukBirlik("bizans", "agir_suvari", 960, 760, 320, 64),
        "mer_p": DonukBirlik("bizans", "piyade", 960, 840, 320, 56),
        "sag_p": DonukBirlik("bizans", "piyade", 1300, 800, 260, 60, yon=-1),
        "sag_s": DonukBirlik("bizans", "suvari", 1520, 800, 150, 56, yon=-1),
        "ihtiyat": DonukBirlik("bizans", "piyade", 960, 960, 400, 56),
    }
    okcular = [DonukBirlik("selcuklu", "atli_okcu", x, y, 190, 90, yon=1 if x < 960 else -1)
               for x, y in ((480, 480), (720, 420), (960, 400), (1200, 420), (1440, 480))]
    sol_ana = DonukBirlik("selcuklu", "suvari", 300, 230, 240, 64, yon=1)
    sag_ana = DonukBirlik("selcuklu", "suvari", 1620, 230, 240, 64, yon=-1)
    sultan = DonukBirlik("selcuklu", "agir_suvari", 960, 200, 260, 64)
    sc.ekle(*bz.values(), *okcular, sol_ana, sag_ana, sultan)
    romen = Komutan("Romen Diyojen", "bizans", bz["mer_a"], ofset=(0, -190), unvan="İmparator")
    bri = Komutan("Briyennios", "bizans", bz["sol_p"], ofset=(0, -170))
    aly = Komutan("Alyates", "bizans", bz["sag_p"], ofset=(0, -170))
    dukas = Komutan("Andronikos Dukas", "bizans", bz["ihtiyat"], ofset=(0, 135))
    alp = Komutan("Alparslan", "selcuklu", sultan, ofset=(0, -170), unvan="Sultan")
    sc.ekle(romen, bri, aly, dukas, alp)

    # p7: tanık tarihçi, Dukas'a dikkat
    t = s["p7"]
    sc.kamera_ayarla(t - 1, x=650, y=540, zoom=1.0)
    for i, b in enumerate(bz.values()):
        b.belir(t + 0.3 + i * 0.25)
    sc.kamera_git(K("p7", "Arka") - 1, K("p7", "Arka") + 2, x=386, y=598, zoom=1.7)
    dukas.belir(K("p7", "Andronikos") - 0.3)
    sc.ekle(EtiketBalonu("İmparatorun düşmanı", K("p7", "düşmanı"), e["p7"] + 0.3, birlik=bz["ihtiyat"],
                         ofset=(0, -150), renk=(1, 0.75, 0.6)))

    # m1-m2 diziliş
    t = s["m1"]
    v.ekran(Lejant([("bizans", "Bizans"), ("selcuklu", "Büyük Selçuklu")], t, e["m12"] - 0.5))
    sc.kamera_git(t, t + 2, x=588, y=540, zoom=1.3)
    romen.belir(K("m1", "Romen") - 0.2)
    sc.kamera_git(K("m1", "Sol") - 0.5, K("m1", "Sol") + 1.2, x=588, y=343, zoom=1.7)
    bri.belir(K("m1", "Briyennios") - 0.3)
    sc.kamera_git(K("m1", "sağ") - 0.5, K("m1", "sağ") + 1.2, x=588, y=737, zoom=1.7)
    aly.belir(K("m1", "Alyates") - 0.3)
    sc.kamera_git(s["m2"], s["m2"] + 1.8, x=433, y=540, zoom=1.6)
    sc.ekle(EtiketBalonu("Geri çekilişi koruyacak", K("m2", "koruyacaktı") - 1.5, e["m2"] + 0.3, birlik=bz["ihtiyat"],
                         ofset=(0, -150)))
    # m3 Selçuklu hilali
    t = s["m3"]
    sc.kamera_git(t, t + 2.2, x=1316, y=540, zoom=1.15)
    sc.ekle(EtiketBalonu("≈ 4 km", K("m3", "dört") - 0.3, K("m3", "Atlı"), x=898, y=540))
    for i, o in enumerate(okcular):
        o.belir(K("m3", "hilal") - 0.5 + abs(i - 2) * 0.3)
    for b in (sol_ana, sag_ana, sultan):
        b.git(K("m3", "Ana") - 0.3, K("m3", "Ana") + 1.2, alfa=0.45)
    alp.belir(K("m3", "Ana"))
    sc.ekle(EtiketBalonu("Pusu", K("m3", "tepelerin"), e["m3"] + 0.4, birlik=sol_ana, ofset=(0, 110)),
            EtiketBalonu("Pusu", K("m3", "tepelerin"), e["m3"] + 0.4, birlik=sag_ana, ofset=(0, -110)))
    # m4-m6 ilerleme, sahte ricat, kamp boş
    t, te = s["m4"], e["m6"]
    sc.kamera_git(t, t + 2.5, x=960, y=540, zoom=1.0)
    yayilma = {"sol_s": -100, "sol_p": -55, "sag_p": 55, "sag_s": 100}
    for k, b in bz.items():
        x, y = b.mantiksal(t)
        b.git(t + 0.5, te - 1, x=x + yayilma.get(k, 0), y=y + (-120 if k == "ihtiyat" else -240))
    hedefler = [bz["sol_p"], bz["sol_p"], bz["mer_a"], bz["sag_p"], bz["sag_p"]]
    for i, o in enumerate(okcular):
        x, y = o.mantiksal(t)
        # dalgalar halinde yaklaş-çekil
        o.git(K("m4", "yaklaşıyor") - 0.5, K("m4", "yaklaşıyor") + 1.5, y=y + 70)
        o.git(K("m4", "geri") - 0.5, K("m4", "geri") + 2.0, y=y - 60)
        o.git(K("m4b", "oklar") - 0.5, K("m4b", "oklar") + 1.5, y=y + 20)
        o.git(K("m4b", "dağılıp") - 0.5, te - 1, y=y - 170, x=x + (i - 2) * 60)
        sc.ekle(OkYagmuru(o, hedefler[i], K("m4", "ok") - 0.3, te - 1.5, yogunluk=6, tohum=i))
    sol_ana.git(K("m4", "kanatları") - 0.5, K("m4", "kanatları") + 3, x=230, y=420)
    sag_ana.git(K("m4", "kanatları") - 0.5, K("m4", "kanatları") + 3, x=1690, y=420)
    for x in (620, 960, 1300):
        sc.ekle(HareketOku("bizans", Dl([(x, 700), (x, 500)]), t + 0.5, t + 3, t_son=t + 7, kalinlik=20))
    sc.ekle(EtiketBalonu("Sahte ricat!", s["m5"], e["m5"] + 0.4, birlik=okcular[2], ofset=(0, 90)))
    sc.ekle(EtiketBalonu("Kamp boş!", K("m6", "kamp"), K("m6", "Atlı"), birlik=sultan, ofset=(0, 90)))
    for k in ("mer_a", "sol_s", "sag_s"):
        x, y = bz[k].mantiksal(K("m6", "süvarileri"))
        bz[k].git(K("m6", "süvarileri") - 0.2, K("m6", "süvarileri") + 1.5, y=y - 60)
        bz[k].git(K("m6", "uzaklaşıyorlardı") - 0.2, K("m6", "uzaklaşıyorlardı") + 2, y=y)
    # m7 dönüş emri
    t, te = s["m7"], e["m7"]
    sc.ekle(EtiketBalonu("Susuz ve yorgun", K("m7", "susuz") - 0.3, K("m7", "Romen"), birlik=bz["mer_a"],
                         ofset=(0, -200), renk=(1, 0.75, 0.6)))
    sc.kamera_git(K("m7", "Romen") - 0.5, K("m7", "Romen") + 2, x=898, y=540, zoom=1.25)
    sc.ekle(EtiketBalonu("Karargâha dönün!", K("m7", "kampa") - 0.5, e["m7"] + 0.5, birlik=bz["mer_a"],
                         ofset=(0, -200)))
    for k in ("sol_s", "sol_p", "mer_a", "mer_p", "sag_p", "sag_s"):
        bz[k].git(K("m7", "sancağı") - 0.3, K("m7", "sancağı") + 1.8, aci=180)
    for k in ("sol_p", "mer_a", "mer_p"):
        bz[k].git(K("m7", "sancağı") + 1.5, e["m8"], y=bz[k].mantiksal(t)[1] + 50)
    # m8 sağ kanat karışıklığı
    t = s["m8"]
    sc.kamera_git(t, t + 2, x=898, y=766, zoom=1.5)
    for k, dx in (("sag_s", 80), ("sag_p", 40)):
        x, y = bz[k].mantiksal(t)
        bz[k].git(K("m8", "yenildiğini") - 0.3, e["m8"] + 1, x=x + dx, y=y + 70)
    sc.ekle(EtiketBalonu("Yenildik mi?", K("m8", "yenildiğini") - 0.5, e["m8"] + 0.3, birlik=bz["sag_s"],
                         ofset=(0, -80), renk=(1, 0.75, 0.6)))
    # m9 Dukas çekilir
    t, te = s["m9"], e["m9"]
    sc.kamera_git(t, t + 2, x=557, y=540, zoom=1.35)
    sc.ekle(EtiketBalonu("“İmparator öldü!”", K("m9", "söylentisini") - 1, K("m9", "söylentisini") + 4,
                         birlik=bz["ihtiyat"], ofset=(0, -150), renk=(1, 0.75, 0.6)))
    bz["ihtiyat"].git(K("m9", "ihtiyat") - 0.5, K("m9", "ihtiyat") + 0.8, aci=180)
    bz["ihtiyat"].git(K("m9", "ihtiyat") + 0.5, te + 1, y=1180, x=600)
    bz["ihtiyat"].kaybol(te - 1, 1.5)
    dukas.kaybol(te - 1.5)
    sc.ekle(HareketOku("bizans", Dl([(960, 900), (760, 1060)]), K("m9", "Malazgirt'teki") - 0.5,
                       K("m9", "Malazgirt'teki") + 1.5, t_son=te + 1, kalinlik=22, renk=(0.55, 0.45, 0.55)))
    # m10 saldırı
    t, te = s["m10"], e["m10"]
    sc.kamera_git(t, t + 2, x=991, y=540, zoom=1.0)
    for b in (sol_ana, sag_ana, sultan):
        b.git(K("m10", "tepelerden") - 0.5, K("m10", "tepelerden") + 0.8, alfa=1)
    sc.ekle(HareketOku("selcuklu", Dl([(230, 480), (300, 560), (480, 640), (640, 620)]), K("m10", "iki") - 0.5,
                       K("m10", "iki") + 2.5, t_son=e["m11"] - 2),
            HareketOku("selcuklu", Dl([(1690, 480), (1620, 560), (1440, 640), (1280, 620)]), K("m10", "iki") - 0.5,
                       K("m10", "iki") + 2.5, t_son=e["m11"] - 2))
    sol_ana.git(K("m10", "iki") - 0.3, K("m10", "iki") + 3.5, x=560, y=620, aci=197)
    sag_ana.git(K("m10", "iki") - 0.3, K("m10", "iki") + 3.5, x=1360, y=620, aci=163)
    for o, (x, y) in zip(okcular, [(640, 560), (790, 450), (960, 420), (1130, 450), (1280, 560)]):
        o.git(K("m10", "iki"), K("m10", "iki") + 3.5, x=x, y=y)
    for k in ("sol_s", "sol_p", "mer_a", "mer_p", "sag_p", "sag_s"):
        bz[k].savas(K("m10", "saldırdı"), e["m11"] - 1)
    for k, dx in (("sag_s", 150), ("sag_p", 90)):
        x, y = bz[k].mantiksal(K("m10", "Sağ"))
        bz[k].git(K("m10", "Sağ") - 0.2, K("m10", "Sağ") + 3, x=x + dx, y=y + 100, g=150, alfa=0.0)
    aly.kaybol(K("m10", "Sağ") + 1)
    sc.ekle(EtiketBalonu("Sağ kanat bozguna uğradı", K("m10", "Sağ"), K("m10", "Sol") + 0.5, x=836, y=853,
                         renk=(1, 0.75, 0.6)))
    for k, dx in (("sol_s", -150), ("sol_p", -100)):
        x, y = bz[k].mantiksal(K("m10", "Sol"))
        bz[k].git(K("m10", "Sol") - 0.2, te, x=x + dx, y=y + 130, g=150, alfa=0.0)
    bri.kaybol(te - 1.5)
    sc.ekle(EtiketBalonu("Briyennios geri çekiliyor", K("m10", "Briyennios"), te + 0.3, x=836, y=227,
                         renk=(1, 0.75, 0.6)))
    # m11 esir
    t, te = s["m11"], e["m11"]
    bz["mer_a"].git(t, t + 3, g=230)
    bz["mer_p"].git(t, t + 3, g=230)
    sultan.git(t, t + 3, y=320)
    sc.kamera_git(t + 0.5, t + 3, x=867, y=540, zoom=1.45)
    sc.ekle(EtiketBalonu("Varang muhafızları", K("m11", "Varang"), K("m11", "Kaçmayı") + 1, birlik=bz["mer_p"],
                         ofset=(0, 125)))
    sc.ekle(EtiketBalonu("Atı öldürüldü, yaralandı", K("m11", "Atı"), K("m11", "Ve"), birlik=bz["mer_a"],
                         ofset=(0, -210), renk=(1, 0.75, 0.6)))
    romen.esir(K("m11", "esir") - 0.5)
    # m12 gece takibi
    t, te = s["m12"], e["m12"]
    sc.kamera_git(t, t + 3, x=991, y=540, zoom=1.0)
    bz["mer_a"].kaybol(K("m12", "Takip"), 2)
    bz["mer_p"].kaybol(K("m12", "Takip"), 2)
    romen.kaybol(K("m12", "Takip") + 1)
    for i, o in enumerate(okcular):
        x, y = o.mantiksal(t)
        o.git(K("m12", "Takip"), te, y=y + 500)
