"""
OCR识别引擎
负责识别游戏画面中的文字和物品
"""

import re
from PIL import Image
import numpy as np

# OCR引擎选择（可选）
OCR_ENGINE = "paddleocr"  # paddleocr / easyocr / tesseract

# 尝试导入OCR库
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class OCREngine:
    """OCR识别引擎"""
    
    # 游戏相关关键词
    MAP_KEYWORDS = {
        "大坝": ["大坝", "DAM", "水坝"],
        "长弓": ["长弓", "LONGBOW", "森林"],
        "巴克什": ["巴克什", "BAKSHI", "沙漠"],
        "航天": ["航天", "SPACE", "发射"],
        "监狱": ["监狱", "PRISON", "牢房"],
    }
    
    MODE_KEYWORDS = {
        "普通": ["普通", "NORMAL", "普通模式"],
        "机密": ["机密", "SECRET", "机密模式"],
        "绝密": ["绝密", "TOP SECRET", "绝密模式"],
        "自适应": ["自适应", "ADAPTIVE", "自适应模式"],
    }
    
    # 物品关键词和价值
    ITEM_KEYWORDS = {
        # 武器
        "M4A1": {"keywords": ["M4A1", "M4"], "value": 80000, "category": "武器"},
        "AK-47": {"keywords": ["AK-47", "AK47", "AK"], "value": 75000, "category": "武器"},
        "HK416": {"keywords": ["HK416", "HK"], "value": 120000, "category": "武器"},
        "SCAR-H": {"keywords": ["SCAR", "SCAR-H"], "value": 150000, "category": "武器"},
        "MP5": {"keywords": ["MP5"], "value": 45000, "category": "武器"},
        "P90": {"keywords": ["P90"], "value": 65000, "category": "武器"},
        "Vector": {"keywords": ["Vector", "VECTOR"], "value": 70000, "category": "武器"},
        "狙击步枪": {"keywords": ["狙击", "AWM", "M24", "98K"], "value": 200000, "category": "武器"},
        "霰弹枪": {"keywords": ["霰弹", "870", "S686"], "value": 35000, "category": "武器"},
        
        # 护甲
        "6级护甲": {"keywords": ["6级", "六级", "LV6"], "value": 250000, "category": "护甲"},
        "5级护甲": {"keywords": ["5级", "五级", "LV5"], "value": 120000, "category": "护甲"},
        "4级护甲": {"keywords": ["4级", "四级", "LV4"], "value": 50000, "category": "护甲"},
        "3级护甲": {"keywords": ["3级", "三级", "LV3"], "value": 20000, "category": "护甲"},
        
        # 头盔
        "6级头盔": {"keywords": ["6级头盔", "六级头"], "value": 180000, "category": "头盔"},
        "5级头盔": {"keywords": ["5级头盔", "五级头"], "value": 80000, "category": "头盔"},
        "4级头盔": {"keywords": ["4级头盔", "四级头"], "value": 35000, "category": "头盔"},
        
        # 医疗
        "医疗包": {"keywords": ["医疗包", "大药"], "value": 15000, "category": "医疗"},
        "止血带": {"keywords": ["止血带", "绷带"], "value": 5000, "category": "医疗"},
        "止痛药": {"keywords": ["止痛药", "止痛"], "value": 8000, "category": "医疗"},
        
        # 特殊物品
        "钥匙卡": {"keywords": ["钥匙卡", "钥匙", "门卡"], "value": 500000, "category": "特殊"},
        "情报文件": {"keywords": ["情报", "文件", "档案"], "value": 300000, "category": "特殊"},
        "芯片": {"keywords": ["芯片", "CPU"], "value": 400000, "category": "特殊"},
        
        # 配件
        "4倍镜": {"keywords": ["4倍镜", "4X", "ACOG"], "value": 25000, "category": "配件"},
        "8倍镜": {"keywords": ["8倍镜", "8X"], "value": 45000, "category": "配件"},
        "消音器": {"keywords": ["消音器", "消音"], "value": 30000, "category": "配件"},
        "扩容弹匣": {"keywords": ["扩容", "弹匣"], "value": 15000, "category": "配件"},
    }
    
    # 游戏状态关键词
    STATUS_KEYWORDS = {
        "撤离成功": ["撤离成功", "成功撤离", "EXTRACTED", "提取成功"],
        "阵亡": ["阵亡", "死亡", "KILLED", "KIA", "你已阵亡"],
        "结算": ["结算", "收益", "获得", "REWARD"],
    }
    
    def __init__(self):
        self.ocr = None
        self.init_ocr()
    
    def init_ocr(self):
        """初始化OCR引擎"""
        if PADDLE_AVAILABLE and OCR_ENGINE == "paddleocr":
            try:
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang="ch",
                    show_log=False,
                    use_gpu=False
                )
                print("使用 PaddleOCR 引擎")
                return
            except Exception as e:
                print(f"PaddleOCR 初始化失败: {e}")
        
        if EASYOCR_AVAILABLE:
            try:
                self.ocr = easyocr.Reader(['ch_sim', 'en'], gpu=False)
                print("使用 EasyOCR 引擎")
                return
            except Exception as e:
                print(f"EasyOCR 初始化失败: {e}")
        
        if TESSERACT_AVAILABLE:
            print("使用 Tesseract 引擎")
            return
        
        print("警告: 没有可用的OCR引擎，请安装 paddleocr / easyocr / pytesseract")
    
    def recognize(self, image):
        """
        识别游戏画面
        
        Args:
            image: PIL.Image 或 numpy array
        
        Returns:
            dict: 识别结果 {
                "map": 地图名,
                "mode": 模式,
                "items": [物品列表],
                "profit": 收益,
                "status": 状态,
                "raw_text": 原始文本
            }
        """
        if image is None:
            return None
        
        # 转换图像格式
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # OCR识别
        raw_text = self.extract_text(img_array)
        
        if not raw_text:
            return None
        
        # 解析结果
        result = {
            "map": self.detect_map(raw_text),
            "mode": self.detect_mode(raw_text),
            "items": self.detect_items(raw_text),
            "profit": self.detect_profit(raw_text),
            "status": self.detect_status(raw_text),
            "raw_text": raw_text
        }
        
        return result
    
    def extract_text(self, image):
        """提取图像中的文字"""
        try:
            if PADDLE_AVAILABLE and isinstance(self.ocr, PaddleOCR):
                result = self.ocr.ocr(image, cls=True)
                if result and result[0]:
                    texts = [line[1][0] for line in result[0]]
                    return " ".join(texts)
            
            elif EASYOCR_AVAILABLE and hasattr(self.ocr, 'readtext'):
                result = self.ocr.readtext(image)
                texts = [item[1] for item in result]
                return " ".join(texts)
            
            elif TESSERACT_AVAILABLE:
                if isinstance(image, np.ndarray):
                    image = Image.fromarray(image)
                text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                return text
            
            return ""
            
        except Exception as e:
            print(f"OCR识别错误: {e}")
            return ""
    
    def detect_map(self, text):
        """检测地图"""
        text_upper = text.upper()
        for map_name, keywords in self.MAP_KEYWORDS.items():
            for keyword in keywords:
                if keyword.upper() in text_upper:
                    return map_name
        return None
    
    def detect_mode(self, text):
        """检测模式"""
        text_upper = text.upper()
        for mode_name, keywords in self.MODE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.upper() in text_upper:
                    return mode_name
        return None
    
    def detect_items(self, text):
        """检测物品"""
        items = []
        text_upper = text.upper()
        
        for item_name, info in self.ITEM_KEYWORDS.items():
            for keyword in info["keywords"]:
                if keyword.upper() in text_upper:
                    items.append({
                        "name": item_name,
                        "value": info["value"],
                        "category": info["category"],
                        "count": 1
                    })
                    break
        
        return items
    
    def detect_profit(self, text):
        """检测收益数值"""
        # 匹配数字（可能带逗号）
        patterns = [
            r'收益[：:]\s*(\d{1,3}(?:,\d{3})*|\d+)',
            r'获得[：:]\s*(\d{1,3}(?:,\d{3})*|\d+)',
            r'(\d{1,3}(?:,\d{3})*)\s*哈夫币',
            r'总计[：:]\s*(\d{1,3}(?:,\d{3})*|\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    return int(value_str)
                except:
                    pass
        
        return 0
    
    def detect_status(self, text):
        """检测游戏状态"""
        text_upper = text.upper()
        for status, keywords in self.STATUS_KEYWORDS.items():
            for keyword in keywords:
                if keyword.upper() in text_upper:
                    return status
        return None
    
    def recognize_region(self, image, region):
        """识别指定区域"""
        if isinstance(image, Image.Image):
            cropped = image.crop((
                region["left"],
                region["top"],
                region["left"] + region["width"],
                region["top"] + region["height"]
            ))
            return self.recognize(cropped)
        return None


class ImagePreprocessor:
    """图像预处理器 - 提高OCR识别率"""
    
    @staticmethod
    def preprocess(image):
        """预处理图像"""
        if isinstance(image, np.ndarray):
            img = Image.fromarray(image)
        else:
            img = image.copy()
        
        # 转灰度
        img = img.convert('L')
        
        # 增强对比度
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # 二值化
        threshold = 128
        img = img.point(lambda p: 255 if p > threshold else 0)
        
        return img
    
    @staticmethod
    def sharpen(image):
        """锐化图像"""
        from PIL import ImageFilter
        return image.filter(ImageFilter.SHARPEN)
    
    @staticmethod
    def denoise(image):
        """降噪"""
        from PIL import ImageFilter
        return image.filter(ImageFilter.MedianFilter(size=3))


if __name__ == "__main__":
    # 测试
    engine = OCREngine()
    
    # 测试文本识别
    test_text = "地图: 大坝 模式: 机密 收益: 350,000 哈夫币"
    print(f"测试地图检测: {engine.detect_map(test_text)}")
    print(f"测试模式检测: {engine.detect_mode(test_text)}")
    print(f"测试收益检测: {engine.detect_profit(test_text)}")
