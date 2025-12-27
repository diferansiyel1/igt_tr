#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IGT + Shimmer EDA/PPG Data Merger
Shimmer EDA/PPG verilerini IGT deney verisiyle eşleştirir

Author: Dr. H. Fehmi ÖZEL
Date: 2025-12-20
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

def load_igt_data(igt_csv_path):
    """IGT CSV dosyasını yükler"""
    print(f"📁 IGT dosyası yükleniyor: {igt_csv_path}")
    df = pd.read_csv(igt_csv_path)
    df['IGT_Time'] = pd.to_datetime(df['Trial_Real_Time'])
    print(f"✅ {len(df)} trial yüklendi")
    return df

def load_shimmer_data(shimmer_csv_path):
    """Shimmer CSV dosyasını yükler"""
    print(f"📁 Shimmer dosyası yükleniyor: {shimmer_csv_path}")
    df = pd.read_csv(shimmer_csv_path)
    print(f"✅ {len(df)} Shimmer sample yüklendi")
    return df

def merge_data(igt_df, shimmer_df, sync_offset_seconds=0):
    """
    IGT ve Shimmer verilerini birleştirir
    
    Args:
        igt_df: IGT DataFrame
        shimmer_df: Shimmer DataFrame
        sync_offset_seconds: Shimmer başlangıç offset (saniye)
    
    Returns:
        Birleştirilmiş DataFrame
    """
    print("\n🔄 Veriler birleştiriliyor...")
    
    # Sync marker'ı al
    if 'Sync_Timestamp' in igt_df.columns and pd.notna(igt_df.loc[0, 'Sync_Timestamp']):
        sync_marker = pd.to_datetime(igt_df.loc[0, 'Sync_Timestamp'])
        print(f"✅ Sync marker bulundu: {sync_marker.isoformat()}")
    else:
        # Fallback: İlk trial zamanını kullan
        sync_marker = igt_df.loc[0, 'IGT_Time']
        print(f"⚠️ Sync marker bulunamadı, ilk trial zamanı kullanılıyor: {sync_marker.isoformat()}")
    
    # Offset ekle
    if sync_offset_seconds != 0:
        sync_marker = sync_marker + timedelta(seconds=sync_offset_seconds)
        print(f"🔧 Sync offset uygulandı: {sync_offset_seconds} saniye")
    
    # Shimmer zamanını ayarla
    if 'Time (s)' in shimmer_df.columns:
        time_col = 'Time (s)'
    elif 'Timestamp (ms)' in shimmer_df.columns:
        time_col = 'Timestamp (ms)'
        shimmer_df['Time (s)'] = shimmer_df[time_col] / 1000.0
        time_col = 'Time (s)'
    else:
        print("❌ Shimmer zaman sütunu bulunamadı!")
        return None
    
    shimmer_df['Shimmer_Time'] = sync_marker + pd.to_timedelta(
        shimmer_df[time_col], unit='s'
    )
    
    # Her trial için SCR hesapla
    results = []
    
    for idx, trial in igt_df.iterrows():
        trial_time = trial['IGT_Time']
        
        # Baseline: Trial öncesi 2 saniye
        baseline_start = trial_time - timedelta(seconds=2)
        baseline_mask = (shimmer_df['Shimmer_Time'] >= baseline_start) & \
                       (shimmer_df['Shimmer_Time'] < trial_time)
        
        # GSR sütununu bul
        gsr_col = None
        for col in shimmer_df.columns:
            if 'GSR' in col or 'Skin_Conductance' in col:
                gsr_col = col
                break
        
        if gsr_col:
            baseline_scr = shimmer_df[baseline_mask][gsr_col].mean()
            
            # Response: Trial sonrası 1-5 saniye (SCR latency)
            response_start = trial_time + timedelta(seconds=1)
            response_end = trial_time + timedelta(seconds=5)
            response_mask = (shimmer_df['Shimmer_Time'] >= response_start) & \
                           (shimmer_df['Shimmer_Time'] <= response_end)
            response_scr = shimmer_df[response_mask][gsr_col].max()
            
            # SCR amplitude
            scr_amplitude = response_scr - baseline_scr if not pd.isna(baseline_scr) else np.nan
        else:
            baseline_scr = np.nan
            response_scr = np.nan
            scr_amplitude = np.nan
            print("⚠️ GSR sütunu bulunamadı!")
        
        # PPG (opsiyonel)
        ppg_col = None
        for col in shimmer_df.columns:
            if 'PPG' in col:
                ppg_col = col
                break
        
        if ppg_col:
            ppg_mask = response_mask
            ppg_mean = shimmer_df[ppg_mask][ppg_col].mean()
        else:
            ppg_mean = np.nan
        
        # Birleştir
        result = trial.to_dict()
        result['SCR_Baseline_uS'] = baseline_scr
        result['SCR_Peak_uS'] = response_scr
        result['SCR_Amplitude_uS'] = scr_amplitude
        result['PPG_Mean'] = ppg_mean
        
        results.append(result)
        
        # İlerleme
        if (idx + 1) % 20 == 0:
            print(f"   İşlenen trial: {idx + 1}/{len(igt_df)}")
    
    merged_df = pd.DataFrame(results)
    
    # İstatistikler
    valid_scr = merged_df['SCR_Amplitude_uS'].notna().sum()
    print(f"\n✅ Birleştirme tamamlandı!")
    print(f"   Toplam trial: {len(merged_df)}")
    print(f"   Geçerli SCR verisi: {valid_scr}/{len(merged_df)} trial ({valid_scr/len(merged_df)*100:.1f}%)")
    
    return merged_df

def main():
    """Ana fonksiyon"""
    print("="*60)
    print("🔬 IGT + Shimmer Veri Birleştirme")
    print("="*60)
    
    # Argüman kontrolü
    if len(sys.argv) < 3:
        print("\n❌ Kullanım hatası!")
        print("\nKullanım:")
        print("  python3 merge_shimmer_igt.py <igt.csv> <shimmer.csv> [offset_seconds]")
        print("\nÖrnek:")
        print("  python3 merge_shimmer_igt.py IGT_D20251220_XXX.csv Shimmer_Session.csv")
        print("  python3 merge_shimmer_igt.py IGT_D20251220_XXX.csv Shimmer_Session.csv 2")
        sys.exit(1)
    
    igt_csv = sys.argv[1]
    shimmer_csv = sys.argv[2]
    sync_offset = float(sys.argv[3]) if len(sys.argv) > 3 else 0
    
    # Dosya kontrolü
    if not os.path.exists(igt_csv):
        print(f"❌ IGT dosyası bulunamadı: {igt_csv}")
        sys.exit(1)
    
    if not os.path.exists(shimmer_csv):
        print(f"❌ Shimmer dosyası bulunamadı: {shimmer_csv}")
        sys.exit(1)
    
    print(f"\n📋 Parametreler:")
    print(f"   IGT: {igt_csv}")
    print(f"   Shimmer: {shimmer_csv}")
    print(f"   Sync offset: {sync_offset} saniye")
    print()
    
    # Veriyi yükle
    igt_df = load_igt_data(igt_csv)
    shimmer_df = load_shimmer_data(shimmer_csv)
    
    # Birleştir
    merged_df = merge_data(igt_df, shimmer_df, sync_offset)
    
    if merged_df is None:
        print("❌ Birleştirme başarısız!")
        sys.exit(1)
    
    # Kaydet
    output_file = igt_csv.replace('.csv', '_Shimmer.csv')
    merged_df.to_csv(output_file, index=False)
    
    print(f"\n💾 Çıktı dosyası: {output_file}")
    print(f"\n📊 Sütun listesi:")
    for col in merged_df.columns:
        if 'SCR' in col or 'PPG' in col:
            print(f"   ✅ {col}")
    
    print("\n" + "="*60)
    print("🎉 İşlem tamamlandı!")
    print("="*60)

if __name__ == "__main__":
    main()

