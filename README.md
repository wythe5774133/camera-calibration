# 相機內參標定工具
# Camera Intrinsic Calibration Tool

## 程式簡介 | Overview

本程式使用OpenCV庫實現相機內參數標定，透過棋盤格標定板的多張照片來計算相機的內部參數，包括焦距、主點座標和畸變係數。程式已完全中文化，提供更友善的操作介面。

This program uses OpenCV to perform camera intrinsic parameter calibration through multiple chessboard pattern photos. It calculates camera internal parameters including focal length, principal point coordinates, and distortion coefficients. The program is fully localized in Chinese for better user experience.

## 功能特色 | Features

- 🎯 **自動角點檢測**：自動檢測棋盤格角點
- 📊 **高精度標定**：亞像素精度提升標定精確度
- 📁 **批次處理**：一次處理多張標定照片
- 📝 **詳細結果輸出**：完整內參矩陣和畸變係數輸出
- 💾 **結果保存**：標定結果以JSON格式保存
- 🖥️ **中文介面**：完全中文化的操作介面和註解
- 📂 **便利操作**：只需將照片放入image資料夾並執行程式
- ⚙️ **設定檔功能**：所有參數皆可透過config.ini設定
- 📊 **RMS誤差顯示**：顯示重投影誤差評估標定品質
- 🔢 **完整輸出資訊**：終端顯示內參矩陣、畸變係數、RMS誤差和使用圖片數量

## 專案結構 | Project Structure

```
camera-calibration/
├── camera_calibration.py    # 主程式 (已完全中文化)
├── config.ini              # 設定檔 (重要！請修改相關參數)
├── README.md               # 說明文件
├── requirements.txt        # 相依套件清單
├── image/                 # 標定照片資料夾 (請將照片放置於此)
└── result/                # 標定結果資料夾 (自動產生)
    └── camera_calibration_YYYY_MM_DD_HH_MM_SS.json  # 標定結果檔案 (含RMS誤差)
```

## System Requirements | 系統需求

### Automatic Installation | 自動安裝
The program will automatically check and install required packages when first run:
程式首次執行時會自動檢查並安裝所需套件：

- `opencv-python>=4.5.0`
- `numpy>=1.19.0`

### Python Version | Python版本
- Python 3.6 or higher | Python 3.6 或更高版本

## Quick Start | 快速開始

### 1. Download and Setup | 下載與設定
```bash
# Download the project | 下載專案
# Extract to desired location | 解壓縮到目標位置
```

### 2. Modify Configuration | 修改設定檔
Edit `config.ini` file to set your camera and calibration board parameters:
編輯 `config.ini` 文件，設定您的相機和標定板參數：

```ini
[相機設定]
物理焦距 = 50.0

[標定板設定]
內角點數量 = 9,6
方格尺寸 = 25.0
```

### 3. Prepare Calibration Photos | 準備標定照片
Place 15-30 chessboard calibration photos in the `image/` folder
將15-30張棋盤格標定照片放入 `image/` 資料夾中

### 4. Run Program | 執行程式
```bash
python camera_calibration.py
```

The program will:
程式會自動：
- Automatically install required packages if missing | 自動安裝缺少的套件
- Load configuration from config.ini | 從設定檔載入參數  
- Process all photos in image folder | 處理image資料夾中的所有照片
- Perform calibration and save results to result folder | 執行校正並將結果保存到result資料夾

## Configuration Details | 設定檔詳細說明

### Edit parameters in `config.ini` | 編輯 `config.ini` 中的參數：

```ini
[相機設定]
# Physical focal length (unit: millimeters) | 相機物理焦距（單位：毫米）
物理焦距 = 50.0

[標定板設定] 
# Chessboard inner corner count (Note: inner corners, not squares)
# 棋盤格內角點數量（注意：這是內角點，不是方格數量）
# Example: 8x6 chessboard has 7x5 inner corners | 例如：8x6的棋盤格有7x5個內角點
# Format: width,height | 格式：寬度,高度
內角點數量 = 9,6

# Actual size of chessboard squares (unit: millimeters)
# 棋盤格方格的實際尺寸（單位：毫米）
方格尺寸 = 25.0

[程式設定]
# Minimum number of successfully detected images required for calibration
# 最少需要成功檢測的影像數量
最少影像數量 = 5

# Reprojection error warning threshold (pixels) | 重投影誤差警告閾值（像素）
誤差警告閾值 = 1.0

[輸出設定]
# Whether to save complete intrinsic matrix and distortion coefficient arrays
# 是否在結果中保存完整的內參矩陣和畸變係數陣列
保存完整矩陣 = true
保存完整畸變係數 = true
```

## Photography Guidelines | 拍攝指南

### Preparation | 準備工作

**Calibration Board | 標定板：**
- **Recommended size | 推薦尺寸**：8x6 or 9x7 chessboard | 8x6 或 9x7 棋盤格
- **Print quality | 印刷要求**：High-quality printing with clear square edges | 高品質列印，確保方格邊緣清晰
- **Material | 材質建議**：Rigid cardboard or acrylic to avoid bending | 硬紙板或亞克力板，避免彎曲變形
- **Size measurement | 尺寸測量**：Accurately measure each square's actual size (unit: mm) | 精確測量每個方格的實際尺寸（單位：毫米）

### Photography Tips | 拍攝建議：
- **Photo count | 照片數量**：15-30 photos recommended | 建議拍攝15-30張照片
- **Angle variation | 角度變化**：Shoot calibration board from different angles | 從不同角度拍攝標定板
- **Position variation | 位置變化**：Place calibration board in different image positions | 將標定板放在影像的不同位置
- **Distance variation | 距離變化**：Shoot calibration board at different distances | 拍攝不同距離的標定板
- **Lighting | 光線條件**：Ensure sufficient and uniform lighting | 確保光線充足且均勻
- **Avoid blur | 避免模糊**：Ensure all photos are sharp and in focus | 確保所有照片都清晰對焦

### Important Notes | 注意事項：
- Calibration board must appear completely in image | 標定板必須完全出現在影像中
- Avoid reflection or shadows on calibration board | 避免標定板反光或陰影
- Each photo should have calibration board in different pose | 每張照片中的標定板應有不同的姿態

## 程式執行流程 | Program Execution Flow

1. **載入設定**：程式自動讀取config.ini設定檔參數
2. **自動檢測**：自動使用image資料夾中的照片
3. **批次處理**：自動處理資料夾中的所有影像檔案（已修正重複計數問題）
4. **顯示進度**：顯示每張照片的處理結果
5. **執行標定**：自動計算相機內參數
6. **中文顯示結果**：在控制台顯示詳細的標定結果（含RMS誤差）
7. **保存檔案**：將結果保存到result資料夾，檔名包含時間戳記

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
- **fx, fy**：Pixel focal lengths in x and y directions | x和y方向的像素焦距
- **cx, cy**：Principal point coordinates (image center offset) | 主點座標（影像中心點偏移）

#### Distortion Coefficients | 畸變係數
- **k1, k2, k3**：Radial distortion coefficients | 徑向畸變係數
- **p1, p2**：Tangential distortion coefficients | 切向畸變係數

### Output Files | 輸出檔案

Program generates timestamped files in result folder:
程式會在result資料夾生成時間戳記命名的檔案：
- `camera_calibration_YYYY_MM_DD_HH_MM_SS.json`：Complete calibration results file | 完整的校正結果檔案
- Each execution generates a new result file for easy comparison and tracking | 每次執行都會產生新的結果檔案，方便比較和追蹤

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
- **< 0.5 pixels | < 0.5 像素**：Excellent | 優秀
- **0.5 - 1.0 pixels | 0.5 - 1.0 像素**：Good | 良好
- **> 1.0 pixels | > 1.0 像素**：Needs improvement | 需要改善

### Improvement Suggestions | 改善建議
If reprojection error is large, try:
如果重投影誤差較大，請嘗試：
1. Increase number of calibration photos | 增加標定照片數量
2. Improve photo quality (avoid blur, ensure good lighting) | 改善照片品質（避免模糊、確保光線充足）
3. Check calibration board quality (ensure flat, clear squares) | 檢查標定板品質（確保平整、方格清晰）
4. Confirm correct calibration board parameter settings | 確認標定板參數設定正確

## Troubleshooting | 常見問題

### Q1: Program shows "No corners detected" | 程式提示「未檢測到角點」
**Solution | 解決方法：**
- Check if calibration board parameters in config.ini are correct | 檢查config.ini中標定板參數設定是否正確
- Confirm calibration board appears completely and clearly in photos | 確認照片中標定板完整且清晰
- Adjust shooting angle, avoid excessive tilt | 調整拍攝角度，避免過度傾斜
- Improve photo lighting conditions | 改善照片光線條件

### Q2: Large reprojection error | 重投影誤差很大
**Solution | 解決方法：**
- Re-measure and set correct square size | 重新測量並設定正確的方格尺寸
- Add more high-quality calibration photos | 增加更多高品質的標定照片
- Ensure calibration board is completely flat | 確保標定板完全平整
- Check camera stability (avoid hand shake) | 檢查相機是否穩定（避免手震）

### Q3: Program cannot read images | 程式無法讀取影像
**Solution | 解決方法：**
- Confirm supported image formats (jpg, png, bmp, tiff) | 確認影像格式受支援（jpg, png, bmp, tiff）
- Check if file paths are correct | 檢查檔案路徑是否正確
- Confirm image files are not corrupted | 確認影像檔案未損壞

### Q4: Configuration file read error | 設定檔讀取錯誤
**Solution | 解決方法：**
- Confirm config.ini file is in same directory as camera_calibration.py | 確認config.ini檔案位於camera_calibration.py同一目錄下
- Check config.ini file format is correct | 檢查config.ini檔案格式是否正確
- Confirm all required configuration items are filled | 確認所有必要的設定項目都已填寫

### Q5: Image folder not found | image資料夾找不到
**Solution | 解決方法：**
- Confirm image folder is in same directory as camera_calibration.py | 確認image資料夾位於camera_calibration.py同一目錄下
- Program will automatically prompt correct folder location and complete path | 程式會自動提示正確的資料夾位置和完整路徑
- If folder doesn't exist, manually create image folder | 如果資料夾不存在，請手動建立image資料夾

### Q6: Package installation fails | 套件安裝失敗
**Solution | 解決方法：**
- Check internet connection | 檢查網路連線
- Try manual installation: `pip install opencv-python numpy` | 嘗試手動安裝：`pip install opencv-python numpy`
- Update pip: `python -m pip install --upgrade pip` | 更新pip：`python -m pip install --upgrade pip`

### Q7: How to choose appropriate calibration board size? | 如何選擇合適的標定板尺寸？
**Recommendations | 建議：**
- Small cameras | 小型相機：6x4 or 7x5 inner corners | 6x4 或 7x5 內角點
- General cameras | 一般相機：8x6 or 9x7 inner corners | 8x6 或 9x7 內角點  
- High-resolution cameras | 高解析度相機：10x7 or larger | 10x7 或更大

## Calibration Board Manufacturing | 標定板製作建議

### Print Requirements | 列印要求
- **Resolution | 解析度**：At least 300 DPI | 至少300 DPI
- **Paper quality | 紙質**：Heavy paper or photo paper | 厚磅數紙張或照片紙
- **Color | 顏色**：Pure black and white contrast, avoid grayscale | 純黑白對比，避免灰階
- **Size | 尺寸**：Choose appropriate size based on shooting distance | 根據拍攝距離選擇適當大小

### Mounting Method | 固定方式
- Mount on rigid flat surface (such as acrylic board, wooden board) | 貼在硬質平板上（如亞克力板、木板）
- Ensure completely flat, no bending or deformation | 確保完全平整，無彎曲變形
- Avoid reflective materials | 避免反光材質

## Usage Summary | 使用流程總結

1. **Configuration | 設定**：Edit config.ini to set camera and calibration board parameters | 編輯config.ini設定相機和標定板參數
2. **Preparation | 準備**：Place calibration photos in `image/` folder | 將標定照片放入 `image/` 資料夾
3. **Execution | 執行**：Run `python camera_calibration.py` | 運行 `python camera_calibration.py`
4. **Auto Installation | 自動安裝**：Program automatically installs missing packages | 程式自動安裝缺少的套件
5. **Loading | 載入**：Program automatically reads configuration file parameters | 程式自動讀取設定檔參數
6. **Processing | 處理**：Program automatically processes all photos in image folder | 程式自動處理image資料夾中的所有照片
7. **Results | 查看**：View detailed calibration results in console | 檢視控制台顯示的校正結果
8. **Output | 取得**：Calibration results saved in `result/` folder with timestamp filename | 校正結果保存在 `result/` 資料夾中，檔名包含時間戳記

## Technical Support | 技術支援

If you encounter problems or have suggestions, please check:
如有問題或建議，請檢查：
1. Python and related package versions meet requirements | Python和相關套件版本是否符合需求
2. config.ini configuration file parameters are correct | config.ini設定檔參數是否正確
3. Photo quality meets requirements | 照片品質是否符合要求
4. image folder is in correct location | image資料夾是否在正確位置
5. Configuration file format is correct | 設定檔格式是否正確

## 版本資訊 | Version Information

- **版本**：4.0
- **更新日期**：2025年7月22日
- **重大更新**：
  - **完全中文化介面**：程式介面、輸出訊息、註解等全面中文化
  - **RMS誤差輸出**：在JSON結果檔案和終端顯示中加入RMS重投影誤差
  - **修正圖片計數問題**：解決檔案副檔名大小寫導致的重複計數問題
  - **增強終端輸出**：中文顯示內參矩陣、畸變係數、RMS誤差和使用圖片數量
  - **優化程式架構**：改善程式流程和錯誤處理機制
  - **更新JSON輸出格式**：改為中文欄位名稱，提高可讀性
- **支援格式**：JPG, JPEG, PNG, BMP, TIFF, TIF
- **相容性**：Windows, Linux, macOS

## License | 授權

This project is for educational and research purposes.
本專案僅供教育和研究使用。