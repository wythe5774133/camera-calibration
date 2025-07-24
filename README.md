# 相機內參標定工具
# Camera Intrinsic Calibration Tool

## 程式簡介 | Overview

本程式使用OpenCV庫實現相機內參數標定，透過棋盤格標定板的多張照片來計算相機的內部參數，包括焦距、主點座標和畸變係數。程式已完全中文化，提供更友善的操作介面。

**特別推薦使用圖形化界面 (GUI) 版本**，它提供了直觀的參數設定、即時狀態顯示和自動化配置管理，讓標定過程更簡單高效。

This program uses OpenCV to perform camera intrinsic parameter calibration through multiple chessboard pattern photos. It calculates camera internal parameters including focal length, principal point coordinates, and distortion coefficients. The program is fully localized in Chinese for better user experience.

**The Graphical User Interface (GUI) version is highly recommended** as it offers intuitive parameter settings, real-time status display, and automated configuration management, making the calibration process simpler and more efficient.

## 功能特色 | Features

### 🖥️ **雙介面支援**
- **圖形化界面 (GUI)**：友善的視覺化操作介面，適合新手使用，自動記憶設定，無需手動編輯 `config.ini`。
- **命令行界面 (CLI)**：傳統命令行操作，適合專業用戶和自動化腳本。

### 🎯 **核心功能**
- **自動角點檢測**：自動檢測棋盤格角點。
- **高精度標定**：亞像素精度提升標定精確度。
- **批次處理**：一次處理多張標定照片。
- **詳細結果輸出**：完整內參矩陣和畸變係數輸出。
- **結果保存**：標定結果以JSON格式保存，包含時間戳記。

### 🎛️ **進階設定**
- **多階畸變係數**：支援5/8/12/14項畸變係數選擇，適用不同精度需求。
- **高精度標定**：支援高階徑向畸變、薄稜鏡畸變、傾斜畸變模型。
- **參數記憶功能**：GUI版本自動記住使用者的標定板參數設定，並自動生成 `config.ini`。
- **靈活路徑選擇**：GUI支援瀏覽和選擇任意圖像資料夾，並記憶最近使用的路徑。

### 🔍 **品質控制**
- **RMS誤差顯示**：顯示重投影誤差評估標定品質。
- **即時圖片檢測**：顯示找到的標定圖像數量和狀態。
- **品質評估指標**：自動評估標定結果品質並提供建議。

### 🌐 **使用者體驗**
- **完全中文化**：程式介面、設定檔註解全面中文化。
- **直觀操作**：GUI版本提供視覺化參數設定和即時反饋。
- **跨平台相容**：支援Windows、Linux、macOS作業系統。

## 專案結構 | Project Structure

```
camera-calibration/
├── camera_calibration.py      # 命令行版本主程式
├── camera_calibration_gui.py  # GUI版本主程式 (推薦新用戶使用)
├── ui_settings.json           # GUI設定記憶檔案 (由GUI自動生成和管理)
├── README.md                  # 說明文件
├── requirements.txt           # 相依套件清單
├── config/                    # 配置文件資料夾
│   └── config.ini             # 設定檔 (CLI版本需手動編輯，GUI版本會自動生成)
├── image/                     # 預設標定照片資料夾 (GUI可選擇其他路徑)
└── result/                    # 標定結果資料夾 (自動產生)
    └── camera_calibration_YYYY_MM_DD_HH_MM_SS.json  # 標定結果檔案
```

## 系統需求 | System Requirements

### 手動安裝套件 | Manual Package Installation
執行程式前請先安裝所需套件：

```bash
pip install opencv-python numpy
```

或使用requirements.txt安裝：
```bash
pip install -r requirements.txt
```

### 必要套件 | Required Packages
- `opencv-python>=4.5.0`
- `numpy>=1.19.0`

### Python版本 | Python Version
- Python 3.6 或更高版本

## Quick Start | 快速開始

### 1. Download and Setup | 下載與設定
```bash
# Download the project | 下載專案
# Extract to desired location | 解壓縮到目標位置
```

### 2. Prepare Calibration Photos | 準備標定照片
將15-30張棋盤格標定照片放入 `image/` 資料夾中。
**提示**：GUI版本允許您瀏覽並選擇任何包含圖像的資料夾。

Place 15-30 chessboard calibration photos in the `image/` folder.
**Tip**: The GUI version allows you to browse and select any folder containing images.

### 3. Run Program | 執行程式

#### **推薦：使用圖形化界面 (GUI) 版本**
```bash
python camera_calibration_gui.py
```
- GUI會自動載入或生成 `config.ini`。
- 您可以在GUI中直觀地設定所有參數，並選擇圖像資料夾。
- 點擊「開始標定」按鈕即可執行。

#### **命令行界面 (CLI) 版本**
```bash
# 如果您選擇使用CLI版本，請先手動編輯 config/config.ini 檔案
# If you choose to use the CLI version, please manually edit the config/config.ini file first
python camera_calibration.py
```

程式會自動：
- 從設定檔載入參數 (GUI會自動生成，CLI需手動編輯)。
- 處理指定資料夾中的所有照片。
- 執行標定並將結果保存到result資料夾。
- 在終端或GUI結果區顯示完整的中文化結果。

## Configuration Details | 設定檔詳細說明

### Edit parameters in `config.ini` | 編輯 `config.ini` 中的參數：
**注意**：如果您使用GUI版本，這些參數會由GUI自動管理和生成，通常無需手動編輯此檔案。

```ini
[相機設定]
# Physical focal length (unit: millimeters) | 相機物理焦距（單位：毫米）
# GUI中對應「相機物理焦距 (mm)」輸入框
物理焦距 = 50.0

[標定板設定] 
# Chessboard inner corner count (Note: inner corners, not squares)
# 棋盤格內角點數量（注意：這是內角點，不是方格數量）
# 例如：8x6的棋盤格有7x5個內角點
# 格式：寬度,高度 (GUI中對應「標定板內角點數量」的寬和高輸入框)
內角點數量 = 9,6

# Actual size of chessboard squares (unit: millimeters)
# 棋盤格方格的實際尺寸（單位：毫米）
# GUI中對應「方格尺寸 (mm)」輸入框
方格尺寸 = 25.0

[程式設定]
# Minimum number of successfully detected images required for calibration
# 最少需要成功檢測的影像數量
最少影像數量 = 5

# Reprojection error warning threshold (pixels) | 重投影誤差警告閾值（像素）
# GUI中對應「誤差警告閾值 (像素)」輸入框
誤差警告閾值 = 1.0

# Distortion coefficient count setting (supports 5, 8, 12, 14 terms)
# 畸變係數數量設定（支援5、8、12、14項）
# 重要提醒：高階畸變係數需要更多圖片來避免過度擬合
# GUI中對應「畸變係數項數」下拉選單
畸變係數項數 = 5

[輸出設定]
# Whether to save complete intrinsic matrix and distortion coefficient arrays
# 是否在結果中保存完整的內參矩陣和畸變係數陣列
# GUI中對應「保存完整矩陣」和「保存完整畸變係數」核取方塊
保存完整矩陣 = true
保存完整畸變係數 = true
```

## 畸變係數選擇指南 | Distortion Coefficients Selection Guide

### 📊 畸變係數項數比較

| 項數 | 係數類型 | 適用場景 | 建議圖片數 | 預期RMS | 備註 |
|------|---------|---------|------------|---------|------|
| **5項** | k1,k2,k3,p1,p2 | 一般應用、廣角鏡頭 | 15-25張 | 0.3-1.0像素 | 標準模型，穩定性好 |
| **8項** | +k4,k5,k6 | 高精度應用、魚眼鏡頭 | 25-35張 | 通常更小 | 適合大多數高精度需求 |
| **12項** | +s1,s2,s3,s4 | 極高精度、雷射測距 | 30-40張 | 最佳精度 | 需覆蓋感測器邊緣 |
| **14項** | +τx,τy | 最高精度、特殊光學 | 40-60張 | 可能過擬合 | 易數值不穩定 ⚠️ |

### 🎯 選擇建議

#### **一般使用者**
- **推薦：5項**（預設值）
- 適合大部分攝影和一般應用
- 穩定性好，不易過度擬合

#### **高精度應用使用者**（如雷射測距、工業檢測）
- **推薦：8項或12項**
- 8項：穩定且精度提升明顯
- 12項：最高實用精度，但需要更多圖片

#### **研究或極端精度需求**
- **可嘗試：14項**
- ⚠️ **警告**：如果RMS反而變大，請改回12項
- 需要非常多樣化的拍攝角度

### 🚨 重要注意事項

1. **過度擬合風險**：項數越多，越容易擬合噪聲而非真實畸變。
2. **圖片數量要求**：高階係數需要更多標定圖片。
3. **拍攝品質**：高階模型對圖片品質要求更嚴格。
4. **數值穩定性**：14項係數可能出現數值不穩定問題。

## 拍攝指南 | Photography Guidelines

### Preparation | 準備工作

**Calibration Board | 標定板：**
- **Recommended size | 推薦尺寸**：8x6 or 9x7 chessboard | 8x6 或 9x7 棋盤格
- **Print quality | 印刷要求**：High-quality printing with clear square edges | 高品質列印，確保方格邊緣清晰。
- **Material | 材質建議**：Rigid cardboard or acrylic to avoid bending | 硬紙板或亞克力板，避免彎曲變形。
- **Size measurement | 尺寸測量**：Acc確測量每個方格的實際尺寸（單位：毫米）。

### 拍攝建議 | Photography Tips

#### **基本要求（適用所有畸變係數項數）**
- **光線條件**：確保光線充足且均勻。
- **避免模糊**：確保所有照片都清晰對焦。
- **標定板品質**：使用高品質印刷的棋盤格。

#### **根據畸變係數項數調整拍攝策略**

##### **5項係數（15-25張照片）**
- **角度變化**：從不同角度拍攝標定板。
- **位置變化**：將標定板放在影像的不同位置。
- **距離變化**：拍攝不同距離的標定板。

##### **8項係數（25-35張照片）**
- **增加角度多樣性**：包含更多傾斜角度。
- **邊緣區域覆蓋**：確保標定板出現在影像邊緣區域。
- **距離範圍擴大**：從近距離到遠距離的更大範圍。

##### **12項係數（30-40張照片）**
- **完整感測器覆蓋**：標定板必須覆蓋感測器的所有區域。
- **極端角度包含**：包含更多極端傾斜角度。
- **邊角重點拍攝**：特別注重影像四個角落的標定板位置。

##### **14項係數（40-60張照片）**
- **最大角度多樣性**：包含各種可能的傾斜和旋轉角度。
- **系統性位置覆蓋**：標定板系統性地覆蓋整個影像平面。
- **多距離多角度組合**：每個距離都要有多個角度的拍攝。

### Important Notes | 注意事項：
- Calibration board must appear completely in image | 標定板必須完全出現在影像中。
- Avoid reflection or shadows on calibration board | 避免標定板反光或陰影。
- Each photo should have calibration board in different pose | 每張照片中的標定板應有不同的姿態。

## 程式執行流程 | Program Execution Flow

### **圖形化界面 (GUI) 版本**
1. **啟動GUI**：執行 `python camera_calibration_gui.py`。
2. **設定參數**：在GUI介面中設定相機、標定板和程式參數。
3. **選擇圖像資料夾**：瀏覽並選擇包含標定照片的資料夾。
4. **自動生成配置**：GUI會根據您的設定自動生成 `config/config.ini`。
5. **執行標定**：點擊「開始標定」按鈕。
6. **即時顯示**：GUI會顯示處理進度、狀態和最終標定結果。
7. **保存結果**：結果自動保存到 `result/` 資料夾。

### **命令行界面 (CLI) 版本**
1. **手動編輯設定**：編輯 `config/config.ini` 檔案，設定所有必要的參數。
2. **啟動CLI**：執行 `python camera_calibration.py`。
3. **自動檢測**：程式自動使用 `image/` 資料夾中的照片。
4. **批次處理**：自動處理資料夾中的所有影像檔案。
5. **顯示進度**：顯示每張照片的處理結果。
6. **執行標定**：自動計算相機內參數。
7. **中文顯示結果**：在終端顯示詳細的標定結果（含RMS誤差）。
8. **保存檔案**：將結果保存到 `result/` 資料夾，檔名包含時間戳記。

### 終端輸出示例 | Terminal Output Example

當您執行程式時，會看到以下中文化的輸出資訊：

```
相機內參標定結果
============================================================

使用圖片數量: 20 張
RMS重投影誤差: 0.3456 像素

相機內參矩陣:
  fx (x方向像素焦距): 308.49
  fy (y方向像素焦距): 307.78
  cx (x方向主點): 198.79
  cy (y方向主點): 151.21

完整內參矩陣:
[[308.49510602   0.         198.78912949]
 [  0.         307.78045942 151.21343271]
 [  0.           0.           1.        ]]

畸變係數:
  k1 (徑向畸變1): 0.417282
  k2 (徑向畸變2): -1.871320
  p1 (切向畸變1): 0.001159
  p2 (切向畸變2): 0.000037
  k3 (徑向畸變3): 2.628209

完整畸變係數陣列:
[[ 0.41728231 -1.8713201   0.00115879  0.00003745  2.62820907]]
```

## Output Results | 輸出結果說明

### Main Parameters | 主要參數

#### Camera Intrinsic Matrix | 相機內參矩陣
- **fx, fy**：Pixel focal lengths in x and y directions | x和y方向的像素焦距。
- **cx, cy**：Principal point coordinates (image center offset) | 主點座標（影像中心點偏移）。

#### Distortion Coefficients | 畸變係數
- **k1, k2, k3**：Radial distortion coefficients | 徑向畸變係數。
- **p1, p2**：Tangential distortion coefficients | 切向畸變係數。

### Output Files | 輸出檔案

Program generates timestamped files in result folder:
程式會在result資料夾生成時間戳記命名的檔案：
- `camera_calibration_YYYY_MM_DD_HH_MM_SS.json`：Complete calibration results file | 完整的校正結果檔案。
- Each execution generates a new result file for easy comparison and tracking | 每次執行都會產生新的結果檔案，方便比較和追蹤。

### JSON檔案內容結構 | JSON File Structure

```json
{
    "標定時間": "2025-07-22 XX:XX:XX",
    "相機設定": {
        "物理焦距_mm": 50.0
    },
    "標定板設定": {
        "內角點數量": "9x6",
        "方格尺寸_mm": 25.0
    },
    "標定結果": {
        "RMS重投影誤差": 0.3456,
        "相機內參矩陣": {
            "fx_像素焦距": 308.49,
            "fy_像素焦距": 307.78,
            "cx_主點": 198.79,
            "cy_主點": 151.21,
            "註記": "fx, fy 為像素焦距，與物理焦距不同",
            "完整矩陣": [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]
        },
        "畸變係數": {
            "k1_徑向畸變1": 0.4172,
            "k2_徑向畸變2": -1.8713,
            "p1_切向畸變1": 0.0011,
            "p2_切向畸變2": 0.0000,
            "k3_徑向畸變3": 2.6282,
            "完整係數陣列": [k1, k2, p1, p2, k3]
        }
    },
    "使用影像數量": 20
}
```

## Quality Assessment | 品質評估

### Reprojection Error (RMS) | 重投影誤差（RMS）
- **< 0.5 pixels | < 0.5 像素**：Excellent | 優秀。
- **0.5 - 1.0 pixels | 0.5 - 1.0 像素**：Good | 良好。
- **> 1.0 pixels | > 1.0 像素**：Needs improvement | 需要改善。

### Improvement Suggestions | 改善建議
If reprojection error is large, try:
如果重投影誤差較大，請嘗試：
1. Increase number of calibration photos | 增加標定照片數量。
2. Improve photo quality (avoid blur, ensure good lighting) | 改善照片品質（避免模糊、確保光線充足）。
3. Check calibration board quality (ensure flat, clear squares) | 檢查標定板品質（確保平整、方格清晰）。
4. Confirm correct calibration board parameter settings | 確認標定板參數設定正確。

## Troubleshooting | 常見問題

### Q1: Program shows "No corners detected" | 程式提示「未檢測到角點」
**Solution | 解決方法：**
- Check if calibration board parameters in config.ini are correct | 檢查config.ini中標定板參數設定是否正確。
- Confirm calibration board appears completely and clearly in photos | 確認照片中標定板完整且清晰。
- Adjust shooting angle, avoid excessive tilt | 調整拍攝角度，避免過度傾斜。
- Improve photo lighting conditions | 改善照片光線條件。

### Q2: Large reprojection error | 重投影誤差很大
**Solution | 解決方法：**
- Re-measure and set correct square size | 重新測量並設定正確的方格尺寸。
- Add more high-quality calibration photos | 增加更多高品質的標定照片。
- Ensure calibration board is completely flat | 確保標定板完全平整。
- Check camera stability (avoid hand shake) | 檢查相機是否穩定（避免手震）。

### Q3: Program cannot read images | 程式無法讀取影像
**Solution | 解決方法：**
- Confirm supported image formats (jpg, png, bmp, tiff) | 確認影像格式受支援（jpg, png, bmp, tiff）。
- Check if file paths are correct | 檢查檔案路徑是否正確。
- Confirm image files are not corrupted | 確認影像檔案未損壞。

### Q4: Configuration file read error | 設定檔讀取錯誤
**Solution | 解決方法：**
- Confirm config.ini file is in same directory as camera_calibration.py | 確認config.ini檔案位於camera_calibration.py同一目錄下。
- Check config.ini file format is correct | 檢查config.ini檔案格式是否正確。
- Confirm all required configuration items are filled | 確認所有必要的設定項目都已填寫。

### Q5: Image folder not found | image資料夾找不到
**Solution | 解決方法：**
- Confirm image folder is in same directory as camera_calibration.py | 確認image資料夾位於camera_calibration.py同一目錄下。
- Program will automatically prompt correct folder location and complete path | 程式會自動提示正確的資料夾位置和完整路徑。
- If folder doesn't exist, manually create image folder | 如果資料夾不存在，請手動建立image資料夾。

### Q6: 套件安裝失敗 | Package installation fails
**解決方法：**
- 檢查網路連線。
- 嘗試手動安裝：`pip install opencv-python numpy`。
- 更新pip：`python -m pip install --upgrade pip`。
- 如果仍有問題，嘗試：`pip install --upgrade pip setuptools wheel`。

### Q7: How to choose appropriate calibration board size? | 如何選擇合適的標定板尺寸？
**Recommendations | 建議：**
- Small cameras | 小型相機：6x4 or 7x5 inner corners | 6x4 或 7x5 內角點。
- General cameras | 一般相機：8x6 or 9x7 inner corners | 8x6 或 9x7 內角點。
- High-resolution cameras | 高解析度相機：10x7 or larger | 10x7 或更大。

## Calibration Board Manufacturing | 標定板製作建議

### Print Requirements | 列印要求
- **Resolution | 解析度**：At least 300 DPI | 至少300 DPI。
- **Paper quality | 紙質**：Heavy paper or photo paper | 厚磅數紙張或照片紙。
- **Color | 顏色**：Pure black and white contrast, avoid grayscale | 純黑白對比，避免灰階。
- **Size | 尺寸**：Choose appropriate size based on shooting distance | 根據拍攝距離選擇適當大小。

### Mounting Method | 固定方式
- Mount on rigid flat surface (such as acrylic board, wooden board) | 貼在硬質平板上（如亞克力板、木板）。
- Ensure completely flat, no bending or deformation | 確保完全平整，無彎曲變形。
- Avoid reflective materials | 避免反光材質。

## 使用流程總結 | Usage Summary

1. **安裝套件**：執行 `pip install opencv-python numpy`。
2. **準備照片**：將標定照片放入 `image/` 資料夾 (GUI可選擇其他路徑)。
3. **執行程式**：
    *   **推薦GUI**：運行 `python camera_calibration_gui.py`，在介面中設定參數並執行。
    *   **CLI**：手動編輯 `config/config.ini`，然後運行 `python camera_calibration.py`。
4. **查看結果**：檢視終端或GUI結果區顯示的中文化校正結果（含RMS誤差）。
5. **取得輸出**：校正結果保存在 `result/` 資料夾中，檔名包含時間戳記。

## Technical Support | 技術支援

If you encounter problems or have suggestions, please check:
如有問題或建議，請檢查：
1. Python and related package versions meet requirements | Python和相關套件版本是否符合需求。
2. config.ini configuration file parameters are correct | config.ini設定檔參數是否正確 (GUI會自動管理)。
3. Photo quality meets requirements | 照片品質是否符合要求。
4. image folder is in correct location | image資料夾是否在正確位置 (GUI可選擇)。
5. Configuration file format is correct | 設定檔格式是否正確。

## 版本資訊 | Version Information

- **版本**：5.0
- **更新日期**：2025年7月24日
- **重大更新**：
  - **圖形化界面 (GUI) 版本**：提供直觀操作、參數記憶和自動配置管理。
  - **多階畸變係數支援**：支援5/8/12/14項畸變係數選擇。
  - **高精度標定模型**：支援高階徑向、薄稜鏡、傾斜畸變。
  - **智慧參數設定**：根據畸變係數項數自動調整OpenCV參數。
  - **詳細拍攝指南**：針對不同畸變係數項數提供專門拍攝建議。
  - **過擬合防護**：提供圖片數量建議和過度擬合警告。
  - **動態係數顯示**：終端和JSON輸出動態顯示實際畸變係數。
  - **完整中文化**：程式介面、設定檔註解全面中文化。
  - **RMS誤差追蹤**：完整的重投影誤差輸出和分析。
- **支援格式**：JPG, JPEG, PNG, BMP, TIFF, TIF
- **相容性**：Windows, Linux, macOS
- **精度等級**：適用於工業檢測、雷射測距等高精度應用

## 授權 | License

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org>

---

本軟體是釋出到公有領域的自由且不受限的軟體。

任何人都可以出於任何目的、商業或非商業性地、以任何方式自由地複製、修改、發布、使用、編譯、銷售或分發本軟體，無論是以原始碼形式還是以編譯後的二進位形式。

在承認著作權法的司法管轄區，本軟體的作者或作者們將本軟體中的任何及所有著作權利益奉獻給公有領域。我們做出此奉獻是為了廣大公眾的利益，並損害我們的繼承人和繼任者的利益。我們打算將此奉獻作為根據著作權法對本軟體所有現在和未來權利的公開永久放棄行為。

本軟體「按原樣」提供，不附有任何明示或暗示的保證，包括但不限於適銷性、特定用途適用性和不侵權的保證。在任何情況下，作者均不對任何索賠、損害或其他責任承擔任何責任，無論是在合約訴訟、侵權行為或其他方面，因本軟體或本軟體的使用或其他交易而產生或與之相關。

更多資訊，請參閱 <https://unlicense.org>