# LeakTrace – Proje Kararları ve Kapsam

*Son güncelleme: 21 Ekim 2026*

## Durum
- **Task 3 teslim edildi.** Prototip: https://leaktrace.ai.studio (AI Studio, Gemini açıklama katmanı).
- Prototip: NEED 2025'ten 36.844 evle eğitilmiş gradient boosting (60 ağaç, 8 özellik). Yıllık doğalgazdan "Sızıntı Skoru" (0–100), "Neden bu skor?" paneli, basit endeks karşılaştırması, TR/EN.
- Doğrulama: eğitim R² 0,339 · 5 katlı CV 0,322 · bölge dışarıda bırakma 0,318. Basit kWh/m² endeksi %20, model %32 açıklıyor; en kötü %10 listeleri %66 örtüşüyor.
- **Bilinen sorunlar (final sürümde çözülecek):**
  - Model elektriğe çok duyarlı: 0 kWh skoru şişiriyor, 35.000 kWh evi verimli gösteriyor (NEED aralığı 500–25.000). Hane kişi sayısını doğrudan sormak gerekiyor.
  - Güneş paneli etkisi anlamsız (533 ev, ölçüm yanılgısı). Modelden çıkarılacak.
  - Yıllık tek rakam bina ile davranışı ayıramıyor → aylık veriye geçilecek.

## Final hedefi (5 gün)
Fikir bütünüyle tasarlanacak, bir dilimi uçtan uca çalışır gösterilecek. Mesaj: "Bugün yapılamıyor çünkü veri kurumlar arasında bölünmüş; teknolojinin her parçası çalışıyor."

## Çekirdek fikir: bina ile hane alışkanlığını ayırmak
Aylık doğalgaz + günlük sıcaklıkla her daireye PRISM / değişken tabanlı derece-gün regresyonu:
- **Isıtma eğimi** → binanın ısı kaybı (bina + kombi verimi)
- **Denge sıcaklığı** → termostat alışkanlığı (yalıtımdan da etkilenir)
- **Baz yük (yaz tüketimi)** → sıcak su, yemek, hane büyüklüğü

**Özgün katkı:** Casey ve ark. (2010) yöntemi müstakil evlerde ve soğuk iklimde (Boulder), sadece simülasyonda gösterdi. LeakTrace onu gerçek veride test ediyor ve **apartmanlara** (daire konumu, komşu ısısı) ve **Akdeniz iklimine** taşıyor.

### IDEAL doğrulama sonuçları (183 ev, aylık fatura, 21 Ekim 2026)
- **Bina sinyali çalışıyor:** ısıtma eğimi ile ölçülmüş iç sıcaklıktan hesaplanan ısı kaybı ρ = 0,93 (m² başına 0,88). En kötü yalıtılmış %25'i yakalama: eğimle %74, yıllık gaz/m² ile %64 (Casey'nin simülasyondaki +10 puanı gerçek veride de var). Evde kalma süresi (kombi saatleri) eğimi bozmuyor (katsayı 0,04). Not: eğim ve ısı kaybı aynı gaz verisinden, 0,93'ün bir kısmı yapısal.
- **Davranış sinyali tek ev için çalışmıyor:** denge sıcaklığı ile iç sıcaklık ρ = 0,25; faturadan çıkan tüm bilgilerle iç sıcaklık tahmini CV R² ≈ 0 (hata 1,4°C, ortalamayla aynı). Neden: iç sıcaklık evden eve ±1,8°C değişiyor, bina farkı çok daha büyük; davranışın izi faturada kayboluyor.
- Baz yük ile kişi sayısı zayıf (aylık ρ 0,11, günlük 0,27); elektrik daha iyi (0,44) → kişi sayısı ADNKS'den alınmalı.
- Enerji yoksulluğu: "fazladan giysi giymek zorundayım"a katılmayanlarda kış iç sıcaklığı ortanca 19,1°C, katılanlarda 17–17,7°C → ~18°C alt sınır anlamlı; ama faturadan tespit edilemiyor.

### Yeni yapı (KARAR)
- **Bina skoru** aylık faturadan (gerçek veride doğrulandı).
- **Davranış ayrımı** aynı binadaki dairelerin karşılaştırmasından: ortak duvar/yapım yılı/iklim, konum etkisi fizikle düzeltilir, kalan fark haneden; aynı dairede farklı haneler de karşılaştırılır. Vatandaş veri girmez, veri kurumlarda. Sınırlar: az daireli binalarda düşük güven, komşu ısısı düzeltilmeli, gerçek doğrulama ancak pilotta (şimdilik Yeşilova simülasyonunda).
- **Kesinleştirme** saatlik akıllı sayaç verisiyle (vizyon).
- Vatandaş girdisi çekirdek veri değil; en fazla vatandaş ekranında isteğe bağlı ek.
- Altın standardın bina açığı yüksek güvenle, kullanım açığı ancak bina karşılaştırması / saatlik veriyle gösterilir; arayüz güven düzeyini açıkça yazar.

### Yeşilova simülasyonu ve zaman testi (22 Ekim)
- Simülasyon: 3.121 gerçek bina (OSM + İBB envanteri, sokak+alan eşleşmesi), 12.883 daire, 11.596 sentetik hane (personalar, TÜİK'e kalibre), 2022–2024 gerçek İzmir hava verisi, fizik tabanlı aylık faturalar. Ortalama 706 m³/yıl (İzmir 2023: 736 m³), aylık PRISM R² 0,88–0,92 (IDEAL: 0,90).
- Gizli çeşitlilik (kısmi ısıtma, havalandırma, tek cam, sıcak su farkı, aydan aya değişen alışkanlık) IDEAL'e yaklaşacak şekilde eklendi; temiz simülasyon gerçekçi değildi.
- **Durgun karşılaştırma zayıf:** mevcut mantolu binaları bulma AUC 0,62–0,70; aynı bina içinde davranış ρ 0,26.
- **Zaman karşılaştırması güçlü (hava normalize yıllık ısıtma, NAC):** Simülasyonun aydan aya gürültüsü IDEAL'e (aylık PRISM R² 0,91 / gerçek 0,90), yıldan yıla oynaklığı NEED'e göre ayarlandı (taşınmayan dairelerde sağlam sapma 0,25; NEED'de 0,12–0,20, yani simülasyon biraz kötümser). Sonuç: 2023'te mantolanan binaları bulma AUC 0,86 (6+ daireli 0,95). Taşınmada tüketim değişimi ile gerçek davranış değişimi ρ 0,70, büyük değişimlerde yön %89 doğru. Aynı ölçüyle durgun skor AUC 0,61.
- Haritadaki "olası iyileştirme" kuralı (en az 2 taşınmayan dairede −%20): 274 bina işaretlendi, 91'i gerçekten mantolanmış (isabet %33, taban oran %7; yakalama %43).
- Yöntem notu: ham ısıtma eğimi yerine PRISM'in hava normalize yıllık tüketimi (NAC) kullanılmalı; çok daha kararlı.
- **KARAR:** Bina skoru ana ürün. Daire bazı (davranış) taşınma öncesi/sonrası karşılaştırmasıyla prototipe girer. Sistemin en güçlü olduğu iş değişimi yakalamak: yalıtım desteğinin işe yarayıp yaramadığını faturadan doğrulamak.

### Eksik yapım yılı modeli (23 Ekim)
- Bornova envanterinde binaların %50'sinde (28.005 bina), Yeşilova'da 819 binada ruhsat tarihi yok.
- Gradient boosting modeli (kat, bodrum, taşıyıcı sistem, nizam, zemin/üst kat kullanımı, alan, mahalle ve sokak ortancası) Bornova'da yılı bilinen 27.955 binada 5 katlı çapraz doğrulamayla: ortalama hata 6,5 yıl (sokak ortancası 7,5, mahalle ortancası 8,8). TS 825 öncesi/sonrası sınıflandırmasında fark yok (%81 vs %82).
- Uyarı: ruhsatı olmayan binalar ruhsatsız/kaçak olabilir; model ruhsatlı binalarla eğitildiği için bu binalarda daha az güvenilir.
- Simülasyon bu yıllarla yeniden üretildi: değişim tespiti AUC 0,85 (6+ daireli 0,98), taşınma ρ 0,69, haritada 259 işaretli bina (82'si gerçek, isabet %32).
- Sunum kararı: problem + altın standart ~30–35 sn, kalanı uygulamalı demo. "Nasıl çalışır" yazılı olarak sitede (videonun dışında). Çekirdek istatistik + fizik; makine öğrenmesi eksik alanlar için.
- Harita: https://claude.ai/artifact/TCYtpDzMT36Av4MF57jB9Y (roller: Yönetim / Vatandaş; sol arama paneli, filtreler, öncelik listesi; Değişim 2023 katmanı; simülasyon doğrulaması).

### İsim değişikliği (24 Ekim)
- "Sızıntı Skoru" yerine **Verimlilik Skoru**: 100 en verimli, 0 en çok ısı kaçıran (eski skorun tersi). Öncelik listesi en düşük skordan başlar.

### Canlı hesaplama ve ısıtma tipi tahmini (24 Ekim)
- Harita artık ham sentetik faturaları (12.883 daire × 36 ay doğalgaz + elektrik) içerir ve açılışta tüm analizi tarayıcıda baştan yapar (~0,4 sn): ısıtma tipi tahmini, PRISM, konum düzeltmesi, bina skoru, değişim tespiti. Bir dairenin PRISM grafiği panelde görünür.
- "Kopya" kaldırıldı: sistem ısıtma tipini bilmez, faturanın şeklinden çıkarır (kış/yaz doğalgaz oranı ≥1,3 → doğalgazla ısınma; kış/ara mevsim elektrik oranı ≥1,25 → klima). Doğruluk %91.
- "Çok düşük ısınma" grubu (doğalgaz var ama kışın neredeyse artmıyor, 853 daire): %40'ı enerji yoksulu (diğerlerinde %8) → enerji yoksulluğu sinyali.
- Canlı sonuçlar: değişim tespiti AUC 0,87; 234 bina işaretli, 93'ü gerçekten mantolanmış (%40; taban oran %7).
- Öncelik listesi önce güvene, sonra skora göre sıralı. Kod ve veri paketi güncellendi (6_kod/web/core.js = sitedeki analiz).

### Eksik veri tamamlama denemesi (24 Ekim)
- Faturası olmayan binaların Verimlilik Skorunu kayıtlardan (yıl, kat, daire, alan, taşıyıcı, nizam, dükkân, 8 komşunun skoru) tahmin: gradient boosting, 5 katlı CV ortalama hata 24 puan, mahalle ortalaması 25 puan (R² 0,06). Aynı binadaki dairelerden daire tüketimi tahmini de başarısız. "Beklenenden iyi" eski binaların %41'i gizli mantolu (taban %25), zayıf sinyal.
- **Bulgu:** Enerjiyi belirleyen mantolama ve alışkanlık kayıtlarda yok; kayıtlardan tahmin yetmiyor, fatura verisi şart. Vizyonda cephe fotoğrafından mantolama tespiti eksik parçayı tamamlar.
- **KARAR:** Tahmini skor haritaya konmadı. Yapay zekâ çalıştığı yerde görünür: yapım yılı (ort. hata 6,5 yıl), ısıtma tipi (%91). Bina panelinde "Veri kaynakları" bölümü (Gerçek / Kural / Model tahmini / Sentetik / Hesaplandı); Nasıl çalışır sayfasında "Yapay zekâ neyi tamamlıyor, neyi tamamlayamıyor" bölümü.

### Destek doğrulama katmanı (25 Ekim)
- Kör aramada değişim tespiti sınırlı (isabet %40, yakalama %44). Asıl kullanım: belediyenin destek verdiği binalarda tasarrufu doğrulamak. Simülasyonda mantolanan binaların %82'sinde, mantolanmayanların %22'sinde %10'dan fazla düşüş.
- Belediye panelinde "Destek doğrulama" katmanı: 210 destekli binadan 156 tasarruf doğrulandı (≥%10 düşüş), 12 belirsiz (%3–10), 23 tasarruf görülmedi, 19 veri yetersiz. Ölçülebilen 452 dairede yılda ~46.000 m³ doğalgaz, ~99 ton CO₂ (üst sınır; prebound).
- **Geri alındı:** Katman beğenilmedi, önceki sürüme dönüldü. Bunun yerine Son kış değişimi katmanının açıklamasına kör aramanın sınırı ve destek doğrulamanın daha güvenilir olduğu (%82'ye %22) yazıldı.

## Altın standart: iki parçalı (KARAR)
Her daire için iki ayrı açık hesaplanır:
- **Bina standardı:** Bu tip/yaştaki binanın iyileştirilmiş hali (C sınıfı / güncel TS 825). Kapanma yolu: yatırım (yalıtım, pencere, kombi).
- **Kullanım standardı:** Benzer hanelerin makul (ortanca) kullanımı. Kapanma yolu: bilgilendirme.
- **Alt sınır:** Asgari iç sıcaklığın altında kalan hane "örnek" sayılmaz, enerji yoksulluğu bayrağı alır (DSÖ önerisi ~18°C, doğrulanacak).
- **Standart ayarlanabilir bir politika parametresidir (KARAR, 22 Ekim):** Sistemin değeri, her dairenin tüketimini ölçüp hesaplayabilmesi; hangi standardın seçileceği sonradan karar vericiye bırakılır. Sistem her standart için "herkes uyarsa toplam azalma"yı hesaplar.
- **Sentetik Yeşilova sonucu:** bina standardı (güncel TS 825 + mantolama) −%15,7, kullanım standardı −%3,9, enerji yoksullarının 18°C tabanı +%0,3 → **net −%19,2** (kombi değişimi henüz dahil değil).
- **Ölçek argümanı:** Türkiye'de konutlar 2024'te 19 milyar m³ doğalgaz tüketti (GAZBİR 2024). Ülke genelinde yalnızca %5 azalma ≈ 0,95 milyar m³ ≈ 10 TWh ≈ 2 Mt CO₂/yıl.

NEED'de "herkes uyarsa toplam azalma":

| Standart | Azalma |
|---|---|
| Benzer evlerin ortancası (eski model) | %20,4 |
| **Bina C sınıfı + kullanım ortanca (seçilen)** | **%24,1** |
| Benzer evlerin en iyi çeyreği | %36,6 |
| Bina C sınıfı + kullanım en iyi çeyrek | %40,4 |

Not: C sınıfı senaryosu gözlenen fark, nedensel değil; rakamlar İngiltere'ye ait, İzmir'de yeniden hesaplanacak.

## Veri (veri – neden – nereden)
**Tüketim ve zaman**
- Aylık doğalgaz – bina/davranış/sıcak su ayrımı – İzmirgaz
- Aylık elektrik – hane aktivitesi, klimayla ısınma – Gediz Elektrik
- Saatlik akıllı sayaç – evde kalma ve ısıtma saatleri – dağıtım şirketi (ham veri şirkette işlenir, sadece türetilmiş özellik çıkar)
- Günlük sıcaklık, mikroklima – derece-gün – MGM
- Okuma dönemi, tahmini okuma – veri temizliği – İzmirgaz
- Doğalgaz fiyatı – şehir geneli düzeltme – EPDK

**Bina**
- Yapım yılı, kat, alan, taşıyıcı sistem – ısı kaybı beklentisi – İBB yapı envanteri
- Dairenin konumu (üst/zemin/ara kat, köşe) – çatı/zemin kaybı – tapu kat irtifakı
- Bitişik/ayrık nizam, güneş alma – dış yüzey, güneş kazancı – imar planı, OSM
- Isıtma sistemi, kombi yaşı/tipi – verim – İzmirgaz abonelik ve cihaz kaydı
- EKB – hesaplanan vs gerçek – Bakanlık (BEP-TR)
- Deprem riski, kentsel dönüşüm – karar filtresi – riskli yapı listeleri

**Hane**
- Kişi sayısı, yaş grupları – sıcak su, evde kalma – ADNKS
- Gündüz evde kalma – ısıtma saatleri – yaş + SGK çalışan var/yok + akıllı sayaç
- Taşınma tarihi – aynı dairede hane karşılaştırması – ADNKS, abonelik kayıtları
- Kiracı/ev sahibi – öneriyi doğru kişiye yöneltme – tapu + ADNKS
- Boş/mevsimlik daire – analiz dışı bırakma – ADNKS + düşük tüketim
- Kömür yardımı, sosyoekonomik durum – enerji yoksulluğu – SYDV, mahalle göstergesi

**Görüntüden (vizyon):** cephe mantolama/doğrama (sokak fotoğrafı), çatı güneş kolektörü (uydu).
**Alınmayan:** meslek, sağlık bilgisi, bireysel gelir, TC kimlik/isim. Eşleştirme UAVT adres koduyla.

## Sentetik veri ve doğrulama (KARAR)
- **Eğitim ve doğrulama gerçek veriyle:** NEED 2025 (beklenti/standart), IDEAL (255 ev, ölçülmüş oda sıcaklıkları → davranış ayrımı gerçekten doğru mu).
- **Test/demo İzmir simülasyonuyla:** Bornova **Yeşilova Mahallesi**, 300–500 gerçek bina (OSM / İBB bina sınırları ve kat sayısı). Google Maps kullanılmaz (kullanım şartları).
- Üretim: gerçek binalar → TS 825 dönemine göre yalıtım, daire konumu, yön → TÜİK dağılımlarından haneler → İzmir gerçek sıcaklıkları → ısı dengesiyle aylık fatura + gürültü → TÜİK/İzmir ortalamalarına kalibrasyon. Her dairede sorunun kaynağı bilindiği için modelin doğruluğu ölçülür. Emsal: Casey 2010 (567 sentetik ev, DOE-2); CREST hane talep modeli.

## Gizlilik (sadece arayüzde gösterilecek)
UAVT kodu kurum tarafında şifrelenir, ham veri kurumdan çıkmaz. Roller: vatandaş (kendi dairesi, e-Devlet), bina yöneticisi (bina geneli), belediye (bina bazında), kamu (mahalle toplamları). Şifreleme KVKK'da anonimleştirme değil takma adlandırmadır; anonimlik çıktı katmanında sağlanır. Açık kaynak.

## Kapsam
**Çalışacak (prototip):** aylık faturadan bina skoru (IDEAL ile doğrulandı), aynı bina karşılaştırmasıyla davranış ayrımı (simülasyonda test), iki parçalı standart ve iki açık, enerji yoksulluğu bayrağı, Yeşilova haritası (bina → daire detayı), rol seçimi.
**Vizyon:** görüntüden mantolama ve kolektör tespiti, bütçe optimizasyonu, belediye sohbet ajanı, verisi olmayan binalar için tahmin (ikinci ayak), gerçek İzmir pilotu.

## Açık sorular
- Yeşilova'da OSM / İBB verisi ne kadar dolu, koordinat var mı?
- İzmir'de abone başına ortalama doğalgaz (kalibrasyon için)
- Türkiye'de yapım dönemine göre U değerleri (Knovel soru 1)
- DSÖ asgari iç sıcaklık önerisi
- Merkezi sistemli binalar: analiz dışı mı, ısı pay ölçerle mi?
- İzmir'in ılıman kışında ısıtma ayı az: regresyon için yeterli veri noktası var mı?

## Çalışma şekli
Planlama kullanıcıda. Veri analizi, kod, makale özetleri Claude'da. Model, sentetik veri ve standart gibi yön belirleyen kararlar birlikte, gerekçesi konuşularak alınır.
