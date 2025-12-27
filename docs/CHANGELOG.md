# 📋 Iowa Gambling Task - Changelog

## 🚀 v3.0 - PyQt6 GUI & Main Menu System (December 20, 2025)

### ✨ New Features

#### 1. **Main Menu System** 🏠
- ✅ Modern main menu screen
- ✅ 🧪 Start New Test button
- ✅ 📊 View Data Records button
- ✅ ℹ️ About & Help button
- ✅ 🚪 Exit button
- ✅ Return to main menu after test completion
- ✅ User-friendly navigation

#### 2. **Data Viewer** 📊
- ✅ Table listing all database records
- ✅ Columns: ID, Participant ID, Age, Gender, Date, Final Balance, Net IGT Score
- ✅ Row selection and file opening operations
- ✅ 📄 Open CSV button
- ✅ 📊 Open Graph (PNG) button
- ✅ 📝 Open Summary (TXT) button
- ✅ 📁 Open Folder button
- ✅ 🔄 Refresh button
- ✅ Color-coded Net IGT score display (positive=green, negative=red)
- ✅ Alternating row colors (readability)
- ✅ Total record count display

#### 3. **Full PyQt6 Integration** 🖼️
- ✅ Tkinter completely removed
- ✅ Consistent GUI with PyQt6
- ✅ Modern, responsive design
- ✅ Professional table appearance with QTableWidget
- ✅ Integration with system file openers (macOS/Windows/Linux)

#### 4. **Enhanced Summary Report** 📝
- ✅ **Net IGT Score** calculation and display
- ✅ Formula: (C+D selections) - (A+B selections)
- ✅ Advantageous/Disadvantageous deck selection counts
- ✅ Detailed per-deck statistics (with percentages)
- ✅ Final balance and net change
- ✅ Block-wise net scores
- ✅ Comprehensive report in TXT format

#### 5. **Shimmer Synchronization** ⏱️
- ✅ 3-2-1 countdown screen
- ✅ Sync timestamp logging
- ✅ Shimmer EDA/PPG device integration ready
- ✅ Post-processing script (`merge_shimmer_igt.py`)
- ✅ Detailed integration guide (`SHIMMER_INTEGRATION_GUIDE.md`)

### 🔧 Improvements

#### UI/UX
- ✅ Central control via main menu
- ✅ Clearer and more organized test flow
- ✅ "Main Menu" and "View Results" buttons on results screen
- ✅ Easy file access in data viewer
- ✅ Modern, professional appearance

#### Code Quality
- ✅ Added MainMenuScreen class
- ✅ Added DataViewerScreen class
- ✅ Added IGTMainWindow navigation methods
- ✅ Fixed FutureWarning warnings (pandas groupby)
- ✅ Cleaner and more modular code structure

#### Analysis
- ✅ Net IGT score calculation function
- ✅ Deck selection statistics
- ✅ Percentage calculations
- ✅ Color-coded score display

### 📊 Technical Details

#### New Classes
```python
class MainMenuScreen(QWidget):
    """Main menu screen"""
    start_new_test_signal = pyqtSignal()
    view_data_signal = pyqtSignal()

class DataViewerScreen(QWidget):
    """Database records viewing screen"""
    back_signal = pyqtSignal()
```

#### New Methods
```python
def show_main_menu(self)
def show_welcome(self)
def show_data_viewer(self)
def calculate_net_score(self, session_id: int) -> int
```

### 🧪 Tested

| Feature | Status | Detail |
|---------|--------|--------|
| Main Menu | ✅ | All buttons working |
| New Test | ✅ | Test flow correct |
| Data Viewer | ✅ | Table loads properly |
| File Opening | ✅ | CSV/PNG/TXT opens |
| Net IGT Score | ✅ | Calculated in TXT |
| Shimmer Sync | ✅ | Countdown working |
| Return to Menu | ✅ | Post-test return |

**Total Success: 7/7 (100%)** ✅

### 🎯 User Experience

#### New Experiment Flow
1. 🏠 **Main Menu** is displayed
2. 🧪 "Start New Test" is clicked
3. 🆔 Participant information is entered
4. 📋 Instructions are read
5. ⏱️ Shimmer synchronization (3-2-1)
6. 🃏 100 card selections are made
7. 📊 Results are displayed
8. 🏠 Return to main menu

#### Data Review Flow
1. 🏠 Click "View Data Records" in main menu
2. 📊 All records displayed in table
3. 🖱️ Select desired record
4. 📄 Open CSV/PNG/TXT files
5. 📁 Open results folder
6. 🏠 Return to main menu

### 🔄 Changes from Previous Version

#### Removed
- ❌ PsychoPy dependency
- ❌ Tkinter dialog system
- ❌ Direct test launch

#### Added
- ✅ PyQt6 full GUI
- ✅ Main menu system
- ✅ Data viewer
- ✅ Net IGT score
- ✅ Shimmer synchronization

### 📚 Documentation

- ✅ README.md updated (v3.0)
- ✅ CHANGELOG.md updated
- ✅ SHIMMER_INTEGRATION_GUIDE.md added
- ✅ merge_shimmer_igt.py script added

### 🐛 Bug Fixes

- ✅ Card click issue fixed (QTimer.singleShot)
- ✅ FutureWarning warnings resolved
- ✅ ID generator millisecond precision added
- ✅ Application doesn't close after test (returns to main menu)

---

## 🎯 v2.1 - Classic IGT Standard (December 20, 2025)

### ✨ New Features

#### 1. **100 Trial Standard** ⭐
- ✅ MAX_TRIALS: 200 → **100** (Classic IGT protocol)
- ✅ 5 blocks x 20 trials = 100 total card selections
- ✅ Compliant with Bechara et al. (1994) original standard

#### 2. **Automatic ID Generation System** 🆔
- ✅ Format: `DYYYYMMDD_HHMMSSmmm` (millisecond precision)
- ✅ Example: `D20251220_173447437`
- ✅ Zero collision risk
- ✅ Sequential ordering (date-based sorting)
- ✅ Manual ID entry removed

#### 3. **GUI Information Input** 🖼️
- ✅ Tkinter-based dialog system
- ✅ Auto-generated ID display
- ✅ Age and gender input (with validation)
- ✅ User-friendly interface
- ✅ Cancel protection

#### 4. **PyInstaller Packaging** 📦
- ✅ `IGT.spec` file added
- ✅ `build_app.sh` (macOS/Linux)
- ✅ `build_app.bat` (Windows)
- ✅ Single-click executable .app/.exe
- ✅ Dependencies included

#### 5. **200 Subject Capacity** 🗄️
- ✅ Database MAX_SESSIONS_STORED: 200
- ✅ Automatic old record cleanup
- ✅ Dashboard shows 50 sessions
- ✅ Full metadata tracking

### 🔧 Improvements

#### Code Quality
- ✅ Type hints in all functions
- ✅ Detailed docstrings
- ✅ Enhanced error handling
- ✅ Logging system (dual output)

#### Test Coverage
- ✅ 7/7 tests successful (100%)
- ✅ ID generator test added
- ✅ Config parameters updated
- ✅ Automated test suite

### 📦 Build Instructions

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

### 🎯 User Experience

#### Experiment Flow
1. 🚀 Application starts
2. 🆔 ID is auto-generated
3. 📋 Age/Gender requested (GUI)
4. 🎬 Introduction screen
5. ▶️ Start button
6. 🃏 100 card selections
7. 📊 Automatic analysis
8. 💾 Database record

#### Outputs
- 📄 CSV (timestamped, 100 rows)
- 📊 PNG (4 panels, 5 blocks)
- 📝 TXT (summary scores)
- 🗄️ SQLite (200 subject capacity)
- 🌐 HTML Dashboard

### � Scientific Compliance

This version complies with the following standards:

1. ✅ **Bechara et al. (1994)** - Original protocol
2. ✅ **100 trials** - Standard IGT
3. ✅ **4 decks** (A, B, C, D)
4. ✅ **Penalty schedules** - Original schedules
5. ✅ **Trial-by-trial recording** - Each selection recorded

---

## 📊 v2.0 - Enhanced UI/UX (December 19, 2025)

### Initial Release
- Modern UI/UX
- Database integration
- Dashboard system
- Type hints & docstrings
- Logging system

---

**Last Updated:** December 27, 2025  
**Developer:** Dr. H. Fehmi ÖZEL  
**Institution:** MCBU - Vocational School of Health Services

