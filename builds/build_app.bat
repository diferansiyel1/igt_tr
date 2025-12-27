@echo off
REM Iowa Gambling Task v3.0 - Build Script for Windows

echo ==================================================
echo 🚀 IGT v3.0 Paketleme Başlıyor (Windows)
echo ==================================================

REM Gerekli paketler
echo.
echo 📦 Gerekli paketler yükleniyor...
pip install -r requirements.txt

REM PyInstaller kontrolü
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller bulunamadı!
    echo Yükleniyor...
    pip install pyinstaller
)

REM Eski build dosyalarını temizle
echo.
echo 🧹 Eski build dosyaları temizleniyor...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
echo ✅ Temizlik tamamlandı

REM PyInstaller ile paketleme
echo.
echo 📦 Uygulama paketleniyor...
pyinstaller IGT.spec

REM Kontrol
if exist "dist\IGT.exe" (
    echo.
    echo ✅ Windows .exe başarıyla oluşturuldu!
    echo 📁 Konum: dist\IGT.exe
    
    echo.
    echo 🎯 Kullanım:
    echo    • Çift tıklama: dist\IGT.exe
) else (
    echo.
    echo ❌ Paketleme başarısız!
    echo Lütfen hata mesajlarını kontrol edin.
    pause
    exit /b 1
)

echo.
echo ==================================================
echo 🎉 Paketleme Tamamlandı!
echo ==================================================
pause

