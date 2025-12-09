"""
游戏检测模块
检测游戏是否运行及窗口状态
"""

import win32gui
import win32process
import psutil
import time


class GameDetector:
    """游戏检测器"""
    
    # 游戏进程名和窗口标题
    GAME_PROCESS_NAMES = [
        "DeltaForce.exe",
        "deltaforce.exe",
        "Delta Force.exe",
        "三角洲行动.exe",
    ]
    
    GAME_WINDOW_TITLES = [
        "DeltaForce",
        "Delta Force",
        "三角洲行动",
        "Delta Force: Hawk Ops",
    ]
    
    def __init__(self):
        self.game_process = None
        self.game_hwnd = None
        self.last_check_time = 0
        self.check_interval = 2  # 检测间隔（秒）
    
    def is_game_running(self):
        """检测游戏是否运行"""
        current_time = time.time()
        
        # 节流检测频率
        if current_time - self.last_check_time < self.check_interval:
            return self.game_process is not None
        
        self.last_check_time = current_time
        
        # 通过进程名检测
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] in self.GAME_PROCESS_NAMES:
                    self.game_process = proc
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self.game_process = None
        return False
    
    def find_game_window(self):
        """查找游戏窗口"""
        def enum_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                for game_title in self.GAME_WINDOW_TITLES:
                    if game_title.lower() in title.lower():
                        results.append(hwnd)
                        return True
            return True
        
        results = []
        win32gui.EnumWindows(enum_callback, results)
        
        if results:
            self.game_hwnd = results[0]
            return self.game_hwnd
        
        self.game_hwnd = None
        return None
    
    def get_game_window_info(self):
        """获取游戏窗口信息"""
        if self.game_hwnd is None:
            self.find_game_window()
        
        if self.game_hwnd is None:
            return None
        
        try:
            rect = win32gui.GetWindowRect(self.game_hwnd)
            title = win32gui.GetWindowText(self.game_hwnd)
            
            return {
                "hwnd": self.game_hwnd,
                "title": title,
                "left": rect[0],
                "top": rect[1],
                "width": rect[2] - rect[0],
                "height": rect[3] - rect[1],
                "is_foreground": win32gui.GetForegroundWindow() == self.game_hwnd
            }
        except:
            return None
    
    def is_game_focused(self):
        """检测游戏是否在前台"""
        if self.game_hwnd is None:
            self.find_game_window()
        
        if self.game_hwnd is None:
            return False
        
        return win32gui.GetForegroundWindow() == self.game_hwnd
    
    def get_game_state(self):
        """获取游戏状态"""
        is_running = self.is_game_running()
        window_info = self.get_game_window_info()
        
        if not is_running:
            return {
                "status": "not_running",
                "message": "游戏未运行"
            }
        
        if window_info is None:
            return {
                "status": "running_no_window",
                "message": "游戏进程运行中，但未找到窗口"
            }
        
        if window_info["is_foreground"]:
            return {
                "status": "focused",
                "message": "游戏运行中（前台）",
                "window": window_info
            }
        else:
            return {
                "status": "background",
                "message": "游戏运行中（后台）",
                "window": window_info
            }
    
    def wait_for_game(self, timeout=60):
        """等待游戏启动"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_game_running():
                return True
            time.sleep(1)
        
        return False


class GameStateMonitor:
    """游戏状态监控器"""
    
    # 游戏内状态（通过画面识别判断）
    STATES = {
        "main_menu": "主菜单",
        "map_select": "选择地图",
        "loading": "加载中",
        "in_game": "游戏中",
        "extraction": "撤离结算",
        "death": "阵亡结算",
        "inventory": "仓库/背包",
        "unknown": "未知"
    }
    
    def __init__(self):
        self.current_state = "unknown"
        self.state_history = []
    
    def update_state(self, new_state):
        """更新状态"""
        if new_state != self.current_state:
            self.state_history.append({
                "from": self.current_state,
                "to": new_state,
                "time": time.time()
            })
            self.current_state = new_state
    
    def get_current_state(self):
        """获取当前状态"""
        return {
            "state": self.current_state,
            "name": self.STATES.get(self.current_state, "未知")
        }
    
    def detect_state_from_screen(self, ocr_result):
        """
        从OCR结果判断游戏状态
        
        Args:
            ocr_result: OCR识别结果
        """
        if not ocr_result or not ocr_result.get("raw_text"):
            return "unknown"
        
        text = ocr_result["raw_text"].upper()
        
        # 检测关键词判断状态
        if any(kw in text for kw in ["撤离成功", "EXTRACTED", "成功撤离"]):
            return "extraction"
        
        if any(kw in text for kw in ["阵亡", "死亡", "KILLED", "你已阵亡"]):
            return "death"
        
        if any(kw in text for kw in ["选择地图", "大坝", "长弓", "巴克什", "航天", "监狱"]):
            if any(kw in text for kw in ["开始", "匹配", "进入"]):
                return "map_select"
        
        if any(kw in text for kw in ["加载中", "LOADING"]):
            return "loading"
        
        if any(kw in text for kw in ["仓库", "背包", "装备"]):
            return "inventory"
        
        # 如果识别到地图和模式，可能在游戏中
        if ocr_result.get("map") and ocr_result.get("mode"):
            return "in_game"
        
        return "unknown"


if __name__ == "__main__":
    # 测试
    detector = GameDetector()
    
    print("检测游戏状态...")
    state = detector.get_game_state()
    print(f"状态: {state}")
    
    if detector.is_game_running():
        window = detector.get_game_window_info()
        if window:
            print(f"窗口: {window}")
