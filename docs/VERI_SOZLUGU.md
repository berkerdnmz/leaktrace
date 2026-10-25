# Veri sözlüğü

Kaynak etiketleri: **G** gerçek · **M** model tahmini · **E** yaklaşık eşleştirme · **S** sentetik · **Ç** model çıktısı · **SG** simülasyonun gerçek cevabı

## 1_gercek_veri/

| Dosya | Açıklama |
|---|---|
| `export.geojson` | OSM'den Yeşilova Mahallesi (relation 10324858) içindeki 3.372 bina ve mahalle etiketi |
| `export_1.geojson` | OSM'den Yeşilova'nın isimli sokakları |
| `bornova_yapi_envanter.csv` | İBB Bina Kimlik Belgesi, Bornova, 55.972 bina, 24 alan |
| `bina-sayilari-mahalle-bazli.csv` | İBB mahalle bazlı bina sayıları (Yeşilova: 3.327) |
| `open-meteo-38_42N27_20E14m.csv` | Bornova günlük ortalama/en düşük/en yüksek sıcaklık ve güneş radyasyonu, 2022–2024 (ilk 3 satır meta bilgi) |
| `anon2025_50k.csv`, `NEED-2025-...metadata.ods` | NEED 2025 50.000 evlik örneklem ve sütun açıklamaları |
| `ideal/ideal_gunluk_csv.gz` | IDEAL saatlik özetlerinden günlük ev özeti (kendi scriptimizle üretildi) |
| `ideal/hava.csv` | IDEAL'in 5 konumu için günlük hava (Open-Meteo) |
| `ideal/metadata/`, `ideal/surveys/` | IDEAL hane, kişi, oda ve anket tabloları |

`ideal_gunluk_csv.gz` sütunları: `homeid`, `date`, `gas_sum` (günlük gaz, Wh), `gas_n` (saat sayısı), `temp_all_mean/min/max` (tüm odalar, °C×10), `temp_living_mean` (salon, °C×10), `chflow_*` (kalorifer gidiş borusu sıcaklığı, °C×10; `chflow_hours_over400` kombinin 40°C üstü çalıştığı saat), `elec100_mean` (ortalama elektrik gücü, W).

## 2_islenmis_gercek_veri/

**`yesilova_binalar.csv`** (3.184 OSM binası, her biri bir envanter kaydıyla)

| Sütun | Kaynak | Açıklama |
|---|---|---|
| `osm_id` | G | OSM bina kimliği |
| `area` | G | Taban alanı, m² (OSM geometrisinden) |
| `cx`, `cy` | G | Yerel metre koordinatları (iç hesap için) |
| `street`, `street_dist` | G | En yakın OSM sokağı ve uzaklığı (m) |
| `BINA_KIMLIK_NO` … `BODRUM_KAT_ADEDI` | G+E | Eşleşen envanter kaydının alanları |
| `year` | G/M | Yapım yılı: ruhsat tarihi, yoksa model tahmini |
| `year_src` | – | `ruhsat` ya da `model` |
| `floors` | G+E | Serbest kat adedi |
| `zarea` | G+E | Envanterdeki zemin kat inşaat alanı (varsa) |
| `match` | – | `sokak+alan` ya da `sadece alan` |

**`yesilova_binalar.geojson`**: aynı bilgiler + bina geometrisi.

**`bornova_yapim_yili_tahmini.csv`**: `BINA_KIMLIK_NO`, `year` (ruhsattaki, G), `year_model` (model tahmini, M; tüm binalar için). Doğrulama: yılı bilinen 27.955 binada ortalama hata 6,5 yıl (sokak ortancası 7,5).

**`ideal_ev_prism_sonuclari.csv`** (IDEAL, 183 ev, PRISM uygulanmış): `tb` denge sıcaklığı (°C), `base` baz yük (kWh/gün), `slope` ısıtma eğimi (W/K), `htc` ölçülmüş iç sıcaklıktan hesaplanan ısı kaybı (W/K), `tin_cold` dışarısı 8°C altındayken ortalama iç sıcaklık, `heat_hours` kombinin günlük çalışma saati, `annual_gas` yıllık gaz (kWh), diğerleri IDEAL meta verisinden.

## 3_sentetik_veri/

**`daireler_ve_haneler.csv`** (12.883 daire; her satır 2022 başındaki durum)

| Sütun | Kaynak | Açıklama |
|---|---|---|
| `flat_id`, `osm_id`, `bina_kimlik` | – | Daire, OSM bina ve envanter kimliği |
| `floor`, `n_floors`, `top`, `ground`, `above_shop` | S (G'den) | Kat, toplam kat, en üst kat, zemin, dükkân üstü |
| `flats_per_floor`, `end_unit`, `ext_sides` | S | Kat başına daire (taban alanından), uç daire, dışa açık cephe sayısı |
| `area` | S | Net daire alanı, m² |
| `year`, `year_src`, `structure`, `nizam` | G/M | Binadan gelen |
| `persona` | S | Hane tipi (yalnız emekli, çocuklu aile, öğrenci, boş …) |
| `persons`, `over65`, `day_home` | S | Kişi sayısı, 65 yaş üstü sayısı, gündüz evde biri var mı |
| `heat_hours`, `setpoint` | S | Günlük ısıtma saati, termostat (°C) |
| `ses`, `renter`, `energy_poor` | S | Gelir grubu, kiracı, enerji yoksulu (evini 15,5–17,5°C'de tutar) |
| `hot_water_l_day` | S | Günlük sıcak su (litre) |
| `heating` | S | `kombi`, `soba`, `klima`, `merkezi` |
| `era` | SG | `pre2000`, `ts825` (2000–2008), `bep` (2009+) |
| `mantolu`, `retrofit` | SG | Baştan mantolu; 2023 Eylül'de mantolandı |
| `orient`, `shade`, `boiler_eff`, `single_glz` | S | Yön katsayısı, gölge, kombi verimi, tek cam |
| `leak_b`, `heated_frac`, `vent`, `gain_mult`, `dhw_mult` | S | Gizli çeşitlilik: bina sızdırmazlığı, ısıtılan alan payı, havalandırma, iç kazanç ve sıcak su çarpanları |
| `move_day` | S | Taşınma günü (2022-01-01'den itibaren gün sırası); −1 taşınma yok |
| `Teff_set`, `T_neigh` | S | Dairenin ve komşu dairelerin ortalama sıcaklığı (komşu ısısı hesabı) |

**`aylik_dogalgaz_faturalari.csv.gz`**: `flat_id`, `ay` (YYYY-AA), `dogalgaz_kwh` (S). Sobalı ve merkezi sistemli dairelerde boştur (daire bazında gaz faturası yok); klimayla ısınan dairelerde yalnızca sıcak su ve yemek gazı vardır. 1 m³ ≈ 10,64 kWh.

**`aylik_elektrik_faturalari.csv.gz`**: `flat_id`, `ay`, `elektrik_kwh` (S). Tüm daireler; klimayla ısınanlarda kış ısıtması, klima sahiplerinde yaz soğutması dahil.

**`tasinan_yeni_haneler.csv`**: 2023 yazında taşınan 1.739 dairenin yeni hanesi (S); sütunlar `daireler_ve_haneler.csv` ile aynı anlamda.

**`bina_gercekleri.csv`**: `osm_id`, `donem`, `bastan_mantolu`, `mantolama_2023`, `daire_sayisi` (SG).

## 4_model_ciktilari/

Haritanın tarayıcıda yaptığı analizin Node.js ile çalıştırılmış çıktısı (`6_kod/web/export.js`).

**`bina_sonuclari.csv`**: `verimlilik_skoru` (0–100; 100 en verimli, 0 en çok ısı kaçıran; mahalledeki sıralama), `guven` (Yüksek 6+, Orta 3–5, Düşük 1–2 analiz edilen daire; yıl model tahminiyse bir seviye düşer), `degisim_2023_yuzde` (taşınmayan dairelerde hava normalize ısıtmanın ortanca değişimi), `olasi_iyilestirme` (en az 2 dairede −%20), `daire_durumlari` (tahmin edilen: kombi, klima, gazsiz, bos, belirsiz = çok düşük ısınma), `SIM_GERCEK_*` (doğrulama için).

**`daire_sonuclari.csv`**: `tahmin_isitma` (faturanın şeklinden), `SIM_GERCEK_isitma`, PRISM parametreleri (`tb_C` ısıtmanın başladığı sıcaklık, `isitma_egimi_kWh_dg`, `baz_yuk_kWh_gun`, `r2`), `nac_2022_23`/`nac_2023_24` (hava normalize yıllık ısıtma, kWh), `bina_ici_goreli_yuzdelik`.

**`need_task3_gradient_boosting_modeli.json`**: Task 3 prototipindeki model (60 ağaç, 8 değişken), NEED 2025 ile eğitildi.
