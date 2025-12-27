# 🧠 Iowa Gambling Task (IGT) - Enhanced v3.0

**Türkçe'ye Uyarlanmış Nöropsikolojik Test Yazılımı**

## 📋 Genel Bakış

Iowa Gambling Task (IGT), karar verme süreçlerini ve risk değerlendirme yeteneklerini ölçmek için kullanılan klinik bir nöropsikolojik test yazılımıdır. Bu uygulama, Bechara et al. (1994) tarafından geliştirilen orijinal protokole sadık kalarak Türkçe'ye uyarlanmıştır.

## ✨ Özellikler

### 🎯 Bilimsel Özellikler
- ✅ Orijinal Bechara protokolüne uygun ceza programları
- ✅ 4 farklı deste (A, B, C, D) - Avantajlı/Dezavantajlı
- ✅ **100 deneme** standardı (Klasik IGT)
- ✅ Trial-by-trial veri kaydı
- ✅ Gerçek zamanlı reaksiyon süresi ölçümü (zaman damgalı)
- ✅ **Shimmer EDA/PPG cihazı entegrasyonu** (SCR ölçümü)
- ✅ **Net IGT Skoru** hesaplama ve raporlama

### 💻 Teknik Özellikler
- ✅ **PyQt6 tabanlı modern GUI** (Full-screen, responsive)
- ✅ **Ana menü sistemi** (Test başlat, Veri görüntüle, Hakkında)
- ✅ **Veri kayıtları görüntüleyici** (Tablo, filtreleme, dosya açma)
- ✅ **Otomatik ID oluşturma** sistemi (DYYYYMMDD_HHMMSSmmm formatı)
- ✅ **GUI ile katılımcı bilgi girişi** (Yaş ve Cinsiyet)
- ✅ SQLite veritabanı entegrasyonu (**200 denek kapasitesi**)
- ✅ **Shimmer senkronizasyon ekranı** (3-2-1 countdown)
- ✅ Otomatik analiz ve görselleştirme
- ✅ Detaylı logging sistemi
- ✅ CSV/PNG/TXT çıktıları (zaman damgalı)
- ✅ **Tek tıkla çalıştırılabilir** (.app/.exe paketleme)

### 📊 Analiz Özellikleri
- 📈 Öğrenme eğrisi grafiği (blok bazlı)
- 💰 Bakiye değişim grafiği
- 🃏 Deste seçim dağılımı
- ⏱️ Ortalama reaksiyon süreleri
- 📝 **Gelişmiş özet rapor** (Net IGT skoru, deste detayları, yüzdeler)
- 🗄️ **Veritabanı görüntüleyici** (Tüm kayıtlar, filtreleme, dosya açma)

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- PsychoPy
- Pandas, Matplotlib, Seaborn

### Adımlar

```bash
# Depoyu klonlayın veya indirin
cd IGTv1

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

## 📖 Kullanım

### 1. Paketlenmiş Uygulama (Önerilen)

#### macOS
```bash
# Uygulamayı çift tıklayarak çalıştırın
open IGT.app
```

#### Windows
```bash
# IGT.exe dosyasını çift tıklayarak çalıştırın
IGT.exe
```

### 2. Python ile Çalıştırma

```bash
python3 main.py
```

**Program akışı:**
1. 🏠 **Ana Menü**
   - 🧪 Yeni Test Başlat
   - 📊 Veri Kayıtlarını Görüntüle
   - ℹ️ Hakkında & Yardım
   - 🚪 Çıkış

2. 🆔 **Katılımcı Bilgileri**
   - Otomatik ID oluşturulur (örn: D20251220_150530123)
   - Yaş girişi (spinner)
   - Cinsiyet seçimi (combo box)

3. 📋 **Talimatlar Ekranı**
   - Test kuralları ve açıklamalar

4. ⏱️ **Shimmer Senkronizasyonu**
   - 3-2-1 countdown
   - Shimmer cihazında kaydı başlatın

5. 🃏 **Deney (100 kart seçimi)**
   - 4 desteden birini seçin
   - Ödül/ceza geri bildirimi
   - Bakiye ve ilerleme takibi

6. 📊 **Sonuçlar**
   - Otomatik analiz ve kayıt
   - CSV/PNG/TXT çıktıları
   - Veritabanına kaydet
   - Ana menüye dön

### 3. Uygulama Paketleme

#### macOS/Linux
```bash
./build_app.sh
```

#### Windows
```bash
build_app.bat
```

Paketlenmiş uygulama `dist/` klasöründe oluşturulur.

### 4. Test Komutları

```bash
# Fonksiyon testleri
python3 test_igt_functions.py

# Dashboard testi
python3 test_dashboard.py
```

## 📁 Çıktı Dosyaları

Tüm çıktılar `Sonuclar/` klasöründe saklanır:

```
Sonuclar/
├── igt_sessions.db           # SQLite veritabanı (200 oturum)
├── igt_dashboard.html        # Web tabanlı analiz paneli
├── igt_debug.log             # Sistem log dosyası
├── IGT_P001_2025-12-20_....csv      # Ham veri
├── IGT_P001_2025-12-20_....png      # Analiz grafikleri
└── IGT_P001_2025-12-20_....txt      # Özet rapor
```

## ⚙️ Yapılandırma

`Config` sınıfı içinde ayarlanabilir:

```python
class Config:
    START_BALANCE = 100000           # Başlangıç bakiyesi (TL)
    MAX_TRIALS = 100                 # Deneme sayısı (Standart IGT)
    FULLSCREEN = False               # Tam ekran modu
    WINDOW_SIZE = (1600, 900)        # Pencere boyutu
    SHOW_CONTROL_BUTTONS = True      # Kontrol butonları (açık/kapalı)
    MAX_SESSIONS_STORED = 200        # Veritabanı kapasitesi (200 denek)
```

## 🆔 Otomatik ID Sistemi

Her test başlangıcında otomatik olarak benzersiz bir ID oluşturulur:

**Format:** `DYYYYMMDD_HHMMSSmmm` (milisaniye hassasiyetli)

**Örnekler:**
- `D20251220_143055123` - 20 Aralık 2025, 14:30:55.123
- `D20251221_091234456` - 21 Aralık 2025, 09:12:34.456

Bu sistem:
- ✅ Çakışma riski yok (milisaniye hassasiyeti)
- ✅ Tarih/saat bilgisi içerir
- ✅ Otomatik oluşturulur
- ✅ İnsan hatası önler
- ✅ Sıralı düzen (tarih bazlı)

## 🎮 Kullanıcı Arayüzü

### Tanıtım Ekranı
- Görev açıklaması
- Katılımcı bilgileri gösterimi
- Başlat butonu (yanıp sönen)

### Ana Deney Ekranı
- 4 renkli kart destesi (A: Kırmızı, B: Turuncu, C: Yeşil, D: Mavi)
- Bakiye göstergesi
- Tur sayacı
- Kontrol butonları (opsiyonel)

### Geri Bildirim
- Kazanç miktarı (yeşil)
- Ceza miktarı (kırmızı)
- Net sonuç (dinamik renk)

## 📊 Dashboard

HTML dashboard'a erişim:

```bash
# Tarayıcıda açın
open Sonuclar/igt_dashboard.html
```

Özellikler:
- 📊 Toplam oturum sayısı
- 💰 Ortalama net değişim
- 🏆 En yüksek/düşük bakiye
- 🔍 Katılımcı arama
- 📋 Oturum detayları tablosu

## 🔧 Geliştirme

### Kod Yapısı

```
igt_experiment.py
├── 1. Logging Setup
├── 2. Configuration (Config class)
├── 3. Penalty Schedules
├── 4. Output Directory Helper
├── 5. Database Helpers
├── 6. Analysis & Visualization
└── 7. Main Experiment GUI
```

### Type Hints
Tüm fonksiyonlar type hint'ler ile dokümente edilmiştir:

```python
def run_analysis(
    csv_path: str,
    subject_id: str,
    age: Optional[int] = None,
    gender: Optional[str] = None
) -> Tuple[str, str]:
    ...
```

## 📚 Bilimsel Referans

```
Bechara, A., Damasio, A. R., Damasio, H., & Anderson, S. W. (1994).
Insensitivity to future consequences following damage to human prefrontal cortex.
Cognition, 50(1-3), 7-15.
```

## 👨‍💻 Geliştirici

**Dr. H. Fehmi ÖZEL**  
Manisa Celal Bayar Üniversitesi  
Sağlık Hizmetleri Meslek Yüksekokulu  
2025

## 📄 Lisans

Bu yazılım akademik ve klinik araştırma amaçlı kullanım içindir.

## 🐛 Sorun Giderme

### Pencere Açılmıyor
- PsychoPy'nin doğru yüklendiğinden emin olun
- `igt_debug.log` dosyasını kontrol edin

### Veritabanı Hatası
- `Sonuclar/` klasörünün yazma izinleri olduğundan emin olun
- Eski `.db` dosyasını silin ve yeniden deneyin

### Grafik Oluşturulmuyor
- Matplotlib'in yüklü olduğundan emin olun
- Agg backend kullanıldığından emin olun (kod içinde ayarlıdır)

## 📞 İletişim

Sorularınız için:
- Log dosyalarını kontrol edin: `Sonuclar/igt_debug.log`
- Test scriptlerini çalıştırın: `python3 test_igt_functions.py`

---

**Son Güncelleme:** 20 Aralık 2025  
**Versiyon:** 2.0 Enhanced


