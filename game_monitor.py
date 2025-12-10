"""
游戏监控模块 - 集成到Streamlit应用
实时监控游戏画面，识别出生点和高价值物品
支持OCR识别降落地点和结算画面
"""

import mss
import cv2
import numpy as np
import time
import os
import threading
from datetime import datetime
from pathlib import Path
import pandas as pd
import json

# 尝试导入OCR
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# 尝试导入语音引擎
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️ pyttsx3未安装，语音播报功能不可用。安装方法: pip install pyttsx3")


class GameMonitor:
    """游戏监控器"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 截图和事件保存目录
        self.save_dir = self.data_dir / 'game_records'
        self.save_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / 'game_events.csv'
        
        self.is_running = False
        self.monitor_thread = None
        
        # 当前会话状态
        self.current_session = {
            "active": False,
            "map": None,
            "spawn_point": None,
            "death_location": None,  # 死亡位置
            "items": [],
            "start_time": None,
            "last_detection_time": None,
            "spawn_detected": False,  # 是否已检测出生点
            "currency": 0,  # 货币
            "inventory_value": 0  # 装备库存价值
        }
        
        # OCR引擎
        self.reader = None
        if OCR_AVAILABLE:
            try:
                print("正在初始化 AI 视觉引擎...")
                self.reader = easyocr.Reader(['ch_sim', 'en'])
                print("✅ OCR引擎初始化成功")
            except Exception as e:
                print(f"⚠️ OCR引擎初始化失败: {e}")
        
        # 屏幕捕获可用性
        self.screen_capture_available = False
        try:
            with mss.mss() as test_sct:
                _ = test_sct.monitors
            self.screen_capture_available = True
            print("✅ 屏幕捕获系统就绪")
        except Exception as e:
            print(f"⚠️ 屏幕捕获不可用: {e}")
        
        # 语音播报引擎
        self.tts_engine = None
        self.tts_enabled = False
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                # 设置语音属性
                self.tts_engine.setProperty('rate', 150)  # 语速
                self.tts_engine.setProperty('volume', 0.9)  # 音量
                self.tts_enabled = True
                print("✅ 语音播报系统就绪")
            except Exception as e:
                print(f"⚠️ 语音引擎初始化失败: {e}")
    
    def speak(self, text):
        """语音播报"""
        if self.tts_enabled and self.tts_engine:
            try:
                # 在新线程中播报，避免阻塞主监控
                threading.Thread(target=self._speak_async, args=(text,), daemon=True).start()
            except Exception as e:
                print(f"[语音播报错误] {e}")
    
    def _speak_async(self, text):
        """异步语音播报"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"[语音播报错误] {e}")
    
    def start_monitoring(self):
        """启动监控"""
        if not self.screen_capture_available:
            return {"status": "error", "message": "屏幕捕获功能不可用"}
        
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
    
    def get_status(self):
        """获取监控状态"""
        return {
            "is_running": self.is_running,
            "current_session": self.current_session
        }
    
    def _monitor_loop(self):
        """监控主循环"""
        print("✅ 游戏监控已启动")
        
        # 在监控线程内创建mss实例（线程安全）
        sct = None
        try:
            sct = mss.mss()
        except Exception as e:
            print(f"[错误] 无法创建屏幕捕获实例: {e}")
            return
        
        try:
            while self.is_running:
                try:
                    # 捕获屏幕
                    screenshot = self._capture_screen(sct)
                    
                    if screenshot is not None:
                        # 分析游戏状态
                        self._analyze_screen(screenshot)
                    
                    # 每1.5秒检测一次
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f"[监控错误] {e}")
                    time.sleep(3)
        finally:
            # 确保关闭mss实例
            if sct:
                sct.close()
    
    def _capture_screen(self, sct):
        """捕获屏幕"""
        try:
            # 捕获主屏幕
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            
            # 转换为numpy数组
            img = np.array(screenshot)
            # MSS截图是BGRA，转换为BGR
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
        except Exception as e:
            print(f"[截图错误] {e}")
            return None
    
    def _analyze_screen(self, img):
        """分析屏幕内容"""
        if not self.reader:
            return
        
        try:
            # OCR识别屏幕文字
            result = self.reader.readtext(img, detail=0)
            text_content = " ".join(result)
            
            # 检测淘汰画面
            if "致命一击" in text_content and "来自" in text_content:
                self._handle_death_screen(text_content, img)
                time.sleep(10)  # 死亡后暂停监控
                return
            
            # 检测结算画面
            if "行动结束" in text_content or "撤离成功" in text_content or "失败撤离" in text_content:
                self._handle_settlement_screen(text_content, img)
                time.sleep(30)  # 结算后暂停监控
                return
            
            # 检测游戏开始（前30秒检测出生点）
            if not self.current_session["active"]:
                # 检测是否进入游戏
                map_places = ["行政区", "游客中心", "水泥厂", "长弓溪谷", "零号大坝"]
                for place in map_places:
                    if place in text_content:
                        self._start_session(place)
                        break
            
            # 如果在游戏中且未检测出生点
            if (self.current_session["active"] and 
                not self.current_session["spawn_detected"] and
                self.current_session["start_time"]):
                elapsed = (datetime.now() - self.current_session["start_time"]).total_seconds()
                if elapsed < 30:  # 前30秒检测出生点
                    self._detect_spawn_point(text_content)
                    
        except Exception as e:
            print(f"[分析错误] {e}")
    
    def _start_session(self, map_name):
        """开始新会话"""
        self.current_session = {
            "active": True,
            "map": map_name,
            "spawn_point": None,
            "items": [],
            "start_time": datetime.now(),
            "last_detection_time": datetime.now(),
            "spawn_detected": False
        }
        print(f"🎮 检测到进入游戏: {map_name}")
        self.speak(f"检测到进入{map_name}")
    
    def _detect_spawn_point(self, text_content):
        """检测出生点"""
        spawn_keywords = ["优势方", "劣势方", "军营", "栏杆", "水泥厂", "后山"]
        for keyword in spawn_keywords:
            if keyword in text_content:
                self.current_session["spawn_point"] = keyword
                self.current_session["spawn_detected"] = True
                print(f"📍 识别出生点: {keyword}")
                self.speak(f"出生点识别：{keyword}")
                break
    
    def _handle_death_screen(self, text_content, img):
        """处理淘汰画面"""
        # 尝试识别武器
        weapon = "未知武器"
        possible_weapons = ["M4A1", "AK-12", "HK416", "P90", "AWM", "突击步枪", "冲锋枪", "狙击枪"]
        for w in possible_weapons:
            if w in text_content:
                weapon = w
                break
        
        # 识别死亡地点（从地图中获取）
        death_location = self._detect_death_location(text_content)
        self.current_session["death_location"] = death_location
        
        print(f"💀 检测到淘汰画面！武器: {weapon} | 位置: {death_location}")
        self.speak(f"检测到淘汰画面，被{weapon}击倒")
        self._save_event("淘汰", f"被 {weapon} 击倒 @ {death_location}", img)
        
        # 保存死亡位置到热力图数据
        self._save_death_location(death_location)
        
        # 结束当前会话
        self.current_session["active"] = False
    
    def _handle_settlement_screen(self, text_content, img):
        """处理结算画面"""
        survived = "撤离成功" in text_content
        status = "✅ 存活" if survived else "❌ 阵亡"
        
        # OCR识别货币和装备价值
        currency, inventory_value = self._extract_currency_and_value(text_content, img)
        self.current_session["currency"] = currency
        self.current_session["inventory_value"] = inventory_value
        
        print(f"🏁 检测到对局结束! 状态: {status}")
        print(f"💰 货币: {currency:,} | 装备价值: {inventory_value:,}")
        
        # 语音播报结果
        total_value = currency + inventory_value
        if survived:
            self.speak(f"撤离成功，本局入账{total_value}哈夫币")
        else:
            self.speak(f"任务失败，损失{total_value}哈夫币")
        
        self._save_event("对局结束", f"{status} | 货币:{currency} 装备:{inventory_value}", img)
        
        # 保存对局记录到主数据文件
        self._save_game_record(survived)
        
        # 结束当前会话
        self.current_session["active"] = False
    
    def _save_event(self, event_type, details, img):
        """保存事件到CSV和截图"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        img_name = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{event_type}.png"
        save_path = self.save_dir / img_name
        
        # 保存截图
        cv2.imwrite(str(save_path), img)
        
        # 保存到CSV
        new_data = pd.DataFrame([[timestamp, event_type, details, img_name]], 
                                columns=['Time', 'Type', 'Details', 'Image'])
        
        hdr = not self.data_file.exists()
        new_data.to_csv(self.data_file, mode='a', header=hdr, index=False)
        print(f"✅ [记录] {event_type}: {details}")
    
    def _extract_currency_and_value(self, text_content, img):
        """从结算画面提取货币和装备价值"""
        import re
        
        currency = 0
        inventory_value = 0
        
        try:
            # 在图像上半部分寻找数字（结算信息通常在上方）
            height = img.shape[0]
            top_half = img[:height//2, :]
            
            # OCR识别上半部分
            result = self.reader.readtext(top_half, detail=1) if self.reader else []
            
            for (bbox, text, prob) in result:
                # 清理文本中的逗号和空格
                clean_text = text.replace(',', '').replace(' ', '').replace('，', '')
                
                # 匹配大数字（货币通常>10000）
                numbers = re.findall(r'\d+', clean_text)
                for num_str in numbers:
                    num = int(num_str)
                    if num > 10000:  # 假设货币>1万
                        if currency == 0:
                            currency = num
                        elif inventory_value == 0:
                            inventory_value = num
                            break
        except Exception as e:
            print(f"[货币识别错误] {e}")
        
        return currency, inventory_value
    
    def _detect_death_location(self, text_content):
        """检测死亡地点"""
        # 常见地点关键词
        locations = [
            "行政区", "游客中心", "水泥厂", "长弓溪谷", "零号大坝",
            "军营", "栏杆", "后山", "主要电站", "渔村", "旅馆"
        ]
        
        for loc in locations:
            if loc in text_content:
                return loc
        
        return "未知位置"
    
    def _save_death_location(self, location):
        """保存死亡位置到热力图数据"""
        if location == "未知位置":
            return
        
        try:
            death_heatmap_file = self.data_dir / "death_heatmap.json"
            
            # 读取现有数据
            if death_heatmap_file.exists():
                with open(death_heatmap_file, 'r', encoding='utf-8') as f:
                    heatmap_data = json.load(f)
            else:
                heatmap_data = {}
            
            # 记录地图和位置
            map_name = self.current_session.get("map", "未知")
            if map_name not in heatmap_data:
                heatmap_data[map_name] = {}
            
            if location not in heatmap_data[map_name]:
                heatmap_data[map_name][location] = 0
            
            heatmap_data[map_name][location] += 1
            
            # 保存
            with open(death_heatmap_file, 'w', encoding='utf-8') as f:
                json.dump(heatmap_data, f, ensure_ascii=False, indent=2)
            
            print(f"📍 死亡位置已记录: {map_name} - {location}")
        except Exception as e:
            print(f"[热力图保存错误] {e}")
    
    def _save_game_record(self, survived):
        """保存对局记录"""
        if not self.current_session.get("start_time"):
            return
        
        # 计算总收益（货币 + 装备价值）
        total_profit = self.current_session.get("currency", 0) + self.current_session.get("inventory_value", 0)
        
        record = {
            "datetime": self.current_session["start_time"].isoformat(),
            "map": self.current_session.get("map", "未知"),
            "mode": "机密",
            "zone": self.current_session.get("spawn_point", ""),
            "items": ";".join(self.current_session.get("items", [])),
            "profit": total_profit,
            "survived": survived
        }
        
        # 保存到主记录文件
        csv_file = self.data_dir / "game_records_export.csv"
        df = pd.DataFrame([record])
        
        hdr = not csv_file.exists()
        df.to_csv(csv_file, mode='a', header=hdr, index=False)
        
        print(f"✅ 对局记录已保存: {record['map']} - {'存活' if survived else '阵亡'} - 收益:{total_profit:,}")


# 主函数 - 用于独立测试
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # 设置数据目录
    data_dir = Path.home() / "Documents" / "DeltaTool"
    
    print("=== 三角洲战术独立监控模式 ===")
    print(f"数据目录: {data_dir}")
    
    # 创建监控器
    monitor = GameMonitor(str(data_dir))
    
    # 启动监控
    result = monitor.start_monitoring()
    print(result["message"])
    
    if result["status"] == "success":
        print("\n按 Ctrl+C 停止监控...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止监控...")
            monitor.stop_monitoring()
            print("已停止")
