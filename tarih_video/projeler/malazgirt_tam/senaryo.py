"""MALAZGİRT MEYDAN MUHAREBESİ (1071) — tam bölüm (~25 dk).

Yapı: her "bolum" anahtarı bir YouTube bölümü başlatır ve tek seferde seslendirilir.
Bölüm içindeki parçalar (id) animasyon senkronu içindir.
"""
from motor.harita import arka_plan_uret
from motor.cografya import Harita, Bolge, Sehir, Rota
from motor.kartlar import (koyu_arka_plan, KarakterKarti, ZamanCizelgesi, Karsilastirma,
                           AlintiKarti, BuyukYazi)
from motor.sahne import (Birlik, Komutan, HareketOku, OkYagmuru, EtiketBalonu, BaslikKarti,
                         BolumEtiketi, Lejant, taraf_tanimla)

taraf_tanimla("bizans", (0.46, 0.17, 0.52), vurgu=(0.97, 0.83, 0.45))
taraf_tanimla("selcuklu", (0.05, 0.50, 0.55), vurgu=(0.93, 0.96, 0.90))
taraf_tanimla("gazneli", (0.78, 0.45, 0.12), vurgu=(0.99, 0.92, 0.75))
taraf_tanimla("fatimi", (0.22, 0.52, 0.22), vurgu=(0.92, 0.95, 0.80))
taraf_tanimla("pecenek", (0.45, 0.42, 0.40), vurgu=(0.92, 0.90, 0.85))
taraf_tanimla("norman", (0.18, 0.32, 0.66), vurgu=(0.90, 0.92, 0.98))
taraf_tanimla("hacli", (0.72, 0.13, 0.10), vurgu=(0.98, 0.92, 0.85))
taraf_tanimla("notr", (0.55, 0.45, 0.25), vurgu=(0.95, 0.85, 0.6))

BOLUMLER = [
    # ------------------------------------------------------------------ 1
    {"id": "g1", "bolum": "Giriş",
     "metin": "Yıl 1071. Doğu Anadolu'da, Van Gölü'nün kuzeyinde geniş bir ova. Bir yanda, bin yıllık Roma "
              "mirasını taşıyan Bizans İmparatorluğu ve onun cesur imparatoru Romen Diyojen. Diğer yanda, Orta "
              "Asya bozkırlarından çıkıp birkaç on yıl içinde koca bir imparatorluk kuran Büyük Selçuklular ve "
              "onların sultanı Alparslan."},
    {"id": "g2",
     "metin": "26 Ağustos günü bu ovada yaşanacak savaş, yalnızca iki ordunun değil, iki dünyanın kaderini "
              "belirleyecekti. Anadolu'nun kapıları Türklere açılacak, Bizans bir daha asla eski gücüne "
              "kavuşamayacaktı. Bu savaşın yankıları, yirmi beş yıl sonra başlayacak Haçlı Seferleri'ne kadar "
              "uzanacaktı."},
    {"id": "g3",
     "metin": "Peki, bozkırdan gelen bu atlılar, dünyanın en köklü imparatorluklarından birini nasıl dize "
              "getirdi? Ve bir imparator, savaş meydanında nasıl esir düştü? Bu hikâyeyi en başından anlatalım.",
     "ek_sure": 1.5},
    # ------------------------------------------------------------------ 2
    {"id": "s1", "bolum": "Bozkırdan Doğan Güç",
     "metin": "Hikâyemiz, Aral Gölü'nün doğusunda, Seyhun Nehri kıyılarında başlıyor. Onuncu yüzyılda burada "
              "yaşayan Oğuz boylarından birinin başında, Selçuk Bey adında bir lider vardı. Selçuk Bey, boyuyla "
              "birlikte Cend şehri çevresine yerleşti ve İslamiyet'i kabul etti."},
    {"id": "s2",
     "metin": "Selçuk Bey'in torunları Tuğrul ve Çağrı Beyler, boylarını güneye, Horasan'a doğru götürdüler. "
              "Ancak bu topraklar güçlü bir devletin, Gaznelilerin elindeydi. Gazneli Sultan Mesud, bu göçebe "
              "Türkmenleri bir tehdit olarak görüyordu ve onları ezmek için büyük bir ordu topladı."},
    {"id": "s3",
     "metin": "1040 yılında, Merv yakınlarındaki Dandanakan'da iki ordu karşılaştı. Selçuklular, ağır zırhlı "
              "Gazneli ordusunu çölde günlerce yıprattı, onu su kaynaklarından uzak tuttu ve sonunda kesin bir "
              "zafer kazandı. Bu zaferle Büyük Selçuklu Devleti kuruldu ve Tuğrul Bey sultan ilan edildi."},
    {"id": "s4",
     "metin": "Bundan sonrası bir fırtına gibiydi. Selçuklular İran'ı baştan başa ele geçirdi. 1055 yılında "
              "Tuğrul Bey, Abbasi halifesinin daveti üzerine Bağdat'a girdi. Birkaç yıl sonra halife ona, Doğunun "
              "ve Batının Sultanı unvanını verdi. Artık Selçuklular, İslam dünyasının siyasi liderleriydi."},
    {"id": "s5",
     "metin": "Selçuklu yükselişi, Türkmen boylarını da harekete geçirmişti. Otlak ve ganimet arayan Türkmen "
              "akıncıları, giderek batıya, Bizans sınırlarına yöneliyordu. 1048 yılında Pasinler Ovası'nda, "
              "Selçuklular ile Bizans arasında ilk büyük savaş yaşandı ve zafer Selçukluların oldu. Ama iki güç "
              "arasındaki asıl hesaplaşma henüz başlamamıştı."},
    # ------------------------------------------------------------------ 3
    {"id": "b1", "bolum": "Bizans'ın Krizi",
     "metin": "Peki, o dönemde Bizans ne durumdaydı? Bunu anlamak için biraz geriye gitmemiz gerekiyor. 1025 "
              "yılında, Bizans'ın en güçlü imparatorlarından İkinci Basileios öldüğünde, imparatorluk İtalya'dan "
              "Kafkaslara kadar uzanan muazzam bir güçtü. Ordusu güçlü, hazinesi doluydu."},
    {"id": "b2",
     "metin": "Ama Basileios'un ölümünden sonra işler hızla kötüye gitti. Taht, saray entrikaları ve darbelerle "
              "sık sık el değiştirdi. Başkentteki sivil bürokratlar, ordunun gücünden korkuyor ve askeri "
              "harcamaları kısıyordu. Sınır boylarındaki köylü askerler, askerlik yerine vergi ödemeye başladı. "
              "Kaynaklara göre doğu sınırındaki koca bir ordu, tasarruf uğruna dağıtıldı."},
    {"id": "b3",
     "metin": "Böylece imparatorluk, giderek yabancı paralı askerlere bağımlı hale geldi. Normanlar, Franklar, "
              "Peçenekler ve Uzlar. Bu askerler cesurdu, ama sadakatleri parayla ölçülüyordu. Üstelik Bizans her "
              "cepheden sıkıştırılıyordu. Balkanlarda Peçenekler akın ediyor, İtalya'da ise Normanlar Bizans "
              "topraklarını tek tek ele geçiriyordu."},
    {"id": "b4",
     "metin": "Doğuda ise Türkmen akınları artık durdurulamaz hale gelmişti. 1064 yılında Ermenistan'ın görkemli "
              "başkenti Ani düştü. 1067'de Kayseri yağmalandı. Akıncılar Anadolu'nun içlerine kadar ilerliyor, "
              "Bizans ise bunlara karşı etkili bir cevap veremiyordu."},
    {"id": "b5",
     "metin": "Bizans'ın bu yorgun dönemi, tam da Selçukluların yükselişiyle aynı zamana denk geliyordu. Bir yanda "
              "hızla büyüyen genç bir güç, diğer yanda yorgun düşmüş köklü bir imparatorluk.", "ek_sure": 1.0},
    # ------------------------------------------------------------------ 4
    {"id": "a1", "bolum": "Sultan Alparslan",
     "metin": "1063 yılında Tuğrul Bey çocuksuz olarak öldü. Taht için kısa bir mücadele yaşandı ve sonunda Çağrı "
              "Bey'in oğlu Alparslan, Büyük Selçuklu sultanı oldu. Alparslan, adının hakkını veren bir liderdi. "
              "Alp, yiğit demekti. Arslan ise aslan."},
    {"id": "a2",
     "metin": "Alparslan, gençliğinden beri babasının yanında savaşmış, tecrübeli bir komutandı. Yanında ise "
              "tarihin en ünlü devlet adamlarından biri vardı: Veziri Nizamülmülk. Nizamülmülk devletin idaresini "
              "düzene sokarken, Alparslan seferlere odaklandı."},
    {"id": "a3",
     "metin": "Sultan olduktan sadece bir yıl sonra, 1064'te Kafkasya'ya yürüdü ve Ani'yi fethetti. Ancak "
              "Alparslan'ın asıl hedefi Bizans değildi. Onun gözü güneyde, Mısır'daki Fatımi Devleti'ndeydi. "
              "Sünni İslam dünyasının lideri olarak, Fatımileri yıkmayı en büyük görevi sayıyordu."},
    {"id": "a4",
     "metin": "Bizans sınırlarındaki Türkmen akınları ise çoğu zaman sultanın kontrolünde değildi. Ama Bizans için "
              "bu ayrım pek önemli değildi. Konstantinopolis'te, doğudaki tehdidi kökünden çözecek bir imparator "
              "aranıyordu.", "ek_sure": 0.5},
    # ------------------------------------------------------------------ 5
    {"id": "r1", "bolum": "İmparator Romen Diyojen",
     "metin": "Bu imparator, Romen Diyojen olacaktı. Kapadokyalı köklü bir aileden gelen Romen, cesareti ve askeri "
              "başarılarıyla tanınan bir generaldi. 1067'de İmparator Konstantin Dukas öldüğünde, dul "
              "imparatoriçe Evdokia, devletin başına güçlü bir asker geçmesi gerektiğine karar verdi."},
    {"id": "r2",
     "metin": "1068 yılının ilk gününde Evdokia, Romen Diyojen ile evlendi ve Romen imparator oldu. Ancak bu "
              "evlilik, sarayın en güçlü ailesi olan Dukasları çok kızdırmıştı. Özellikle Kaysar Yuhanna Dukas, "
              "yeni imparatoru bir gaspçı olarak görüyordu. Romen, sarayda düşmanlarla çevriliydi."},
    {"id": "r3",
     "metin": "Romen, tahta çıkar çıkmaz doğuya seferler düzenledi. 1068 ve 1069'da Türkmenlerle çarpıştı, bazı "
              "başarılar kazandı ama kesin bir sonuç alamadı. Artık şuna inanıyordu: Bu sorunu çözmenin tek yolu, "
              "Selçuklu sultanını büyük bir meydan savaşında yenmekti.", "ek_sure": 0.5},
    # ------------------------------------------------------------------ 6
    {"id": "k1", "bolum": "1071 Seferi",
     "metin": "1071 yılının baharında iki hükümdar da harekete geçti. Alparslan, ordusuyla Suriye'ye inmiş, "
              "Fatımilere karşı sefere hazırlanıyordu. Bir yıl önce yol üzerindeki Malazgirt ve Erciş kalelerini "
              "ele geçirmiş, ardından Urfa'yı kuşatmış, sonra Halep'e yönelmişti."},
    {"id": "k2",
     "metin": "Tam bu sırada, Mart ayında, Romen Diyojen de devasa bir orduyla Konstantinopolis'ten yola çıktı. "
              "Bizans ordusu Anadolu'yu boydan boya geçti ve Sivas ile Erzurum üzerinden doğuya ilerledi. Hedef "
              "açıktı: Malazgirt'i geri almak ve Selçukluları Anadolu'dan söküp atmak."},
    {"id": "k3",
     "metin": "Bizans ordusunun yola çıktığı haberi Halep önlerindeki Alparslan'a ulaştığında, sultan büyük bir "
              "karar verdi. Mısır seferini bıraktı ve hızla kuzeye döndü. Ordusunun bir kısmı bu ani dönüşte "
              "dağılmıştı. Ama Alparslan, yol boyunca Türkmen boylarını ve müttefiklerini toplayarak ilerledi."},
    {"id": "k4",
     "metin": "Romen Diyojen ise Erzurum'da kritik bir karar aldı ve ordusunu ikiye böldü. Generali Yusuf "
              "Tarkaniyotis'i ve Normandiyalı paralı asker komutanı Russel'i, ordunun büyük bir bölümüyle Ahlat'a "
              "gönderdi. Kendisi ise geri kalan kuvvetlerle Malazgirt'e yürüdü."},
    {"id": "k5",
     "metin": "Malazgirt'teki küçük Selçuklu garnizonu fazla direnemedi ve kale teslim oldu. Romen bu ilk "
              "başarıyla moral buldu. Ancak Ahlat'a giden ordu, savaşa hiç katılmadan geri çekilecekti. Nedenini "
              "kaynaklar hâlâ tartışıyor. Ama sonuç değişmiyordu: Romen, ordusunun belki de yarısını savaştan önce "
              "kaybetmişti.", "ek_sure": 0.5},
    # ------------------------------------------------------------------ 7
    {"id": "o1", "bolum": "İki Ordu",
     "metin": "Peki, Malazgirt'te karşı karşıya gelecek ordular nasıldı? Önce rakamlara bakalım. Ortaçağ "
              "kaynakları, Bizans ordusunun iki yüz bin, hatta daha fazla olduğunu yazar. Ancak modern tarihçiler "
              "bu sayıları abartılı bulur. Bugünkü tahminlere göre, Malazgirt'e ulaşan Bizans ordusu kırk bin ile "
              "yetmiş bin arasındaydı."},
    {"id": "o2",
     "metin": "Bu ordu rengârenk bir topluluktu. Zırhlı Bizans süvarileri, piyadeler ve okçuların yanında; Ermeni "
              "birlikleri, Frank ve Norman şövalyeleri, bozkır kökenli Uz ve Peçenek atlıları vardı. Bu son grup "
              "çok önemliydi. Çünkü Uzlar da, tıpkı Selçuklular gibi, Oğuz kökenli Türklerdi."},
    {"id": "o3",
     "metin": "Selçuklu ordusu ise daha küçüktü. Tahminler yirmi bin ile otuz bin arasında değişiyor. Ama bu "
              "ordunun büyük kısmı, bozkırın en korkulan silahından oluşuyordu: Atlı okçular. Hafif zırhlı, son "
              "derece hızlı ve at üstündeyken her yöne ok atabilen savaşçılar. Bunların yanında, sultanın seçkin "
              "muhafız süvarileri olan gulamlar bulunuyordu."},
    {"id": "o4",
     "metin": "İki ordu, tamamen farklı iki savaş anlayışını temsil ediyordu. Bizans, sıkı düzen ve göğüs göğüse "
              "çarpışmaya güveniyordu. Selçuklular ise hız, hareket ve sabırla düşmanı yıpratmaya. Malazgirt, bu "
              "iki anlayışın sınavı olacaktı.", "ek_sure": 0.5},
    # ------------------------------------------------------------------ 8
    {"id": "p1", "bolum": "Savaştan Önce",
     "metin": "Malazgirt'i aldıktan sonra Bizans öncü birlikleri, Selçuklu kuvvetleriyle karşılaşmaya başladı. Bu "
              "ilk çatışmalarda Türk atlı okçuları Bizans birliklerini pusuya düşürdü. Bizans komutanlarından "
              "Nikeforos Vasilakis esir alındı. Romen, sultanın bizzat geldiğini ancak şimdi anlıyordu."},
    {"id": "p2",
     "metin": "Savaştan önce Alparslan, imparatora bir elçi gönderdi ve barış teklif etti. Bazı tarihçilere göre "
              "sultan, Fatımi seferine geri dönmek istiyordu ve uzun bir savaşa girmeyi tercih etmiyordu. Ancak "
              "Romen, teklifi ağır şartlar öne sürerek reddetti. Bu kadar büyük bir orduyu buraya kadar "
              "getirmişti. Kesin bir zafer olmadan geri dönmek, onun için siyasi bir intihar olurdu."},
    {"id": "p3",
     "metin": "26 Ağustos 1071, bir Cuma günüydü. Rivayete göre Alparslan, o sabah askerleriyle birlikte Cuma "
              "namazını kıldı. Sonra beyaz bir elbise giydi ve atının kuyruğunu kendi eliyle bağladı. Ardından "
              "askerlerine döndü ve şöyle seslendi."},
    {"id": "p4",
     "metin": "Eğer şehit düşersem, bu beyaz elbise kefenim olsun. Benimle gelmek isteyen gelsin, dönmek isteyen "
              "dönsün. Bugün burada ne emir veren bir sultan var, ne de emir alan bir asker. Ben de sizden "
              "biriyim.", "ek_sure": 1.0},
    {"id": "p5",
     "metin": "Savaşa bizzat katılan Bizanslı tarihçi Mihail Attaleiates, o gün Bizans ordusunun güçlü ve kendinden "
              "emin göründüğünü yazar. Ama Romen'in ordusunda sessiz bir tehlike vardı. Arka saflarda, imparatorun "
              "düşmanı Dukas ailesinden bir komutan bekliyordu: Andronikos Dukas."},
    # ------------------------------------------------------------------ 9
    {"id": "m1", "bolum": "Malazgirt Muharebesi",
     "metin": "Romen Diyojen ordusunu geniş bir hat halinde dizdi. Merkezde bizzat kendisi vardı. Sol kanadı "
              "Nikeforos Briyennios, sağ kanadı Teodor Alyates yönetiyordu. Arkada ise ihtiyat kuvvetleriyle "
              "Andronikos Dukas bekliyordu."},
    {"id": "m2",
     "metin": "Alparslan ise ordusunu hilal biçiminde yaydı. Atlı okçular öndeydi. Ana kuvvetler ise tepelerin "
              "ardında, görünmeden bekliyordu."},
    {"id": "m3",
     "metin": "Öğleden sonra Bizans ordusu ilerlemeye başladı. Selçuklu atlı okçuları ok yağdırıyor, sonra göğüs "
              "göğüse çarpışmaya girmeden geri çekiliyordu. Bu, bozkırın asırlık taktiğiydi: Sahte ricat."},
    {"id": "m4",
     "metin": "Bizans ordusu saatlerce ilerledi. Selçuklu kampına ulaştılar ama kamp boştu. Atlı okçular sürekli ok "
              "atıyor, Bizans süvarileri onları yakalamaya çalıştıkça daha da uzaklaşıyorlardı. Güneş batmaya "
              "yaklaşırken Bizans hatları uzamış, askerler susuz ve yorgun düşmüştü.", "ek_sure": 1.0},
    {"id": "m5",
     "metin": "Romen Diyojen, karanlıkta savunmasız kalmaktan korkarak ordusuna kampa dönme emri verdi. İmparatorluk "
              "sancağı geri döndü. Ama bu emir, cephenin uzak kanatlarında yanlış anlaşıldı. Bazı birlikler, "
              "imparatorun yenildiğini sanarak geri çekilmeye başladı."},
    {"id": "m6",
     "metin": "Tam bu sırada, arka saflardaki Andronikos Dukas, imparatorun öldüğü söylentisini yaydı ve ihtiyat "
              "kuvvetleriyle birlikte savaş alanını terk etti. Romen'in arkası artık tamamen açıktı. Bazı "
              "kaynaklara göre, Bizans ordusundaki Uz atlılarının bir kısmı da bu karmaşada Selçuklu tarafına "
              "geçti.", "ek_sure": 1.0},
    {"id": "m7",
     "metin": "İşte Alparslan'ın beklediği an buydu. Selçuklu kuvvetleri tepelerden inip iki yandan saldırdı. Bizans "
              "kanatları birer birer çöktü. Sağ kanat dağıldı. Sol kanattaki Briyennios ise ağır kayıplar vererek "
              "geri çekildi."},
    {"id": "m8",
     "metin": "Romen Diyojen, merkezdeki birlikleriyle birlikte kuşatıldı. Kaçmayı reddetti ve askerleriyle "
              "sonuna kadar savaştı. Atı öldürüldü, elinden yaralandı. Ve sonunda, bir Bizans imparatoru savaş "
              "meydanında esir düştü.", "ek_sure": 2.0},
    # ------------------------------------------------------------------ 10
    {"id": "e1", "bolum": "Esir İmparator",
     "metin": "Ertesi gün yaralı imparator, Alparslan'ın huzuruna getirildi. Sultan başta, karşısındaki tozlu ve "
              "yorgun askerin imparator olduğuna inanmadı. Ancak esir Bizanslılar onu tanıyınca gerçek ortaya "
              "çıktı. Kaynaklara göre aralarında şöyle bir konuşma geçti."},
    {"id": "e2", "metin": "Alparslan sordu: Eğer ben senin önüne esir olarak getirilseydim, ne yapardın?",
     "ek_sure": 0.8},
    {"id": "e3", "metin": "Romen dürüstçe cevap verdi: Belki seni öldürürdüm. Belki de Konstantinopolis "
                          "sokaklarında teşhir ederdim.", "ek_sure": 0.8},
    {"id": "e4", "metin": "Alparslan'ın cevabı tarihe geçti: Benim cezam bundan çok daha ağır. Seni affediyor ve "
                          "serbest bırakıyorum.", "ek_sure": 1.5},
    {"id": "e5",
     "metin": "Alparslan, imparatora büyük bir saygıyla davrandı ve onu kendi sofrasına oturttu. Bir hafta kadar "
              "sonra iki hükümdar arasında bir antlaşma yapıldı. Kaynaklara göre Bizans, büyük bir fidye ve yıllık "
              "vergi ödemeyi, Müslüman esirleri serbest bırakmayı ve bazı sınır şehirlerini teslim etmeyi kabul "
              "etti. Romen Diyojen, Selçuklu askerlerinin eşliğinde ülkesine uğurlandı.", "ek_sure": 0.5},
    # ------------------------------------------------------------------ 11
    {"id": "n1", "bolum": "Sonuçlar",
     "metin": "Ancak Romen'i Konstantinopolis'te bir zafer kutlaması beklemiyordu. Dukaslar, imparatorun esir "
              "düştüğünü duyar duymaz sarayda darbe yapmış ve Mihail Dukas'ı tahta çıkarmışlardı. Romen, tahtını "
              "geri almak için savaştı ama yenildi. Canının bağışlanacağına dair söz verilerek teslim oldu. Fakat "
              "bu söz tutulmadı. 1072 yılında gözlerine mil çekildi ve kısa süre sonra, aldığı yaraların etkisiyle "
              "öldü."},
    {"id": "n2",
     "metin": "Rivayete göre Alparslan, imparatorun başına gelenleri duyunca çok öfkelendi ve antlaşmanın artık "
              "geçerli olmadığını ilan etti. Ama Alparslan da uzun yaşamadı. 1072'de Orta Asya'daki bir sefer "
              "sırasında, esir alınan bir kale komutanı tarafından hançerlenerek öldürüldü. Yerine oğlu Melikşah "
              "geçti."},
    {"id": "n3",
     "metin": "Malazgirt'ten sonra Bizans'ın doğu sınırı fiilen çöktü. Bizans'ta yıllarca süren iç savaşlar, "
              "Türkmen boylarının Anadolu'ya akın akın gelmesinin önünü açtı. Sadece birkaç yıl içinde Türkler, "
              "Anadolu'nun içlerine, hatta Ege kıyılarına kadar ulaştı."},
    {"id": "n4",
     "metin": "Kutalmışoğlu Süleyman Şah, 1075 civarında İznik'i ele geçirdi ve burayı başkent yaptı. Böylece "
              "Anadolu Selçuklu Devleti kuruldu. Konstantinopolis'in hemen karşısında, bir Türk devleti "
              "yükseliyordu."},
    {"id": "n5",
     "metin": "Çaresiz kalan Bizans, Batı'dan yardım istedi. 1095 yılında Papa İkinci Urbanus, Bizans'ın yardım "
              "çağrısının ardından Haçlı Seferi çağrısını yaptı. Yani Malazgirt'in yankıları, Avrupa'dan Kudüs'e "
              "uzanan, iki yüz yıllık bir çatışma döneminin de başlangıcı oldu.", "ek_sure": 1.0},
    # ------------------------------------------------------------------ 12
    {"id": "x1", "bolum": "Kapanış",
     "metin": "Malazgirt, bugün Türk tarihinin en önemli dönüm noktalarından biri olarak anılıyor. Öyle ki, sekiz "
              "yüz elli bir yıl sonra, 26 Ağustos 1922'de başlayan Büyük Taarruz da aynı güne denk geliyordu. Bir "
              "Ağustos günü başlayan bu hikâye, Anadolu'yu yurt edinen bir milletin hikâyesine dönüştü."},
    {"id": "x2", "metin": "Bir sonraki büyük savaşta görüşmek üzere.", "ek_sure": 3.0},
]

# ---------------------------------------------------------------- haritalar
_DENIZ = [(34.5, 43.2, "Karadeniz", 34, "deniz"), (31.0, 34.2, "Akdeniz", 34, "deniz"),
          (50.6, 40.8, "Hazar Denizi", 30, "deniz")]
ANADOLU = Harita(25.5, 47.5, 38.6, etiketler=_DENIZ + [(33.5, 39.0, "Anadolu", 34, "bolge")], tohum=21,
                 dag_olcek=1.4)
ORTA = Harita(23.0, 58.0, 35.6, etiketler=_DENIZ + [(52.5, 33.5, "İran", 30, "bolge"),
                                                     (29.5, 26.8, "Mısır", 30, "bolge")], tohum=22)
GENIS = Harita(19.0, 73.0, 36.5, etiketler=_DENIZ + [(52.5, 32.0, "İran", 30, "bolge"),
                                                      (61.5, 35.0, "Horasan", 26, "bolge"),
                                                      (66.0, 41.5, "Maveraünnehir", 24, "bolge"),
                                                      (68.0, 46.2, "Oğuz Bozkırları", 24, "bolge")],
                tohum=23, dag_olcek=0.8)
BATI = Harita(11.0, 50.0, 39.6, etiketler=_DENIZ + [(26.0, 46.2, "Peçenek Bozkırları", 24, "bolge"),
                                                     (14.5, 43.5, "İtalya", 26, "bolge")], tohum=24)

# Yaklaşık sınırlar (kara ile kırpılır; temsili, kesin sınır değildir)
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

KOORD = {
    "İstanbul": (28.98, 41.01), "Malazgirt": (42.54, 39.14), "Ahlat": (42.49, 38.75), "Erzurum": (41.27, 39.9),
    "Sivas": (37.02, 39.75), "Kayseri": (35.48, 38.72), "Ankara": (32.86, 39.93), "İzmit": (29.92, 40.77),
    "Ani": (43.57, 40.5), "Urfa": (38.79, 37.16), "Halep": (37.15, 36.2), "Musul": (43.13, 36.34),
    "Hoy": (44.95, 38.55), "Erciş": (43.36, 39.03), "Malatya": (38.31, 38.35), "Bağdat": (44.37, 33.31),
    "Kahire": (31.24, 30.04), "Cend": (65.6, 44.8), "Buhara": (64.42, 39.77), "Merv": (61.83, 37.6),
    "Dandanakan": (62.2, 37.1), "Rey": (51.43, 35.59), "İsfahan": (51.67, 32.65), "Nişabur": (58.8, 36.2),
    "Pasinler": (41.68, 39.98), "İznik": (29.72, 40.43), "Konya": (32.48, 37.87), "Bari": (16.87, 41.12),
    "Antakya": (36.16, 36.2), "Kudüs": (35.21, 31.77), "Gazne": (68.42, 33.55), "Trabzon": (39.72, 41.0),
}


def _sehir(h, ad, t0, t1=1e9, **k):
    lon, lat = KOORD[ad]
    return Sehir(h, lon, lat, ad, t0, t1, **k)


def _rota(h, taraf, adlar_veya_nokta, t0, t1, **k):
    pts = [KOORD[a] if isinstance(a, str) else a for a in adlar_veya_nokta]
    return Rota(h, taraf, pts, t0, t1, **k)


def _kamera(sc, h, t0, t1, lon, lat, zoom):
    x, y = h.proj(lon, lat)
    sc.kamera_git(t0, t1, x=x, y=y, zoom=zoom)


def _kamera_ayarla(sc, h, t, lon, lat, zoom):
    x, y = h.proj(lon, lat)
    sc.kamera_ayarla(t, x=x, y=y, zoom=zoom)


def kur(v, T):
    ids = [b["id"] for b in BOLUMLER]
    s = {k: a for k, (a, b) in T.items()}
    e = {k: b for k, (a, b) in T.items()}

    def aralik(ilk, son):
        t0 = 0.0 if ilk == ids[0] else s[ilk] - 0.4
        j = ids.index(son) + 1
        t1 = s[ids[j]] - 0.4 if j < len(ids) else 1e9
        return t0, t1

    koyu = koyu_arka_plan(ANADOLU)
    v.acilis(0, 1.5)

    # Bölüm etiketleri (sol üst)
    for b in BOLUMLER:
        if b.get("bolum") and b["id"] not in ("g1", "x1"):
            v.ekran(BolumEtiketi(b["bolum"], s[b["id"]] + 0.3, s[b["id"]] + 6.5))

    # ============================================================ 1) GİRİŞ
    sc = v.sahne(*aralik("g1", "g2"), ANADOLU.yuzey)
    h = ANADOLU
    _kamera_ayarla(sc, h, 0, 36.5, 38.6, 1.0)
    sc.ekle(Bolge(h, "bizans", BIZANS_1071, 2.5, ad="Bizans", etiket_konum=(33.0, 39.6)),
            Bolge(h, "selcuklu", SELCUKLU_1071, 5, ad="Büyük Selçuklu", etiket_konum=(45.8, 36.0)))
    sc.ekle(_sehir(h, "İstanbul", 3.5, onemli=True), _sehir(h, "Malazgirt", 1.5, onemli=True, nabiz=True))
    _kamera(sc, h, 1.0, s["g1"] + 6, 42.0, 39.0, 2.2)
    _kamera(sc, h, s["g1"] + 7, e["g1"], 36.5, 38.6, 1.0)
    _kamera(sc, h, s["g2"], e["g2"], 39.5, 38.8, 1.25)

    sc = v.sahne(*aralik("g3", "g3"), koyu)
    sc.ekle(BuyukYazi("MALAZGİRT", s["g3"] + 0.5, e["g3"] + 0.4, ust="Büyük Savaşlar",
                      alt="26 Ağustos 1071", boyut=170))
    sc.kamera_git(s["g3"], e["g3"], zoom=1.06)

    # ============================================================ 2) BOZKIRDAN DOĞAN GÜÇ
    sc = v.sahne(*aralik("s1", "s5"), GENIS.yuzey)
    h = GENIS
    t = s["s1"]
    _kamera_ayarla(sc, h, t - 1, 63, 42.5, 1.9)
    sc.ekle(_sehir(h, "Cend", t + 3, e["s2"], onemli=True, nabiz=True))
    sc.ekle(EtiketBalonu("Selçuk Bey", t + 6, e["s1"], x=h.proj(*KOORD["Cend"])[0],
                         y=h.proj(*KOORD["Cend"])[1] - 60))
    t = s["s2"]
    _kamera(sc, h, t, t + 3, 63.5, 38.5, 1.5)
    sc.ekle(_rota(h, "selcuklu", ["Cend", "Buhara", "Merv"], t + 0.5, t + 5, t_son=e["s3"],
                  etiket="Tuğrul ve Çağrı"))
    gaz = sc.ekle(Bolge(h, "gazneli", GAZNELI, t + 5, ad="Gazneliler", etiket_konum=(66.5, 33.0)))
    sc.ekle(_sehir(h, "Merv", t + 4), _sehir(h, "Nişabur", t + 6), _sehir(h, "Gazne", t + 6.5))
    t = s["s3"]
    _kamera(sc, h, t, t + 2.5, 62.2, 37.3, 2.4)
    sc.ekle(_sehir(h, "Dandanakan", t + 1, e["s3"] + 1, onemli=True, nabiz=True, yon="alt"))
    sc.ekle(EtiketBalonu("1040 — Dandanakan Zaferi", e["s3"] - 7, e["s3"], x=h.proj(62.2, 37.1)[0],
                         y=h.proj(62.2, 37.1)[1] - 70))
    gaz.kaybol(e["s3"] - 3)
    sc.ekle(Bolge(h, "selcuklu", SELCUKLU_1040, e["s3"] - 3, s["s4"] + 4, ad="Selçuklu", etiket_konum=(59.5, 37.2),
                  etiket_boyut=26))
    t = s["s4"]
    _kamera(sc, h, t, t + 4, 52, 35.5, 1.15)
    sc.ekle(Bolge(h, "selcuklu", SELCUKLU_1055, t + 2, ad="Büyük Selçuklu", etiket_konum=(54.5, 33.0)))
    sc.ekle(_sehir(h, "Rey", t + 3), _sehir(h, "İsfahan", t + 3.5), _sehir(h, "Bağdat", t + 6, onemli=True, nabiz=True))
    sc.ekle(_rota(h, "selcuklu", ["Rey", (48.0, 34.6), "Bağdat"], t + 5, t + 8, t_son=e["s4"], etiket="1055"))
    t = s["s5"]
    _kamera(sc, h, t, t + 4, 41, 38.5, 1.7)
    sc.ekle(Bolge(h, "bizans", BIZANS_1025, t + 1, ad="Bizans", etiket_konum=(32.5, 39.2)))
    for i, (bas, son) in enumerate((((47, 37.5), (39.5, 39.5)), ((46, 39.5), (40.5, 40.6)),
                                     ((45.5, 36.5), (38.5, 38.0)))):
        sc.ekle(HareketOku("selcuklu", [h.proj(*bas), h.proj(*son)], t + 3 + i * 0.7, t + 6 + i * 0.7,
                           t_son=e["s5"] + 0.3, kalinlik=12))
    sc.ekle(_sehir(h, "Pasinler", t + 8, onemli=True, nabiz=True, yon="ust"))

    # ============================================================ 3) BİZANS'IN KRİZİ
    sc = v.sahne(*aralik("b1", "b3"), BATI.yuzey)
    h = BATI
    t = s["b1"]
    _kamera_ayarla(sc, h, t - 1, 30.5, 39.6, 1.0)
    sc.ekle(Bolge(h, "bizans", BIZANS_1025, t + 3, ad="Bizans İmparatorluğu", etiket_konum=(32.0, 39.3)),
            Bolge(h, "bizans", BIZANS_ITALYA, t + 3, s["b3"] + 9))
    sc.ekle(_sehir(h, "İstanbul", t + 2, onemli=True, nabiz=True))
    sc.ekle(EtiketBalonu("1025 — İkinci Basileios ölüyor", e["b1"] - 4, e["b1"] + 0.3,
                         x=h.proj(*KOORD["İstanbul"])[0], y=h.proj(*KOORD["İstanbul"])[1] - 60))
    t = s["b2"]
    _kamera(sc, h, t, e["b2"], 33, 40.0, 1.35)
    ix, iy = h.proj(*KOORD["İstanbul"])
    sc.ekle(EtiketBalonu("Saray entrikaları", t + 2, t + 8, x=ix, y=iy - 60),
            EtiketBalonu("Askeri harcamalar kısılıyor", t + 9, e["b2"] - 5, x=ix, y=iy - 60))
    ax, ay = h.proj(42.5, 40.0)
    sc.ekle(EtiketBalonu("Sınır ordusu dağıtıldı", e["b2"] - 5, e["b2"] + 0.3, x=ax, y=ay - 40, renk=(1, 0.75, 0.6)))
    t = s["b3"]
    _kamera(sc, h, t, t + 3, 25, 41.5, 1.1)
    sc.ekle(HareketOku("pecenek", [h.proj(31, 47.2), h.proj(28.5, 45.5), h.proj(26.5, 43.6)], t + 7, t + 10,
                       t_son=e["b3"] + 0.3, kalinlik=18))
    sc.ekle(EtiketBalonu("Peçenekler", t + 8, e["b3"], x=h.proj(30.5, 46.4)[0], y=h.proj(30.5, 46.4)[1] - 30))
    sc.ekle(HareketOku("norman", [h.proj(12.5, 43.3), h.proj(14.5, 42.0), h.proj(16.5, 41.0)], t + 10, t + 13,
                       t_son=e["b3"] + 0.3, kalinlik=18))
    sc.ekle(EtiketBalonu("Normanlar", t + 11, e["b3"], x=h.proj(13.0, 42.8)[0], y=h.proj(13.0, 42.8)[1] - 40))

    sc = v.sahne(*aralik("b4", "b4"), ANADOLU.yuzey)
    h = ANADOLU
    t = s["b4"]
    _kamera_ayarla(sc, h, t - 1, 39, 39.3, 1.4)
    sc.ekle(Bolge(h, "bizans", BIZANS_1071, t - 1, ad="Bizans", etiket_konum=(32.0, 39.4)),
            Bolge(h, "selcuklu", SELCUKLU_1071, t - 1, ad="Selçuklu", etiket_konum=(45.5, 37.0)))
    sc.ekle(_sehir(h, "Ani", t + 2, onemli=True, nabiz=True, yon="ust"))
    sc.ekle(EtiketBalonu("1064", t + 3, t + 8, x=h.proj(*KOORD["Ani"])[0], y=h.proj(*KOORD["Ani"])[1] - 70))
    sc.ekle(_sehir(h, "Kayseri", t + 7, onemli=True, nabiz=True))
    sc.ekle(EtiketBalonu("1067", t + 8, e["b4"], x=h.proj(*KOORD["Kayseri"])[0],
                         y=h.proj(*KOORD["Kayseri"])[1] - 70))
    for i, (bas, son) in enumerate((((44.5, 38.2), (35.8, 38.9)), ((43.5, 37.2), (37.5, 38.0)),
                                     ((44.0, 40.0), (38.0, 40.0)), ((42.5, 36.8), (34.0, 38.2)))):
        sc.ekle(HareketOku("selcuklu", [h.proj(*bas), h.proj(*son)], t + 9 + i * 0.6, t + 12 + i * 0.6,
                           t_son=e["b4"] + 0.3, kalinlik=13))

    sc = v.sahne(*aralik("b5", "b5"), koyu)
    t = s["b5"]
    sc.ekle(ZamanCizelgesi("Yükselen ve Yorulan", [
        (t + 0.5, "1025", "İkinci Basileios ölür", "bizans"),
        (t + 1.5, "1040", "Dandanakan Zaferi", "selcuklu"),
        (t + 2.5, "1048", "Pasinler Savaşı", "selcuklu"),
        (t + 3.5, "1055", "Tuğrul Bey Bağdat'ta", "selcuklu"),
        (t + 4.5, "1064", "Ani'nin fethi", "selcuklu"),
        (t + 5.5, "1068", "Romen Diyojen tahtta", "bizans"),
    ], t, e["b5"] + 0.6))

    # ============================================================ 4) ALPARSLAN
    sc = v.sahne(*aralik("a1", "a2"), koyu)
    t = s["a1"]
    sc.kamera_git(t, e["a2"], zoom=1.04)
    sc.ekle(KarakterKarti("Alparslan", "Büyük Selçuklu Sultanı", "Saltanatı: 1064 – 1072", "selcuklu",
                          t + 0.3, e["a2"] + 0.6, monogram="A", maddeler=[
                              (t + 6, "Çağrı Bey'in oğlu, Tuğrul Bey'in yeğeni"),
                              (e["a1"] - 4, "Adının anlamı: Yiğit Aslan"),
                              (s["a2"] + 2, "Tecrübeli bir süvari komutanı"),
                              (s["a2"] + 7, "Veziri: Nizamülmülk"),
                          ]))

    sc = v.sahne(*aralik("a3", "a4"), ORTA.yuzey)
    h = ORTA
    t = s["a3"]
    _kamera_ayarla(sc, h, t - 1, 42, 38.5, 1.6)
    sc.ekle(Bolge(h, "bizans", BIZANS_1071, t - 1, ad="Bizans", etiket_konum=(32.0, 39.4)),
            Bolge(h, "selcuklu", SELCUKLU_1071, t - 1, ad="Büyük Selçuklu", etiket_konum=(52.0, 34.8)))
    sc.ekle(_sehir(h, "Ani", t + 1, onemli=True, nabiz=True, yon="ust"))
    _kamera(sc, h, t + 6, t + 10, 38, 33.5, 1.0)
    sc.ekle(Bolge(h, "fatimi", FATIMI, t + 7, ad="Fatımiler", etiket_konum=(29.5, 28.5)))
    sc.ekle(_sehir(h, "Kahire", t + 8, onemli=True), _sehir(h, "Bağdat", t + 8))
    sc.ekle(_rota(h, "selcuklu", ["Bağdat", (40.0, 33.6), (35.5, 31.5), "Kahire"], t + 9, t + 13,
                  t_son=e["a3"] + 0.3, etiket="Asıl hedef"))
    t = s["a4"]
    _kamera(sc, h, t, t + 3, 34, 38.8, 1.5)
    for i, (bas, son) in enumerate((((42.5, 38.0), (36.0, 39.0)), ((41.5, 37.0), (34.5, 37.8)))):
        sc.ekle(HareketOku("selcuklu", [h.proj(*bas), h.proj(*son)], t + 0.5 + i * 0.6, t + 3 + i * 0.6,
                           t_son=e["a4"] + 0.3, kalinlik=12))
    sc.ekle(EtiketBalonu("Türkmen akınları", t + 2, t + 7, x=h.proj(37.5, 38.6)[0], y=h.proj(37.5, 38.6)[1] - 50))
    _kamera(sc, h, t + 7, e["a4"], 29.0, 40.5, 2.2)
    sc.ekle(_sehir(h, "İstanbul", t + 6, onemli=True, nabiz=True))

    # ============================================================ 5) ROMEN DİYOJEN
    sc = v.sahne(*aralik("r1", "r3"), koyu)
    t = s["r1"]
    sc.kamera_git(t, e["r3"], zoom=1.05)
    sc.ekle(KarakterKarti("Romen Diyojen", "Bizans İmparatoru", "Saltanatı: 1068 – 1071", "bizans",
                          t + 0.3, e["r3"] + 0.6, monogram="R", maddeler=[
                              (t + 5, "Kapadokyalı köklü bir askeri aileden"),
                              (s["r2"] + 1, "İmparatoriçe Evdokia ile evlenerek tahta çıktı"),
                              (s["r2"] + 8, "Sarayda güçlü rakipleri: Dukas ailesi"),
                              (s["r3"] + 2, "1068 ve 1069'da doğu seferleri"),
                              (e["r3"] - 6, "Hedefi: Sultanı meydan savaşında yenmek"),
                          ]))

    # ============================================================ 6) 1071 SEFERİ
    sc = v.sahne(*aralik("k1", "k3"), ORTA.yuzey)
    h = ORTA
    t = s["k1"]
    _kamera_ayarla(sc, h, t - 1, 40, 37.8, 1.6)
    sc.ekle(Bolge(h, "bizans", BIZANS_1071, t - 1, ad="Bizans", etiket_konum=(32.0, 39.4)),
            Bolge(h, "selcuklu", SELCUKLU_1071, t - 1, ad="Büyük Selçuklu", etiket_konum=(52.0, 34.8)),
            Bolge(h, "fatimi", FATIMI, t - 1, ad="Fatımiler", etiket_konum=(29.5, 28.5)))
    sc.ekle(_sehir(h, "Malazgirt", t + 7, yon="ust"), _sehir(h, "Erciş", t + 7.5, yon="sag"),
            _sehir(h, "Urfa", t + 9.5), _sehir(h, "Halep", t + 11, onemli=True))
    sc.ekle(_rota(h, "selcuklu", ["Hoy", "Erciş", "Malazgirt", (40.5, 38.3), "Urfa", "Halep"], t + 6, t + 13,
                  t_son=s["k3"] + 1, etiket="Alparslan"))
    t = s["k2"]
    _kamera(sc, h, t, t + 3, 34, 39.5, 1.3)
    sc.ekle(_sehir(h, "İstanbul", t + 1, onemli=True), _sehir(h, "Sivas", t + 7), _sehir(h, "Erzurum", t + 9))
    sc.ekle(_rota(h, "bizans", ["İstanbul", "İzmit", "Ankara", "Sivas", "Erzurum"], t + 2, t + 11,
                  t_son=1e9, etiket="Romen Diyojen", kalinlik=18))
    t = s["k3"]
    _kamera(sc, h, t, t + 3, 41, 37.8, 1.6)
    sc.ekle(EtiketBalonu("Mısır seferi iptal!", t + 4, t + 9, x=h.proj(*KOORD["Halep"])[0],
                         y=h.proj(*KOORD["Halep"])[1] - 55))
    sc.ekle(_sehir(h, "Musul", t + 8), _sehir(h, "Ahlat", t + 13, yon="sol"))
    sc.ekle(_rota(h, "selcuklu", ["Halep", "Musul", "Hoy", "Ahlat"], t + 8, t + 15, t_son=1e9,
                  etiket="Alparslan"))

    sc = v.sahne(*aralik("k4", "k5"), ANADOLU.yuzey)
    h = ANADOLU
    t = s["k4"]
    _kamera_ayarla(sc, h, t - 1, 41.8, 39.2, 2.4)
    sc.ekle(Bolge(h, "bizans", BIZANS_1071, t - 1, alfa=0.3), Bolge(h, "selcuklu", SELCUKLU_1071, t - 1, alfa=0.3))
    sc.ekle(_sehir(h, "Erzurum", t - 1, onemli=True), _sehir(h, "Malazgirt", t - 1, yon="ust"),
            _sehir(h, "Ahlat", t - 1, yon="sol"))
    sc.ekle(_rota(h, "bizans", ["Erzurum", (41.6, 39.0), "Ahlat"], t + 4, t + 9, t_son=s["k5"] + 8,
                  etiket="Tarkaniyotis ve Russel"))
    sc.ekle(_rota(h, "bizans", ["Erzurum", (41.9, 39.6), "Malazgirt"], t + 10, t + 14, t_son=1e9,
                  etiket="Romen Diyojen"))
    t = s["k5"]
    mx, my = h.proj(*KOORD["Malazgirt"])
    sc.ekle(EtiketBalonu("Kale teslim oldu", t + 1, t + 6, x=mx, y=my - 70))
    sc.ekle(_rota(h, "pecenek", ["Ahlat", (40.5, 38.6), "Malatya"], t + 8, t + 13, t_son=e["k5"] + 0.3,
                  etiket="Savaşmadan çekildi"))
    _kamera(sc, h, t + 7, t + 11, 40.5, 38.8, 1.7)
    sc.ekle(_sehir(h, "Malatya", t + 8))

    # ============================================================ 7) İKİ ORDU
    sc = v.sahne(*aralik("o1", "o4"), koyu)
    t = s["o1"]
    sc.kamera_git(t, e["o4"], zoom=1.03)
    sc.ekle(Karsilastirma(
        {"taraf": "bizans", "baslik": "Bizans", "sayi": "40-70 bin", "alt": "modern tahmin",
         "maddeler": [(s["o2"] + 1, "Zırhlı süvari, piyade ve okçular"),
                      (s["o2"] + 6, "Ermeni, Frank ve Norman birlikleri"),
                      (s["o2"] + 10, "Uz ve Peçenek paralı atlıları"),
                      (s["o4"] + 4, "Taktik: sıkı düzen, göğüs göğüse")]},
        {"taraf": "selcuklu", "baslik": "Büyük Selçuklu", "sayi": "20-30 bin", "alt": "modern tahmin",
         "maddeler": [(s["o3"] + 7, "Türkmen atlı okçular"),
                      (s["o3"] + 14, "Hızlı ve hafif zırhlı"),
                      (e["o3"] - 4, "Sultanın seçkin gulam süvarileri"),
                      (s["o4"] + 8, "Taktik: yıpratma ve sahte ricat")]},
        t + 0.5, e["o4"] + 0.6, baslik="Karşı Karşıya"))

    # ============================================================ 8) SAVAŞTAN ÖNCE
    sc = v.sahne(*aralik("p1", "p2"), ANADOLU.yuzey)
    h = ANADOLU
    t = s["p1"]
    _kamera_ayarla(sc, h, t - 1, 42.4, 38.95, 2.6)
    sc.ekle(_sehir(h, "Malazgirt", t - 1, onemli=True, yon="ust"), _sehir(h, "Ahlat", t - 1, onemli=True, yon="sol"))
    sc.ekle(HareketOku("bizans", [h.proj(42.54, 39.08), h.proj(42.5, 38.88)], t + 1, t + 4, t_son=t + 12, kalinlik=10))
    sc.ekle(HareketOku("selcuklu", [h.proj(42.2, 38.82), h.proj(42.45, 38.88)], t + 5, t + 7, t_son=t + 12, kalinlik=10),
            HareketOku("selcuklu", [h.proj(42.8, 38.82), h.proj(42.6, 38.88)], t + 5.5, t + 7.5, t_son=t + 12, kalinlik=10))
    sc.ekle(EtiketBalonu("Vasilakis esir alındı", t + 8, e["p1"], x=h.proj(42.52, 38.9)[0],
                         y=h.proj(42.52, 38.9)[1] - 40, renk=(1, 0.75, 0.6)))
    t = s["p2"]
    sc.ekle(_rota(h, "selcuklu", [(42.49, 38.8), (42.53, 39.08)], t + 1, t + 5, t_son=e["p2"],
                  kalinlik=8, etiket="Barış elçisi"))
    sc.ekle(EtiketBalonu("Teklif reddedildi", t + 12, e["p2"], x=h.proj(42.54, 39.14)[0],
                         y=h.proj(42.54, 39.14)[1] - 50, renk=(1, 0.75, 0.6)))

    sc = v.sahne(*aralik("p3", "p4"), koyu)
    t = s["p3"]
    sc.ekle(BuyukYazi("26 Ağustos 1071", t + 0.3, e["p3"] + 0.2, ust="Cuma", alt="Malazgirt Ovası", boyut=120))
    sc.ekle(AlintiKarti("Eğer şehit düşersem, bu beyaz elbise kefenim olsun. Benimle gelmek isteyen gelsin, "
                        "dönmek isteyen dönsün. Bugün burada ne emir veren bir sultan var, ne de emir alan bir "
                        "asker. Ben de sizden biriyim.", "Alparslan (rivayet)", s["p4"], e["p4"] + 0.6,
                        taraf="selcuklu"))
    sc.kamera_git(t, e["p4"], zoom=1.05)

    # ============================================================ 8-9) TAKTİK SAVAŞ ALANI
    sc = v.sahne(*aralik("p5", "m8"), arka_plan_uret(
        zemin="bozkir",
        tepeler=[(260, 170, 300, 0.9), (1660, 160, 320, 0.95), (960, 60, 260, 0.55),
                 (80, 620, 200, 0.4), (1850, 640, 220, 0.45)],
        nehirler=[[(-20, 760), (90, 820), (160, 940), (120, 1100)]],
        yollar=[[(230, 1000), (520, 960), (900, 1010), (1300, 990), (1940, 1030)]],
        yerlesimler=[(250, 990, "Malazgirt")],
        etiketler=[(1380, 965, "Malazgirt Ovası", 40)], tohum=1071))
    _taktik(sc, v, s, e)

    # ============================================================ 10) ESİR İMPARATOR
    sc = v.sahne(*aralik("e1", "e5"), koyu)
    t = s["e1"]
    sc.kamera_git(t, e["e5"], zoom=1.05)
    sc.ekle(BuyukYazi("Esir İmparator", t + 0.3, e["e1"] + 0.3, ust="Ertesi gün", alt="Sultanın otağında",
                      boyut=130))
    sc.ekle(AlintiKarti("Eğer ben senin önüne esir olarak getirilseydim, ne yapardın?", "Alparslan",
                        s["e2"], e["e2"] + 0.3, taraf="selcuklu"),
            AlintiKarti("Belki seni öldürürdüm. Belki de Konstantinopolis sokaklarında teşhir ederdim.",
                        "Romen Diyojen", s["e3"], e["e3"] + 0.3, taraf="bizans"),
            AlintiKarti("Benim cezam bundan çok daha ağır. Seni affediyor ve serbest bırakıyorum.", "Alparslan",
                        s["e4"], e["e4"] + 0.3, taraf="selcuklu"))
    t = s["e5"]
    sc.ekle(KarakterKarti("Antlaşma", "Malazgirt Sonrası", "Ağustos – Eylül 1071", "notr", t + 0.3, e["e5"] + 0.6,
                          monogram="1071", maddeler=[
                              (t + 9, "Büyük bir fidye ve yıllık vergi"),
                              (t + 12, "Müslüman esirlerin serbest bırakılması"),
                              (t + 15, "Bazı sınır şehirlerinin teslimi"),
                              (e["e5"] - 5, "İmparator ülkesine uğurlandı"),
                          ]))

    # ============================================================ 11) SONUÇLAR
    sc = v.sahne(*aralik("n1", "n2"), koyu)
    t = s["n1"]
    sc.kamera_git(t, e["n2"], zoom=1.04)
    sc.ekle(KarakterKarti("Romen Diyojen", "Bir İmparatorun Sonu", "1071 – 1072", "bizans", t + 0.3, e["n1"] + 0.3,
                          monogram="R", maddeler=[
                              (t + 6, "Dukaslar sarayda darbe yaptı"),
                              (t + 9, "Mihail Dukas tahta çıktı"),
                              (t + 17, "Söz verilerek teslim alındı"),
                              (e["n1"] - 6, "1072: Gözlerine mil çekildi, öldü"),
                          ]))
    t = s["n2"]
    sc.ekle(KarakterKarti("Alparslan", "Bir Sultanın Sonu", "1072", "selcuklu", t + 0.3, e["n2"] + 0.6,
                          monogram="A", maddeler=[
                              (t + 3, "Antlaşmayı geçersiz saydı (rivayet)"),
                              (t + 10, "1072: Orta Asya seferinde hançerlendi"),
                              (e["n2"] - 3, "Yerine oğlu Melikşah geçti"),
                          ]))

    sc = v.sahne(*aralik("n3", "n4"), ANADOLU.yuzey)
    h = ANADOLU
    t = s["n3"]
    _kamera_ayarla(sc, h, t - 1, 36.5, 38.6, 1.0)
    b71 = sc.ekle(Bolge(h, "bizans", BIZANS_1071, t - 1, ad="Bizans", etiket_konum=(32.0, 39.4)))
    sc.ekle(Bolge(h, "selcuklu", SELCUKLU_1071, t - 1, ad="Büyük Selçuklu", etiket_konum=(45.5, 36.6)))
    for i, (bas, son) in enumerate((((43, 38.5), (31.0, 39.5)), ((42, 37.5), (32.5, 37.6)), ((43, 40.0), (34.0, 40.6)),
                                     ((40, 38.6), (28.0, 38.5)), ((41, 39.5), (30.0, 40.2)))):
        sc.ekle(HareketOku("selcuklu", [h.proj(*bas), h.proj(*son)], t + 2 + i * 0.8, t + 7 + i * 0.8,
                           t_son=e["n3"] + 0.3, kalinlik=14))
    t = s["n4"]
    b71.kaybol(t + 1)
    sc.ekle(Bolge(h, "bizans", BIZANS_1080, t + 1, ad="Bizans", etiket_konum=(27.0, 41.6), etiket_boyut=28),
            Bolge(h, "bizans", BIZANS_KARADENIZ, t + 1),
            Bolge(h, "selcuklu", TURKIYE_SELCUKLU, t + 2, ad="Anadolu Selçuklu", etiket_konum=(34.8, 38.8)))
    sc.ekle(_sehir(h, "İznik", t + 3, onemli=True, nabiz=True, yon="alt"), _sehir(h, "İstanbul", t + 3, onemli=True))
    _kamera(sc, h, t + 3, e["n4"], 32.5, 39.6, 1.5)

    sc = v.sahne(*aralik("n5", "n5"), koyu)
    t = s["n5"]
    sc.ekle(ZamanCizelgesi("Malazgirt'in Yankıları", [
        (t + 0.5, "1071", "Malazgirt Zaferi", "selcuklu"),
        (t + 1.5, "1072", "Romen ve Alparslan ölür", "notr"),
        (t + 2.5, "1075", "İznik başkent olur", "selcuklu"),
        (t + 3.5, "1081", "Aleksios Komnenos tahtta", "bizans"),
        (t + 5.0, "1095", "Haçlı Seferi çağrısı", "hacli"),
        (t + 6.5, "1096", "Birinci Haçlı Seferi", "hacli"),
    ], t, e["n5"] + 0.6))

    # ============================================================ 12) KAPANIŞ
    sc = v.sahne(*aralik("x1", "x2"), ANADOLU.yuzey)
    h = ANADOLU
    t = s["x1"]
    _kamera_ayarla(sc, h, t - 1, 42.5, 39.1, 2.6)
    _kamera(sc, h, t, e["x1"], 35.5, 38.8, 1.0)
    sc.ekle(_sehir(h, "Malazgirt", t - 1, onemli=True, nabiz=True))
    sc.ekle(Bolge(h, "selcuklu", TURKIYE_SELCUKLU, t + 4, alfa=0.35))
    v.ekran(BaslikKarti("BÜYÜK SAVAŞLAR", "MALAZGİRT", "26 Ağustos 1071", s["x2"] - 0.2, e["x2"] + 2))
    v.kapanis(e["x2"] + 0.5, 1.5)


def _taktik(sc, v, s, e):
    """Malazgirt muharebesi taktik animasyonu (p5 + m1..m8)."""
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
    sc.ekle(*bz.values(), *okcular, sol_ana, sag_ana, sultan)

    romen = Komutan("Romen Diyojen", "bizans", bz["mer_a"], ofset=(0, -118), unvan="İmparator")
    bri = Komutan("Briyennios", "bizans", bz["sol_p"], ofset=(0, -105))
    aly = Komutan("Alyates", "bizans", bz["sag_p"], ofset=(0, -105))
    dukas = Komutan("Andronikos Dukas", "bizans", bz["ihtiyat"], ofset=(300, -30))
    alp = Komutan("Alparslan", "selcuklu", sultan, ofset=(0, -112), unvan="Sultan")
    sc.ekle(romen, bri, aly, dukas, alp)

    # ---- p5: ordu görünür, Dukas'a dikkat
    t = s["p5"]
    sc.kamera_ayarla(t - 1, x=960, y=760, zoom=1.0)
    for i, b in enumerate(bz.values()):
        b.belir(t + 0.5 + i * 0.25)
    sc.kamera_git(e["p5"] - 7, e["p5"] - 3, x=1040, y=930, zoom=1.7)
    dukas.belir(e["p5"] - 5)
    sc.ekle(EtiketBalonu("Dukas ailesinden", e["p5"] - 4, e["p5"] + 0.3, birlik=bz["ihtiyat"], ofset=(0, -80),
                         renk=(1, 0.75, 0.6)))

    # ---- m1: Bizans dizilişi
    t = s["m1"]
    v.ekran(Lejant([("bizans", "Bizans"), ("selcuklu", "Büyük Selçuklu")], t, e["m8"]))
    sc.kamera_git(t, t + 2.5, x=960, y=800, zoom=1.35)
    romen.belir(t + 1.2)
    bri.belir(t + 5)
    aly.belir(t + 8)
    sc.kamera_git(t + 11, t + 13, y=860)

    # ---- m2: Selçuklu dizilişi
    t = s["m2"]
    sc.kamera_git(t, t + 2.5, x=960, y=330, zoom=1.2)
    for i, o in enumerate(okcular):
        o.belir(t + 1 + abs(i - 2) * 0.35)
    for b in (sol_ana, sag_ana, sultan):
        b.git(t + 4, t + 5.5, alfa=0.45)
    alp.belir(t + 4.5)
    sc.ekle(EtiketBalonu("Pusu", t + 5, e["m2"] + 0.5, birlik=sol_ana, ofset=(0, 80)),
            EtiketBalonu("Pusu", t + 5, e["m2"] + 0.5, birlik=sag_ana, ofset=(0, 80)))

    # ---- m3 + m4: ilerleme ve sahte ricat
    t, te = s["m3"], e["m4"]
    sc.kamera_git(t, t + 2.5, x=960, y=560, zoom=1.0)
    yayilma = {"sol_s": -90, "sol_p": -50, "sag_p": 50, "sag_s": 90}
    for k, b in bz.items():
        x, y = b.merkez(t)
        dy = -120 if k == "ihtiyat" else -230
        b.git(t + 1, te - 1, x=x + yayilma.get(k, 0), y=y + dy)
    for i, o in enumerate(okcular):
        x, y = o.merkez(t)
        o.git(t + 3, te - 1, y=y - 150)
        hedef = [bz["sol_p"], bz["sol_p"], bz["mer_a"], bz["sag_p"], bz["sag_p"]][i]
        sc.ekle(OkYagmuru(o, hedef, t + 1.5, te - 1.5, yogunluk=7, tohum=i))
    for x in (610, 960, 1310):
        sc.ekle(HareketOku("bizans", [(x, 720), (x, 520)], t + 1, t + 3.5, t_son=t + 8, kalinlik=22))
    sc.ekle(EtiketBalonu("Sahte ricat!", e["m3"] - 4, e["m3"] + 3, birlik=okcular[2], ofset=(0, 85)))
    sc.ekle(EtiketBalonu("Kamp boş!", s["m4"] + 3, s["m4"] + 8, birlik=sultan, ofset=(0, 85)))
    sc.ekle(EtiketBalonu("Susuz ve yorgun", e["m4"] - 6, e["m4"], birlik=bz["mer_a"], ofset=(0, -190),
                         renk=(1, 0.75, 0.6)))

    # ---- m5: dönüş emri
    t, te = s["m5"], e["m5"]
    sc.kamera_git(t, t + 2.5, x=960, y=700, zoom=1.15)
    for k in ("sol_s", "sol_p", "mer_a", "mer_p", "sag_p", "sag_s"):
        bz[k].git(t + 1, t + 3, aci=180)
    for k in ("sol_p", "mer_a", "mer_p"):
        bz[k].git(t + 3, te, y=bz[k].merkez(t)[1] + 55)
    bz["sag_s"].git(t + 4, te, x=bz["sag_s"].merkez(t)[0] + 50, y=bz["sag_s"].merkez(t)[1] + 40)
    sc.ekle(EtiketBalonu("Karargâha dönün!", t + 2, t + 7, birlik=bz["mer_a"], ofset=(0, -190)))
    sc.ekle(EtiketBalonu("Yenildik mi?", te - 5, te + 0.3, birlik=bz["sag_s"], ofset=(0, -70), renk=(1, 0.75, 0.6)))

    # ---- m6: Dukas çekiliyor
    t, te = s["m6"], e["m6"]
    sc.kamera_git(t, t + 2.5, y=790, zoom=1.15)
    sc.ekle(EtiketBalonu("“İmparator öldü!”", t + 1, t + 8, birlik=bz["ihtiyat"], ofset=(0, -80),
                         renk=(1, 0.75, 0.6)))
    bz["ihtiyat"].git(t + 2, t + 3, aci=180)
    bz["ihtiyat"].git(t + 3.5, t + 10, y=1180)
    bz["ihtiyat"].kaybol(t + 8.5, 1.5)
    dukas.kaybol(t + 8)
    sc.ekle(HareketOku("bizans", [(960, 900), (960, 1060)], t + 3, t + 5, t_son=t + 10, kalinlik=22,
                       renk=(0.55, 0.45, 0.55)))
    # Uz atlıları taraf değiştiriyor (sağ kanat süvarisinden kopan küçük grup)
    uz = sc.ekle(Birlik("selcuklu", "atli_okcu", 1560, 640, 110, 50))
    uz.iz.ekle(t + 11, {"x": bz["sag_s"].merkez(t + 11)[0], "y": bz["sag_s"].merkez(t + 11)[1] - 60})
    uz.git(t + 11, t + 11.8, alfa=1)
    uz.git(t + 12, te, x=1500, y=440)
    sc.ekle(EtiketBalonu("Uzlar saf değiştiriyor", t + 12.5, te + 0.3, birlik=uz, ofset=(0, -70)))

    # ---- m7: kuşatma, kanatlar çöker
    t, te = s["m7"], e["m7"]
    sc.kamera_git(t, t + 2.5, x=960, y=540, zoom=1.0)
    for b in (sol_ana, sag_ana, sultan):
        b.git(t + 0.5, t + 1.5, alfa=1)
    sc.ekle(HareketOku("selcuklu", [(300, 290), (230, 560), (420, 820), (640, 800)], t + 2, t + 6, t_son=e["m8"] - 2),
            HareketOku("selcuklu", [(1620, 290), (1690, 560), (1500, 820), (1280, 800)], t + 2, t + 6, t_son=e["m8"] - 2),
            HareketOku("selcuklu", [(960, 270), (960, 400)], t + 3, t + 6, t_son=e["m8"] - 2, kalinlik=22))
    sol_ana.git(t + 2, t + 7, x=560, y=760, aci=60)
    sag_ana.git(t + 2, t + 7, x=1360, y=760, aci=-60)
    sultan.git(t + 3, t + 8, y=320)
    halka = [(640, 560), (790, 450), (960, 420), (1130, 450), (1280, 560)]
    for o, (x, y) in zip(okcular, halka):
        o.git(t + 2, t + 7, x=x, y=y)
    uz.git(t + 2, t + 7, x=1260, y=640)
    for k in ("sol_s", "sol_p", "mer_a", "mer_p", "sag_p", "sag_s"):
        bz[k].savas(t + 6, e["m8"] - 1)
    for k, dx in (("sag_s", 140), ("sag_p", 80)):
        x, y = bz[k].merkez(t + 7)
        bz[k].git(t + 7, t + 10, x=x + dx, y=y + 90, g=150, alfa=0.0)
    aly.kaybol(t + 8)
    for k, dx in (("sol_s", -140), ("sol_p", -90)):
        x, y = bz[k].merkez(t + 10)
        bz[k].git(t + 10, te, x=x + dx, y=y + 120, g=150, alfa=0.0)
    bri.kaybol(te - 2)
    sc.ekle(EtiketBalonu("Sağ kanat dağıldı", t + 8, t + 12, x=1500, y=640, renk=(1, 0.75, 0.6)),
            EtiketBalonu("Briyennios çekiliyor", te - 5, te + 0.3, x=420, y=640, renk=(1, 0.75, 0.6)))

    # ---- m8: merkez kuşatılır, imparator esir
    t, te = s["m8"], e["m8"]
    bz["mer_a"].git(t, t + 4, g=220)
    bz["mer_p"].git(t, t + 4, g=220)
    sc.kamera_git(t + 1, t + 5, x=960, y=600, zoom=1.35)
    romen.esir(te - 4.5)
