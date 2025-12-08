import streamlit as st

# ⚠️ 关键修正：这行代码必须放在所有代码的最前面，否则必白屏！
st.set_page_config(page_title="三角洲战术终端", layout="wide", initial_sidebar_state="collapsed")

# CSS 黑客代码：隐藏 Streamlit 自带的红条和菜单，让它看起来像你网站的原生组件
hide_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.block-container {padding-top: 1rem; padding-left: 1rem; padding-right: 1rem;}
</style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- 界面开始 ---
st.title("🚀 三角洲战术终端")
st.caption("当前状态：系统在线 | 数据源：实时计算")

# 简单的交互区域
col1, col2 = st.columns(2)
with col1:
    difficulty = st.selectbox("选择地图难度", ["普通", "哈夫币模式", "绝密行动"])
    armor_level = st.slider("护甲等级", 3, 6, 5)

with col2:
    # 简单的模拟数据
    loot_prob = {"普通": "20%", "哈夫币模式": "45%", "绝密行动": "80%"}
    st.metric(label="预计出金率", value=loot_prob[difficulty])
    
    cost_map = {3: 20000, 4: 50000, 5: 120000, 6: 250000}
    st.metric(label="推荐整备预算", value
