# 📋 Iowa Gambling Task - Değişiklik Günlüğü

## 🚀 v3.0 - PyQt6 GUI & Ana Menü Sistemi (20 Aralık 2025)

### ✨ Yeni Özellikler

#### 1. **Ana Menü Sistemi** 🏠
- ✅ Modern ana menü ekranı
- ✅ 🧪 Yeni Test Başlat butonu
- ✅ 📊 Veri Kayıtlarını Görüntüle butonu
- ✅ ℹ️ Hakkında & Yardım butonu
- ✅ 🚪 Çıkış butonu
- ✅ Test tamamlandıktan sonra ana menüye dönüş
- ✅ Kullanıcı dostu navigasyon

#### 2. **Veri Görüntüleyici** 📊
- ✅ Veritabanındaki tüm kayıtları listeleyen tablo
- ✅ Kolon başlıkları: ID, Katılımcı ID, Yaş, Cinsiyet, Tarih, Final Bakiye, Net IGT Skoru
- ✅ Satır seçimi ve dosya açma işlemleri
- ✅ 📄 CSV Aç butonu
- ✅ 📊 Grafik Aç (PNG) butonu
- ✅ 📝 Özet Aç (TXT) butonu
- ✅ 📁 Klasörü Aç butonu
- ✅ 🔄 Yenile butonu
- ✅ Net IGT skorunun renkli gösterimi (pozitif=yeşil, negatif=kırmızı)
- ✅ Alternating row colors (okunabilirlik)
- ✅ Toplam kayıt sayısı gösterimi

#### 3. **PyQt6 Tam Entegrasyonu** 🖼️
- ✅ Tkinter tamamen kaldırıldı
- ✅ PyQt6 ile tutarlı GUI
- ✅ Modern, responsive tasarım
- ✅ QTableWidget ile profesyonel tablo görünümü
- ✅ Sistem dosya açıcılarıyla entegrasyon (macOS/Windows/Linux)

#### 4. **Gelişmiş Özet Rapor** 📝
- ✅ **Net IGT Skoru** hesaplama ve gösterimi
- ✅ Formül: (C+D seçimleri) - (A+B seçimleri)
- ✅ Avantajlı/Dezavantajlı deste seçim sayıları
- ✅ Deste bazlı detaylı istatistikler (yüzde ile)
- ✅ Final bakiye ve net değişim
- ✅ Blok bazlı net skorlar
- ✅ TXT formatında kapsamlı rapor

#### 5. **Shimmer Senkronizasyonu** ⏱️
- ✅ 3-2-1 countdown ekranı
- ✅ Sync timestamp logging
- ✅ Shimmer EDA/PPG cihazı entegrasyon hazırlığı
- ✅ Post-processing script (`merge_shimmer_igt.py`)
- ✅ Detaylı entegrasyon kılavuzu (`SHIMMER_INTEGRATION_GUIDE.md`)

### 🔧 İyileştirmeler

#### UI/UX
- ✅ Ana menü ile merkezi kontrol
- ✅ Test akışı daha net ve organize
- ✅ Sonuç ekranında "Ana Menü" ve "Sonuçları Görüntüle" butonları
- ✅ Veri görüntüleyicide kolay dosya erişimi
- ✅ Modern, profesyonel görünüm

#### Kod Kalitesi
- ✅ MainMenuScreen class'ı eklendi
- ✅ DataViewerScreen class'ı eklendi
- ✅ IGTMainWindow navigasyon metodları eklendi
- ✅ FutureWarning uyarıları giderildi (pandas groupby)
- ✅ Daha temiz ve modüler kod yapısı

#### Analiz
- ✅ Net IGT skoru hesaplama fonksiyonu
- ✅ Deste seçim istatistikleri
- ✅ Yüzde hesaplamaları
- ✅ Renkli skor gösterimi

### 📊 Teknik Detaylar

#### Yeni Sınıflar
```python
class MainMenuScreen(QWidget):
    """Ana menü ekranı"""
    start_new_test_signal = pyqtSignal()
    view_data_signal = pyqtSignal()

class DataViewerScreen(QWidget):
    """Veritabanı kayıtlarını görüntüleme ekranı"""
    back_signal = pyqtSignal()
```

#### Yeni Metodlar
```python
def show_main_menu(self)
def show_welcome(self)
def show_data_viewer(self)
def calculate_net_score(self, session_id: int) -> int
```

#### Widget Güncellemeleri
```python
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, 
    QHeaderView, QAbstractItemView
)
```

### 🧪 Test Edildi

| Özellik | Durum | Detay |
|---------|-------|-------|
| Ana Menü | ✅ | Tüm butonlar çalışıyor |
| Yeni Test | ✅ | Test akışı düzgün |
| Veri Görüntüleyici | ✅ | Tablo yükleniyor |
| Dosya Açma | ✅ | CSV/PNG/TXT açılıyor |
| Net IGT Skoru | ✅ | TXT'de hesaplanıyor |
| Shimmer Sync | ✅ | Countdown çalışıyor |
| Ana Menüye Dönüş | ✅ | Test sonrası dönüş |

**Toplam Başarı: 7/7 (100%)** ✅

### 🎯 Kullanıcı Deneyimi

#### Yeni Deney Akışı
1. 🏠 **Ana Menü** gösterilir
2. 🧪 "Yeni Test Başlat" tıklanır
3. 🆔 Katılımcı bilgileri girilir
4. 📋 Talimatlar okunur
5. ⏱️ Shimmer senkronizasyonu (3-2-1)
6. 🃏 100 kart seçimi yapılır
7. 📊 Sonuçlar gösterilir
8. 🏠 Ana menüye dönülür

#### Veri İnceleme Akışı
1. 🏠 Ana menüde "Veri Kayıtlarını Görüntüle" tıklanır
2. 📊 Tüm kayıtlar tablo halinde görülür
3. 🖱️ İstenen kayıt seçilir
4. 📄 CSV/PNG/TXT dosyaları açılır
5. 📁 Sonuçlar klasörü açılır
6. 🏠 Ana menüye dönülür

### 🔄 Önceki Versiyondan Değişiklikler

#### Kaldırılanlar
- ❌ PsychoPy bağımlılığı
- ❌ Tkinter dialog sistemi
- ❌ Direkt test başlatma

#### Eklenenler
- ✅ PyQt6 full GUI
- ✅ Ana menü sistemi
- ✅ Veri görüntüleyici
- ✅ Net IGT skoru
- ✅ Shimmer senkronizasyonu

### 📚 Dokümantasyon

- ✅ README.md güncellendi (v3.0)
- ✅ CHANGELOG.md güncellendi
- ✅ SHIMMER_INTEGRATION_GUIDE.md eklendi
- ✅ merge_shimmer_igt.py script'i eklendi

### 🐛 Düzeltilen Hatalar

- ✅ Kart tıklama sorunu düzeltildi (QTimer.singleShot)
- ✅ FutureWarning uyarıları giderildi
- ✅ ID generator millisaniye hassasiyeti eklendi
- ✅ Test tamamlandıktan sonra uygulama kapanmıyor (ana menüye dönüyor)

---

## 🎯 v2.1 - Klasik IGT Standardı (20 Aralık 2025)

### ✨ Yeni Özellikler

#### 1. **100 Deneme Standardı** ⭐
- ✅ MAX_TRIALS: 200 → **100** (Klasik IGT protokolü)
- ✅ 5 blok x 20 deneme = 100 toplam kart seçimi
- ✅ Bechara et al. (1994) orijinal standardına uygun

#### 2. **Otomatik ID Oluşturma Sistemi** 🆔
- ✅ Format: `DYYYYMMDD_HHMMSSmmm` (milisaniye hassasiyetli)
- ✅ Örnek: `D20251220_173447437`
- ✅ Çakışma riski sıfır
- ✅ Sıralı düzen (tarih bazlı sıralama)
- ✅ Manuel ID girişi kaldırıldı

#### 3. **GUI ile Bilgi Girişi** 🖼️
- ✅ Tkinter tabanlı dialog sistemı
- ✅ Otomatik oluşturulan ID gösterimi
- ✅ Yaş ve cinsiyet girişi (validasyon ile)
- ✅ Kullanıcı dostu arayüz
- ✅ İptal koruması

#### 4. **PyInstaller Paketleme** 📦
- ✅ `IGT.spec` dosyası eklendi
- ✅ `build_app.sh` (macOS/Linux)
- ✅ `build_app.bat` (Windows)
- ✅ Tek tıkla çalıştırılabilir .app/.exe
- ✅ Bağımlılıklar dahil

#### 5. **200 Denek Kapasitesi** 🗄️
- ✅ Veritabanı MAX_SESSIONS_STORED: 200
- ✅ Otomatik eski kayıt temizleme
- ✅ Dashboard 50 oturum gösterimi
- ✅ Tam metadata tracking

### 🔧 İyileştirmeler

#### Kod Kalitesi
- ✅ Tüm fonksiyonlarda type hints
- ✅ Detaylı docstrings
- ✅ Gelişmiş error handling
- ✅ Logging sistemi (dual output)

#### Test Coverage
- ✅ 7/7 test başarılı (100%)
- ✅ ID generator testi eklendi
- ✅ Config parametreleri güncellendi
- ✅ Otomatik test suite

#### Dokümantasyon
- ✅ README.md güncel
- ✅ CHANGELOG.md eklendi
- ✅ TEST_RESULTS.md güncellendi
- ✅ Build scriptleri dokümante edildi

### 📊 Teknik Detaylar

#### Format Değişiklikleri
```python
# Öncesi
MAX_TRIALS = 200
subject_id = input("ID giriniz:")  # Manuel giriş

# Sonrası  
MAX_TRIALS = 100  # Standart IGT
subject_id = generate_subject_id()  # Otomatik: D20251220_173447437
```

#### Yeni Fonksiyonlar
```python
def generate_subject_id() -> str
    """Otomatik benzersiz ID oluşturur"""

def get_subject_info_gui() -> Tuple[str, int, str]
    """Tkinter GUI ile bilgi alır"""
```

#### Dependency Güncellemesi
```python
import tkinter as tk
from tkinter import messagebox, simpledialog
```

### 🧪 Test Sonuçları

| Test | Durum | Detay |
|------|-------|-------|
| Import | ✅ | Tüm modüller |
| Config | ✅ | MAX_TRIALS=100, SESSIONS=200 |
| Deck | ✅ | Kart çekimi çalışıyor |
| Output Dir | ✅ | Sonuclar/ klasörü |
| Database | ✅ | SQLite yapısı |
| Schedule | ✅ | Randomize ceza |
| ID Generator | ✅ | Benzersiz milisaniye ID |

**Toplam Başarı: 7/7 (100%)** ✅

### 📦 Paketleme Talimatları

#### macOS
```bash
./build_app.sh
open dist/IGT.app
```

#### Windows
```bash
build_app.bat
IGT.exe
```

#### Sonuç
- 📦 dist/IGT.app (macOS)
- 📦 dist/IGT.exe (Windows)
- 📦 Bağımlılıklar dahil
- 📦 Tek tıkla çalıştırma

### 🎯 Kullanıcı Deneyimi

#### Deney Akışı
1. 🚀 Uygulama başlatılır
2. 🆔 ID otomatik oluşturulur
3. 📋 Yaş/Cinsiyet sorulur (GUI)
4. 🎬 Tanıtım ekranı
5. ▶️ Başlat butonu
6. 🃏 100 kart seçimi
7. 📊 Otomatik analiz
8. 💾 Veritabanı kaydı

#### Çıktılar
- 📄 CSV (zaman damgalı, 100 satır)
- 📊 PNG (4 panel, 5 blok)
- 📝 TXT (özet skorlar)
- 🗄️ SQLite (200 denek kapasiteli)
- 🌐 HTML Dashboard

### 🔄 Geriye Dönük Uyumluluk

⚠️ **UYARI:** Bu versiyon önceki versiyonlarla uyumlu DEĞİLDİR:

- ❌ CLI argümanları kaldırıldı (--subject_id, --age, --gender)
- ❌ Manuel ID girişi kaldırıldı
- ❌ 200 deneme desteği kaldırıldı

✅ **Uyumlu:** Veritabanı şeması, CSV formatı, analiz algoritmaları

### 📚 Bilimsel Uyumluluk

Bu versiyon aşağıdaki standartlara uyar:

1. ✅ **Bechara et al. (1994)** - Orijinal protokol
2. ✅ **100 deneme** - Standart IGT
3. ✅ **4 deste** (A, B, C, D)
4. ✅ **Ceza programları** - Orijinal çizelgeler
5. ✅ **Trial-by-trial kayıt** - Her seçim kaydedilir

### 🐛 Bilinen Sorunlar

- ⚠️ macOS Sonoma'da ilk açılışta izin sorulabilir
- ⚠️ PyInstaller paketleme ~100 MB boyut
- ⚠️ PsychoPy yükleme süresi ~15 saniye

### 🚀 Gelecek Planlar

- [ ] Multi-language desteği (İngilizce)
- [ ] Ses efektleri (opsiyonel)
- [ ] Kart animasyonları
- [ ] Cloud sync (opsiyonel)
- [ ] Excel export
- [ ] Statistical analysis tools

---

## 📊 v2.0 - Enhanced UI/UX (19 Aralık 2025)

### İlk Sürüm
- Modern UI/UX
- Veritabanı entegrasyonu
- Dashboard sistemi
- Type hints & docstrings
- Logging sistemi

---

**Son Güncelleme:** 20 Aralık 2025  
**Geliştirici:** Dr. H. Fehmi ÖZEL  
**Kurum:** MCBÜ - Sağlık Hizmetleri MYO

