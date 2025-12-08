import streamlit as st

# 1. 页面配置 (这行代码必须放在第一行)
st.set_page_config(page_title="三角洲战术终端", layout="wide", initial_sidebar_state="collapsed")

# 2. 隐藏多余菜单
hide_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.block-container {padding-top: 1rem; padding-left: 1rem; padding-right: 1rem;}
</style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# 3. 标题区
st.title("🚀 三角洲战术终端")
st.caption("当前状态：系统在线 | 数据源：实时模拟")

# 4. 核心功能区 (两列布局)
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛠️ 战备配置")
    # 下拉菜单：选择难度
    difficulty = st.selectbox("选择地图难度", ["普通模式", "哈夫币模式", "绝密行动"])
    # 滑动条：选择护甲
    armor_level = st.slider("护甲等级 (3-6级)", 3, 6, 5)
    # 数字输入：子弹价格
    ammo_price = st.number_input("单发子弹价格 (哈夫币)", value=850, step=50)

with col2:
    st.subheader("📊 收益预测")
    
    # 模拟数据
    loot_prob = {"普通模式": "20%", "哈夫币模式": "45%", "绝密行动": "80%"}
    avg_revenue = {"普通模式": 150000, "哈夫币模式": 450000, "绝密行动": 1200000}
    armor_cost = {3: 20000, 4: 50000, 5: 120000, 6: 250000}
    
    # 计算逻辑
    total_cost = armor_cost[armor_level] + (ammo_price * 180) # 假设带180发子弹
    expected_profit = avg_revenue[difficulty] - total_cost

    # 结果显示 (之前报错就是这里断了，现在是完整的)
    st.metric(label="预计出金率", value=loot_prob[difficulty])
    st.metric(label="预估净利润", value=f"{expected_profit:,} 哈夫币", delta="盈利" if expected_profit > 0 else "亏损")

# 5. 底部提示
st.info("💡 战术建议：检测到您选择了高风险地图，建议携带 5 级以上护甲以保证生存率。")
