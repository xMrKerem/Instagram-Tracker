# 📸 Instagram Tracker — Instaloader + Discord Bot

Bu proje, **belirli bir Instagram hesabını otomatik olarak izleyen** ve profil verilerinde (takipçi sayısı, takip edilenler, gönderi sayısı vb.) değişiklik olduğunda **Discord kanalına bildirim gönderen** bir bottur.

---

## 🚀 Özellikler

- Belirtilen Instagram hesabını periyodik olarak kontrol eder.  
- Profildeki değişiklikleri algılar:  
  - Takipçi sayısı  
  - Takip edilen sayısı  
  - Gönderi sayısı  
  - Biyografi  
  - Ad / Kullanıcı adı  
- Değişiklik tespit edildiğinde, Discord kanalına otomatik olarak **Embed mesaj** gönderir.  
- Rate-limit hatalarında otomatik olarak bekleme süresini uzatır.  
- Oturumu (`session`) dosyada saklayarak yeniden giriş ihtiyacını en aza indirir.  
- Python `.env` dosyası üzerinden gizli bilgileri (token, şifre vb.) yönetir.

---

## ⚙️ Kurulum

### 1️⃣ Repoyu Klonla:
```bash
git clone https://github.com/xMrKerem/Instagram-Tracker.git
cd Instagram-Tracker
```

### 2️⃣ .env Dosyası Oluştur
Proje dizinine .env adında bir dosya oluştur ve içine aşağıdaki bilgileri gir:
```dotenv
DISCORD_TOKEN=discord-bot-tokenin
INSTAGRAM_USERNAME=instagram-kullanici-adin
INSTAGRAM_PASSWORD=instagram-sifren
CHANNEL_ID=discord-kanal-id
TRACK=takip_edilecek_hesap
```

### 3️⃣ Gerekli Modülleri Yükle
```bash
pip install instaloader discord.py pickledb python-dotenv pytz
```

## 🧠 Çalışma Mantığı

- Bot başlatıldığında .env içindeki kullanıcı bilgileriyle giriş yapar.
- İlk turda hedef profilin verilerini db.json dosyasına kaydeder.
- Her 10 dakikada bir profili yeniden kontrol eder.
- Yeni veri, öncekinden farklıysa Discord’a değişiklikleri gösteren bir embed mesaj yollar.
- Rate-limit veya bağlantı hatası durumunda oturumu yeniler ve süreyi otomatik olarak uzatır.

## 🛡️ Rate-Limit Koruması

- instaloader’ın max_connection_attempts=1 parametresiyle sadece tek deneme yapılır.
- Bağlantı hatası sonrası tekrar denemeler exponential backoff (sürekli artan bekleme) yöntemiyle yapılır.
- Uzun süreli hatalarda oturum dosyası otomatik yenilenir.

## 🧾 Gelecek Planları (TODO)

- Takipçi / Takip edilen listelerini kaydedip değişimleri göstermek
- Hedef profil gizliyse özel durum mesajı
- Discord’da özel log kanalı desteği
- Daha gelişmiş rate-limit yönetimi

## 🖋️ Lisans

- Bu proje MIT Lisansı ile yayımlanmıştır.
- Her türlü geliştirme, fork veya kişisel kullanım için serbesttir.

## 👨‍💻 Geliştirici

### xMrKerem