"""
游戏监控模块 - 集成到Streamlit应用
实时监控游戏画面，识别出生点和高价值物品
支持OCR识别降落地点和结算画面
"""

import threading
import time
from datetime import datetime
from pathlib import Path
import json
import mss
import numpy as np
from PIL import Image
import cv2

# 尝试导入OCR模块
try:
    from game_ocr import get_ocr_engine
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class GameMonitor:
    """游戏监控器"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_running = False
        self.monitor_thread = None
        
        # 当前会话状态
        self.current_session = {
            "active": False,
            "map": None,
            "spawn_point": None,
            "items": [],
            "start_time": None,
            "last_detection_time": None,
            "spawn_detected_by_ocr": False  # OCR是否已识别出生点
        }
        
        # 屏幕捕获
        self.sct = mss.mss()
        
        # OCR引擎
        self.ocr_engine = None
        if OCR_AVAILABLE:
            try:
                self.ocr_engine = get_ocr_engine(self.data_dir)
                print(f"✅ OCR引擎已加载: {self.ocr_engine.engine_type if self.ocr_engine.is_available() else '未初始化'}")
            except Exception as e:
                print(f"❌ OCR引擎加载失败: {e}")
        
        # 检测配置
        self.detection_interval = 2  # 每2秒检测一次
        self.spawn_detection_duration = 30  # 前30秒检测出生点
        self.settlement_check_interval = 5  # 每5秒检查一次结算画面
        
        # 检测配置
        self.detection_interval = 2  # 每2秒检测一次
        self.spawn_detection_duration = 30  # 前30秒检测出生点
        
        # 物品颜色范围（HSV）
        self.golden_color_range = {
            "lower": np.array([20, 100, 100]),  # 金色下限
            "upper": np.array([30, 255, 255])   # 金色上限
        }
        self.red_color_range = {
            "lower": np.array([0, 100, 100]),   # 红色下限
            "upper": np.array([10, 255, 255])   # 红色上限
        }
        
        # 地图关键词匹配
        self.map_keywords = {
            "大坝": ["大坝", "Dam", "会议", "金融", "海军"],
            "长弓": ["长弓", "Longbow", "森林", "营地"],
            "巴克什": ["巴克什", "Bazaar", "集市", "清真寺"],
            "航天": ["航天", "Space", "发射台", "控制中心"],
            "监狱": ["监狱", "Prison", "牢房", "监控室"]
        }
        
        # 出生点关键词
        self.spawn_keywords = {
            "大坝": {
                "军营": ["军营", "栏杆", "TO"],
                "维修通道": ["维修", "通道"],
                "变电站": ["变电站", "变电"],
                "济舍": ["济舍", "中心", "正门"],
                "水泥厂": ["水泥厂", "后山"],
                "河滩": ["河滩", "野地"]
            }
        }
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_running:
            return {"status": "error", "message": "监控已在运行中"}
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        return {"status": "success", "message": "游戏监控已启动"}
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        return {"status": "success", "message": "游戏监控已停止"}
    
    def _monitor_loop(self):
        """监控主循环"""
        while self.is_running:
            try:
                # 捕获屏幕
                screenshot = self._capture_screen()
                
                if screenshot is not None:
                    # 检测游戏状态
                    self._detect_game_state(screenshot)
                    
                    # 如果在游戏中，检测物品
                    if self.current_session["active"]:
                        elapsed_time = (datetime.now() - self.current_session["start_time"]).total_seconds()
                        
                        # 前30秒用OCR检测出生点文字
                        if (elapsed_time < self.spawn_detection_duration and 
                            not self.current_session["spawn_detected_by_ocr"] and
                            self.ocr_engine and self.ocr_engine.is_available()):
                            self._detect_spawn_point_ocr(screenshot)
                        
                        # 持续检测高价值物品（颜色检测）
                        self._detect_valuable_items(screenshot)
                        
                        # 定期检查结算画面
                        if elapsed_time > 60 and elapsed_time % self.settlement_check_interval == 0:
                            self._check_settlement_screen(screenshot)
                
                time.sleep(self.detection_interval)
                
            except Exception as e:
                print(f"[监控错误] {e}")
                time.sleep(5)
    
    def _capture_screen(self):
        """捕获屏幕"""
        try:
            # 捕获主屏幕
            monitor = self.sct.monitors[1]
            screenshot = self.sct.grab(monitor)
            
            # 转换为numpy数组
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
        except Exception as e:
            print(f"[截图错误] {e}")
            return None
    
    def _detect_game_state(self, screenshot):
        """检测游戏状态（是否在游戏中）"""
        # 简化版：检测屏幕特定区域是否有游戏UI元素
        # 这里可以用OCR或图像识别
        
        # 如果检测到游戏开始
        if not self.current_session["active"]:
            # 检测是否有小地图、血条等UI元素
            if self._has_game_ui(screenshot):
                self._start_new_session()
    
    def _has_game_ui(self, screenshot):
        """检测是否有游戏UI（简化版）"""
        # 这里可以实现更复杂的检测逻辑
        # 目前返回True作为示例
        return False  # 需要实际实现
    
    def _start_new_session(self):
        """开始新会话"""
        self.current_session = {
            "active": True,
            "map": None,
            "spawn_point": None,
            "items": [],
            "start_time": datetime.now(),
            "last_detection_time": datetime.now(),
            "spawn_detected_by_ocr": False
        }
        print(f"[新会话] 游戏开始于 {self.current_session['start_time']}")
    
    def _detect_spawn_point_ocr(self, screenshot):
        """
        使用OCR识别降落地点文字
        游戏开始时屏幕上方会显示出生点名称
        """
        if not self.ocr_engine or not self.ocr_engine.is_available():
            return
        
        try:
            # 转换screenshot为PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            
            # OCR识别上方中央区域
            result = self.ocr_engine.detect_spawn_point(img, region="top_center")
            
            if result["success"] and result["confidence"] > 0.6:
                spawn_text = result["text"]
                confidence = result["confidence"]
                
                # 保存到会话
                self.current_session["spawn_point"] = spawn_text
                self.current_session["spawn_detected_by_ocr"] = True
                
                # 保存截图用于验证
                screenshot_path = self.data_dir / f"spawn_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                img.save(screenshot_path)
                
                # 记录到日志
                self.ocr_engine.log_spawn_detection(spawn_text, confidence, screenshot_path)
                
                print(f"✅ [OCR识别] 出生点: {spawn_text} (置信度: {confidence:.2f})")
                
                # 如果识别到的文字包含已知关键词，尝试匹配地图
                self._match_map_from_spawn(spawn_text)
        
        except Exception as e:
            print(f"❌ [OCR错误] 出生点识别失败: {e}")
    
    def _check_settlement_screen(self, screenshot):
        """
        检查是否进入结算画面
        识别撤离点、收益等信息
        """
        if not self.ocr_engine or not self.ocr_engine.is_available():
            return
        
        try:
            # 转换为PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            
            # OCR识别结算画面
            result = self.ocr_engine.detect_settlement_screen(img)
            
            if result["success"]:
                # 检测到关键词（成功撤离或阵亡）
                if result["survived"] is not None:
                    print(f"✅ [OCR识别] 结算画面:")
                    print(f"   - 状态: {'成功撤离' if result['survived'] else '阵亡'}")
                    if result["profit"] is not None:
                        print(f"   - 收益: {result['profit']} 哈夫币")
                    if result["extract_point"]:
                        print(f"   - 撤离点: {result['extract_point']}")
                    
                    # 自动结束会话
                    self.end_session(
                        survived=result["survived"],
                        profit=result.get("profit", 0),
                        extract_point=result.get("extract_point")
                    )
        
        except Exception as e:
            print(f"❌ [OCR错误] 结算画面识别失败: {e}")
    
    def _match_map_from_spawn(self, spawn_text):
        """从出生点文字推断地图"""
        for map_name, keywords in self.spawn_keywords.items():
            for spawn_area, spawn_keywords in keywords.items():
                if any(keyword in spawn_text for keyword in spawn_keywords):
                    self.current_session["map"] = map_name
                    print(f"  → 推断地图: {map_name}")
                    return
    
    def _detect_valuable_items(self, screenshot):
        """检测金色/红色物品"""
        try:
            # 转换为HSV
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            
            # 检测金色物品
            golden_mask = cv2.inRange(hsv, self.golden_color_range["lower"], self.golden_color_range["upper"])
            golden_pixels = cv2.countNonZero(golden_mask)
            
            # 检测红色物品
            red_mask = cv2.inRange(hsv, self.red_color_range["lower"], self.red_color_range["upper"])
            red_pixels = cv2.countNonZero(red_mask)
            
            # 如果检测到足够多的金色或红色像素
            threshold = 1000  # 像素阈值
            
            if golden_pixels > threshold:
                self._record_item_detection("金色物品", golden_pixels)
            
            if red_pixels > threshold:
                self._record_item_detection("红色物品", red_pixels)
                
        except Exception as e:
            print(f"[物品检测错误] {e}")
    
    def _record_item_detection(self, item_type, pixel_count):
        """记录物品检测"""
        now = datetime.now()
        
        # 避免重复记录（5秒内不重复）
        if self.current_session["last_detection_time"]:
            time_diff = (now - self.current_session["last_detection_time"]).total_seconds()
            if time_diff < 5:
                return
        
        detection = {
            "type": item_type,
            "time": now.isoformat(),
            "pixel_count": pixel_count,
            "map": self.current_session.get("map"),
            "spawn_point": self.current_session.get("spawn_point")
        }
        
        self.current_session["items"].append(detection)
        self.current_session["last_detection_time"] = now
        
        # 保存到文件
        self._save_detection(detection)
        
        print(f"[检测到] {item_type} - {pixel_count} 像素")
    
    def _save_detection(self, detection):
        """保存检测记录"""
        try:
            detection_file = self.data_dir / "item_detections.json"
            
            # 读取现有记录
            detections = []
            if detection_file.exists():
                with open(detection_file, 'r', encoding='utf-8') as f:
                    detections = json.load(f)
            
            # 添加新记录
            detections.append(detection)
            
            # 保存
            with open(detection_file, 'w', encoding='utf-8') as f:
                json.dump(detections, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[保存错误] {e}")
    
    def get_current_session(self):
        """获取当前会话状态"""
        return self.current_session.copy()
    
    def end_session(self, survived=True, profit=0):
        """结束当前会话"""
        if not self.current_session["active"]:
            return {"status": "error", "message": "没有活跃的会话"}
        
        # 保存会话记录
        session_record = {
            "datetime": self.current_session["start_time"].isoformat(),
            "map": self.current_session.get("map", "未知"),
            "mode": "机密",  # 可以从检测中获取
            "zone": self.current_session.get("spawn_point", "未知"),
            "items": ";".join([item["type"] for item in self.current_session["items"]]),
            "profit": profit,
            "survived": survived,
            "item_count": len(self.current_session["items"])
        }
        
        # 保存到CSV
        self._save_session_record(session_record)
        
        # 重置会话
        self.current_session["active"] = False
        
        return {"status": "success", "message": "会话已结束", "record": session_record}
    
    def _save_session_record(self, record):
        """保存会话记录到CSV"""
        import pandas as pd
        
        csv_file = self.data_dir / f"auto_records_{datetime.now().strftime('%Y%m%d')}.csv"
        
        try:
            # 转换为DataFrame
            df_new = pd.DataFrame([record])
            
            # 如果文件存在，追加；否则创建新文件
            if csv_file.exists():
                df_existing = pd.read_csv(csv_file, encoding='utf-8-sig')
                df = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df = df_new
            
            # 保存
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"[已保存] 会话记录到 {csv_file}")
            
        except Exception as e:
            print(f"[保存会话错误] {e}")


# 全局监控器实例
_monitor_instance = None

def get_monitor():
    """获取监控器实例（单例）"""
    global _monitor_instance
    if _monitor_instance is None:
        data_dir = Path.home() / "Documents" / "DeltaTool"
        _monitor_instance = GameMonitor(data_dir)
    return _monitor_instance
