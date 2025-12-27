# 🔬 IGT + Shimmer EDA/PPG Entegrasyon Kılavuzu

## 📋 Genel Bakış

Iowa Gambling Task (IGT) uygulaması, Shimmer3 EDA/PPG cihazı ile senkronize çalışacak şekilde yapılandırılmıştır. Bu kılavuz, entegrasyonu ve veri analizi sürecini açıklar.

## ✨ Eklenen Özellikler

### 1. **Senkronizasyon Countdown Ekranı**
- ⏱️ 3-2-1 countdown sistemi
- 🔄 Sync marker otomatik kaydı
- 📊 Log dosyasına timestamp
- 🎯 Shimmer ve IGT senkronizasyonu

### 2. **Gelişmiş Loglama**
- 🔄 Sync marker timestamp
- 📝 Experiment start logging
- 🃏 Her kart seçimi kaydı
- ⏱️ Reaksiyon zamanları

### 3. **CSV Metadata**
- 📅 İlk trial'da sync timestamp
- 🕐 Milisaniye hassasiyeti
- 📊 Post-processing için hazır

---

## 🎮 Kullanım Adımları

### **Deney Öncesi Hazırlık**

#### 1. Shimmer Cihazını Hazırlayın
```
✅ Shimmer3 GSR+ sensörünü şarj edin
✅ Katılımcıya takın (parmak elektrodu)
✅ ConsensysPRO yazılımını açın
✅ Cihazı Bluetooth ile bağlayın
```

#### 2. IGT Uygulamasını Başlatın
```bash
python3 main.py
```

---

### **Deney Sırasında**

#### **Adım 1: Katılımcı Bilgileri**
- 🆔 Otomatik ID oluşur: `DYYYYMMDD_HHMMSSmmm`
- 🎂 Yaş girin
- ⚧ Cinsiyet seçin (Erkek/Kadın)
- ▶️ "TESTE BAŞLA" tıklayın

#### **Adım 2: Talimatlar**
- 📋 Katılımcıya görev açıklamasını okutun
- ▶️ "BAŞLA" tıklayın

#### **Adım 3: Shimmer Senkronizasyonu** ⭐
```
┌─────────────────────────────────────┐
│  ⏱️ SHIMMER SENKRONIZASYONU        │
│                                     │
│  📋 SENKRONIZASYON ADIMLARI:       │
│                                     │
│  1️⃣ Shimmer cihazını takın         │
│  2️⃣ ConsensysPRO'da hazırlayın    │
│  3️⃣ Aşağıdaki butona tıklayın     │
│  4️⃣ Countdown'da Shimmer BAŞLAT   │
│                                     │
│          [Bekleniyor...]            │
│                                     │
│  [🔄 SENKRONIZASYON BAŞLAT]        │
└─────────────────────────────────────┘
```

**ÇOK ÖNEMLİ:**
1. IGT'de "SENKRONIZASYON BAŞLAT" butonuna tıklayın
2. **3-2-1 countdown başlar**
3. **"3" göründüğünde ConsensysPRO'da "Start" tıklayın**
4. Countdown "BAŞLA! 🚀" gösterir
5. IGT deneyi otomatik başlar

#### **Adım 4: Deney**
- 🃏 100 kart seçimi
- 💾 Otomatik kayıt

#### **Adım 5: Deney Sonrası**
- ⏹️ ConsensysPRO'da "Stop" tıklayın
- 📁 Shimmer CSV'sini dışa aktarın
- ✅ IGT otomatik analiz yapar

---

## 📊 Çıktılar

### **IGT Dosyaları** (`Sonuclar/` klasörü)

#### 1. **CSV Dosyası**
```csv
Subject_ID,Trial_Number,Deck_Selected,Reaction_Time,Trial_Real_Time,Sync_Timestamp
D20251220_202747429,1,A,1.234,2025-12-20T20:28:15,2025-12-20T20:28:12.345
D20251220_202747429,2,C,0.987,2025-12-20T20:28:18,
...
```

**Önemli Sütunlar:**
- `Trial_Real_Time`: Her trial'ın gerçek zamanı (ISO 8601)
- `Sync_Timestamp`: İlk trial'da sync marker (milisaniye hassasiyetli)
- `Reaction_Time`: Kart tıklama süresi

#### 2. **Log Dosyası** (`igt_app.log`)
```
============================================================
🔄 SYNC_MARKER: 2025-12-20T20:28:12.345678
   Timestamp: 2025-12-20 20:28:12.345678
============================================================

============================================================
🎮 EXPERIMENT STARTING
   Subject: D20251220_202747429
   Age: 25
   Gender: E
   Start Time: 2025-12-20T20:28:12.345678
   ✅ Synced with Shimmer countdown
============================================================
```

### **Shimmer Dosyaları** (ConsensysPRO Export)

#### Format Örneği:
```csv
Time (s),GSR_Skin_Conductance_CAL,PPG_A13_CAL
0.000,2.345,1234.56
0.050,2.347,1235.12
0.100,2.351,1236.78
...
```

---

## 🔧 Post-Processing: Veri Birleştirme

### **Python Script** (`merge_shimmer_igt.py`)

```python
#!/usr/bin/env python3
"""
IGT + Shimmer Veri Birleştirme Script'i
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def merge_igt_shimmer(igt_csv, shimmer_csv):
    """IGT ve Shimmer verilerini birleştirir"""
    
    # 1. Dosyaları yükle
    igt_df = pd.read_csv(igt_csv)
    shimmer_df = pd.read_csv(shimmer_csv)
    
    # 2. Zaman damgalarını ayarla
    igt_df['IGT_Time'] = pd.to_datetime(igt_df['Trial_Real_Time'])
    
    # Sync marker'ı al (ilk trial)
    sync_marker = pd.to_datetime(igt_df.loc[0, 'Sync_Timestamp'])
    
    # Shimmer zamanını sync marker'a göre ayarla
    shimmer_df['Shimmer_Time'] = sync_marker + pd.to_timedelta(
        shimmer_df['Time (s)'], unit='s'
    )
    
    # 3. Her trial için SCR hesapla
    results = []
    
    for idx, trial in igt_df.iterrows():
        trial_time = trial['IGT_Time']
        
        # Baseline: Trial öncesi 2 saniye
        baseline_start = trial_time - timedelta(seconds=2)
        baseline_mask = (shimmer_df['Shimmer_Time'] >= baseline_start) & \
                       (shimmer_df['Shimmer_Time'] < trial_time)
        baseline_scr = shimmer_df[baseline_mask]['GSR_Skin_Conductance_CAL'].mean()
        
        # Response: Trial sonrası 1-5 saniye (SCR latency)
        response_start = trial_time + timedelta(seconds=1)
        response_end = trial_time + timedelta(seconds=5)
        response_mask = (shimmer_df['Shimmer_Time'] >= response_start) & \
                       (shimmer_df['Shimmer_Time'] <= response_end)
        response_scr = shimmer_df[response_mask]['GSR_Skin_Conductance_CAL'].max()
        
        # SCR amplitude
        scr_amplitude = response_scr - baseline_scr if not pd.isna(baseline_scr) else np.nan
        
        # PPG (opsiyonel)
        if 'PPG_A13_CAL' in shimmer_df.columns:
            ppg_mean = shimmer_df[response_mask]['PPG_A13_CAL'].mean()
        else:
            ppg_mean = np.nan
        
        # Birleştir
        result = trial.to_dict()
        result['SCR_Baseline'] = baseline_scr
        result['SCR_Peak'] = response_scr
        result['SCR_Amplitude'] = scr_amplitude
        result['PPG_Mean'] = ppg_mean
        
        results.append(result)
    
    # 4. Kaydet
    merged_df = pd.DataFrame(results)
    output_file = igt_csv.replace('.csv', '_Shimmer.csv')
    merged_df.to_csv(output_file, index=False)
    
    print(f"✅ Birleştirilmiş dosya: {output_file}")
    print(f"📊 Toplam trial: {len(merged_df)}")
    print(f"📈 SCR verisi bulunan trial: {merged_df['SCR_Amplitude'].notna().sum()}")
    
    return merged_df

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Kullanım: python merge_shimmer_igt.py <igt.csv> <shimmer.csv>")
        sys.exit(1)
    
    merge_igt_shimmer(sys.argv[1], sys.argv[2])
```

### **Kullanım:**

```bash
python3 merge_shimmer_igt.py \
  Sonuclar/IGT_D20251220_202747429_2025-12-20_20-28-15.csv \
  Shimmer_Session_20251220.csv
```

### **Çıktı:**

```csv
Subject_ID,Trial_Number,Deck_Selected,Reaction_Time,Trial_Real_Time,SCR_Baseline,SCR_Peak,SCR_Amplitude,PPG_Mean
D20251220_202747429,1,A,1.234,2025-12-20T20:28:15,2.345,2.567,0.222,1235.67
D20251220_202747429,2,C,0.987,2025-12-20T20:28:18,2.351,2.389,0.038,1236.89
...
```

---

## 📈 Analiz Örnekleri

### **1. Advantageous vs Disadvantageous Decks SCR**

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Veriyi yükle
df = pd.read_csv('IGT_XXXXX_Shimmer.csv')

# Deste tipine göre grupla
df['Deck_Type'] = df['Deck_Selected'].apply(
    lambda x: 'Disadvantageous' if x in ['A', 'B'] else 'Advantageous'
)

# SCR karşılaştır
sns.boxplot(data=df, x='Deck_Type', y='SCR_Amplitude')
plt.title('SCR Amplitude by Deck Type')
plt.ylabel('SCR Amplitude (µS)')
plt.show()
```

### **2. Trial Bloklarına Göre SCR Değişimi**

```python
# 20'lik bloklara böl
df['Block'] = ((df['Trial_Number'] - 1) // 20) + 1

# Blok bazında ortalama SCR
block_scr = df.groupby('Block').agg({
    'SCR_Amplitude': ['mean', 'std']
}).reset_index()

plt.errorbar(block_scr['Block'], 
             block_scr[('SCR_Amplitude', 'mean')],
             yerr=block_scr[('SCR_Amplitude', 'std')])
plt.xlabel('Block (20 trials)')
plt.ylabel('Mean SCR Amplitude')
plt.title('SCR Changes Across Blocks')
plt.show()
```

---

## ⚠️ Sorun Giderme

### **Senkronizasyon Sorunları**

#### **Sorun 1: Zaman farkı var**
```
Çözüm: Sync marker'ı manuel düzeltin
```

```python
# merge script'te sync offset ekle
sync_offset_seconds = 2  # Shimmer 2 saniye geç başladı
sync_marker_adjusted = sync_marker + timedelta(seconds=sync_offset_seconds)
```

#### **Sorun 2: ConsensysPRO geç başlatıldı**
```
Çözüm: İlk birkaç trial'ı analiz dışı bırakın
```

```python
# İlk 5 trial'ı atla
df_analysis = df[df['Trial_Number'] > 5]
```

### **Veri Kalitesi**

#### **Eksik SCR Verisi**
```python
# Eksik veriyi kontrol et
missing_scr = df['SCR_Amplitude'].isna().sum()
print(f"Eksik SCR: {missing_scr}/{len(df)} trial")

# Eksik veriyi interpolate et (opsiyonel)
df['SCR_Amplitude'].interpolate(method='linear', inplace=True)
```

---

## 📚 Referanslar

### **Shimmer Sampling Rate**
- EDA: 51.2 Hz (önerilen)
- PPG: 51.2 Hz

### **SCR Penceresi**
- Baseline: Trial öncesi 2 saniye
- Response: Trial sonrası 1-5 saniye (pik latency)

### **Bilimsel Referanslar**
```
Dawson, M. E., Schell, A. M., & Filion, D. L. (2007).
The electrodermal system. Handbook of psychophysiology, 200-223.

Boucsein, W. (2012).
Electrodermal activity. Springer Science & Business Media.
```

---

## ✅ Checklist

### **Deney Öncesi**
- [ ] Shimmer şarj edildi
- [ ] Elektrotlar takıldı
- [ ] ConsensysPRO bağlandı
- [ ] IGT uygulaması test edildi
- [ ] Merge script hazır

### **Deney Sırasında**
- [ ] Katılımcı bilgileri girildi
- [ ] Sync countdown yapıldı
- [ ] Shimmer kaydı başlatıldı
- [ ] 100 trial tamamlandı
- [ ] Shimmer kaydı durduruldu

### **Deney Sonrası**
- [ ] IGT CSV kaydedildi
- [ ] Shimmer CSV dışa aktarıldı
- [ ] Merge script çalıştırıldı
- [ ] Veri kalitesi kontrol edildi
- [ ] Analiz tamamlandı

---

## 🎯 Özet

**Entegrasyon Tipi:** Post-processing + Senkronizasyon Countdown

**Avantajlar:**
- ✅ Güvenilir (bağımsız sistemler)
- ✅ Basit (karmaşık API yok)
- ✅ Esnek (farklı analizler)
- ✅ Test edilmiş

**Dosyalar:**
- `main.py` - Sync ekranı eklenmiş IGT
- `merge_shimmer_igt.py` - Veri birleştirme script'i
- `igt_app.log` - Sync marker log

**Destek:**
- Log dosyasını kontrol edin
- Pilot test yapın
- Senkronizasyon doğrulayın

---

**Geliştiren:** Dr. H. Fehmi ÖZEL  
**Tarih:** 20 Aralık 2025  
**Versiyon:** IGT v3.0 + Shimmer Integration

