from PIL import Image
from ocr_engine import OCREngine
import pprint
import sys

def main(path):
    try:
        img = Image.open(path)
    except Exception as e:
        print("无法打开图片:", path, e)
        return
    try:
        ocr = OCREngine()
        res = ocr.recognize(img)
    except Exception as e:
        print("OCR 引擎出错:", e)
        return

    print("=== RAW TEXT ===")
    print(res.get("raw_text", ""))
    print("\n=== PARSED RESULT ===")
    pprint.pprint(res)

if __name__ == '__main__':
    # 如果没有提供参数，自动查找当前目录下的 png/jpg 文件并使用第一个
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        import glob
        candidates = glob.glob('*.png') + glob.glob('*.jpg') + glob.glob('*.jpeg')
        if len(candidates) == 0:
            print('当前目录没有找到 PNG/JPG 图片。请把截图放到此目录或用完整路径作为参数。')
            print('目录内容如下:')
            import os
            for f in os.listdir('.'):
                print('  ', f)
            sys.exit(2)
        img_path = candidates[0]
        print(f"未指定图片，自动使用: {img_path}")

    main(img_path)
