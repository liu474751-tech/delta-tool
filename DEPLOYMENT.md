# 🚀 Streamlit Cloud 部署指南

## 📋 部署步骤

### 1️⃣ 访问 Streamlit Cloud
打开: https://share.streamlit.io/

### 2️⃣ 登录 GitHub 账号
使用你的 GitHub 账号 `liu474751-tech` 登录

### 3️⃣ 创建新应用
点击 "New app" 按钮

### 4️⃣ 配置部署参数
填写以下信息:

- **Repository**: `liu474751-tech/delta-tool`
- **Branch**: `main`
- **Main file path**: `app.py`
- **App URL** (可选): `delta-tool` 或自定义名称

### 5️⃣ 高级设置 (Advanced settings)
- **Python version**: `3.11` (已在 .python-version 中指定)
- **Requirements file**: `requirements.txt` (自动检测)
- **System packages**: `packages.txt` (自动检测，OpenCV需要)

### 6️⃣ 部署
点击 "Deploy!" 按钮

等待3-5分钟，Streamlit Cloud会自动:
1. ✅ 安装系统依赖 (libgl1-mesa-glx, libglib2.0-0)
2. ✅ 创建 Python 3.11 环境
3. ✅ 安装所有 Python 包
4. ✅ 启动应用

### 7️⃣ 访问你的应用
部署完成后，你会得到一个类似这样的URL:
```
https://delta-tool.streamlit.app
```
或
```
https://liu474751-tech-delta-tool-app-xyz123.streamlit.app
```

## 🔧 部署配置文件说明

### requirements.txt
```txt
streamlit>=1.28.0       # Web框架
pandas>=2.0.0           # 数据处理
plotly>=5.18.0          # 图表
opencv-python>=4.8.0    # 图像识别
mss>=9.0.0              # 屏幕捕获
numpy>=1.24.0           # 数值计算
pillow>=10.0.0          # 图片处理
```

### packages.txt
```txt
libgl1-mesa-glx         # OpenCV所需的OpenGL库
libglib2.0-0            # GLib库支持
```

### .streamlit/config.toml
```toml
[theme]
primaryColor = "#FFD700"           # 金色主题
backgroundColor = "#0E1117"        # 深色背景
secondaryBackgroundColor = "#1A1A2E"
textColor = "#FAFAFA"

[server]
headless = true                    # 无头模式
enableCORS = false
enableXsrfProtection = false
```

### .python-version
```
python-3.11
```

## ⚠️ 注意事项

### 1. OpenCV 依赖
- 已添加 `libgl1-mesa-glx` 到 `packages.txt`
- 这是 OpenCV 在 Linux 环境运行所必需的

### 2. 屏幕捕获限制
- Streamlit Cloud 是云端环境，**无法捕获用户本地屏幕**
- 游戏监控功能只能在本地运行
- 但历史数据分析、地图工具等功能完全可用

### 3. 数据存储
- Streamlit Cloud 是无状态的
- 每次重启会清空数据
- 建议用户下载 CSV 备份

### 4. 解决方案
可以在 `app.py` 中添加环境检测:

```python
import os

# 检测是否在云端环境
IS_CLOUD = os.getenv("STREAMLIT_SHARING_MODE") is not None

if menu == "💻 实时监控":
    if IS_CLOUD:
        st.warning("⚠️ 游戏监控功能仅支持本地运行")
        st.info("""
        如需使用实时监控功能，请在本地运行:
        ```bash
        git clone https://github.com/liu474751-tech/delta-tool.git
        cd delta-tool
        pip install -r requirements.txt
        streamlit run app.py
        ```
        """)
    else:
        # 正常的监控功能代码
        ...
```

## 📊 功能支持情况

### ✅ 完全支持 (云端)
- 🏠 战备配置
- 💰 战备计算器
- 🎖️ 干员指南
- 🗺️ 战术地图
- 📊 物资分析
- 🎒 装备推荐
- 📈 数据管理 (导入/导出)
- 📋 游戏记录 (查看)
- 📉 深度分析
- 🤖 智能推荐

### ⚠️ 部分支持
- 💻 实时监控 (仅本地可用)

## 🔄 更新应用

当你推送新代码到 GitHub:
```bash
git add .
git commit -m "update: xxx"
git push origin main
```

Streamlit Cloud 会**自动检测并重新部署**，无需手动操作！

## 🐛 常见问题

### Q: 部署失败怎么办？
**A:** 查看部署日志 (Deploy logs)，通常是依赖问题:
- 检查 `requirements.txt` 版本兼容性
- 确认 `packages.txt` 系统依赖正确

### Q: OpenCV 报错？
**A:** 确保 `packages.txt` 包含:
```txt
libgl1-mesa-glx
libglib2.0-0
```

### Q: 应用很慢？
**A:** Streamlit Cloud 免费版资源有限:
- 1 GB RAM
- 1 CPU core
- 考虑优化数据加载逻辑

### Q: 数据会丢失吗？
**A:** 是的，云端是无状态的:
- 用户需要手动上传数据文件
- 或使用外部数据库 (Supabase, MongoDB等)

## 🎯 推荐配置

对于最佳体验:
1. **云端**: 用于数据分析、地图查询、战术规划
2. **本地**: 用于实时游戏监控、数据采集

## 📝 后续优化建议

### 1. 添加数据库支持
使用 Supabase 或 MongoDB Atlas (免费)存储用户数据

### 2. 用户认证
添加简单的密码保护功能

### 3. API 集成
创建 REST API 让本地客户端上传数据到云端

### 4. WebSocket
实现真正的实时同步功能

---

**准备好了吗？** 现在就去 https://share.streamlit.io/ 部署你的应用吧！🚀
