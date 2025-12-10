快速说明 - 使用百度在线 OCR

1) 获取 API Key / Secret Key
   - 打开百度智能云文字识别产品页：https://cloud.baidu.com/product/ocr
   - 注册/登录 -> 创建应用 -> 获取 `API Key` 和 `Secret Key`（通用文字识别）

2) 填写配置文件
   - 打开 `desktop/ocr_config.json`，将 `api_key` 和 `secret_key` 填入对应字段并保存。

3) 运行测试
   - 将测试截图放到 `desktop` 目录（命名例如 `test_screenshot.png`），然后运行：
     ```powershell
     cd 'C:\Users\这个名字花五块\Desktop\delta-tool\desktop'
     python .\test_ocr.py .\test_screenshot.png
     ```
   - 脚本会在没有本地 OCR 引擎时自动调用百度在线 OCR，并打印 `=== RAW TEXT ===` 与 `=== PARSED RESULT ===`。

注意
- 百度在线 OCR 需要网络连接并可能有免费额度限制。请保管好你的 API Key/Secret 不要泄露。
- 如果你愿意，我也可以改用其他在线 OCR（腾讯/阿里/OCR.space），或者把 Key 存到 `data_manager` 的安全位置。