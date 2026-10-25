# AI Studio'ya aktarma

Bu klasördeki `index.html`, uygulamanın kodudur (~100 KB). Veriyi açılışta `live_data.json` dosyasından yükler.
Veri dosyası aynı klasörde bulunamazsa GitHub'daki kopyayı kullanır.

## Adımlar

1. `index.html` içindeki şu satırda `KULLANICI_ADI` kısmını kendi GitHub kullanıcı adınla değiştir:
   `https://raw.githubusercontent.com/KULLANICI_ADI/leaktrace/main/data/live_data.json`
   (Depo adın `leaktrace` değilse onu da değiştir.)
2. AI Studio'da Build bölümünde yeni bir uygulama aç ve Gemini'ye şunu yaz, `index.html` dosyasını da ekle:

> Ekteki index.html dosyasını uygulamanın tek sayfası olarak birebir kullan. Kodu değiştirme, React'e ya da başka bir yapıya dönüştürme, stil ve metinleri değiştirme. Sadece bu HTML dosyasını sun. Dosya, harita kütüphanesini (deck.gl) cdn.jsdelivr.net üzerinden, veriyi ise live_data.json dosyasından ya da GitHub'daki ham adresten fetch ile yükler; bu istekleri engelleme.

3. Uygulama açılınca önce "Veriler yükleniyor…" yazısı görünür, birkaç saniye içinde ana sayfa açılır.
4. Paylaşmadan önce linki giriş yapılmamış bir gizli pencerede test et.
