"""
OCR识别模块 - 识别游戏中的文字信息
支持降落地点、结算画面等文字提取
"""

import cv2
import numpy as np
from PIL import Image
import json
from pathlib import Path
from datetime import datetime

try:
    import easyocr
    OCR_AVAILABLE = True
    OCR_ENGINE = "easyocr"
except ImportError:
    try:
        from paddleocr import PaddleOCR
        OCR_AVAILABLE = True
        OCR_ENGINE = "paddleocr"
    except ImportError:
        OCR_AVAILABLE = False
        OCR_ENGINE = None

class GameOCR:
    """游戏OCR识别器"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 识别结果保存
        self.ocr_log = self.data_dir / "ocr_detections.json"
        self.spawn_names_log = self.data_dir / "spawn_names_detected.json"
        
        # 初始化OCR引擎
        self.ocr_engine = None
        self.engine_type = None
        
        if OCR_AVAILABLE:
            self._init_ocr_engine()
    
    def _init_ocr_engine(self):
        """初始化OCR引擎"""
        try:
            if OCR_ENGINE == "easyocr":
                # EasyOCR (支持中文和英文)
                self.ocr_engine = easyocr.Reader(['ch_sim', 'en'], gpu=False)
                self.engine_type = "easyocr"
                print("✅ EasyOCR 已加载")
            elif OCR_ENGINE == "paddleocr":
                # PaddleOCR (更适合中文)
                self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
                self.engine_type = "paddleocr"
                print("✅ PaddleOCR 已加载")
        except Exception as e:
            print(f"❌ OCR引擎初始化失败: {e}")
            self.ocr_engine = None
    
    def is_available(self):
        """检查OCR是否可用"""
        return self.ocr_engine is not None
    
    def detect_spawn_point(self, image, region="top_center"):
        """
        识别降落地点文字
        
        Args:
            image: PIL Image 或 numpy array
            region: 识别区域 (top_center, full)
        
        Returns:
            dict: {"success": bool, "text": str, "confidence": float}
        """
        if not self.is_available():
            return {"success": False, "error": "OCR引擎未初始化"}
        
        try:
            # 转换为numpy array
            if isinstance(image, Image.Image):
                img_array = np.array(image)
            else:
                img_array = image
            
            # 裁剪到关键区域 (降落地点通常显示在屏幕上方中央)
            if region == "top_center":
                h, w = img_array.shape[:2]
                # 截取上方30%，中间50%区域
                crop_img = img_array[0:int(h*0.3), int(w*0.25):int(w*0.75)]
            else:
                crop_img = img_array
            
            # 预处理：转灰度、增强对比度
            gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.equalizeHist(gray)
            
            # OCR识别
            if self.engine_type == "easyocr":
                results = self.ocr_engine.readtext(enhanced)
                if results:
                    # 取置信度最高的结果
                    best_result = max(results, key=lambda x: x[2])
                    text = best_result[1]
                    confidence = best_result[2]
                    
                    return {
                        "success": True,
                        "text": text,
                        "confidence": confidence,
                        "all_results": [{"text": r[1], "confidence": r[2]} for r in results]
                    }
            
            elif self.engine_type == "paddleocr":
                results = self.ocr_engine.ocr(enhanced, cls=True)
                if results and results[0]:
                    # 取第一个结果
                    best_result = results[0][0]
                    text = best_result[1][0]
                    confidence = best_result[1][1]
                    
                    return {
                        "success": True,
                        "text": text,
                        "confidence": confidence,
                        "all_results": [{"text": r[1][0], "confidence": r[1][1]} for r in results[0]]
                    }
            
            return {"success": False, "error": "未检测到文字"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def detect_settlement_screen(self, image):
        """
        识别结算画面
        提取：撤离点、收益、状态等信息
        
        Args:
            image: PIL Image 或 numpy array
        
        Returns:
            dict: 结算信息
        """
        if not self.is_available():
            return {"success": False, "error": "OCR引擎未初始化"}
        
        try:
            # 转换为numpy array
            if isinstance(image, Image.Image):
                img_array = np.array(image)
            else:
                img_array = image
            
            # 预处理
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.equalizeHist(gray)
            
            # OCR识别全屏
            if self.engine_type == "easyocr":
                results = self.ocr_engine.readtext(enhanced)
                all_text = [r[1] for r in results]
            elif self.engine_type == "paddleocr":
                results = self.ocr_engine.ocr(enhanced, cls=True)
                all_text = [r[1][0] for r in results[0]] if results and results[0] else []
            else:
                return {"success": False, "error": "无可用OCR引擎"}
            
            # 解析关键信息
            settlement_info = self._parse_settlement_info(all_text)
            settlement_info["success"] = True
            settlement_info["raw_text"] = all_text
            
            return settlement_info
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_settlement_info(self, text_list):
        """
        从识别到的文字中解析结算信息
        
        关键词匹配：
        - "成功撤离" / "撤离成功" -> survived = True
        - "阵亡" / "死亡" -> survived = False
        - "哈夫币" / "收益" -> profit
        - "撤离点" / "提取点" -> extract_point
        """
        info = {
            "survived": None,
            "profit": None,
            "extract_point": None,
            "duration": None
        }
        
        for text in text_list:
            text = text.strip()
            
            # 检测撤离状态
            if any(keyword in text for keyword in ["成功撤离", "撤离成功", "EXTRACTED"]):
                info["survived"] = True
            elif any(keyword in text for keyword in ["阵亡", "死亡", "KILLED", "KIA"]):
                info["survived"] = False
            
            # 提取收益数字
            if "哈夫币" in text or "收益" in text or "PROFIT" in text.upper():
                # 提取数字
                import re
                numbers = re.findall(r'-?\d+[,\d]*', text)
                if numbers:
                    # 移除逗号并转换为整数
                    profit_str = numbers[0].replace(',', '')
                    try:
                        info["profit"] = int(profit_str)
                    except:
                        pass
            
            # 提取撤离点
            if "撤离点" in text or "提取点" in text or "EXTRACT" in text.upper():
                # 尝试提取撤离点名称
                for extract_name in ["直升机", "货车", "船只", "火车", "山路", "隧道"]:
                    if extract_name in text:
                        info["extract_point"] = extract_name
                        break
            
            # 提取用时
            if "用时" in text or "时长" in text or "DURATION" in text.upper():
                import re
                time_match = re.search(r'(\d+):(\d+)', text)
                if time_match:
                    minutes = int(time_match.group(1))
                    seconds = int(time_match.group(2))
                    info["duration"] = minutes * 60 + seconds
        
        return info
    
    def log_spawn_detection(self, spawn_text, confidence, screenshot_path=None):
        """
        记录识别到的出生点名称
        用于完善战术地图数据
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "spawn_point": spawn_text,
            "confidence": confidence,
            "screenshot": str(screenshot_path) if screenshot_path else None
        }
        
        # 加载已有记录
        if self.spawn_names_log.exists():
            with open(self.spawn_names_log, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # 添加新记录
        logs.append(log_entry)
        
        # 保存
        with open(self.spawn_names_log, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 出生点识别已记录: {spawn_text} (置信度: {confidence:.2f})")
        
        return log_entry
    
    def get_spawn_name_statistics(self):
        """
        获取出生点名称统计
        返回所有识别到的出生点及其出现频率
        """
        if not self.spawn_names_log.exists():
            return {}
        
        with open(self.spawn_names_log, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # 统计出现频率
        spawn_counts = {}
        for entry in logs:
            spawn = entry["spawn_point"]
            if spawn in spawn_counts:
                spawn_counts[spawn]["count"] += 1
                spawn_counts[spawn]["avg_confidence"] = (
                    spawn_counts[spawn]["avg_confidence"] * (spawn_counts[spawn]["count"] - 1) +
                    entry["confidence"]
                ) / spawn_counts[spawn]["count"]
            else:
                spawn_counts[spawn] = {
                    "count": 1,
                    "avg_confidence": entry["confidence"],
                    "first_seen": entry["timestamp"]
                }
        
        # 按出现次数排序
        sorted_spawns = dict(sorted(spawn_counts.items(), key=lambda x: x[1]["count"], reverse=True))
        
        return sorted_spawns


def install_ocr_engine():
    """
    安装OCR引擎的辅助函数
    """
    print("检测OCR依赖...")
    
    if OCR_AVAILABLE:
        print(f"✅ 已安装 {OCR_ENGINE}")
        return True
    
    print("❌ 未安装OCR引擎")
    print("\n推荐安装方案:")
    print("\n1. EasyOCR (简单易用):")
    print("   pip install easyocr")
    
    print("\n2. PaddleOCR (中文识别更强):")
    print("   pip install paddlepaddle paddleocr")
    
    return False


# 单例模式
_ocr_instance = None

def get_ocr_engine(data_dir):
    """获取OCR引擎实例"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = GameOCR(data_dir)
    return _ocr_instance
