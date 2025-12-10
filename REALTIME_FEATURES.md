# 🎮 实时记录功能说明

## 功能概述

现在你的三角洲工具已经支持**实时记录游戏数据**！桌面客户端会自动识别并记录：
- 🎯 **出生地（spawn point）**
- 📦 **收获物品**
- 💰 **撤出价值**
- 📊 **实时上传到Web分析页面**

## 使用流程

### 1. 启动桌面客户端

```bash
cd desktop
python main.py
```

### 2. 开始新会话

在桌面客户端中：
1. 切换到"📊 实时会话"标签
2. 点击"🎮 开始新会话"按钮
3. 开始游戏

### 3. 自动识别与记录

客户端会自动：
- 识别地图和模式
- 检测出生地
- 实时识别拾取的物品
- 计算累计价值

### 4. 结束会话

游戏结束时：
- **自动检测**：识别到"撤离成功"或"阵亡"会自动保存
- **手动操作**：点击"✅ 成功撤离"或"❌ 阵亡"按钮

### 5. Web端查看

打开 Streamlit 应用：
```bash
streamlit run app.py
```

在侧边栏选择"💻 实时会话"查看：
- 实时游戏状态
- 当前价值显示
- 物品收集列表
- 价值趋势图

## 数据存储位置

所有数据保存在：
```
C:\Users\你的用户名\Documents\DeltaTool\
├── live_session.json          # 实时会话数据
├── game_records.json          # 历史记录
├── game_records_export.csv    # CSV导出（供Streamlit读取）
└── stats.json                 # 统计数据
```

## 实时会话数据结构

```json
{
  "spawn_point": "发电站",      // 出生地
  "map": "大坝",                // 地图
  "mode": "机密",               // 模式
  "items_collected": [          // 收集的物品
    {
      "name": "M4A1",
      "value": 80000,
      "category": "武器",
      "time": "2025-12-09T14:30:15"
    }
  ],
  "total_value": 350000,        // 总价值
  "start_time": "2025-12-09T14:15:00",
  "status": "进行中"            // 状态
}
```

## 功能特性

### 🔄 实时同步
- Web页面每2秒自动刷新
- 无需手动操作，数据实时更新

### 📊 数据可视化
- 按类别统计物品价值
- 累计价值趋势图
- 收集时间线

### 💾 自动保存
- 每次添加物品自动保存
- 结束会话自动导出CSV
- 历史记录永久保存

### 📈 统计分析
- 总局数、存活率
- 总收益、场均收益
- 地图/模式分布
- 物品收集分析

## API 接口

### DataManager 主要方法

```python
# 开始新会话
start_new_session(map_name=None, mode=None, spawn_point=None)

# 更新出生地
update_session_spawn(spawn_point)

# 更新地图和模式
update_session_map_mode(map_name=None, mode=None)

# 添加物品
add_item_to_session(item_name, item_value, category="其他")

# 结束会话
end_session(survived=True, final_value=None)

# 获取当前会话
get_current_session()
```

## OCR识别要点

### 支持的OCR引擎
1. **PaddleOCR**（推荐）- 中文识别最佳
2. **EasyOCR** - 多语言支持
3. **Tesseract** - 开源免费
4. **百度OCR** - 在线API（需配置）

### 识别内容
- ✅ 地图名称（大坝、长弓、巴克什等）
- ✅ 游戏模式（普通、机密、绝密等）
- ✅ 物品名称（武器、护甲、医疗等）
- ✅ 价值数字
- ✅ 游戏状态（撤离成功、阵亡）

### 提高识别率
1. 游戏画质设置为**高**或**极高**
2. 分辨率建议 **1920x1080** 或更高
3. 使用 **PaddleOCR** 引擎
4. 确保界面文字清晰可见

## 常见问题

### Q: 实时会话数据不显示？
**A:** 
1. 确认桌面客户端已启动
2. 检查是否点击了"开始新会话"
3. 查看数据文件是否存在（Documents/DeltaTool/）

### Q: OCR识别不准确？
**A:**
1. 切换到 PaddleOCR 引擎
2. 提高游戏画质和分辨率
3. 手动框选识别区域

### Q: Web页面数据延迟？
**A:**
- 页面每2秒自动刷新
- 可以手动点击"立即刷新"按钮
- 检查数据文件是否正常保存

### Q: 如何重置会话？
**A:**
在桌面客户端点击"开始新会话"会自动重置

## 更新日志

### v1.1 - 2025-12-09
- ✨ 新增实时会话功能
- ✨ 支持出生地记录
- ✨ 实时物品识别和价值计算
- ✨ Web端实时显示
- ✨ 自动CSV导出
- ✨ 增强OCR识别准确度

## 技术架构

```
Desktop Client (PyQt6)
    ↓ OCR识别
    ↓ 数据处理
DataManager
    ↓ JSON保存
    ↓ CSV导出
Documents/DeltaTool/
    ↓ 文件读取
Streamlit App
    ↓ 实时显示
用户界面
```

## 下一步计划

- [ ] 支持多人组队数据同步
- [ ] 添加语音提示
- [ ] 云端数据备份
- [ ] 手机端查看
- [ ] AI智能推荐装备

---

**享受你的实时数据记录体验！** 🎮✨
