import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# 1. 页面配置 (必须在第一行)
st.set_page_config(
    page_title="三角洲战术终端", 
    page_icon="🎯",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. 自定义样式
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.block-container {padding-top: 1rem; padding-left: 1rem; padding-right: 1rem;}
.stat-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 1.5rem;
    border-radius: 15px;
    border: 1px solid #333;
    margin-bottom: 1rem;
}
.highlight {
    color: #FFD700;
    font-weight: bold;
}
.map-card {
    background: #1e1e2e;
    border-radius: 10px;
    padding: 1rem;
    border: 1px solid #444;
    transition: all 0.3s;
}
.map-card:hover {
    border-color: #FFD700;
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
}
</style>
""", unsafe_allow_html=True)

# ==================== 数据定义 ====================

# 地图数据
MAPS_DATA = {
    "哈维斯特庄园": {
        "description": "农场地图，适合中远距离作战，物资分布均匀",
        "size": "中型",
        "difficulty": "简单",
        "player_count": "8-12人",
        "loot_zones": ["农舍", "谷仓", "水塔", "拖拉机库", "主屋", "地窖"],
        "hot_zones": ["主屋", "地窖"],
        "extract_points": ["北部公路", "东侧农田", "西部树林"],
    },
    "矿山": {
        "description": "矿洞地图，近距离CQB为主，高价值物资集中",
        "size": "小型",
        "difficulty": "中等",
        "player_count": "6-10人",
        "loot_zones": ["矿洞入口", "深处矿道", "控制室", "运输站", "仓库", "矿井底部"],
        "hot_zones": ["控制室", "矿井底部"],
        "extract_points": ["矿洞出口", "运输通道", "紧急出口"],
    },
    "港口": {
        "description": "码头地图，多层建筑复杂，适合团队配合",
        "size": "大型",
        "difficulty": "困难",
        "player_count": "12-16人",
        "loot_zones": ["集装箱区", "码头", "办公楼", "仓储区", "船坞", "海关大楼"],
        "hot_zones": ["海关大楼", "船坞"],
        "extract_points": ["货运码头", "办公区后门", "海上撤离点"],
    },
    "研究所": {
        "description": "科研设施，高价值物资集中，PVP激烈",
        "size": "中型",
        "difficulty": "困难",
        "player_count": "10-14人",
        "loot_zones": ["实验室", "服务器室", "休息区", "地下层", "停机坪", "档案室"],
        "hot_zones": ["服务器室", "地下层"],
        "extract_points": ["直升机停机坪", "地下通道", "正门"],
    },
    "边境哨站": {
        "description": "开阔地形，狙击手天堂，远距离交战",
        "size": "大型",
        "difficulty": "中等",
        "player_count": "10-14人",
        "loot_zones": ["哨站主楼", "瞭望塔", "军营", "弹药库", "车库", "通讯塔"],
        "hot_zones": ["弹药库", "通讯塔"],
        "extract_points": ["边境关卡", "山路", "直升机"],
    },
}

# 物资出货概率数据
LOOT_PROBABILITY = {
    "哈维斯特庄园": {
        "高级武器": 12, "中级武器": 35, "低级武器": 53,
        "高级护甲": 8, "中级护甲": 28, "低级护甲": 40,
        "医疗物资": 45, "弹药": 80, "钥匙卡": 3, "情报文件": 5,
    },
    "矿山": {
        "高级武器": 18, "中级武器": 40, "低级武器": 42,
        "高级护甲": 12, "中级护甲": 32, "低级护甲": 35,
        "医疗物资": 50, "弹药": 75, "钥匙卡": 6, "情报文件": 8,
    },
    "港口": {
        "高级武器": 22, "中级武器": 43, "低级武器": 35,
        "高级护甲": 18, "中级护甲": 38, "低级护甲": 30,
        "医疗物资": 55, "弹药": 85, "钥匙卡": 10, "情报文件": 12,
    },
    "研究所": {
        "高级武器": 28, "中级武器": 42, "低级武器": 30,
        "高级护甲": 22, "中级护甲": 40, "低级护甲": 28,
        "医疗物资": 60, "弹药": 70, "钥匙卡": 15, "情报文件": 18,
    },
    "边境哨站": {
        "高级武器": 20, "中级武器": 38, "低级武器": 42,
        "高级护甲": 15, "中级护甲": 35, "低级护甲": 35,
        "医疗物资": 48, "弹药": 90, "钥匙卡": 8, "情报文件": 10,
    },
}

# 战备推荐数据
LOADOUT_RECOMMENDATIONS = {
    "哈维斯特庄园": {
        "主武器": ["M4A1", "AK-47", "SCAR-L"],
        "副武器": ["格洛克18", "沙漠之鹰"],
        "推荐护甲": "4级防弹衣",
        "推荐配件": ["4倍镜", "消音器", "垂直握把", "扩容弹匣"],
        "必带物资": ["止血带x2", "医疗包x1", "止痛药x3"],
        "战术建议": "保持中远距离交战，利用农舍和谷仓作为掩体。主屋和地窖是高价值区，但竞争激烈。",
        "风险等级": "低",
        "预估成本": 85000,
    },
    "矿山": {
        "主武器": ["MP5", "UMP45", "P90"],
        "副武器": ["霰弹枪", "格洛克18"],
        "推荐护甲": "5级防弹衣 + 头盔",
        "推荐配件": ["红点瞄具", "战术手电", "扩容弹匣", "激光指示器"],
        "必带物资": ["止血带x3", "医疗包x2", "闪光弹x2"],
        "战术建议": "近距离CQB为主，注意听脚步声，清角要仔细。控制室有高价值物资但敌人密集。",
        "风险等级": "中",
        "预估成本": 120000,
    },
    "港口": {
        "主武器": ["M4A1", "AK-47", "HK416"],
        "副武器": ["MP5", "格洛克18"],
        "推荐护甲": "5级防弹衣 + 头盔",
        "推荐配件": ["全息瞄具", "消音器", "战术握把", "扩容弹匣"],
        "必带物资": ["止血带x3", "医疗包x2", "烟雾弹x2"],
        "战术建议": "注意多层建筑的高低差，集装箱区适合伏击。海关大楼价值最高但风险极大。",
        "风险等级": "高",
        "预估成本": 150000,
    },
    "研究所": {
        "主武器": ["MP7", "Vector", "P90"],
        "副武器": ["格洛克18", "沙漠之鹰"],
        "推荐护甲": "6级防弹衣 + 头盔",
        "推荐配件": ["红点瞄具", "消音器", "激光指示器", "扩容弹匣"],
        "必带物资": ["止血带x4", "医疗包x2", "肾上腺素x1"],
        "战术建议": "高价值区域竞争激烈，建议组队前往。服务器室必争之地，注意撤离路线规划。",
        "风险等级": "极高",
        "预估成本": 200000,
    },
    "边境哨站": {
        "主武器": ["狙击步枪", "DMR", "SCAR-H"],
        "副武器": ["M4A1", "MP5"],
        "推荐护甲": "5级防弹衣",
        "推荐配件": ["8倍镜", "消音器", "两脚架", "扩容弹匣"],
        "必带物资": ["止血带x2", "医疗包x1", "烟雾弹x3"],
        "战术建议": "开阔地形适合远距离狙击，瞭望塔视野好但容易被集火。弹药库物资丰富。",
        "风险等级": "中",
        "预估成本": 130000,
    },
}

# 收益数据
REVENUE_DATA = {
    "普通模式": {"出金率": "20%", "平均收益": 150000, "风险": "低"},
    "哈夫币模式": {"出金率": "45%", "平均收益": 450000, "风险": "中"},
    "绝密行动": {"出金率": "80%", "平均收益": 1200000, "风险": "极高"},
}

# 护甲成本
ARMOR_COST = {3: 20000, 4: 50000, 5: 120000, 6: 250000}

# ==================== 侧边栏导航 ====================

with st.sidebar:
    st.markdown("## 🎯 三角洲战术终端")
    st.markdown("---")
    
    menu = st.radio(
        "功能菜单",
        ["🏠 战备配置", "📊 地图出货统计", "🎒 装备推荐", "📈 数据管理", "📋 游戏记录"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📅 系统信息")
    st.info(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("数据来源: 社区统计 + 个人记录")
    
    st.markdown("---")
    st.markdown("### 🎮 快捷统计")
    if 'total_games' not in st.session_state:
        st.session_state.total_games = 0
        st.session_state.total_profit = 0
    st.metric("总局数", st.session_state.total_games)
    st.metric("累计收益", f"{st.session_state.total_profit:,}")

# ==================== 功能模块 ====================

if menu == "🏠 战备配置":
    st.title("🚀 战备配置与收益预测")
    st.caption("当前状态：系统在线 | 实时计算")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛠️ 配置参数")
        selected_map = st.selectbox("选择地图", list(MAPS_DATA.keys()))
        difficulty = st.selectbox("选择模式", list(REVENUE_DATA.keys()))
        armor_level = st.slider("护甲等级 (3-6级)", 3, 6, 5)
        ammo_price = st.number_input("单发子弹价格 (哈夫币)", value=850, step=50)
        ammo_count = st.number_input("携带弹药数量", value=180, step=30)
        
        # 额外成本
        extra_cost = st.number_input("其他成本 (医疗/投掷物等)", value=15000, step=1000)
    
    with col2:
        st.subheader("📊 收益预测")
        
        # 计算逻辑
        total_cost = ARMOR_COST[armor_level] + (ammo_price * ammo_count) + extra_cost
        revenue_info = REVENUE_DATA[difficulty]
        expected_revenue = revenue_info["平均收益"]
        expected_profit = expected_revenue - total_cost
        
        # 显示结果
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("预计出金率", revenue_info["出金率"])
            st.metric("平均收益", f"{expected_revenue:,} 哈夫币")
        with col_b:
            st.metric("总成本", f"{total_cost:,} 哈夫币")
            delta_color = "normal" if expected_profit > 0 else "inverse"
            st.metric("预估净利润", f"{expected_profit:,}", 
                     delta="盈利" if expected_profit > 0 else "亏损",
                     delta_color=delta_color)
        
        # 风险提示
        st.markdown("---")
        risk = revenue_info["风险"]
        if risk == "极高":
            st.error(f"⚠️ 风险等级: {risk} - 建议携带最高级装备，组队行动！")
        elif risk == "中":
            st.warning(f"⚡ 风险等级: {risk} - 注意战术配合，规划撤离路线")
        else:
            st.success(f"✅ 风险等级: {risk} - 适合练习和积累资源")
    
    # 地图信息
    st.markdown("---")
    st.subheader(f"🗺️ {selected_map} - 地图信息")
    map_info = MAPS_DATA[selected_map]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**描述:** {map_info['description']}")
        st.markdown(f"**地图大小:** {map_info['size']}")
    with col2:
        st.markdown(f"**难度:** {map_info['difficulty']}")
        st.markdown(f"**玩家数:** {map_info['player_count']}")
    with col3:
        st.markdown(f"**热点区域:** {', '.join(map_info['hot_zones'])}")
        st.markdown(f"**撤离点:** {', '.join(map_info['extract_points'])}")

elif menu == "📊 地图出货统计":
    st.title("📊 地图出货概率统计")
    
    # 地图选择
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_map = st.selectbox("选择地图", list(MAPS_DATA.keys()), key="loot_map")
        
        # 地图信息卡片
        map_info = MAPS_DATA[selected_map]
        st.markdown(f"""
        ### 🗺️ {selected_map}
        - **描述:** {map_info['description']}
        - **大小:** {map_info['size']}
        - **难度:** {map_info['difficulty']}
        - **玩家数:** {map_info['player_count']}
        """)
        
        st.markdown("### 📍 刷新点位")
        for zone in map_info['loot_zones']:
            if zone in map_info['hot_zones']:
                st.markdown(f"- 🔥 **{zone}** (热点)")
            else:
                st.markdown(f"- {zone}")
    
    with col2:
        # 出货概率图表
        loot_data = LOOT_PROBABILITY[selected_map]
        df = pd.DataFrame({
            "物资类型": list(loot_data.keys()),
            "出货概率(%)": list(loot_data.values())
        })
        
        # 柱状图
        fig = px.bar(
            df, 
            x="物资类型", 
            y="出货概率(%)",
            color="出货概率(%)",
            color_continuous_scale="YlOrRd",
            title=f"{selected_map} - 物资出货概率分布"
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 雷达图
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=list(loot_data.values()),
            theta=list(loot_data.keys()),
            fill='toself',
            name=selected_map,
            line_color='#FFD700'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title="物资分布雷达图",
            height=400
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # 所有地图对比
    st.markdown("---")
    st.subheader("📈 各地图出货对比")
    
    compare_items = st.multiselect(
        "选择要对比的物资类型",
        list(LOOT_PROBABILITY["哈维斯特庄园"].keys()),
        default=["高级武器", "高级护甲", "钥匙卡"]
    )
    
    if compare_items:
        compare_data = []
        for map_name, loot in LOOT_PROBABILITY.items():
            for item in compare_items:
                compare_data.append({
                    "地图": map_name,
                    "物资": item,
                    "概率(%)": loot[item]
                })
        
        df_compare = pd.DataFrame(compare_data)
        fig_compare = px.bar(
            df_compare,
            x="地图",
            y="概率(%)",
            color="物资",
            barmode="group",
            title="各地图物资出货概率对比"
        )
        fig_compare.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_compare, use_container_width=True)

elif menu == "🎒 装备推荐":
    st.title("🎒 最佳战备推荐")
    
    selected_map = st.selectbox("选择目标地图", list(LOADOUT_RECOMMENDATIONS.keys()))
    loadout = LOADOUT_RECOMMENDATIONS[selected_map]
    
    # 风险等级显示
    risk = loadout["风险等级"]
    if risk == "极高":
        st.error(f"⚠️ 风险等级: {risk}")
    elif risk == "高":
        st.warning(f"⚡ 风险等级: {risk}")
    elif risk == "中":
        st.info(f"📊 风险等级: {risk}")
    else:
        st.success(f"✅ 风险等级: {risk}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔫 主武器推荐")
        for weapon in loadout["主武器"]:
            st.markdown(f"- {weapon}")
        
        st.markdown("### 🔫 副武器推荐")
        for weapon in loadout["副武器"]:
            st.markdown(f"- {weapon}")
    
    with col2:
        st.markdown("### 🛡️ 防护装备")
        st.info(loadout["推荐护甲"])
        
        st.markdown("### 🔧 推荐配件")
        for attachment in loadout["推荐配件"]:
            st.markdown(f"- {attachment}")
    
    with col3:
        st.markdown("### 💊 必带物资")
        for item in loadout["必带物资"]:
            st.markdown(f"- {item}")
        
        st.markdown("### 💰 预估成本")
        st.metric("总成本", f"{loadout['预估成本']:,} 哈夫币")
    
    # 战术建议
    st.markdown("---")
    st.markdown("### 💡 战术建议")
    st.success(loadout["战术建议"])
    
    # 地图所有装备对比
    st.markdown("---")
    st.subheader("📊 各地图推荐装备对比")
    
    comparison_data = []
    for map_name, rec in LOADOUT_RECOMMENDATIONS.items():
        comparison_data.append({
            "地图": map_name,
            "主武器": rec["主武器"][0],
            "护甲": rec["推荐护甲"],
            "风险": rec["风险等级"],
            "预估成本": f"{rec['预估成本']:,}"
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)

elif menu == "📈 数据管理":
    st.title("📈 数据管理")
    
    tab1, tab2, tab3 = st.tabs(["📁 文件上传", "✏️ 手动录入", "📊 我的数据"])
    
    with tab1:
        st.markdown("### 上传出货记录")
        st.markdown("支持 CSV 格式，包含列: 地图, 物资, 数量, 日期")
        
        uploaded_file = st.file_uploader("选择 CSV 文件", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df)
            st.success("✅ 数据导入成功！")
            
            if st.button("保存到本地"):
                st.session_state.imported_data = df
                st.success("数据已保存！")
    
    with tab2:
        st.markdown("### 手动录入出货记录")
        
        col1, col2 = st.columns(2)
        with col1:
            record_map = st.selectbox("地图", list(MAPS_DATA.keys()), key="record_map")
            record_mode = st.selectbox("模式", list(REVENUE_DATA.keys()), key="record_mode")
            record_zone = st.selectbox("刷新点", MAPS_DATA[record_map]["loot_zones"])
        
        with col2:
            record_item = st.text_input("获得物资")
            record_value = st.number_input("物资价值 (哈夫币)", value=0, step=1000)
            record_survived = st.checkbox("成功撤离", value=True)
        
        if st.button("添加记录", type="primary"):
            if 'game_records' not in st.session_state:
                st.session_state.game_records = []
            
            st.session_state.game_records.append({
                "日期": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "地图": record_map,
                "模式": record_mode,
                "刷新点": record_zone,
                "物资": record_item,
                "价值": record_value,
                "撤离": "✅" if record_survived else "❌"
            })
            
            st.session_state.total_games += 1
            if record_survived:
                st.session_state.total_profit += record_value
            
            st.success(f"✅ 已记录: 在 {record_map} 的 {record_zone} 获得 {record_item}")
            st.balloons()
    
    with tab3:
        st.markdown("### 我的游戏记录")
        
        if 'game_records' in st.session_state and st.session_state.game_records:
            df_records = pd.DataFrame(st.session_state.game_records)
            st.dataframe(df_records, use_container_width=True, hide_index=True)
            
            # 统计
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总局数", len(df_records))
            with col2:
                survived = len(df_records[df_records["撤离"] == "✅"])
                st.metric("存活率", f"{survived/len(df_records)*100:.1f}%")
            with col3:
                total_value = df_records["价值"].sum()
                st.metric("总收益", f"{total_value:,}")
            
            # 下载
            csv = df_records.to_csv(index=False).encode('utf-8')
            st.download_button("📥 导出数据", csv, "game_records.csv", "text/csv")
        else:
            st.info("暂无记录，请先手动录入或上传数据")

elif menu == "📋 游戏记录":
    st.title("📋 游戏记录与统计")
    
    if 'game_records' in st.session_state and st.session_state.game_records:
        df = pd.DataFrame(st.session_state.game_records)
        
        # 统计概览
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总局数", len(df))
        with col2:
            survived = len(df[df["撤离"] == "✅"])
            st.metric("存活率", f"{survived/len(df)*100:.1f}%")
        with col3:
            st.metric("总收益", f"{df['价值'].sum():,}")
        with col4:
            st.metric("场均收益", f"{df['价值'].mean():,.0f}")
        
        st.markdown("---")
        
        # 地图分布
        col1, col2 = st.columns(2)
        with col1:
            fig_map = px.pie(df, names="地图", title="地图游玩分布")
            fig_map.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_map, use_container_width=True)
        
        with col2:
            fig_mode = px.pie(df, names="模式", title="模式分布")
            fig_mode.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_mode, use_container_width=True)
        
        # 详细记录
        st.markdown("### 📋 详细记录")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📝 暂无游戏记录")
        st.markdown("请前往 **数据管理** 页面添加记录")

# ==================== 页脚 ====================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>🎮 三角洲战术终端 v2.0 | Built with Streamlit | 数据仅供参考</p>",
    unsafe_allow_html=True
)
