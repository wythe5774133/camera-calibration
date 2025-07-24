#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相機內參標定工具 - GUI版本

作者: Toby
描述: 提供圖形化界面進行相機內參標定，同時保留原有命令行功能
日期: 2025/07/24
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import threading
import configparser
from datetime import datetime
import glob

# 導入原有的標定類別
try:
    from camera_calibration import CameraCalibration
    import cv2
    import numpy as np
except ImportError as e:
    print(f"導入錯誤: {e}")
    print("請確保已安裝 opencv-python 和 numpy，並且 camera_calibration.py 存在")
    sys.exit(1)


class CameraCalibrationGUI:
    """
    相機標定GUI類別
    提供圖形化界面進行相機內參標定
    """
    
    def __init__(self, root):
        """
        初始化GUI介面
        
        參數:
            root: tkinter主視窗
        """
        self.root = root
        self.root.title("相機內參標定工具 - GUI版本")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 設定檔案路徑
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.script_dir, "config", "config.ini")
        self.ui_settings_file = os.path.join(self.script_dir, "ui_settings.json")
        self.images_folder = os.path.join(self.script_dir, "image")
        
        # 初始化變數
        self.is_calibrating = False
        self.calibrator = None
        
        # 載入UI設定
        self.load_ui_settings()
        
        # 確保必要資料夾存在
        self.ensure_directories()
        
        # 建立UI介面
        self.create_widgets()
        
        # 更新圖片數量顯示
        self.update_image_count()
    
    def ensure_directories(self):
        """
        確保必要的資料夾存在
        """
        directories = [
            self.images_folder,
            os.path.join(self.script_dir, "result"),
            os.path.dirname(self.config_file)  # config資料夾
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    print(f"✅ 已創建資料夾: {directory}")
                except Exception as e:
                    print(f"❌ 創建資料夾失敗: {directory}, 錯誤: {e}")
    
    def load_ui_settings(self):
        """
        載入UI記憶設定
        """
        default_settings = {
            "board_width": 11,
            "board_height": 7,
            "square_size": 30.0,
            "focal_length": 50.0,
            "error_threshold": 1.0,
            "distortion_coeffs_count": 8,
            "save_full_matrix": True,
            "save_full_distortion": True,
            "image_folder": self.images_folder,  # 預設圖像路徑
            "recent_folders": []  # 最近使用的資料夾
        }
        
        try:
            if os.path.exists(self.ui_settings_file):
                with open(self.ui_settings_file, 'r', encoding='utf-8') as f:
                    self.ui_settings = json.load(f)
                # 確保所有必要的鍵都存在
                for key, value in default_settings.items():
                    if key not in self.ui_settings:
                        self.ui_settings[key] = value
            else:
                self.ui_settings = default_settings
        except Exception as e:
            print(f"載入UI設定錯誤: {e}")
            self.ui_settings = default_settings
    
    def save_ui_settings(self):
        """
        保存UI記憶設定
        """
        try:
            with open(self.ui_settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.ui_settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存UI設定錯誤: {e}")
    
    def create_widgets(self):
        """
        創建GUI元件
        """
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # 標題
        title_label = ttk.Label(main_frame, text="相機內參標定工具", 
                               font=('Microsoft YaHei', 16, 'bold'))
        title_label.grid(row=row, column=0, columnspan=2, pady=(0, 20))
        row += 1
        
        # 文件夾提示區域
        folder_frame = ttk.LabelFrame(main_frame, text="📁 標定圖像位置", padding="10")
        folder_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(0, weight=1)
        row += 1
        
        # 路徑選擇區域
        path_select_frame = ttk.Frame(folder_frame)
        path_select_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        path_select_frame.columnconfigure(1, weight=1)
        
        ttk.Label(path_select_frame, text="圖像資料夾:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        # 路徑下拉選單
        self.folder_var = tk.StringVar(value=self.ui_settings.get("image_folder", self.images_folder))
        self.folder_combo = ttk.Combobox(path_select_frame, state="readonly", width=50)
        self.folder_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.folder_combo.bind('<<ComboboxSelected>>', self.on_folder_changed)
        
        # 瀏覽按鈕
        browse_btn = ttk.Button(path_select_frame, text="📁 瀏覽", command=self.browse_folder)
        browse_btn.grid(row=0, column=2, padx=(0, 5))
        
        # 刷新按鈕
        refresh_btn = ttk.Button(path_select_frame, text="🔄 刷新", command=self.update_image_count)
        refresh_btn.grid(row=0, column=3)
        
        # 當前路徑顯示
        self.current_path_label = ttk.Label(folder_frame, text="", font=('Consolas', 9), foreground="gray")
        self.current_path_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 圖片數量顯示
        self.image_count_label = ttk.Label(folder_frame, text="", font=('Microsoft YaHei', 9))
        self.image_count_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 初始化路徑選單
        self.update_folder_combo()
        self.update_current_path_display()
        
        # 參數設定區域（左右排列）
        params_container = ttk.Frame(main_frame)
        params_container.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        # 設定1:1比例的左右分布
        params_container.columnconfigure(0, weight=1, uniform="params")
        params_container.columnconfigure(1, weight=1, uniform="params")
        row += 1
        
        # 必要參數設定區域（左側）
        required_frame = ttk.LabelFrame(params_container, text="⚙️ 必要參數設定", padding="10")
        required_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        required_frame.columnconfigure(1, weight=1)
        
        # 相機物理焦距
        ttk.Label(required_frame, text="相機物理焦距 (mm):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.focal_length_var = tk.DoubleVar(value=self.ui_settings["focal_length"])
        focal_entry = ttk.Entry(required_frame, textvariable=self.focal_length_var, width=15)
        focal_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 標定板內角點數量
        ttk.Label(required_frame, text="標定板內角點數量:").grid(row=1, column=0, sticky=tk.W, pady=2)
        board_frame = ttk.Frame(required_frame)
        board_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        self.board_width_var = tk.IntVar(value=self.ui_settings["board_width"])
        self.board_height_var = tk.IntVar(value=self.ui_settings["board_height"])
        
        width_entry = ttk.Entry(board_frame, textvariable=self.board_width_var, width=8)
        width_entry.pack(side=tk.LEFT)
        ttk.Label(board_frame, text=" × ").pack(side=tk.LEFT)
        height_entry = ttk.Entry(board_frame, textvariable=self.board_height_var, width=8)
        height_entry.pack(side=tk.LEFT)
        ttk.Label(board_frame, text=" (寬 × 高)").pack(side=tk.LEFT, padx=(5, 0))
        
        # 方格尺寸
        ttk.Label(required_frame, text="方格尺寸 (mm):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.square_size_var = tk.DoubleVar(value=self.ui_settings["square_size"])
        square_entry = ttk.Entry(required_frame, textvariable=self.square_size_var, width=15)
        square_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 進階參數設定區域（右側）
        advanced_frame = ttk.LabelFrame(params_container, text="🔧 進階參數設定 (可選)", padding="10")
        advanced_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        advanced_frame.columnconfigure(1, weight=1)
        
        # 誤差警告閾值
        ttk.Label(advanced_frame, text="誤差警告閾值 (像素):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.error_threshold_var = tk.DoubleVar(value=self.ui_settings["error_threshold"])
        error_entry = ttk.Entry(advanced_frame, textvariable=self.error_threshold_var, width=15)
        error_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 畸變係數項數
        ttk.Label(advanced_frame, text="畸變係數項數:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.distortion_var = tk.IntVar(value=self.ui_settings["distortion_coeffs_count"])
        distortion_combo = ttk.Combobox(advanced_frame, textvariable=self.distortion_var, 
                                       values=[5, 8, 12, 14], state="readonly", width=12)
        distortion_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # 輸出設定
        output_frame = ttk.Frame(advanced_frame)
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.save_matrix_var = tk.BooleanVar(value=self.ui_settings["save_full_matrix"])
        matrix_check = ttk.Checkbutton(output_frame, text="保存完整矩陣", 
                                      variable=self.save_matrix_var)
        matrix_check.pack(side=tk.LEFT)
        
        self.save_distortion_var = tk.BooleanVar(value=self.ui_settings["save_full_distortion"])
        distortion_check = ttk.Checkbutton(output_frame, text="保存完整畸變係數", 
                                          variable=self.save_distortion_var)
        distortion_check.pack(side=tk.LEFT, padx=(20, 0))
        
        # 執行區域
        execute_frame = ttk.LabelFrame(main_frame, text="🚀 執行標定", padding="10")
        execute_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        execute_frame.columnconfigure(0, weight=1)
        row += 1
        
        # 開始標定按鈕
        self.calibrate_btn = ttk.Button(execute_frame, text="開始標定", 
                                       command=self.start_calibration, style="Accent.TButton")
        self.calibrate_btn.grid(row=0, column=0, pady=5)
        
        # 進度條
        self.progress = ttk.Progressbar(execute_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 狀態標籤
        self.status_label = ttk.Label(execute_frame, text="準備就緒", font=('Microsoft YaHei', 9))
        self.status_label.grid(row=2, column=0, pady=2)
        
        # 結果顯示區域
        result_frame = ttk.LabelFrame(main_frame, text="📊 標定結果", padding="10")
        result_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        # 結果文字框
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, width=70,
                                                    font=('Consolas', 9))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 初始化結果顯示
        self.result_text.insert(tk.END, "相機內參標定工具 - GUI版本\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n")
        self.result_text.insert(tk.END, f"OpenCV版本: {cv2.__version__}\n")
        self.result_text.insert(tk.END, f"NumPy版本: {np.__version__}\n\n")
        self.result_text.insert(tk.END, "請設定參數並點擊'開始標定'按鈕...\n")
    
    def update_folder_combo(self):
        """
        更新資料夾下拉選單
        """
        # 取得預設路徑和最近使用的路徑
        default_folder = self.images_folder
        recent_folders = self.ui_settings.get("recent_folders", [])
        
        # 建立選項清單
        folder_options = []
        
        # 添加預設路徑（固定顯示專案相對路徑）
        folder_options.append(f"📁 camera-calibration\\image (預設)")
        
        # 添加最近使用的路徑
        for folder in recent_folders:
            if folder != default_folder and os.path.exists(folder):
                # 直接顯示完整路徑，避免解析問題
                folder_options.append(f"📁 {folder}")
        
        # 更新下拉選單
        self.folder_combo['values'] = folder_options
        
        # 設定當前選擇
        current_folder = self.folder_var.get()
        if current_folder == default_folder:
            self.folder_combo.current(0)
        else:
            # 尋找對應的選項
            found_match = False
            for i, option in enumerate(folder_options):
                # 從選項中提取路徑部分
                if option.startswith("📁 "):
                    path_part = option[2:].strip()
                    if path_part == "camera-calibration\\image (預設)":
                        # 這是預設選項，比較實際路徑
                        if current_folder == default_folder:
                            self.folder_combo.current(i)
                            found_match = True
                            break
                    elif path_part == current_folder:
                        self.folder_combo.current(i)
                        found_match = True
                        break
            
            # 如果沒找到匹配項，添加當前路徑到選項中
            if not found_match and current_folder and os.path.exists(current_folder):
                new_option = f"📁 {current_folder}"
                folder_options.append(new_option)
                self.folder_combo['values'] = folder_options
                self.folder_combo.current(len(folder_options) - 1)
    
    def update_current_path_display(self):
        """
        更新當前路徑顯示
        """
        current_folder = self.folder_var.get()
        if current_folder:
            # 顯示完整路徑
            self.current_path_label.config(text=f"完整路徑: {current_folder}")
        else:
            self.current_path_label.config(text="")
    
    def on_folder_changed(self, event=None):
        """
        資料夾選擇改變時的處理
        """
        selected = self.folder_combo.get()
        if not selected:
            return
        
        print(f"DEBUG - on_folder_changed: 選擇='{selected}'")
        
        # 解析選擇的路徑
        if selected.startswith("📁 "):
            # 移除emoji和標籤
            path_part = selected[2:].strip()
            
            if path_part == "camera-calibration\\image (預設)":
                # 預設路徑，使用實際的image資料夾路徑
                new_folder = self.images_folder
                print(f"DEBUG - on_folder_changed: 使用預設路徑='{new_folder}'")
            else:
                # 直接使用顯示的路徑（因為下拉選單中的路徑就是實際路徑）
                new_folder = path_part
                print(f"DEBUG - on_folder_changed: 使用其他路徑='{new_folder}'")
        else:
            # 可能是用戶直接輸入的路徑或其他情況
            new_folder = selected
            print(f"DEBUG - on_folder_changed: 直接使用='{new_folder}'")
        
        # 標準化路徑（處理不同的斜線格式）
        if new_folder:
            new_folder = os.path.normpath(new_folder)
            print(f"DEBUG - on_folder_changed: 標準化路徑='{new_folder}'")
        
        # 更新路徑變數
        self.folder_var.set(new_folder)
        print(f"DEBUG - on_folder_changed: 設定folder_var='{new_folder}'")
        
        # 更新路徑顯示
        self.update_current_path_display()
        
        # 更新圖片數量
        self.update_image_count()
    
    def browse_folder(self):
        """
        瀏覽選擇資料夾
        """
        # 取得當前路徑作為初始目錄
        current_folder = self.folder_var.get()
        if not current_folder or not os.path.exists(current_folder):
            initial_dir = self.script_dir
        else:
            initial_dir = current_folder
        
        # 開啟資料夾選擇對話框
        selected_folder = filedialog.askdirectory(
            title="選擇標定圖像資料夾",
            initialdir=initial_dir
        )
        
        if selected_folder:
            # 標準化路徑
            selected_folder = os.path.normpath(selected_folder)
            
            # 更新路徑
            self.folder_var.set(selected_folder)
            
            # 加入到最近使用清單
            self.add_to_recent_folders(selected_folder)
            
            # 更新介面
            self.update_folder_combo()
            self.update_current_path_display()
            self.update_image_count()
    
    def add_to_recent_folders(self, folder_path):
        """
        將資料夾加入到最近使用清單
        
        參數:
            folder_path: 資料夾路徑
        """
        # 標準化路徑
        folder_path = os.path.normpath(folder_path)
        
        recent_folders = self.ui_settings.get("recent_folders", [])
        
        # 移除重複項
        if folder_path in recent_folders:
            recent_folders.remove(folder_path)
        
        # 加到清單開頭
        recent_folders.insert(0, folder_path)
        
        # 限制最多保存10個最近路徑
        recent_folders = recent_folders[:10]
        
        # 更新設定
        self.ui_settings["recent_folders"] = recent_folders
        self.save_ui_settings()
    
    def update_image_count(self):
        """
        更新圖片數量顯示
        """
        try:
            current_folder = self.folder_var.get()
            print(f"DEBUG - update_image_count: 當前路徑='{current_folder}'")
            
            # 標準化路徑
            if current_folder:
                current_folder = os.path.normpath(current_folder)
                print(f"DEBUG - update_image_count: 標準化路徑='{current_folder}'")
            
            print(f"DEBUG - update_image_count: 路徑存在={os.path.exists(current_folder) if current_folder else False}")
            
            if not current_folder or not os.path.exists(current_folder):
                self.image_count_label.config(text="❌ 選擇的資料夾不存在", foreground="red")
                return
            
            # 支援的影像格式
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
            image_files = []
            
            for extension in image_extensions:
                image_files.extend(glob.glob(os.path.join(current_folder, extension)))
                image_files.extend(glob.glob(os.path.join(current_folder, extension.upper())))
            
            # 移除重複項
            image_files = list(set(image_files))
            count = len(image_files)
            
            if count == 0:
                self.image_count_label.config(text="❌ 未找到標定圖像", foreground="red")
            elif count < 5:
                self.image_count_label.config(text=f"⚠️ 找到 {count} 張圖像 (建議至少5張)", foreground="orange")
            else:
                self.image_count_label.config(text=f"✅ 找到 {count} 張標定圖像", foreground="green")
        
        except Exception as e:
            self.image_count_label.config(text=f"❌ 檢查圖像錯誤: {e}", foreground="red")
    
    def generate_config_ini(self):
        """
        根據UI輸入生成config.ini檔案
        """
        # 直接寫入字符串格式，避免ConfigParser的格式問題
        config_content = f"""[相機設定]
# 相機物理焦距（單位：毫米）
# 請輸入您相機鏡頭的實際焦距，例如：50, 85, 135等
物理焦距 = {self.focal_length_var.get()}

[標定板設定]
# 棋盤格內角點數量（注意：這是內角點，不是方格數量）
# 例如：8x6的棋盤格有7x5個內角點，9x7的棋盤格有8x6個內角點
# 格式：寬度,高度
內角點數量 = {self.board_width_var.get()},{self.board_height_var.get()}

# 棋盤格方格的實際尺寸（單位：mm）
# 請使用尺子精確測量您標定板上每個方格的邊長
# 這個數值的準確性直接影響校正結果的品質
方格尺寸 = {self.square_size_var.get()}

[程式設定]
# 最少需要成功檢測的影像數量才能進行校正
最少影像數量 = 5

# 重投影誤差警告閾值（像素）
# 超過此值會顯示警告訊息
誤差警告閾值 = {self.error_threshold_var.get()}

# 畸變係數數量設定（支援5、8、12、14項）
# 重要提醒：高階畸變係數需要更多圖片來避免過度擬合
# 
# 5項：k1, k2, k3, p1, p2（標準畸變模型）
#     - 適用：一般應用、廣角鏡頭
#     - 建議圖片數量：15-25張
#     - RMS目標：通常0.3-1.0像素
# 
# 8項：k1-k6（高階徑向）, p1, p2（切向）
#     - 適用：高精度應用、魚眼鏡頭、極廣角
#     - 建議圖片數量：25-35張
#     - RMS目標：通常比5項更小
# 
# 12項：8項 + s1-s4（薄稜鏡畸變）
#      - 適用：極高精度應用、工業檢測、雷射測距
#      - 建議圖片數量：30-40張
#      - 注意：需要圖片覆蓋感測器邊緣區域
# 
# 14項：12項 + τx, τy（傾斜畸變）
#      - 適用：最高精度要求、特殊光學系統
#      - 建議圖片數量：40-60張
#      - 警告：容易過度擬合，需要更多樣化的拍攝角度
#      - 如果RMS反而變大，建議改用12項
畸變係數項數 = {self.distortion_var.get()}

[輸出設定]
# 是否在結果中保存相機內參矩陣的完整陣列
保存完整矩陣 = {str(self.save_matrix_var.get()).lower()}

# 是否在結果中保存畸變係數的完整陣列
保存完整畸變係數 = {str(self.save_distortion_var.get()).lower()}
"""
        
        # 寫入檔案
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
    
    def validate_inputs(self):
        """
        驗證輸入參數
        
        回傳:
            bool: 驗證是否通過
        """
        try:
            # 檢查必要參數
            if self.focal_length_var.get() <= 0:
                messagebox.showerror("輸入錯誤", "相機物理焦距必須大於0")
                return False
            
            if self.board_width_var.get() < 3 or self.board_height_var.get() < 3:
                messagebox.showerror("輸入錯誤", "標定板內角點數量必須大於等於3")
                return False
            
            if self.square_size_var.get() <= 0:
                messagebox.showerror("輸入錯誤", "方格尺寸必須大於0")
                return False
            
            if self.error_threshold_var.get() <= 0:
                messagebox.showerror("輸入錯誤", "誤差警告閾值必須大於0")
                return False
            
            # 檢查圖像資料夾
            current_folder = self.folder_var.get()
            if not current_folder or not os.path.exists(current_folder):
                messagebox.showerror("資料夾錯誤", f"選擇的圖像資料夾不存在: {current_folder}")
                return False
            
            return True
            
        except tk.TclError:
            messagebox.showerror("輸入錯誤", "請確保所有數值輸入正確")
            return False
    
    def update_status(self, message):
        """
        更新狀態顯示
        
        參數:
            message: 狀態訊息
        """
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def add_result_text(self, text):
        """
        添加結果文字
        
        參數:
            text: 要添加的文字
        """
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)
        self.root.update_idletasks()
    
    def calibration_thread(self):
        """
        標定執行緒
        """
        try:
            self.add_result_text("\n" + "="*50 + "\n")
            self.add_result_text("開始相機內參標定...\n")
            self.add_result_text("="*50 + "\n")
            
            # 生成config.ini
            self.update_status("生成設定檔...")
            self.generate_config_ini()
            self.add_result_text("✅ 設定檔已生成\n")
            
            # 建立標定物件
            self.update_status("初始化標定器...")
            self.calibrator = CameraCalibration()
            self.add_result_text(f"✅ 標定器初始化完成\n")
            self.add_result_text(f"   物理焦距: {self.calibrator.focal_length}mm\n")
            self.add_result_text(f"   棋盤格內角點: {self.calibrator.board_size[0]}x{self.calibrator.board_size[1]}\n")
            self.add_result_text(f"   方格尺寸: {self.calibrator.square_size}mm\n")
            self.add_result_text(f"   畸變係數項數: {self.calibrator.distortion_coeffs_count}項\n\n")
            
            # 處理影像
            current_folder = self.folder_var.get()
            self.update_status("處理標定影像...")
            self.add_result_text(f"處理標定影像...\n")
            self.add_result_text(f"圖像資料夾: {current_folder}\n")
            success = self.calibrator.process_images(current_folder)
            
            if not success:
                self.add_result_text("❌ 影像處理失敗\n")
                raise Exception("影像處理失敗")
            
            self.add_result_text(f"✅ 成功處理 {len(self.calibrator.object_points)} 張影像\n\n")
            
            # 取得影像尺寸
            self.update_status("分析影像尺寸...")
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                files = glob.glob(os.path.join(current_folder, ext))
                if files:
                    sample_img = cv2.imread(files[0])
                    if sample_img is not None:
                        image_size = (sample_img.shape[1], sample_img.shape[0])
                        break
            else:
                raise Exception("無法取得影像尺寸")
            
            # 執行標定
            self.update_status("執行相機標定...")
            self.add_result_text("執行相機標定計算...\n")
            calibration_success = self.calibrator.calibrate_camera(image_size)
            
            if not calibration_success:
                raise Exception("相機標定失敗")
            
            # 顯示結果
            self.add_result_text("\n" + "="*50 + "\n")
            self.add_result_text("📊 標定結果\n")
            self.add_result_text("="*50 + "\n")
            self.add_result_text(f"使用圖片數量: {len(self.calibrator.object_points)} 張\n")
            self.add_result_text(f"畸變係數項數: {self.calibrator.distortion_coeffs_count} 項\n")
            self.add_result_text(f"RMS重投影誤差: {self.calibrator.rms_error:.4f} 像素\n\n")
            
            # 評估結果品質
            if self.calibrator.rms_error < 0.5:
                self.add_result_text("✅ 優秀: 重投影誤差非常小，標定品質良好\n")
            elif self.calibrator.rms_error < 1.0:
                self.add_result_text("✅ 良好: 重投影誤差在可接受範圍內\n")
            else:
                self.add_result_text("⚠️ 警告: 重投影誤差較大，請檢查標定板品質或增加更多影像\n")
            
            self.add_result_text(f"\n相機內參矩陣:\n")
            self.add_result_text(f"  fx (x方向像素焦距): {self.calibrator.camera_matrix[0, 0]:.2f}\n")
            self.add_result_text(f"  fy (y方向像素焦距): {self.calibrator.camera_matrix[1, 1]:.2f}\n")
            self.add_result_text(f"  cx (x方向主點): {self.calibrator.camera_matrix[0, 2]:.2f}\n")
            self.add_result_text(f"  cy (y方向主點): {self.calibrator.camera_matrix[1, 2]:.2f}\n\n")
            
            # 儲存結果
            self.update_status("保存標定結果...")
            result_dir = os.path.join(self.script_dir, "result")
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            output_file = os.path.join(result_dir, f"camera_calibration_{timestamp}.json")
            
            save_success = self.calibrator.save_results(output_file)
            if save_success:
                self.add_result_text(f"✅ 標定結果已保存至: {os.path.basename(output_file)}\n")
            else:
                self.add_result_text("❌ 保存結果失敗\n")
            
            self.update_status("標定完成！")
            self.add_result_text("\n🎉 標定完成！\n")
            
            # 保存UI設定
            self.save_current_settings()
            
        except Exception as e:
            self.add_result_text(f"\n❌ 標定過程發生錯誤: {str(e)}\n")
            self.update_status(f"標定失敗: {str(e)}")
        
        finally:
            # 恢復UI狀態
            self.is_calibrating = False
            self.calibrate_btn.config(state="normal", text="開始標定")
            self.progress.stop()
    
    def save_current_settings(self):
        """
        保存當前UI設定到記憶檔案
        """
        try:
            self.ui_settings.update({
                "board_width": self.board_width_var.get(),
                "board_height": self.board_height_var.get(),
                "square_size": self.square_size_var.get(),
                "focal_length": self.focal_length_var.get(),
                "error_threshold": self.error_threshold_var.get(),
                "distortion_coeffs_count": self.distortion_var.get(),
                "save_full_matrix": self.save_matrix_var.get(),
                "save_full_distortion": self.save_distortion_var.get(),
                "image_folder": self.folder_var.get()
            })
            
            # 加入當前資料夾到最近使用清單
            current_folder = self.folder_var.get()
            if current_folder and current_folder != self.images_folder:
                self.add_to_recent_folders(current_folder)
            
            self.save_ui_settings()
            self.add_result_text("✅ UI設定已記憶\n")
        except Exception as e:
            print(f"保存UI設定錯誤: {e}")
    
    def start_calibration(self):
        """
        開始標定流程
        """
        if self.is_calibrating:
            return
        
        # 驗證輸入
        if not self.validate_inputs():
            return
        
        # 更新UI狀態
        self.is_calibrating = True
        self.calibrate_btn.config(state="disabled", text="標定中...")
        self.progress.start()
        self.result_text.delete(1.0, tk.END)
        
        # 啟動標定執行緒
        calibration_thread = threading.Thread(target=self.calibration_thread, daemon=True)
        calibration_thread.start()


def main():
    """
    主程式入口
    """
    # 創建主視窗
    root = tk.Tk()
    
    # 設定樣式
    style = ttk.Style()
    
    # 創建GUI應用
    app = CameraCalibrationGUI(root)
    
    # 啟動主循環
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("程式被使用者中斷")
    except Exception as e:
        print(f"程式錯誤: {e}")


if __name__ == "__main__":
    main()