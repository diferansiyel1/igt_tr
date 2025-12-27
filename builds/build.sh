#!/bin/bash
# Iowa Gambling Task v3.0 - Build Script (macOS/Linux)

echo "=================================================="
echo "🚀 IGT v3.0 Paketleme Başlıyor"
echo "=================================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# PyQt6 kontrolü
echo -e "\n${YELLOW}📦 Gerekli paketler kontrol ediliyor...${NC}"
pip3 install -r requirements.txt

# PyInstaller kontrolü
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${RED}❌ PyInstaller bulunamadı!${NC}"
    echo -e "${YELLOW}Yükleniyor...${NC}"
    pip3 install pyinstaller
fi

# Eski build dosyalarını temizle
echo -e "\n${YELLOW}🧹 Eski build dosyaları temizleniyor...${NC}"
rm -rf build/ dist/ __pycache__/
echo -e "${GREEN}✅ Temizlik tamamlandı${NC}"

# PyInstaller ile paketleme
echo -e "\n${YELLOW}📦 Uygulama paketleniyor...${NC}"
pyinstaller IGT.spec

# Kontrol
if [ -d "dist/IGT.app" ]; then
    echo -e "\n${GREEN}✅ macOS .app başarıyla oluşturuldu!${NC}"
    echo -e "${GREEN}📁 Konum: dist/IGT.app${NC}"
    
    SIZE=$(du -sh dist/IGT.app | cut -f1)
    echo -e "${GREEN}📏 Boyut: ${SIZE}${NC}"
    
    chmod +x dist/IGT.app/Contents/MacOS/IGT
    
    echo -e "\n${YELLOW}🎯 Kullanım:${NC}"
    echo "   • Çift tıklama: dist/IGT.app"
    echo "   • Terminal: open dist/IGT.app"
    
elif [ -f "dist/IGT" ]; then
    echo -e "\n${GREEN}✅ Linux binary başarıyla oluşturuldu!${NC}"
    echo -e "${GREEN}📁 Konum: dist/IGT${NC}"
    
    chmod +x dist/IGT
    
    echo -e "\n${YELLOW}🎯 Kullanım:${NC}"
    echo "   Terminal: ./dist/IGT"
else
    echo -e "\n${RED}❌ Paketleme başarısız!${NC}"
    exit 1
fi

echo -e "\n=================================================="
echo -e "${GREEN}🎉 Paketleme Tamamlandı!${NC}"
echo "=================================================="

