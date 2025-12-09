"""
屏幕捕获模块
负责捕获游戏画面
"""

import mss
import mss.tools
from PIL import Image
import numpy as np
import win32gui
import win32con
import win32ui
from ctypes import windll
import time


class ScreenCapture:
    """屏幕捕获类"""
    
    def __init__(self):
        self.sct = mss.mss()
        self.latest_screenshot = None
        self.game_window_title = "DeltaForce"  # 游戏窗口标题
        self.game_hwnd = None
        
    def find_game_window(self):
        """查找游戏窗口"""
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if self.game_window_title.lower() in title.lower():
                    hwnds.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        
        if hwnds:
            self.game_hwnd = hwnds[0]
            return True
        return False
    
    def get_game_window_rect(self):
        """获取游戏窗口区域"""
        if self.game_hwnd is None:
            self.find_game_window()
        
        if self.game_hwnd:
            try:
                rect = win32gui.GetWindowRect(self.game_hwnd)
                return {
                    "left": rect[0],
                    "top": rect[1],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1]
                }
            except:
                pass
        return None
    
    def capture(self, region=None):
        """
        捕获屏幕
        
        Args:
            region: 截图区域 {"left", "top", "width", "height"}，默认全屏
        
        Returns:
            PIL.Image 对象
        """
        try:
            if region is None:
                # 尝试捕获游戏窗口
                region = self.get_game_window_rect()
            
            if region is None:
                # 捕获整个主显示器
                region = self.sct.monitors[1]
            
            # 截图
            screenshot = self.sct.grab(region)
            
            # 转换为PIL Image
            img = Image.frombytes(
                "RGB",
                (screenshot.width, screenshot.height),
                screenshot.rgb
            )
            
            self.latest_screenshot = img
            return img
            
        except Exception as e:
            print(f"截图失败: {e}")
            return None
    
    def capture_region(self, x, y, width, height):
        """捕获指定区域"""
        region = {
            "left": x,
            "top": y,
            "width": width,
            "height": height
        }
        return self.capture(region)
    
    def capture_game_window(self):
        """只捕获游戏窗口"""
        if self.find_game_window():
            rect = self.get_game_window_rect()
            if rect:
                return self.capture(rect)
        return None
    
    def get_latest(self):
        """获取最近一次截图"""
        return self.latest_screenshot
    
    def save_screenshot(self, filepath):
        """保存截图"""
        if self.latest_screenshot:
            self.latest_screenshot.save(filepath)
            return True
        return False


class RegionSelector:
    """区域选择器 - 用于用户选择识别区域"""
    
    def __init__(self):
        self.selected_region = None
    
    def select(self):
        """
        让用户框选区域
        TODO: 实现拖拽选择功能
        """
        pass


if __name__ == "__main__":
    # 测试
    sc = ScreenCapture()
    
    # 全屏截图
    img = sc.capture()
    if img:
        print(f"截图成功: {img.size}")
        img.save("test_screenshot.png")
    
    # 查找游戏窗口
    if sc.find_game_window():
        print(f"找到游戏窗口: {sc.game_hwnd}")
        game_img = sc.capture_game_window()
        if game_img:
            game_img.save("test_game_screenshot.png")
    else:
        print("未找到游戏窗口")
