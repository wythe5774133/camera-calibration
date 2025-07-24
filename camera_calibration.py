#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相機內參標定工具

作者: Toby
描述: 使用棋盤格圖案自動進行相機內參標定
日期: 2025/07/22
"""

import sys
import os

# 導入所需套件
try:
    import cv2
    import numpy as np
    import glob
    import json
    import configparser
    from datetime import datetime
except ImportError as e:
    print(f"導入錯誤: {e}")
    print("請確保已安裝 opencv-python 和 numpy")
    sys.exit(1)

class CameraCalibration:
    """
    相機標定類別
    
    用於執行相機內參標定流程，包含：
    - 讀取設定檔
    - 處理標定影像
    - 計算相機內參
    - 儲存標定結果
    """
    
    def __init__(self):
        """
        初始化相機標定類別
        """
        print("相機內參標定工具")
        print("=" * 50)
        print(f"OpenCV版本: {cv2.__version__}")
        print(f"NumPy版本: {np.__version__}")
        
        # 載入設定檔
        self.load_config()
        
        # 顯示載入的設定
        print(f"\n設定檔載入成功:")
        print(f"  物理焦距: {self.focal_length}mm")
        print(f"  棋盤格內角點: {self.board_size[0]}x{self.board_size[1]}")
        print(f"  方格尺寸: {self.square_size}mm")
        print(f"  畸變係數項數: {self.distortion_coeffs_count}項")
        
        # 初始化物件點陣列 (3D世界座標)
        self.object_points = []   # 3D真實世界座標系統中的點 
        self.image_points = []    # D影像座標系統中的點
        
        # 建立標定板的3D座標
        self.create_object_points()
        
        # 標定結果
        self.camera_matrix = None       # 相機內參矩陣 
        self.distortion_coeffs = None   # 畸變係數 
        self.rvecs = None               # 旋轉向量
        self.tvecs = None               # 平移向量
        self.rms_error = None           # RMS重投影誤差
        
    def load_config(self):
        """
        從設定檔載入參數
        
        讀取config.ini檔案中的相機設定、標定板設定等參數
        """
        config = configparser.ConfigParser()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config", "config.ini")
        
        if not os.path.exists(config_path):
            print(f"錯誤: 找不到設定檔 {config_path}")
            print("請確保程式目錄中的config資料夾內存在 config.ini")
            raise FileNotFoundError("找不到設定檔")
        
        config.read(config_path, encoding='utf-8')
        
        try:
            # 讀取相機設定
            self.focal_length = config.getfloat('相機設定', '物理焦距')
            
            # 讀取標定板設定
            board_size_str = config.get('標定板設定', '內角點數量')
            width, height = map(int, board_size_str.split(','))
            self.board_size = (width, height)
            self.square_size = config.getfloat('標定板設定', '方格尺寸')
            
            # 讀取程式設定
            self.min_images = config.getint('程式設定', '最少影像數量')
            self.error_threshold = config.getfloat('程式設定', '誤差警告閾值')
            
            # 讀取畸變係數項數設定（預設為5項）
            self.distortion_coeffs_count = config.getint('程式設定', '畸變係數項數')
            
            # 驗證畸變係數項數的有效性
            valid_counts = [5, 8, 12, 14]
            if self.distortion_coeffs_count not in valid_counts:
                print(f"警告: 畸變係數項數 {self.distortion_coeffs_count} 無效，使用預設值 5")
                self.distortion_coeffs_count = 5
            
            # 讀取輸出設定
            self.save_full_matrix = config.getboolean('輸出設定', '保存完整矩陣')
            self.save_full_distortion = config.getboolean('輸出設定', '保存完整畸變係數')
            
        except Exception as e:
            print(f"讀取設定檔錯誤: {e}")
            print("請檢查 config.ini 的格式")
            raise
        
    def create_object_points(self):
        """
        建立標定板的3D座標點
        
        建立棋盤格的3D座標點 (Z=0，因為標定板是平面)
        """
        # 建立棋盤格的3D座標點 (Z=0，因為標定板是平面)
        objp = np.zeros((self.board_size[0] * self.board_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.board_size[0], 0:self.board_size[1]].T.reshape(-1, 2)
        
        # 乘以實際尺寸
        objp *= self.square_size
        
        self.objp = objp
        print(f"標定板設定: {self.board_size[0]}x{self.board_size[1]} 個內角點")
        print(f"方格尺寸: {self.square_size}mm")
    
    def find_corners_in_image(self, image_path):
        """
        在單一影像中尋找棋盤格角點
        
        參數:
            image_path: 影像檔案路徑
            
        回傳:
            success: 是否成功找到角點
            corners: 角點座標
        """
        # 讀取影像
        img = cv2.imread(image_path)
        if img is None:
            print(f"錯誤: 無法讀取影像 {image_path}")
            return False, None
            
        # 轉換為灰階 (棋盤格檢測需要灰階影像)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 尋找棋盤格角點
        ret, corners = cv2.findChessboardCorners(
            gray, 
            self.board_size,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FILTER_QUADS
        )
        
        if ret:
            # 提升角點精度 (亞像素精度)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            
            print(f"角點檢測成功: {os.path.basename(image_path)}")
            return True, corners2
        else:
            print(f"未找到角點: {os.path.basename(image_path)}")
            return False, None
    
    def process_images(self, images_folder):
        """
        處理資料夾中的所有影像
        
        參數:
            images_folder: 包含標定影像的資料夾路徑
        """
        print(f"\n處理資料夾: {images_folder}")
        
        # 支援的影像格式
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
        
        # 收集所有影像檔案
        image_files = []
        for extension in image_extensions:
            image_files.extend(glob.glob(os.path.join(images_folder, extension)))
            image_files.extend(glob.glob(os.path.join(images_folder, extension.upper())))
        
        # 移除重複項 (相同檔案但副檔名大小寫不同)
        image_files = list(set(image_files))
        
        if not image_files:
            print("錯誤: 在指定資料夾中找不到影像檔案")
            return False
            
        print(f"找到 {len(image_files)} 個影像檔案")
        
        # 清除先前的資料
        self.object_points = []
        self.image_points = []
        
        successful_images = 0
        
        # 處理每個影像
        for image_path in image_files:
            success, corners = self.find_corners_in_image(image_path)
            
            if success:
                # 如果成功找到角點，加入標定資料
                self.object_points.append(self.objp)
                self.image_points.append(corners)
                successful_images += 1
        
        print(f"\n處理完成: {successful_images}/{len(image_files)} 個影像")
        
        if successful_images < self.min_images:
            print(f"警告: 建議至少 {self.min_images} 個成功檢測的影像進行標定")
            return False
            
        return successful_images > 0
    
    def _get_calibration_flags(self):
        """
        根據畸變係數項數設定OpenCV標定參數
        
        回傳:
            flags: OpenCV calibrateCamera使用的flags參數
        """
        if self.distortion_coeffs_count == 5:
            # 5項：k1, k2, k3, p1, p2（OpenCV預設）
            return 0
        elif self.distortion_coeffs_count == 8:
            # 8項：k1, k2, k3, k4, k5, k6, p1, p2
            return cv2.CALIB_RATIONAL_MODEL
        elif self.distortion_coeffs_count == 12:
            # 12項：8項 + s1, s2, s3, s4（薄稜鏡畸變）
            return cv2.CALIB_RATIONAL_MODEL | cv2.CALIB_THIN_PRISM_MODEL
        elif self.distortion_coeffs_count == 14:
            # 14項：12項 + τx, τy（傾斜畸變）
            return cv2.CALIB_RATIONAL_MODEL | cv2.CALIB_THIN_PRISM_MODEL | cv2.CALIB_TILTED_MODEL
        else:
            # 預設使用5項
            return 0
    
    def _get_distortion_names(self):
        """
        根據畸變係數項數返回係數名稱列表
        
        回傳:
            names: 畸變係數名稱列表
        """
        if self.distortion_coeffs_count == 5:
            return ["k1_徑向畸變1", "k2_徑向畸變2", "p1_切向畸變1", "p2_切向畸變2", "k3_徑向畸變3"]
        elif self.distortion_coeffs_count == 8:
            return ["k1_徑向畸變1", "k2_徑向畸變2", "p1_切向畸變1", "p2_切向畸變2", 
                   "k3_徑向畸變3", "k4_徑向畸變4", "k5_徑向畸變5", "k6_徑向畸變6"]
        elif self.distortion_coeffs_count == 12:
            return ["k1_徑向畸變1", "k2_徑向畸變2", "p1_切向畸變1", "p2_切向畸變2", 
                   "k3_徑向畸變3", "k4_徑向畸變4", "k5_徑向畸變5", "k6_徑向畸變6",
                   "s1_薄稜鏡1", "s2_薄稜鏡2", "s3_薄稜鏡3", "s4_薄稜鏡4"]
        elif self.distortion_coeffs_count == 14:
            return ["k1_徑向畸變1", "k2_徑向畸變2", "p1_切向畸變1", "p2_切向畸變2", 
                   "k3_徑向畸變3", "k4_徑向畸變4", "k5_徑向畸變5", "k6_徑向畸變6",
                   "s1_薄稜鏡1", "s2_薄稜鏡2", "s3_薄稜鏡3", "s4_薄稜鏡4",
                   "τx_傾斜畸變x", "τy_傾斜畸變y"]
        else:
            return ["k1_徑向畸變1", "k2_徑向畸變2", "p1_切向畸變1", "p2_切向畸變2", "k3_徑向畸變3"]
    
    def _generate_distortion_dict(self):
        """
        根據實際畸變係數生成字典格式的畸變係數資料
        
        回傳:
            distortion_dict: 畸變係數字典
        """
        distortion_names = self._get_distortion_names()
        distortion_dict = {}
        
        # 實際畸變係數數量（可能少於設定的項數）
        actual_count = min(self.distortion_coeffs.shape[1], len(distortion_names))
        
        # 根據實際係數數量生成字典
        for i in range(actual_count):
            name = distortion_names[i] if i < len(distortion_names) else f"係數_{i+1}"
            distortion_dict[name] = float(self.distortion_coeffs[0, i])
        
        return distortion_dict
    
    def calibrate_camera(self, image_size):
        """
        執行相機標定計算
        
        參數:
            image_size: 影像尺寸 (寬度, 高度)
        """
        print(f"\n開始相機標定計算...")
        print(f"使用 {self.distortion_coeffs_count} 項畸變係數")
        
        if len(self.object_points) == 0:
            print("錯誤: 沒有有效的標定資料")
            return False
        
        # 根據畸變係數項數設定標定參數
        flags = self._get_calibration_flags()
        
        # 執行相機標定
        ret, self.camera_matrix, self.distortion_coeffs, self.rvecs, self.tvecs = cv2.calibrateCamera(
            self.object_points,
            self.image_points,
            image_size,
            None,
            None,
            flags=flags
        )
        
        # 儲存RMS誤差
        self.rms_error = ret
        
        print(f"標定完成!")
        print(f"重投影誤差 (RMS): {ret:.4f} 像素")
        
        if ret > self.error_threshold:
            print("警告: 重投影誤差較大，請檢查標定板品質或增加更多影像")
        elif ret < 0.5:
            print("優秀: 重投影誤差非常小，標定品質良好")
        else:
            print("良好: 重投影誤差在可接受範圍內")
            
        return True
    
    def save_results(self, output_path):
        """
        儲存標定結果到檔案
        
        參數:
            output_path: 輸出檔案路徑
        """
        if self.camera_matrix is None:
            print("錯誤: 尚未進行標定，無法儲存結果")
            return False
        
        # 確保輸出目錄存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 準備儲存的資料
        calibration_data = {
            "標定時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "相機設定": {
                "物理焦距_mm": self.focal_length if self.focal_length is not None else "未設定"
            },
            "標定板設定": {
                "內角點數量": f"{self.board_size[0]}x{self.board_size[1]}",
                "方格尺寸_mm": self.square_size
            },
            "標定結果": {
                "RMS重投影誤差": float(self.rms_error),
                "畸變係數項數": self.distortion_coeffs_count,
                "相機內參矩陣": {
                    "fx_像素焦距": float(self.camera_matrix[0, 0]),
                    "fy_像素焦距": float(self.camera_matrix[1, 1]),
                    "cx_主點": float(self.camera_matrix[0, 2]),
                    "cy_主點": float(self.camera_matrix[1, 2]),
                    "註記": "fx, fy 為像素焦距，與物理焦距不同"
                },
                "畸變係數": self._generate_distortion_dict()
            },
            "使用影像數量": len(self.object_points)
        }
        
        # 根據設定儲存完整陣列
        if self.save_full_matrix:
            calibration_data["標定結果"]["相機內參矩陣"]["完整矩陣"] = self.camera_matrix.tolist()
            
        if self.save_full_distortion:
            calibration_data["標定結果"]["畸變係數"]["完整係數陣列"] = self.distortion_coeffs.tolist()
        
        # 以JSON格式儲存
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(calibration_data, f, ensure_ascii=False, indent=4)
            print(f"標定結果已儲存至: {output_path}")
            return True
        except Exception as e:
            print(f"儲存檔案錯誤: {e}")
            return False
    
    def print_results(self):
        """
        顯示標定結果
        """
        if self.camera_matrix is None:
            print("無標定結果")
            return
            
        print("\n" + "="*60)
        print("相機內參標定結果")
        print("="*60)
        
        # 顯示使用的圖片數量和畸變係數項數
        print(f"\n使用圖片數量: {len(self.object_points)} 張")
        print(f"畸變係數項數: {self.distortion_coeffs_count} 項")
        
        # 顯示RMS重投影誤差
        if self.rms_error is not None:
            print(f"RMS重投影誤差: {self.rms_error:.4f} 像素")
        
        print(f"\n相機內參矩陣:")
        print(f"  fx (x方向像素焦距): {self.camera_matrix[0, 0]:.2f}")
        print(f"  fy (y方向像素焦距): {self.camera_matrix[1, 1]:.2f}")
        print(f"  cx (x方向主點): {self.camera_matrix[0, 2]:.2f}")
        print(f"  cy (y方向主點): {self.camera_matrix[1, 2]:.2f}")
        
        print(f"\n完整內參矩陣:")
        print(self.camera_matrix)
        
        # 動態顯示畸變係數
        print(f"\n畸變係數 ({self.distortion_coeffs_count}項):")
        distortion_names = self._get_distortion_names()
        
        # 顯示實際有效的畸變係數數量
        actual_count = min(self.distortion_coeffs.shape[1], len(distortion_names))
        for i in range(actual_count):
            name = distortion_names[i] if i < len(distortion_names) else f"係數_{i+1}"
            print(f"  {name}: {self.distortion_coeffs[0, i]:.6f}")
        
        print(f"\n完整畸變係數陣列:")
        print(self.distortion_coeffs)


def main():
    """
    主程式
    
    執行相機內參標定的完整流程
    """
    print("\n開始相機內參標定...")
    
    # 建立標定物件 (自動載入設定檔)
    try:
        calibrator = CameraCalibration()
    except FileNotFoundError:
        print("程式終止")
        return
    except Exception as e:
        print(f"初始化錯誤: {e}")
        return
    
    # 使用程式目錄中的image資料夾
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_folder = os.path.join(script_dir, "image")
    
    print(f"\n使用影像資料夾: {images_folder}")
    
    # 檢查影像資料夾是否存在
    if not os.path.exists(images_folder):
        print(f"錯誤: image資料夾不存在")
        print(f"請建立image資料夾並放入標定照片")
        print(f"完整路徑: {images_folder}")
        return
    
    # 處理影像
    success = calibrator.process_images(images_folder)
    if not success:
        print("影像處理失敗，程式終止")
        return
    
    # 取得影像尺寸 (從第一個成功的影像)
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        files = glob.glob(os.path.join(images_folder, ext))
        if files:
            sample_img = cv2.imread(files[0])
            if sample_img is not None:
                image_size = (sample_img.shape[1], sample_img.shape[0])
                break
    else:
        print("錯誤: 無法取得影像尺寸")
        return
    
    # 執行標定
    calibration_success = calibrator.calibrate_camera(image_size)
    if not calibration_success:
        print("相機標定失敗")
        return
    
    # 顯示結果
    calibrator.print_results()
    
    # 儲存結果到result資料夾，以時間戳記命名
    result_dir = os.path.join(script_dir, "result")
    # 確保result資料夾存在
    os.makedirs(result_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    output_file = os.path.join(result_dir, f"camera_calibration_{timestamp}.json")
    calibrator.save_results(output_file)
    
    print(f"\n標定完成！結果已儲存至: {output_file}")
    print(f"\n總結:")
    print(f"  焦距: {calibrator.focal_length}mm")
    print(f"  棋盤格尺寸: {calibrator.board_size[0]}x{calibrator.board_size[1]} 個內角點")
    print(f"  畸變係數項數: {calibrator.distortion_coeffs_count} 項")
    print(f"  使用影像: {len(calibrator.object_points)} 張")
    print(f"  RMS重投影誤差: {calibrator.rms_error:.4f} 像素")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n程式被使用者中斷")
    except Exception as e:
        print(f"\n\n未預期的錯誤: {e}")
        print(f"請檢查您的設定並重試")