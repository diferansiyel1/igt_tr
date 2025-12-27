#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iowa Gambling Task (IGT) - PyQt6 GUI Version
Author: Dr. H. Fehmi ÖZEL
Institution: MCBÜ - Sağlık Hizmetleri MYO
Version: 3.0
"""

import sys
import os
import random
import sqlite3
import logging
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QComboBox, QMessageBox,
    QStackedWidget, QProgressBar, QFrame, QGridLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

# Data analysis imports
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# =============================================================================
# CONFIGURATION
# =============================================================================
class Config:
    """Uygulama yapılandırma parametreleri"""
    
    # Experiment Parameters
    START_BALANCE = 100000
    REWARD_BAD_DECK = 5000
    REWARD_GOOD_DECK = 2500
    MAX_TRIALS = 100  # Klasik IGT standardı
    
    # Database
    MAX_SESSIONS_STORED = 200
    
    # Colors (Modern Palette)
    BG_COLOR = '#0f0f1e'
    CARD_COLORS = {
        'A': '#e94560',  # Coral red
        'B': '#f39c12',  # Warm orange
        'C': '#00b894',  # Emerald green
        'D': '#0984e3'   # Ocean blue
    }
    PRIMARY_COLOR = '#667eea'
    ACCENT_COLOR = '#f1c40f'
    TEXT_COLOR = '#ffffff'
    SUCCESS_COLOR = '#2ecc71'
    ERROR_COLOR = '#e74c3c'

# =============================================================================
# PENALTY SCHEDULES
# =============================================================================
penalties_A = [0, -7500, 0, -10000, 0, -12500, 0, -15000, 0, -17500] * 10
penalties_B = [0, 0, 0, 0, 0, 0, 0, 0, 0, -62500] * 10
penalties_C = [0, -1250, 0, -1250, 0, -2500, 0, -2500, 0, -5000] * 10
penalties_D = [0, 0, 0, 0, 0, 0, 0, 0, 0, -12500] * 10

def create_schedule(base_list: List[int]) -> List[int]:
    """Ceza listesini 10'luk bloklara böler ve karıştırır"""
    final_schedule = []
    for i in range(0, len(base_list), 10):
        block = base_list[i:i+10]
        random.shuffle(block)
        final_schedule.extend(block)
    return final_schedule

class Deck:
    """Kart destesi sınıfı"""
    def __init__(self, name: str, reward: int, schedule: List[int]):
        self.name = name
        self.reward = reward
        self.schedule = create_schedule(schedule)
        self.draw_count = 0
    
    def draw_card(self) -> Tuple[int, int, int]:
        """Kart çeker ve (reward, penalty, net) döndürür"""
        penalty = self.schedule[self.draw_count % len(self.schedule)]
        self.draw_count += 1
        return self.reward, penalty, self.reward + penalty

# =============================================================================
# DATABASE & FILE MANAGEMENT
# =============================================================================
def get_output_dir() -> str:
    """Çıktı dizinini oluşturur"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    output_dir = os.path.join(base_dir, 'Sonuclar')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def setup_logging():
    """Logging sistemini konfigüre eder"""
    log_path = os.path.join(get_output_dir(), 'igt_app.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('IGT')

def generate_subject_id() -> str:
    """Otomatik benzersiz ID oluşturur"""
    now = datetime.now()
    millisecond = now.microsecond // 1000
    return f"D{now.strftime('%Y%m%d_%H%M%S')}{millisecond:03d}"

def init_database() -> str:
    """SQLite veritabanını hazırlar"""
    db_path = os.path.join(get_output_dir(), 'igt_sessions.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            trials_completed INTEGER DEFAULT 0,
            final_balance INTEGER,
            net_change INTEGER,
            csv_path TEXT,
            png_path TEXT,
            txt_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trials (
            session_id TEXT NOT NULL,
            trial_number INTEGER NOT NULL,
            deck_selected TEXT NOT NULL,
            reaction_time REAL,
            reward INTEGER,
            penalty INTEGER,
            net_outcome INTEGER,
            total_balance INTEGER,
            trial_timestamp TEXT,
            PRIMARY KEY (session_id, trial_number),
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)
    
    conn.commit()
    conn.close()
    return db_path

def save_session_to_db(session_meta: Dict, data_records: List[Dict], 
                       csv_path: str, png_path: str, txt_path: str):
    """Oturumu veritabanına kaydeder"""
    db_path = init_database()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Session kaydı
        cur.execute("""
            INSERT OR REPLACE INTO sessions (
                session_id, subject_id, age, gender, start_time, end_time,
                trials_completed, final_balance, net_change, csv_path, png_path, txt_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_meta["session_id"], session_meta["subject_id"],
            session_meta["age"], session_meta["gender"],
            session_meta["start_time"], session_meta["end_time"],
            session_meta["trials_completed"], session_meta["final_balance"],
            session_meta["net_change"], csv_path, png_path, txt_path
        ))
        
        # Trial kayıtları
        if data_records:
            trial_rows = [
                (session_meta["session_id"], rec["Trial_Number"], rec["Deck_Selected"],
                 rec["Reaction_Time"], rec["Reward"], rec["Penalty"],
                 rec["Net_Outcome"], rec["Total_Balance"], rec["Trial_Real_Time"])
                for rec in data_records
            ]
            cur.executemany("""
                INSERT OR REPLACE INTO trials (
                    session_id, trial_number, deck_selected, reaction_time,
                    reward, penalty, net_outcome, total_balance, trial_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, trial_rows)
        
        # Eski kayıtları temizle (200 limit)
        cur.execute("SELECT session_id FROM sessions ORDER BY start_time DESC")
        rows = cur.fetchall()
        if len(rows) > Config.MAX_SESSIONS_STORED:
            stale_ids = [row[0] for row in rows[Config.MAX_SESSIONS_STORED:]]
            placeholders = ",".join("?" * len(stale_ids))
            cur.execute(f"DELETE FROM trials WHERE session_id IN ({placeholders})", stale_ids)
            cur.execute(f"DELETE FROM sessions WHERE session_id IN ({placeholders})", stale_ids)
        
        conn.commit()
        logging.info(f"✅ Oturum veritabanına kaydedildi: {session_meta['session_id']}")
    except Exception as e:
        logging.error(f"❌ Veritabanı hatası: {e}")
    finally:
        conn.close()

# =============================================================================
# ANALYSIS MODULE
# =============================================================================
def run_analysis(csv_path: str, subject_id: str, age: int, gender: str) -> Tuple[str, str]:
    """Deney sonrası analiz ve görselleştirme"""
    df = pd.read_csv(csv_path)
    
    # 2x2 Dashboard
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'IGT Analiz Raporu - Katılımcı: {subject_id}', 
                 fontsize=16, fontweight='bold')
    
    # --- 1. Learning Curve ---
    ax1 = axes[0, 0]
    df['Block'] = ((df['Trial_Number'] - 1) // 20) + 1
    
    # Net score hesaplama (FutureWarning'i önlemek için)
    block_scores = []
    for block in range(1, 6):
        block_df = df[df['Block'] == block]
        net_score = (block_df['Deck_Selected'].isin(['C', 'D']).sum() - 
                     block_df['Deck_Selected'].isin(['A', 'B']).sum())
        block_scores.append({'Block': block, 'Net_Score': net_score})
    block_data = pd.DataFrame(block_scores)
    
    ax1.plot(block_data['Block'], block_data['Net_Score'], 
             marker='o', linewidth=2.5, markersize=10, color='#3498db')
    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
    ax1.fill_between(block_data['Block'], block_data['Net_Score'], 0,
                     where=(block_data['Net_Score'] >= 0), alpha=0.3, color='green')
    ax1.fill_between(block_data['Block'], block_data['Net_Score'], 0,
                     where=(block_data['Net_Score'] < 0), alpha=0.3, color='red')
    ax1.set_xlabel('Blok (20 Deneme)', fontsize=11)
    ax1.set_ylabel('Net Skor [(C+D) - (A+B)]', fontsize=11)
    ax1.set_title('📈 Öğrenme Eğrisi', fontsize=13, fontweight='bold')
    ax1.set_xticks(range(1, len(block_data) + 1))
    
    # --- 2. Balance Trajectory ---
    ax2 = axes[0, 1]
    ax2.plot(df['Trial_Number'], df['Total_Balance'], 
             linewidth=2, color='#2ecc71')
    ax2.axhline(y=Config.START_BALANCE, color='#e74c3c', linestyle='--', linewidth=1.5)
    ax2.set_xlabel('Deneme Sayısı', fontsize=11)
    ax2.set_ylabel('Toplam Bakiye (TL)', fontsize=11)
    ax2.set_title('💰 Bakiye Değişimi', fontsize=13, fontweight='bold')
    
    # --- 3. Deck Selection ---
    ax3 = axes[1, 0]
    deck_counts = df['Deck_Selected'].value_counts().reindex(['A', 'B', 'C', 'D'], fill_value=0)
    colors = [Config.CARD_COLORS[d] for d in ['A', 'B', 'C', 'D']]
    bars = ax3.bar(deck_counts.index, deck_counts.values, color=colors, edgecolor='white', linewidth=2)
    ax3.set_xlabel('Deste', fontsize=11)
    ax3.set_ylabel('Seçim Sayısı', fontsize=11)
    ax3.set_title('🃏 Deste Seçim Dağılımı', fontsize=13, fontweight='bold')
    for bar, count in zip(bars, deck_counts.values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                 str(count), ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # --- 4. Reaction Time ---
    ax4 = axes[1, 1]
    if 'Reaction_Time' in df.columns:
        rt_stats = df.groupby('Deck_Selected')['Reaction_Time'].agg(['mean', 'std']).reindex(['A', 'B', 'C', 'D'])
        ax4.bar(rt_stats.index, rt_stats['mean'], yerr=rt_stats['std'], 
                color=colors, edgecolor='white', linewidth=2, capsize=5)
        ax4.set_ylabel('Reaksiyon Süresi (sn)', fontsize=11)
    ax4.set_xlabel('Deste', fontsize=11)
    ax4.set_title('⏱️ Ortalama Karar Süresi', fontsize=13, fontweight='bold')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Save
    png_path = csv_path.replace('.csv', '_Analysis.png')
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    
    # Text Summary
    txt_path = csv_path.replace('.csv', '_Summary.txt')
    
    # Net IGT skoru hesapla
    total_net_score = block_data['Net_Score'].sum()
    
    # Deste seçimlerini hesapla
    deck_counts = df['Deck_Selected'].value_counts().reindex(['A', 'B', 'C', 'D'], fill_value=0)
    advantageous_count = deck_counts['C'] + deck_counts['D']
    disadvantageous_count = deck_counts['A'] + deck_counts['B']
    
    # Final bakiye
    final_balance = df['Total_Balance'].iloc[-1]
    net_change = final_balance - Config.START_BALANCE
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write("IGT DENEY ÖZET RAPORU\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Katılımcı ID: {subject_id}\n")
        f.write(f"Yaş: {age}\n")
        f.write(f"Cinsiyet: {gender}\n")
        f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        f.write("-" * 50 + "\n")
        f.write("TEMEL METRİKLER\n")
        f.write("-" * 50 + "\n")
        f.write(f"Net IGT Skoru: {int(total_net_score):+d}\n")
        f.write(f"   [(C+D) - (A+B) seçimleri]\n\n")
        f.write(f"Avantajlı Deste (C+D): {advantageous_count} seçim\n")
        f.write(f"Dezavantajlı Deste (A+B): {disadvantageous_count} seçim\n\n")
        f.write(f"Başlangıç Bakiyesi: {Config.START_BALANCE:,} TL\n")
        f.write(f"Son Bakiye: {final_balance:,} TL\n")
        f.write(f"Net Değişim: {net_change:+,} TL\n\n")
        
        f.write("-" * 50 + "\n")
        f.write("BLOK BAZLI NET SKORLAR\n")
        f.write("-" * 50 + "\n")
        for _, row in block_data.iterrows():
            f.write(f"Blok {int(row['Block'])}: {int(row['Net_Score']):+d}\n")
        
        f.write("\n" + "-" * 50 + "\n")
        f.write("DESTE SEÇİM DETAYLARI\n")
        f.write("-" * 50 + "\n")
        for deck in ['A', 'B', 'C', 'D']:
            count = deck_counts.get(deck, 0)
            deck_type = "Dezavantajlı" if deck in ['A', 'B'] else "Avantajlı"
            percentage = (count / len(df) * 100) if len(df) > 0 else 0
            f.write(f"Deste {deck} ({deck_type}): {count} seçim ({percentage:.1f}%)\n")
    
    logging.info(f"✅ Analiz tamamlandı: {png_path}")
    return png_path, txt_path

# =============================================================================
# PyQt6 GUI - MAIN MENU SCREEN
# =============================================================================
class MainMenuScreen(QWidget):
    """Ana menü ekranı"""
    start_new_test_signal = pyqtSignal()
    view_data_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(100, 100, 100, 100)
        
        # Logo ve Başlık
        title = QLabel("🧠 IOWA GAMBLING TASK")
        title.setFont(QFont('Arial', 42, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {Config.ACCENT_COLOR};")
        layout.addWidget(title)
        
        subtitle = QLabel("Karar Verme ve Risk Değerlendirme Testi")
        subtitle.setFont(QFont('Arial', 16))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #95a5a6;")
        layout.addWidget(subtitle)
        
        version_label = QLabel("v3.0 | Dr. H. Fehmi ÖZEL - MCBU - Sağlık Hizmetleri MYO")
        version_label.setFont(QFont('Arial', 11))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(version_label)
        
        layout.addSpacing(50)
        
        # Butonlar
        button_style = f"""
            QPushButton {{
                background-color: {Config.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
                min-height: 60px;
            }}
            QPushButton:hover {{
                background-color: #5568d3;
            }}
            QPushButton:pressed {{
                background-color: #4a5bc4;
            }}
        """
        
        # Yeni Test Başlat
        new_test_btn = QPushButton("🧪 YENİ TEST BAŞLAT")
        new_test_btn.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        new_test_btn.setStyleSheet(button_style)
        new_test_btn.clicked.connect(self.start_new_test_signal.emit)
        layout.addWidget(new_test_btn)
        
        # Veri Kayıtlarını Görüntüle
        view_data_btn = QPushButton("📊 VERİ KAYITLARINI GÖRÜNTÜLE")
        view_data_btn.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        view_data_btn.setStyleSheet(button_style.replace(Config.PRIMARY_COLOR, '#27ae60'))
        view_data_btn.clicked.connect(self.view_data_signal.emit)
        layout.addWidget(view_data_btn)
        
        # Hakkında
        about_btn = QPushButton("ℹ️ HAKKINDA & YARDIM")
        about_btn.setFont(QFont('Arial', 16))
        about_btn.setStyleSheet(button_style.replace(Config.PRIMARY_COLOR, '#34495e'))
        about_btn.clicked.connect(self.show_about)
        layout.addWidget(about_btn)
        
        layout.addSpacing(30)
        
        # Çıkış
        exit_btn = QPushButton("🚪 ÇIKIŞ")
        exit_btn.setFont(QFont('Arial', 14))
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #95a5a6;
                border: 2px solid #95a5a6;
                border-radius: 8px;
                padding: 10px;
                min-height: 40px;
            }
            QPushButton:hover {
                color: #e74c3c;
                border-color: #e74c3c;
            }
        """)
        exit_btn.clicked.connect(QApplication.quit)
        layout.addWidget(exit_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def show_about(self):
        """Hakkında diyalogu"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Hakkında - Iowa Gambling Task")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            "<h2>Iowa Gambling Task (IGT)</h2>"
            "<p><b>Versiyon:</b> 3.0</p>"
            "<p><b>Geliştirici:</b> Dr. H. Fehmi ÖZEL</p>"
            "<p><b>Kurum:</b> Manisa Celal Bayar Üniversitesi<br>"
            "Sağlık Hizmetleri Meslek Yüksekokulu</p><br>"
            "<p><b>Açıklama:</b></p>"
            "<p>Iowa Gambling Task (IGT), karar verme süreçlerini ve "
            "risk değerlendirme yeteneğini ölçen nöropsikolojik bir testtir (Bechara et al. (1994)). "
            "Test, katılımcıların avantajlı ve dezavantajlı desteler arasında "
            "seçim yapma yeteneklerini değerlendirir.</p><br>"
            "<p><b>Test Özellikleri:</b></p>"
            "<ul>"
            "<li>100 deneme (5 blok × 20 deneme)</li>"
            "<li>4 deste (A, B, C, D)</li>"
            "<li>Shimmer EDA/PPG entegrasyonu</li>"
            "<li>Otomatik veri kayıt ve analiz</li>"
            "<li>200 katılımcı kapasiteli veritabanı</li>"
            "</ul>"
        )
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d3436;
            }
            QLabel {
                color: white;
            }
        """)
        msg.exec()

# =============================================================================
# PyQt6 GUI - DATA VIEWER SCREEN
# =============================================================================
class DataViewerScreen(QWidget):
    """Veritabanı kayıtlarını görüntüleme ekranı"""
    back_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 VERİ KAYITLARI")
        title.setFont(QFont('Arial', 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Config.ACCENT_COLOR};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Yenile butonu
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setFont(QFont('Arial', 12))
        refresh_btn.setFixedSize(120, 40)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #5568d3;
            }}
        """)
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        # Geri butonu
        back_btn = QPushButton("← Ana Menü")
        back_btn.setFont(QFont('Arial', 12))
        back_btn.setFixedSize(120, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        back_btn.clicked.connect(self.back_signal.emit)
        header_layout.addWidget(back_btn)
        
        layout.addLayout(header_layout)
        
        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Katılımcı ID", "Yaş", "Cinsiyet", "Tarih", 
            "Final Bakiye", "Net IGT Skoru"
        ])
        
        # Tablo stil ve davranış
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        
        # Kolon genişlikleri
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2d3436;
                alternate-background-color: #34495e;
                gridline-color: #4a5568;
                border: 2px solid #667eea;
                border-radius: 10px;
            }
            QTableWidget::item {
                padding: 10px;
                color: white;
            }
            QTableWidget::item:selected {
                background-color: #667eea;
            }
            QHeaderView::section {
                background-color: #1e272e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Aksiyon butonları
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        action_btn_style = """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """
        
        self.open_csv_btn = QPushButton("📄 CSV Aç")
        self.open_csv_btn.setStyleSheet(action_btn_style)
        self.open_csv_btn.setEnabled(False)
        self.open_csv_btn.clicked.connect(self.open_csv)
        action_layout.addWidget(self.open_csv_btn)
        
        self.open_png_btn = QPushButton("📊 Grafik Aç")
        self.open_png_btn.setStyleSheet(action_btn_style.replace('#27ae60', '#3498db').replace('#229954', '#2980b9'))
        self.open_png_btn.setEnabled(False)
        self.open_png_btn.clicked.connect(self.open_png)
        action_layout.addWidget(self.open_png_btn)
        
        self.open_txt_btn = QPushButton("📝 Özet Aç")
        self.open_txt_btn.setStyleSheet(action_btn_style.replace('#27ae60', '#e67e22').replace('#229954', '#d35400'))
        self.open_txt_btn.setEnabled(False)
        self.open_txt_btn.clicked.connect(self.open_txt)
        action_layout.addWidget(self.open_txt_btn)
        
        self.open_folder_btn = QPushButton("📁 Klasörü Aç")
        self.open_folder_btn.setStyleSheet(action_btn_style.replace('#27ae60', '#9b59b6').replace('#229954', '#8e44ad'))
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self.open_folder)
        action_layout.addWidget(self.open_folder_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setFont(QFont('Arial', 11))
        self.info_label.setStyleSheet("color: #95a5a6;")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
        
        # Seçim değiştiğinde
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Veriyi yükle
        self.load_data()
    
    def load_data(self):
        """Veritabanından kayıtları yükle"""
        try:
            db_path = os.path.join(get_output_dir(), 'igt_sessions.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, subject_id, age, gender, 
                       start_time, final_balance
                FROM sessions
                ORDER BY start_time DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            self.table.setRowCount(len(rows))
            self.session_data = []  # Subject ID'leri saklamak için
            
            for i, row in enumerate(rows):
                session_id, subject_id, age, gender, start_time, final_balance = row
                
                # Subject ID'yi sakla
                self.session_data.append(subject_id)
                
                # Net IGT skorunu hesapla
                net_score = self.calculate_net_score(session_id)
                
                # Tarihi formatla
                try:
                    dt = datetime.fromisoformat(start_time)
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_date = start_time
                
                # Session ID'nin sadece sıra numarasını göster
                display_id = str(i + 1)
                self.table.setItem(i, 0, QTableWidgetItem(display_id))
                self.table.setItem(i, 1, QTableWidgetItem(subject_id))
                self.table.setItem(i, 2, QTableWidgetItem(str(age)))
                self.table.setItem(i, 3, QTableWidgetItem(gender))
                self.table.setItem(i, 4, QTableWidgetItem(formatted_date))
                self.table.setItem(i, 5, QTableWidgetItem(f"{final_balance:,} TL"))
                
                net_score_item = QTableWidgetItem(f"{net_score:+d}")
                font = QFont()
                font.setBold(True)
                net_score_item.setFont(font)
                if net_score > 0:
                    net_score_item.setForeground(QColor('#2ecc71'))
                elif net_score < 0:
                    net_score_item.setForeground(QColor('#e74c3c'))
                self.table.setItem(i, 6, net_score_item)
            
            self.info_label.setText(f"Toplam {len(rows)} kayıt bulundu. (Maksimum kapasite: {Config.MAX_SESSIONS_STORED})")
            
        except Exception as e:
            logging.error(f"Veri yükleme hatası: {e}")
            self.info_label.setText(f"❌ Veri yükleme hatası: {e}")
    
    def calculate_net_score(self, session_id: int) -> int:
        """Session için net IGT skorunu hesapla"""
        try:
            db_path = os.path.join(get_output_dir(), 'igt_sessions.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT deck_selected FROM trials
                WHERE session_id = ?
            """, (session_id,))
            
            selections = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            advantageous = sum(1 for d in selections if d in ['C', 'D'])
            disadvantageous = sum(1 for d in selections if d in ['A', 'B'])
            
            return advantageous - disadvantageous
            
        except Exception as e:
            logging.error(f"Net score hesaplama hatası: {e}")
            return 0
    
    def on_selection_changed(self):
        """Seçim değiştiğinde butonları aktifleştir"""
        has_selection = len(self.table.selectedItems()) > 0
        self.open_csv_btn.setEnabled(has_selection)
        self.open_png_btn.setEnabled(has_selection)
        self.open_txt_btn.setEnabled(has_selection)
        self.open_folder_btn.setEnabled(has_selection)
    
    def get_selected_subject_id(self) -> Optional[str]:
        """Seçili satırdaki subject_id'yi al"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows and hasattr(self, 'session_data'):
            row = selected_rows[0].row()
            if row < len(self.session_data):
                return self.session_data[row]
        return None
    
    def open_csv(self):
        """CSV dosyasını aç"""
        subject_id = self.get_selected_subject_id()
        if subject_id:
            csv_path = self.find_latest_file(subject_id, '.csv')
            if csv_path:
                self.open_file(csv_path)
    
    def open_png(self):
        """PNG grafiğini aç"""
        subject_id = self.get_selected_subject_id()
        if subject_id:
            png_path = self.find_latest_file(subject_id, '_Analysis.png')
            if png_path:
                self.open_file(png_path)
    
    def open_txt(self):
        """TXT özetini aç"""
        subject_id = self.get_selected_subject_id()
        if subject_id:
            txt_path = self.find_latest_file(subject_id, '_Summary.txt')
            if txt_path:
                self.open_file(txt_path)
    
    def open_folder(self):
        """Sonuçlar klasörünü aç"""
        output_dir = get_output_dir()
        if sys.platform == 'darwin':  # macOS
            os.system(f'open "{output_dir}"')
        elif sys.platform == 'win32':  # Windows
            os.startfile(output_dir)
        else:  # Linux
            os.system(f'xdg-open "{output_dir}"')
    
    def find_latest_file(self, subject_id: str, suffix: str) -> Optional[str]:
        """Subject ID için en son dosyayı bul"""
        output_dir = get_output_dir()
        files = [f for f in os.listdir(output_dir) if f.startswith(f"IGT_{subject_id}") and f.endswith(suffix)]
        if files:
            files.sort(reverse=True)
            return os.path.join(output_dir, files[0])
        return None
    
    def open_file(self, filepath: str):
        """Dosyayı sistem varsayılan uygulamasıyla aç"""
        try:
            if sys.platform == 'darwin':  # macOS
                os.system(f'open "{filepath}"')
            elif sys.platform == 'win32':  # Windows
                os.startfile(filepath)
            else:  # Linux
                os.system(f'xdg-open "{filepath}"')
            logging.info(f"Dosya açıldı: {filepath}")
        except Exception as e:
            logging.error(f"Dosya açma hatası: {e}")
            QMessageBox.warning(self, "Hata", f"Dosya açılamadı:\n{e}")

# =============================================================================
# PyQt6 GUI - WELCOME SCREEN
# =============================================================================
class WelcomeScreen(QWidget):
    """Karşılama ve katılımcı bilgi girişi ekranı"""
    start_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.subject_id = generate_subject_id()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("🧠 IOWA GAMBLING TASK")
        title.setFont(QFont('Arial', 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {Config.ACCENT_COLOR};")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Karar Verme ve Risk Değerlendirme Testi")
        subtitle.setFont(QFont('Arial', 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #95a5a6;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Auto-generated ID
        id_label = QLabel(f"🆔 Katılımcı ID: {self.subject_id}")
        id_label.setFont(QFont('Arial', 16))
        id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        id_label.setStyleSheet(f"color: {Config.PRIMARY_COLOR}; padding: 10px;")
        layout.addWidget(id_label)
        
        layout.addSpacing(20)
        
        # Form
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Age
        age_layout = QHBoxLayout()
        age_label = QLabel("🎂 Yaş:")
        age_label.setFont(QFont('Arial', 14))
        age_label.setFixedWidth(100)
        self.age_input = QSpinBox()
        self.age_input.setMinimum(1)
        self.age_input.setMaximum(150)
        self.age_input.setValue(25)
        self.age_input.setFont(QFont('Arial', 14))
        self.age_input.setFixedHeight(40)
        age_layout.addWidget(age_label)
        age_layout.addWidget(self.age_input)
        form_layout.addLayout(age_layout)
        
        # Gender
        gender_layout = QHBoxLayout()
        gender_label = QLabel("⚧ Cinsiyet:")
        gender_label.setFont(QFont('Arial', 14))
        gender_label.setFixedWidth(100)
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Erkek", "Kadın"])
        self.gender_input.setFont(QFont('Arial', 14))
        self.gender_input.setFixedHeight(40)
        gender_layout.addWidget(gender_label)
        gender_layout.addWidget(self.gender_input)
        form_layout.addLayout(gender_layout)
        
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)
        
        layout.addSpacing(30)
        
        # Start button
        self.start_btn = QPushButton("▶ TESTE BAŞLA")
        self.start_btn.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        self.start_btn.setFixedHeight(60)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.SUCCESS_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
            }}
        """)
        self.start_btn.clicked.connect(self.start_experiment)
        layout.addWidget(self.start_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def start_experiment(self):
        """Deney başlatma"""
        gender_map = {"Erkek": "E", "Kadın": "K"}
        participant_info = {
            "subject_id": self.subject_id,
            "age": self.age_input.value(),
            "gender": gender_map[self.gender_input.currentText()]
        }
        logging.info(f"✅ Katılımcı bilgileri: {participant_info}")
        self.start_signal.emit(participant_info)

# =============================================================================
# PyQt6 GUI - SYNC COUNTDOWN SCREEN
# =============================================================================
class SyncCountdownScreen(QWidget):
    """Shimmer senkronizasyon countdown ekranı"""
    sync_complete = pyqtSignal(datetime)
    
    def __init__(self):
        super().__init__()
        self.sync_time = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("⏱️ SHIMMER SENKRONIZASYONU")
        title.setFont(QFont('Arial', 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {Config.ACCENT_COLOR};")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "📋 SENKRONIZASYON ADIMLARI:\n\n"
            "1️⃣ Shimmer cihazını katılımcıya takın\n"
            "2️⃣ ConsensysPRO'da kaydı hazırlayın\n"
            "3️⃣ Aşağıdaki butona tıklayın\n"
            "4️⃣ Countdown başladığında Shimmer'da KAYDI BAŞLATIN\n\n"
            "⏰ 3-2-1 countdown sırasında her iki sistemde kayıt senkronize edilecek"
        )
        instructions.setFont(QFont('Arial', 13))
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: white; line-height: 1.8;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        layout.addSpacing(30)
        
        # Countdown display
        self.countdown_label = QLabel("")
        self.countdown_label.setFont(QFont('Arial', 120, QFont.Weight.Bold))
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet(f"color: {Config.ACCENT_COLOR};")
        self.countdown_label.setMinimumHeight(200)
        layout.addWidget(self.countdown_label)
        
        layout.addSpacing(30)
        
        # Start button
        self.start_btn = QPushButton("🔄 SENKRONIZASYON BAŞLAT")
        self.start_btn.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        self.start_btn.setFixedHeight(60)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: #5568d3;
            }}
        """)
        self.start_btn.clicked.connect(self.start_countdown)
        layout.addWidget(self.start_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def start_countdown(self):
        """Countdown başlat"""
        self.start_btn.setEnabled(False)
        self.countdown = 3
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)
        
        # İlk sayıyı göster
        self.countdown_label.setText("3")
    
    def update_countdown(self):
        """Countdown güncelle"""
        if self.countdown > 1:
            self.countdown -= 1
            self.countdown_label.setText(str(self.countdown))
        elif self.countdown == 1:
            self.countdown -= 1
            self.countdown_label.setText("BAŞLA! 🚀")
            self.countdown_label.setStyleSheet(f"color: {Config.SUCCESS_COLOR};")
            
            # Sync timestamp kaydet
            self.sync_time = datetime.now()
            logging.info("="*60)
            logging.info(f"🔄 SYNC_MARKER: {self.sync_time.isoformat()}")
            logging.info(f"   Timestamp: {self.sync_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
            logging.info("="*60)
        else:
            self.timer.stop()
            QTimer.singleShot(1500, lambda: self.sync_complete.emit(self.sync_time))

# =============================================================================
# PyQt6 GUI - INSTRUCTION SCREEN
# =============================================================================
class InstructionScreen(QWidget):
    """Talimat ekranı"""
    continue_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("📋 GÖREV TALİMATLARI")
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {Config.ACCENT_COLOR};")
        layout.addWidget(title)
        
        # Instructions
        instructions = """
Önünüzde 4 farklı kart destesi bulunmaktadır.
Kasanızda 100.000 TL nakit sermaye vardır.

🃏 Her kart seçiminiz size para kazandırır,
   ancak bazı kartlar ceza da getirebilir!

🎯 Göreviniz: 100 tur boyunca en yüksek bakiyeye ulaşmak

💡 İpucu: Başlangıçta hangi destenin avantajlı olduğunu bilemezsiniz.
   Deneyerek öğrenmeniz ve stratejinizi geliştirmeniz beklenmektedir.

⏱️ Her seçiminizde tepki süreniz kaydedilecektir.

⚠️ Önemli: Test boyunca doğal davranın ve içgüdülerinizi takip edin.
        """
        
        inst_label = QLabel(instructions)
        inst_label.setFont(QFont('Arial', 13))
        inst_label.setWordWrap(True)
        inst_label.setStyleSheet("color: white; padding: 20px; line-height: 1.6;")
        layout.addWidget(inst_label)
        
        layout.addSpacing(20)
        
        # Continue button
        continue_btn = QPushButton("▶ BAŞLA")
        continue_btn.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        continue_btn.setFixedHeight(50)
        continue_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: #5568d3;
            }}
        """)
        continue_btn.clicked.connect(self.continue_signal.emit)
        layout.addWidget(continue_btn)
        
        self.setLayout(layout)

# =============================================================================
# PyQt6 GUI - EXPERIMENT SCREEN
# =============================================================================
class ExperimentScreen(QWidget):
    """Ana deney ekranı"""
    experiment_complete = pyqtSignal(list)
    
    def __init__(self, participant_info: Dict, sync_timestamp: datetime = None):
        super().__init__()
        self.participant_info = participant_info
        self.trial_num = 0
        self.balance = Config.START_BALANCE
        self.data_records = []
        self.start_time = sync_timestamp if sync_timestamp else datetime.now()
        self.sync_timestamp = sync_timestamp
        
        # Log experiment start with sync info
        logging.info("\n" + "="*60)
        logging.info("🎮 EXPERIMENT STARTING")
        logging.info(f"   Subject: {participant_info['subject_id']}")
        logging.info(f"   Age: {participant_info['age']}")
        logging.info(f"   Gender: {participant_info['gender']}")
        logging.info(f"   Start Time: {self.start_time.isoformat()}")
        if sync_timestamp:
            logging.info(f"   ✅ Synced with Shimmer countdown")
        logging.info("="*60 + "\n")
        
        # Decks
        self.decks = [
            Deck('A', Config.REWARD_BAD_DECK, penalties_A),
            Deck('B', Config.REWARD_BAD_DECK, penalties_B),
            Deck('C', Config.REWARD_GOOD_DECK, penalties_C),
            Deck('D', Config.REWARD_GOOD_DECK, penalties_D)
        ]
        
        self.init_ui()
        self.trial_start_time = None
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Top bar
        top_layout = QHBoxLayout()
        
        self.trial_label = QLabel(f"Tur: {self.trial_num}/{Config.MAX_TRIALS}")
        self.trial_label.setFont(QFont('Arial', 14))
        self.trial_label.setStyleSheet("color: #95a5a6;")
        top_layout.addWidget(self.trial_label)
        
        top_layout.addStretch()
        
        self.balance_label = QLabel(f"💰 BAKİYE: {self.balance:,} TL")
        self.balance_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        self.balance_label.setStyleSheet(f"color: {Config.ACCENT_COLOR};")
        top_layout.addWidget(self.balance_label)
        
        main_layout.addLayout(top_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(Config.MAX_TRIALS)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(10)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #2d3436;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {Config.PRIMARY_COLOR};
                border-radius: 5px;
            }}
        """)
        main_layout.addWidget(self.progress)
        
        main_layout.addSpacing(30)
        
        # Instruction
        self.instruction_label = QLabel("Bir kart destesi seçin")
        self.instruction_label.setFont(QFont('Arial', 18))
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.instruction_label)
        
        main_layout.addSpacing(20)
        
        # Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        self.card_buttons = []
        for i, (deck_name, color) in enumerate([('A', Config.CARD_COLORS['A']),
                                                  ('B', Config.CARD_COLORS['B']),
                                                  ('C', Config.CARD_COLORS['C']),
                                                  ('D', Config.CARD_COLORS['D'])]):
            btn = QPushButton(deck_name)
            btn.setFont(QFont('Arial', 48, QFont.Weight.Bold))
            btn.setFixedSize(200, 300)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: 3px solid white;
                    border-radius: 15px;
                }}
                QPushButton:hover {{
                    border: 5px solid #ffeaa7;
                    transform: scale(1.05);
                }}
                QPushButton:pressed {{
                    background-color: {color}dd;
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self.card_selected(idx))
            self.card_buttons.append(btn)
            cards_layout.addWidget(btn)
        
        main_layout.addLayout(cards_layout)
        
        main_layout.addSpacing(30)
        
        # Feedback area
        self.feedback_widget = QFrame()
        self.feedback_widget.setFixedHeight(150)
        self.feedback_widget.setStyleSheet("""
            QFrame {
                background-color: #2d3436;
                border-radius: 10px;
                border: 2px solid #f1c40f;
            }
        """)
        self.feedback_widget.setVisible(False)
        
        feedback_layout = QVBoxLayout()
        
        self.reward_label = QLabel()
        self.reward_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        self.reward_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feedback_layout.addWidget(self.reward_label)
        
        self.penalty_label = QLabel()
        self.penalty_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        self.penalty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feedback_layout.addWidget(self.penalty_label)
        
        self.net_label = QLabel()
        self.net_label.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        self.net_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feedback_layout.addWidget(self.net_label)
        
        self.feedback_widget.setLayout(feedback_layout)
        main_layout.addWidget(self.feedback_widget)
        
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Start first trial with delay to ensure UI is ready
        QTimer.singleShot(100, self.start_trial)
    
    def start_trial(self):
        """Yeni deneme başlat"""
        self.trial_start_time = datetime.now()
        self.enable_cards(True)
        logging.info(f"▶️ Trial {self.trial_num + 1} başladı, kartlar aktif")
    
    def enable_cards(self, enabled: bool):
        """Kart butonlarını aktif/pasif yap"""
        for btn in self.card_buttons:
            btn.setEnabled(enabled)
    
    def card_selected(self, deck_idx: int):
        """Kart seçildiğinde"""
        logging.info(f"🃏 Kart {['A','B','C','D'][deck_idx]} tıklandı")
        
        if self.trial_start_time is None:
            logging.warning("⚠️ Trial başlamadan kart seçildi, başlatılıyor...")
            self.start_trial()
            return
        
        # Reaction time
        reaction_time = (datetime.now() - self.trial_start_time).total_seconds()
        logging.info(f"⏱️ Reaksiyon zamanı: {reaction_time:.3f} sn")
        
        # Draw card
        deck = self.decks[deck_idx]
        reward, penalty, net = deck.draw_card()
        self.balance += net
        self.trial_num += 1
        
        # Record data
        trial_data = {
            'Subject_ID': self.participant_info['subject_id'],
            'Subject_Age': self.participant_info['age'],
            'Subject_Gender': self.participant_info['gender'],
            'Experiment_Start': self.start_time.isoformat(timespec='seconds'),
            'Trial_Number': self.trial_num,
            'Deck_Selected': deck.name,
            'Reaction_Time': round(reaction_time, 3),
            'Reward': reward,
            'Penalty': penalty,
            'Net_Outcome': net,
            'Total_Balance': self.balance,
            'Trial_Real_Time': datetime.now().isoformat(timespec='seconds')
        }
        
        # İlk trial'a sync timestamp ekle
        if self.trial_num == 1 and self.sync_timestamp:
            trial_data['Sync_Timestamp'] = self.sync_timestamp.isoformat(timespec='milliseconds')
        
        self.data_records.append(trial_data)
        
        # Disable cards
        self.enable_cards(False)
        
        # Show feedback
        self.show_feedback(reward, penalty, net)
        
        # Update UI
        self.trial_label.setText(f"Tur: {self.trial_num}/{Config.MAX_TRIALS}")
        self.balance_label.setText(f"💰 BAKİYE: {self.balance:,} TL")
        self.progress.setValue(self.trial_num)
        
        # Check if complete
        if self.trial_num >= Config.MAX_TRIALS:
            QTimer.singleShot(2000, self.complete_experiment)
        else:
            QTimer.singleShot(2000, self.hide_feedback)
    
    def show_feedback(self, reward: int, penalty: int, net: int):
        """Geri bildirimi göster"""
        self.reward_label.setText(f"✅ KAZANÇ: +{reward:,} TL")
        self.reward_label.setStyleSheet(f"color: {Config.SUCCESS_COLOR};")
        
        if penalty < 0:
            self.penalty_label.setText(f"❌ CEZA: {penalty:,} TL")
            self.penalty_label.setStyleSheet(f"color: {Config.ERROR_COLOR};")
        else:
            self.penalty_label.setText("✨ CEZA YOK")
            self.penalty_label.setStyleSheet("color: #95a5a6;")
        
        net_color = Config.SUCCESS_COLOR if net >= 0 else Config.ERROR_COLOR
        net_symbol = "📈" if net >= 0 else "📉"
        self.net_label.setText(f"{net_symbol} NET: {net:+,} TL")
        self.net_label.setStyleSheet(f"color: {net_color};")
        
        self.feedback_widget.setVisible(True)
    
    def hide_feedback(self):
        """Geri bildirimi gizle"""
        self.feedback_widget.setVisible(False)
        self.start_trial()
    
    def complete_experiment(self):
        """Deneyi tamamla"""
        logging.info("✅ Deney tamamlandı!")
        self.experiment_complete.emit(self.data_records)

# =============================================================================
# PyQt6 GUI - COMPLETION SCREEN
# =============================================================================
class CompletionScreen(QWidget):
    """Tamamlanma ekranı"""
    close_signal = pyqtSignal()
    
    def __init__(self, final_balance: int, net_change: int, png_path: str):
        super().__init__()
        self.final_balance = final_balance
        self.net_change = net_change
        self.png_path = png_path
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("🎉 TEST TAMAMLANDI!")
        title.setFont(QFont('Arial', 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {Config.SUCCESS_COLOR};")
        layout.addWidget(title)
        
        layout.addSpacing(30)
        
        # Results
        results = f"""
        💰 Son Bakiye: {self.final_balance:,} TL
        
        📊 Net Değişim: {self.net_change:+,} TL
        
        ✅ {Config.MAX_TRIALS} deneme tamamlandı
        
        📁 Sonuçlarınız kaydedildi:
           • CSV (Ham veri)
           • PNG (Grafikler)
           • TXT (Özet rapor)
           • Veritabanı
        """
        
        results_label = QLabel(results)
        results_label.setFont(QFont('Arial', 16))
        results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_label.setStyleSheet("color: white;")
        layout.addWidget(results_label)
        
        layout.addSpacing(30)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        # Ana Menü button
        menu_btn = QPushButton("🏠 ANA MENÜ")
        menu_btn.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        menu_btn.setFixedHeight(50)
        menu_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: #5568d3;
            }}
        """)
        menu_btn.clicked.connect(self.close_signal.emit)
        btn_layout.addWidget(menu_btn)
        
        # Sonuçları Görüntüle button
        view_btn = QPushButton("📊 SONUÇLARI GÖRÜNTÜLE")
        view_btn.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        view_btn.setFixedHeight(50)
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        view_btn.clicked.connect(self.view_results)
        btn_layout.addWidget(view_btn)
        
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def view_results(self):
        """Sonuç dosyalarını aç"""
        import subprocess
        output_dir = get_output_dir()
        
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.call(['open', output_dir])
            elif sys.platform == 'win32':  # Windows
                os.startfile(output_dir)
            else:  # Linux
                subprocess.call(['xdg-open', output_dir])
        except Exception as e:
            logging.error(f"Sonuçlar açılamadı: {e}")

# =============================================================================
# MAIN WINDOW
# =============================================================================
class IGTMainWindow(QMainWindow):
    """Ana pencere"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iowa Gambling Task - MCBÜ")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup
        setup_logging()
        init_database()
        
        # Stacked widget for screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Screens
        # Ana Menü
        self.main_menu_screen = MainMenuScreen()
        self.main_menu_screen.start_new_test_signal.connect(self.show_welcome)
        self.main_menu_screen.view_data_signal.connect(self.show_data_viewer)
        self.stacked_widget.addWidget(self.main_menu_screen)
        
        # Veri Görüntüleyici
        self.data_viewer_screen = DataViewerScreen()
        self.data_viewer_screen.back_signal.connect(self.show_main_menu)
        self.stacked_widget.addWidget(self.data_viewer_screen)
        
        # Welcome Screen
        self.welcome_screen = WelcomeScreen()
        self.welcome_screen.start_signal.connect(self.show_instructions)
        self.stacked_widget.addWidget(self.welcome_screen)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        logging.info("🚀 IGT Uygulaması başlatıldı")
    
    def apply_dark_theme(self):
        """Koyu tema uygula"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Config.BG_COLOR};
            }}
            QWidget {{
                background-color: {Config.BG_COLOR};
                color: {Config.TEXT_COLOR};
            }}
            QLabel {{
                color: {Config.TEXT_COLOR};
            }}
            QSpinBox, QComboBox {{
                background-color: #2d3436;
                color: white;
                border: 2px solid {Config.PRIMARY_COLOR};
                border-radius: 5px;
                padding: 5px;
            }}
        """)
    
    def show_main_menu(self):
        """Ana menüyü göster"""
        self.stacked_widget.setCurrentWidget(self.main_menu_screen)
    
    def show_welcome(self):
        """Katılımcı bilgi ekranını göster"""
        # Yeni bir welcome screen oluştur (temiz ID için)
        self.welcome_screen = WelcomeScreen()
        self.welcome_screen.start_signal.connect(self.show_instructions)
        
        # Eski welcome screen'i kaldır ve yenisini ekle
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            if isinstance(widget, WelcomeScreen) and widget != self.welcome_screen:
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()
                break
        
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
    
    def show_data_viewer(self):
        """Veri görüntüleme ekranını göster"""
        self.data_viewer_screen.load_data()  # Veriyi yeniden yükle
        self.stacked_widget.setCurrentWidget(self.data_viewer_screen)
    
    def show_instructions(self, participant_info: Dict):
        """Talimat ekranını göster"""
        self.participant_info = participant_info
        
        instruction_screen = InstructionScreen()
        instruction_screen.continue_signal.connect(self.show_sync_screen)
        self.stacked_widget.addWidget(instruction_screen)
        self.stacked_widget.setCurrentWidget(instruction_screen)
    
    def show_sync_screen(self):
        """Shimmer senkronizasyon ekranını göster"""
        sync_screen = SyncCountdownScreen()
        sync_screen.sync_complete.connect(self.start_experiment_with_sync)
        self.stacked_widget.addWidget(sync_screen)
        self.stacked_widget.setCurrentWidget(sync_screen)
    
    def start_experiment_with_sync(self, sync_time: datetime):
        """Deneyi sync timestamp ile başlat"""
        self.sync_timestamp = sync_time
        self.start_experiment()
    
    def start_experiment(self):
        """Deneyi başlat"""
        sync_ts = getattr(self, 'sync_timestamp', None)
        self.experiment_screen = ExperimentScreen(self.participant_info, sync_ts)
        self.experiment_screen.experiment_complete.connect(self.complete_experiment)
        self.stacked_widget.addWidget(self.experiment_screen)
        self.stacked_widget.setCurrentWidget(self.experiment_screen)
    
    def complete_experiment(self, data_records: List[Dict]):
        """Deneyi tamamla ve sonuçları kaydet"""
        # Save CSV
        df = pd.DataFrame(data_records)
        output_dir = get_output_dir()
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"IGT_{self.participant_info['subject_id']}_{timestamp}"
        csv_path = os.path.join(output_dir, f"{filename}.csv")
        df.to_csv(csv_path, index=False)
        
        # Run analysis
        png_path, txt_path = run_analysis(
            csv_path,
            self.participant_info['subject_id'],
            self.participant_info['age'],
            self.participant_info['gender']
        )
        
        # Save to database
        final_balance = data_records[-1]['Total_Balance']
        session_meta = {
            "session_id": filename,
            "subject_id": self.participant_info['subject_id'],
            "age": self.participant_info['age'],
            "gender": self.participant_info['gender'],
            "start_time": data_records[0]['Experiment_Start'],
            "end_time": datetime.now().isoformat(timespec='seconds'),
            "trials_completed": len(data_records),
            "final_balance": final_balance,
            "net_change": final_balance - Config.START_BALANCE
        }
        save_session_to_db(session_meta, data_records, csv_path, png_path, txt_path)
        
        # Show completion screen
        completion_screen = CompletionScreen(
            final_balance,
            final_balance - Config.START_BALANCE,
            png_path
        )
        completion_screen.close_signal.connect(self.show_main_menu)
        self.stacked_widget.addWidget(completion_screen)
        self.stacked_widget.setCurrentWidget(completion_screen)

# =============================================================================
# MAIN
# =============================================================================
def main():
    """Ana uygulama"""
    app = QApplication(sys.argv)
    app.setApplicationName("Iowa Gambling Task")
    app.setOrganizationName("MCBÜ")
    
    window = IGTMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

