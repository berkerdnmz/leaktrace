# LeakTrace

**Görünmeyen enerji kaybını haritada görün.**

LeakTrace, kurumlarda zaten bulunan doğalgaz ve elektrik faturalarını bina kayıtlarıyla bir araya getirerek her binanın enerji verimliliğini değerlendirir. Belediyeye iyileştirme desteğine hangi binalardan başlaması gerektiğini ve yapılan iyileştirmelerin faturalara yansıyıp yansımadığını gösterir.

Prototip: İzmir, Bornova, Yeşilova Mahallesi'nin **3.121 gerçek binası ve 12.883 dairesi.**

- **Canlı uygulama:** _(AI Studio linki)_
- **GitHub Pages kopyası:** _(Settings → Pages açıldıktan sonra: https://KULLANICI_ADI.github.io/leaktrace/)_
- **Demo videosu:** _(YouTube linki)_
- **Proje dokümanları:** [`docs/`](docs/) (Problem Definition, PDR, kararlar, kaynaklar)

## Ne yapıyor?

1. **Isıtma tipini ayırır:** Faturanın şeklinden dairenin doğalgazla mı, klimayla mı ısındığını ya da doğalgaz faturası olmadığını çıkarır (kural tabanlı, simülasyonda %91 doğru). Kışın neredeyse hiç ısınmayan haneleri enerji yoksulluğu riski olarak işaretler.
2. **Binaları karşılaştırır:** Her dairenin aylık faturası günlük sıcaklıkla karşılaştırılır (PRISM yöntemi), dairenin konumu düzeltilir ve her binaya mahalle içinde bir **Verimlilik Skoru** (0–100) verilir.
3. **Değişimi izler:** Aynı dairelerin iki kışı karşılaştırılır; tüketimi belirgin düşen binalar olası iyileştirme olarak işaretlenir.
4. **Eksik bilgiyi tamamlar:** Kayıtlarda olmayan yapım yılı bir makine öğrenmesi modeliyle tahmin edilir (Bornova'da 27.955 binada ortalama hata 6,5 yıl).

Bütün analiz **tarayıcıda canlı** yapılır: uygulama ham faturaları yükler ve skorları her açılışta baştan hesaplar.

## Neyin gerçek, neyin sentetik olduğu

- **Gerçek:** Bina konumları ve şekilleri (OpenStreetMap), kat sayısı, taşıyıcı sistem, yapı nizamı, ruhsat tarihi (İBB Yapı Envanteri), İzmir'in günlük sıcaklıkları (Open-Meteo).
- **Model tahmini:** Ruhsat tarihi olmayan binaların yapım yılı.
- **Sentetik:** Daireler, haneler ve faturalar. Gerçek faturalar dağıtım şirketlerinde olduğu için fizik tabanlı bir simülasyonla üretildi ve gerçek ölçümlere göre kalibre edildi (hane başı 707 m³; İzmir 2023 ortalaması 736 m³).
- **Doğrulama:** Yöntem İngiltere'nin NEED veri setinde (36.844 ev) ve Edinburgh'daki IDEAL veri setinde (183 gerçek ev) test edildi.

## Depo yapısı

| Klasör | İçerik |
|---|---|
| `index.html` | Uygulamanın tek dosyalık hali (veri gömülü). GitHub Pages ile doğrudan yayınlanabilir. |
| `app/ai_studio/` | AI Studio için hafif sürüm: kod (`index.html`, ~100 KB) ve veri (`live_data.json`) ayrı. |
| `data/1_gercek_veri/` | Kaynaklardan indirilen ham veriler |
| `data/2_islenmis_gercek_veri/` | Bina eşleştirmesi, yapım yılı tahminleri, IDEAL analiz sonuçları |
| `data/3_sentetik_veri/` | Sentetik daireler, haneler, aylık doğalgaz ve elektrik faturaları |
| `data/4_model_ciktilari/` | Bina ve daire sonuçları (uygulamadaki analizin Node.js çıktısı) |
| `data/live_data.json` | Uygulamanın yüklediği ham veri |
| `code/` | Veriyi baştan üreten ve analiz eden bütün kod |
| `docs/` | Problem Definition, PDR, proje kararları, kaynaklar, veri sözlüğü |

Ayrıntılı sütun açıklamaları: [`docs/VERI_SOZLUGU.md`](docs/VERI_SOZLUGU.md).

## Kodu çalıştırma

Python 3.10+ (`pandas`, `numpy`, `scipy`, `scikit-learn`) ve Node.js. Komutlar `code/` klasöründen çalıştırılır:

```
python impute.py        # eksik yapım yılları
python match.py         # OSM binaları + İBB envanteri eşleştirmesi
python flats.py         # binaları dairelere böler
python households.py    # sentetik haneler
python bills_time.py    # 2022–2024 aylık doğalgaz ve elektrik faturaları
python prep_live.py     # uygulamanın yüklediği live_data.json
node web/export.js live_data.json ../data/4_model_ciktilari   # uygulamadaki analizin aynısı
```

Rastgele sayı tohumları sabit olduğu için çıktılar her çalıştırmada aynıdır.

## Lisanslar

- **Kod:** MIT (bkz. `LICENSE`)
- **OpenStreetMap verisi ve ondan türetilen dosyalar:** © OpenStreetMap katkıcıları, ODbL
- **İzmir Büyükşehir Belediyesi Açık Veri:** CC BY 4.0
- **Open-Meteo:** CC BY 4.0
- **NEED 2025 (DESNZ):** Open Government Licence
- **IDEAL Household Energy Dataset (Edinburgh Üniversitesi):** CC BY 4.0; Pullinger ve ark. (2021), Scientific Data 8, 146

Gerçek bir uygulamada faturalar ve nüfus bilgisi gibi kişisel veriler hiçbir zaman paylaşılmaz; bu depodaki faturalar ve haneler sentetiktir.
