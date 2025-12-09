# 三角洲战术终端 - 桌面客户端 v1.1

## 🎮 快速开始

### 一键安装（推荐）
双击运行 `install.bat`，按提示完成安装。

### 启动程序
双击运行 `run.bat` 或在命令行执行：
```bash
python main.py
```

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| **F9** | 手动截图 |
| **F10** | 开始/停止监控 |
| **F11** | 识别当前画面 |
| **Ctrl+S** | 快速保存记录 |

## 功能特性

### 🖥️ 屏幕捕获
- 自动检测游戏窗口
- 实时屏幕截图
- 支持全屏/窗口模式
- 全局热键支持

### 🔍 OCR识别
- 识别地图、模式
- 识别物品和收益
- 识别游戏状态（撤离/阵亡）
- 自动记录游戏结果

### 📊 数据统计
- 自动记录游戏数据
- 本地数据存储
- 导出CSV/同步网页版
- 会话统计

### 🔔 系统托盘
- 最小化到托盘运行
- 托盘右键菜单
- 消息通知

## 详细安装说明

### 1. 安装Python
需要 Python 3.10 或更高版本

### 2. 安装依赖
```bash
cd desktop
pip install -r requirements.txt
```

### 3. 安装OCR引擎（选择其一）

#### 推荐：PaddleOCR（中文识别效果最好）
```bash
pip install paddlepaddle paddleocr
```

#### 备选：EasyOCR（安装简单）
```bash
pip install easyocr
```

#### 备选：Tesseract
1. 下载安装 [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. 添加到系统PATH
3. 安装Python包：`pip install pytesseract`

### 4. 运行程序
```bash
python main.py
```

## 使用说明

### 基本操作
1. 双击 `run.bat` 启动程序
2. 启动游戏《三角洲行动》
3. 点击「开始监控」或按 **F10**
4. 程序会自动识别游戏画面并记录数据
5. 关闭窗口时，程序最小化到系统托盘

### 手动操作
- **F9**：手动截图
- **F11**：对当前截图进行OCR识别
- **Ctrl+S**：快速保存当前游戏记录

### 自动功能
- 自动检测游戏进程启动/退出
- 自动识别游戏结算画面
- 自动记录撤离/阵亡结果
- 自动保存数据（每60秒）

### 数据管理
- 数据存储在 `文档/DeltaTool/` 目录
- 支持导出CSV格式
- 支持同步到网页版

## 注意事项

1. **管理员权限**：全局热键功能需要管理员权限运行
2. **游戏检测**：确保游戏窗口标题包含 "DeltaForce" 或 "三角洲"
3. **OCR准确率**：识别准确率受游戏画质和分辨率影响
4. **托盘图标**：关闭窗口后程序在托盘运行，双击恢复

## 文件结构

```
desktop/
├── main.py           # 主程序入口
├── screen_capture.py # 屏幕捕获模块
├── ocr_engine.py     # OCR识别引擎
├── data_manager.py   # 数据管理模块
├── game_detector.py  # 游戏检测模块
├── requirements.txt  # 依赖列表
├── install.bat       # 一键安装脚本
├── run.bat           # 启动脚本
└── README.md         # 说明文档
```

## 开发计划

- [x] 基础框架搭建
- [x] 屏幕捕获功能
- [x] OCR引擎集成
- [x] 数据存储管理
- [x] 游戏状态自动检测
- [x] 热键支持
- [x] 系统托盘
- [x] 自动保存
- [ ] 实时物品识别优化
- [ ] 数据同步API
- [ ] 打包为exe

## 网页版

在线分析工具：https://delta-tool-fe3emrkp2gxagxpdeuuwcd.streamlit.app/

## 版本历史

### v1.0.0 (2024-12)
- 初始版本
- 基础屏幕捕获和OCR功能
- PyQt6 GUI界面
