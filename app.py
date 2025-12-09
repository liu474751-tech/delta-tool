import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import random

# 1. 页面配置 (必须在第一行)
st.set_page_config(
    page_title="三角洲战术终端 v3.0", 
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

# ==================== 新增: 干员数据 ====================

OPERATORS_DATA = {
    "突击型": {
        "麦小雯": {
            "技能": "闪电突击 - 短时间内提升移动速度和换弹速度",
            "被动": "枪械后坐力降低10%",
            "适合地图": ["矿山", "研究所", "港口"],
            "推荐武器": ["冲锋枪", "突击步枪"],
            "评分": 9.2,
            "难度": "中等",
            "特点": "高机动性，适合CQB突破"
        },
        "威龙": {
            "技能": "战术无人机 - 侦察敌人位置",
            "被动": "瞄准速度提升15%",
            "适合地图": ["哈维斯特庄园", "边境哨站", "港口"],
            "推荐武器": ["突击步枪", "狙击步枪"],
            "评分": 8.8,
            "难度": "简单",
            "特点": "信息获取强，团队核心"
        },
        "疾风": {
            "技能": "翻滚闪避 - 快速位移躲避伤害",
            "被动": "冲刺速度提升20%",
            "适合地图": ["矿山", "研究所"],
            "推荐武器": ["冲锋枪", "霰弹枪"],
            "评分": 8.5,
            "难度": "困难",
            "特点": "极限操作空间大"
        },
    },
    "工程型": {
        "比特": {
            "技能": "机械蜘蛛 - 自爆腐蚀敌人，增加受到伤害",
            "被动": "陷阱放置速度提升25%",
            "适合地图": ["研究所", "矿山", "港口"],
            "推荐武器": ["冲锋枪", "突击步枪"],
            "评分": 8.7,
            "难度": "中等",
            "特点": "控场能力强，S6新干员"
        },
        "老太": {
            "技能": "加固板 - 强化门窗防护",
            "被动": "防护装备耐久+15%",
            "适合地图": ["哈维斯特庄园", "边境哨站"],
            "推荐武器": ["突击步枪", "轻机枪"],
            "评分": 7.5,
            "难度": "简单",
            "特点": "防守专精，适合新手"
        },
    },
    "医疗型": {
        "蜂医": {
            "技能": "治疗针剂 - 快速恢复队友生命",
            "被动": "医疗物品效果+20%",
            "适合地图": ["港口", "研究所", "边境哨站"],
            "推荐武器": ["冲锋枪", "手枪"],
            "评分": 9.0,
            "难度": "简单",
            "特点": "团队续航核心"
        },
        "深蓝": {
            "技能": "肾上腺素注射 - 暂时免疫伤害",
            "被动": "自我恢复速度+30%",
            "适合地图": ["研究所", "矿山"],
            "推荐武器": ["突击步枪", "冲锋枪"],
            "评分": 8.3,
            "难度": "中等",
            "特点": "生存能力强"
        },
    },
    "侦察型": {
        "无名": {
            "技能": "隐身披风 - 短时间隐形",
            "被动": "脚步声降低50%",
            "适合地图": ["港口", "研究所", "哈维斯特庄园"],
            "推荐武器": ["冲锋枪", "近战武器"],
            "评分": 8.9,
            "难度": "困难",
            "特点": "偷袭专精，高风险高回报"
        },
        "哈夫克": {
            "技能": "脑机接口 - 标记敌人",
            "被动": "敌人标记持续时间+5秒",
            "适合地图": ["边境哨站", "哈维斯特庄园"],
            "推荐武器": ["狙击步枪", "DMR"],
            "评分": 8.6,
            "难度": "中等",
            "特点": "远距离信息战"
        },
    },
}

# 武器市场价格数据 (模拟交易行价格)
WEAPONS_MARKET = {
    "突击步枪": {
        "M4A1": {"基础价": 45000, "改装价": 85000, "弹药消耗": 800},
        "AK-47": {"基础价": 38000, "改装价": 72000, "弹药消耗": 750},
        "HK416": {"基础价": 52000, "改装价": 98000, "弹药消耗": 850},
        "SCAR-L": {"基础价": 48000, "改装价": 88000, "弹药消耗": 820},
        "SCAR-H": {"基础价": 55000, "改装价": 102000, "弹药消耗": 900},
    },
    "冲锋枪": {
        "MP5": {"基础价": 25000, "改装价": 48000, "弹药消耗": 600},
        "UMP45": {"基础价": 22000, "改装价": 42000, "弹药消耗": 550},
        "P90": {"基础价": 35000, "改装价": 65000, "弹药消耗": 650},
        "MP7": {"基础价": 32000, "改装价": 58000, "弹药消耗": 620},
        "Vector": {"基础价": 40000, "改装价": 75000, "弹药消耗": 700},
    },
    "狙击步枪": {
        "AWM": {"基础价": 85000, "改装价": 150000, "弹药消耗": 1500},
        "M24": {"基础价": 65000, "改装价": 110000, "弹药消耗": 1200},
        "Kar98k": {"基础价": 58000, "改装价": 95000, "弹药消耗": 1100},
        "SVD": {"基础价": 72000, "改装价": 125000, "弹药消耗": 1350},
    },
    "霰弹枪": {
        "M870": {"基础价": 18000, "改装价": 35000, "弹药消耗": 400},
        "SPAS-12": {"基础价": 22000, "改装价": 42000, "弹药消耗": 450},
    },
    "手枪": {
        "格洛克18": {"基础价": 8000, "改装价": 15000, "弹药消耗": 300},
        "沙漠之鹰": {"基础价": 15000, "改装价": 28000, "弹药消耗": 500},
        "M1911": {"基础价": 6000, "改装价": 12000, "弹药消耗": 280},
    },
}

# 护甲市场价格
ARMOR_MARKET = {
    "3级防弹衣": {"价格": 20000, "耐久": 35, "防护": "30%"},
    "4级防弹衣": {"价格": 50000, "耐久": 45, "防护": "45%"},
    "5级防弹衣": {"价格": 120000, "耐久": 55, "防护": "60%"},
    "6级防弹衣": {"价格": 250000, "耐久": 65, "防护": "75%"},
    "3级头盔": {"价格": 15000, "耐久": 25, "防护": "25%"},
    "4级头盔": {"价格": 35000, "耐久": 35, "防护": "40%"},
    "5级头盔": {"价格": 80000, "耐久": 45, "防护": "55%"},
    "6级头盔": {"价格": 180000, "耐久": 55, "防护": "70%"},
}

# 医疗物资价格
MEDICAL_MARKET = {
    "止血带": {"价格": 2500, "效果": "止血", "数量建议": "3-4"},
    "绷带": {"价格": 1500, "效果": "小量恢复", "数量建议": "5-8"},
    "医疗包": {"价格": 8000, "效果": "大量恢复", "数量建议": "1-2"},
    "急救包": {"价格": 15000, "效果": "满血", "数量建议": "0-1"},
    "止痛药": {"价格": 3500, "效果": "临时增益", "数量建议": "2-3"},
    "肾上腺素": {"价格": 12000, "效果": "极限续命", "数量建议": "0-1"},
}

# 投掷物价格
THROWABLES_MARKET = {
    "烟雾弹": {"价格": 3000, "用途": "掩护撤离/进攻"},
    "闪光弹": {"价格": 4000, "用途": "清房必备"},
    "破片手雷": {"价格": 8000, "用途": "AOE伤害"},
    "燃烧弹": {"价格": 6000, "用途": "区域封锁"},
    "土豆雷": {"价格": 5000, "用途": "陷阱埋伏"},
}

# 赛季段位数据
RANK_DATA = {
    "青铜": {"分数范围": "0-999", "奖励": "赛季皮肤碎片x10"},
    "白银": {"分数范围": "1000-1999", "奖励": "赛季皮肤碎片x25"},
    "黄金": {"分数范围": "2000-2999", "奖励": "赛季皮肤碎片x50"},
    "铂金": {"分数范围": "3000-3999", "奖励": "赛季皮肤碎片x80"},
    "钻石": {"分数范围": "4000-4999", "奖励": "赛季专属皮肤"},
    "大师": {"分数范围": "5000-5999", "奖励": "赛季专属皮肤+称号"},
    "三角洲巅峰": {"分数范围": "6000+", "奖励": "限定皮肤+专属头像框"},
}

# ==================== 侧边栏导航 ====================

with st.sidebar:
    st.markdown("## 🎯 三角洲战术终端 v3.0")
    st.markdown("---")
    
    menu = st.radio(
        "功能菜单",
        ["🏠 战备配置", "💰 战备计算器", "🎖️ 干员指南", "📊 地图出货统计", 
         "🎰 爆率模拟器", "🎒 装备推荐", "📈 数据管理", "📋 游戏记录"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📅 系统信息")
    st.info(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("数据来源: 社区统计 + TapTap + 个人记录")
    
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
    st.caption("当前状态：系统在线 | 实时计算 | S6赛季阿萨拉")
    
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

elif menu == "💰 战备计算器":
    st.title("💰 战备价值计算器")
    st.caption("🔥 实时计算最低价战备配置 - 鼠鼠玩家必备工具！")
    
    tab1, tab2, tab3 = st.tabs(["🔫 武器计算", "🛡️ 防护计算", "📦 完整配置"])
    
    with tab1:
        st.subheader("武器市场价格查询")
        
        weapon_type = st.selectbox("武器类型", list(WEAPONS_MARKET.keys()))
        
        # 显示该类型所有武器
        weapons = WEAPONS_MARKET[weapon_type]
        
        df_weapons = pd.DataFrame([
            {
                "武器名称": name,
                "基础价格": f"{info['基础价']:,}",
                "改装价格": f"{info['改装价']:,}",
                "每发弹药": f"{info['弹药消耗']:,}",
                "30发弹匣": f"{info['弹药消耗'] * 30:,}"
            }
            for name, info in weapons.items()
        ])
        st.dataframe(df_weapons, use_container_width=True, hide_index=True)
        
        # 计算器
        st.markdown("---")
        st.subheader("💵 成本计算器")
        
        col1, col2 = st.columns(2)
        with col1:
            selected_weapon = st.selectbox("选择武器", list(weapons.keys()))
            use_modded = st.checkbox("使用改装版本", value=False)
            ammo_mags = st.slider("携带弹匣数", 1, 10, 3)
        
        with col2:
            weapon_info = weapons[selected_weapon]
            weapon_cost = weapon_info['改装价'] if use_modded else weapon_info['基础价']
            ammo_cost = weapon_info['弹药消耗'] * 30 * ammo_mags
            total = weapon_cost + ammo_cost
            
            st.metric("武器成本", f"{weapon_cost:,} 哈夫币")
            st.metric("弹药成本", f"{ammo_cost:,} 哈夫币")
            st.metric("总计", f"{total:,} 哈夫币", delta=f"{ammo_mags*30}发弹药")
    
    with tab2:
        st.subheader("防护装备价格")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🦺 防弹衣")
            for name, info in ARMOR_MARKET.items():
                if "防弹衣" in name:
                    st.markdown(f"**{name}** - 💰{info['价格']:,} | 耐久:{info['耐久']} | 防护:{info['防护']}")
        
        with col2:
            st.markdown("### 🪖 头盔")
            for name, info in ARMOR_MARKET.items():
                if "头盔" in name:
                    st.markdown(f"**{name}** - 💰{info['价格']:,} | 耐久:{info['耐久']} | 防护:{info['防护']}")
        
        st.markdown("---")
        st.subheader("计算防护装备成本")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            armor_choice = st.selectbox("选择防弹衣", [k for k in ARMOR_MARKET.keys() if "防弹衣" in k])
        with col2:
            helmet_choice = st.selectbox("选择头盔", ["不带头盔"] + [k for k in ARMOR_MARKET.keys() if "头盔" in k])
        with col3:
            armor_cost = ARMOR_MARKET[armor_choice]["价格"]
            helmet_cost = ARMOR_MARKET[helmet_choice]["价格"] if helmet_choice != "不带头盔" else 0
            st.metric("防护总成本", f"{armor_cost + helmet_cost:,}")
    
    with tab3:
        st.subheader("📦 完整战备配置计算")
        st.markdown("一键计算你的完整出装成本！")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🔫 武器配置")
            main_weapon_type = st.selectbox("主武器类型", list(WEAPONS_MARKET.keys()), key="main_type")
            main_weapon = st.selectbox("主武器", list(WEAPONS_MARKET[main_weapon_type].keys()), key="main")
            main_modded = st.checkbox("主武器改装", key="main_mod")
            main_ammo = st.slider("主武器弹匣", 1, 8, 4, key="main_ammo")
            
            secondary_type = st.selectbox("副武器类型", list(WEAPONS_MARKET.keys()), key="sec_type")
            secondary_weapon = st.selectbox("副武器", list(WEAPONS_MARKET[secondary_type].keys()), key="sec")
            secondary_ammo = st.slider("副武器弹匣", 0, 4, 2, key="sec_ammo")
        
        with col2:
            st.markdown("### 🛡️ 防护装备")
            full_armor = st.selectbox("防弹衣", list(ARMOR_MARKET.keys())[:4], key="full_armor")
            full_helmet = st.selectbox("头盔", ["不带"] + list(ARMOR_MARKET.keys())[4:], key="full_helmet")
            
            st.markdown("### 💊 医疗物资")
            med_items = {}
            for item, info in MEDICAL_MARKET.items():
                med_items[item] = st.number_input(
                    f"{item} (建议:{info['数量建议']})", 
                    0, 10, 
                    int(info['数量建议'].split('-')[0]),
                    key=f"med_{item}"
                )
        
        with col3:
            st.markdown("### 💣 投掷物")
            throw_items = {}
            for item, info in THROWABLES_MARKET.items():
                throw_items[item] = st.number_input(f"{item}", 0, 5, 0, key=f"throw_{item}")
        
        # 计算总成本
        st.markdown("---")
        st.subheader("💰 总成本统计")
        
        main_info = WEAPONS_MARKET[main_weapon_type][main_weapon]
        sec_info = WEAPONS_MARKET[secondary_type][secondary_weapon]
        
        costs = {
            "主武器": main_info['改装价'] if main_modded else main_info['基础价'],
            "主武器弹药": main_info['弹药消耗'] * 30 * main_ammo,
            "副武器": sec_info['基础价'],
            "副武器弹药": sec_info['弹药消耗'] * 30 * secondary_ammo,
            "防弹衣": ARMOR_MARKET[full_armor]["价格"],
            "头盔": ARMOR_MARKET[full_helmet]["价格"] if full_helmet != "不带" else 0,
            "医疗物资": sum(MEDICAL_MARKET[item]["价格"] * count for item, count in med_items.items()),
            "投掷物": sum(THROWABLES_MARKET[item]["价格"] * count for item, count in throw_items.items()),
        }
        
        total_cost = sum(costs.values())
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("武器+弹药", f"{costs['主武器']+costs['主武器弹药']+costs['副武器']+costs['副武器弹药']:,}")
        with col2:
            st.metric("防护装备", f"{costs['防弹衣']+costs['头盔']:,}")
        with col3:
            st.metric("消耗品", f"{costs['医疗物资']+costs['投掷物']:,}")
        with col4:
            st.metric("💰 总计", f"{total_cost:,}", delta="哈夫币")
        
        # 成本分析图
        fig = px.pie(
            values=list(costs.values()),
            names=list(costs.keys()),
            title="成本构成分析"
        )
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
        
        # 省钱建议
        if total_cost > 200000:
            st.error("⚠️ 战备成本较高！建议：降低护甲等级或使用基础武器来减少风险")
        elif total_cost > 100000:
            st.warning("💡 中等成本配置，建议选择中高级地图以获得更好收益")
        else:
            st.success("✅ 经济型配置！适合跑刀积累资金")

elif menu == "🎖️ 干员指南":
    st.title("🎖️ 干员选择指南")
    st.caption("根据地图和玩法选择最佳干员 - 数据来源: TapTap社区")
    
    tab1, tab2, tab3 = st.tabs(["📋 干员总览", "🗺️ 地图推荐", "⚔️ 阵容搭配"])
    
    with tab1:
        st.subheader("全干员数据库")
        
        for op_type, operators in OPERATORS_DATA.items():
            st.markdown(f"### {op_type}")
            
            cols = st.columns(len(operators))
            for idx, (name, info) in enumerate(operators.items()):
                with cols[idx]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                                padding: 1rem; border-radius: 10px; border: 1px solid #444;">
                        <h4 style="color: #FFD700;">👤 {name}</h4>
                        <p><b>评分:</b> ⭐ {info['评分']}/10</p>
                        <p><b>难度:</b> {info['难度']}</p>
                        <p><b>技能:</b> {info['技能']}</p>
                        <p><b>被动:</b> {info['被动']}</p>
                        <p><b>特点:</b> {info['特点']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")
    
    with tab2:
        st.subheader("根据地图选择干员")
        
        target_map = st.selectbox("选择目标地图", list(MAPS_DATA.keys()))
        
        st.markdown(f"### 🗺️ {target_map} 推荐干员")
        
        recommended = []
        for op_type, operators in OPERATORS_DATA.items():
            for name, info in operators.items():
                if target_map in info['适合地图']:
                    recommended.append({
                        "类型": op_type,
                        "干员": name,
                        "评分": info['评分'],
                        "特点": info['特点'],
                        "推荐武器": ", ".join(info['推荐武器'])
                    })
        
        if recommended:
            df_rec = pd.DataFrame(recommended).sort_values("评分", ascending=False)
            st.dataframe(df_rec, use_container_width=True, hide_index=True)
            
            # 显示最佳选择
            best = df_rec.iloc[0]
            st.success(f"🏆 最佳选择: **{best['干员']}** ({best['类型']}) - {best['特点']}")
        else:
            st.info("该地图暂无特别推荐的干员")
    
    with tab3:
        st.subheader("三人小队阵容搭配")
        st.markdown("推荐的团队配置组合")
        
        team_presets = [
            {
                "名称": "🔥 突击小队",
                "阵容": ["麦小雯(突击)", "疾风(突击)", "蜂医(医疗)"],
                "战术": "快速突破，压制敌人，适合矿山、研究所等CQB地图",
                "难度": "困难"
            },
            {
                "名称": "🛡️ 防守反击",
                "阵容": ["老太(工程)", "深蓝(医疗)", "威龙(突击)"],
                "战术": "稳扎稳打，利用加固板守点，等敌人来送",
                "难度": "简单"
            },
            {
                "名称": "👁️ 情报优先",
                "阵容": ["威龙(突击)", "哈夫克(侦察)", "蜂医(医疗)"],
                "战术": "无人机+标记掌控信息，远距离交战",
                "难度": "中等"
            },
            {
                "名称": "🕵️ 渗透小队",
                "阵容": ["无名(侦察)", "比特(工程)", "疾风(突击)"],
                "战术": "隐身+陷阱+快速转移，偷袭专精",
                "难度": "困难"
            },
        ]
        
        for preset in team_presets:
            with st.expander(f"{preset['名称']} - 难度: {preset['难度']}"):
                st.markdown(f"**阵容:** {' + '.join(preset['阵容'])}")
                st.markdown(f"**战术:** {preset['战术']}")

elif menu == "🎰 爆率模拟器":
    st.title("🎰 出货概率模拟器")
    st.caption("模拟跑刀出货概率 - 看看你的运气如何！")
    
    tab1, tab2 = st.tabs(["🎲 单次模拟", "📊 批量统计"])
    
    with tab1:
        st.subheader("单次跑刀模拟")
        
        sim_map = st.selectbox("选择地图", list(MAPS_DATA.keys()), key="sim_map")
        map_info = MAPS_DATA[sim_map]
        
        col1, col2 = st.columns(2)
        
        with col1:
            sim_zone = st.selectbox("选择搜索区域", map_info['loot_zones'])
            is_hot_zone = sim_zone in map_info['hot_zones']
            if is_hot_zone:
                st.warning("🔥 这是热点区域！出货率+50%，但风险也更高！")
        
        if st.button("🎲 开始搜索！", type="primary"):
            loot_probs = LOOT_PROBABILITY[sim_map]
            
            # 热点区域加成
            modifier = 1.5 if is_hot_zone else 1.0
            
            results = []
            st.markdown("### 📦 搜索结果:")
            
            for item, base_prob in loot_probs.items():
                actual_prob = min(base_prob * modifier, 100)
                roll = random.random() * 100
                found = roll < actual_prob
                
                if found:
                    # 计算物资价值
                    if "高级" in item:
                        value = random.randint(50000, 150000)
                        emoji = "🔴"
                    elif "中级" in item:
                        value = random.randint(15000, 50000)
                        emoji = "🟣"
                    elif "钥匙卡" in item:
                        value = random.randint(80000, 200000)
                        emoji = "🔑"
                    elif "情报文件" in item:
                        value = random.randint(100000, 300000)
                        emoji = "📄"
                    else:
                        value = random.randint(2000, 15000)
                        emoji = "⚪"
                    
                    results.append({"物资": f"{emoji} {item}", "价值": value})
            
            if results:
                total_value = sum(r['价值'] for r in results)
                
                for r in results:
                    st.markdown(f"- {r['物资']}: **{r['价值']:,}** 哈夫币")
                
                st.markdown("---")
                st.metric("💰 本次收益", f"{total_value:,} 哈夫币")
                
                if total_value > 100000:
                    st.balloons()
                    st.success("🎉 大丰收！运气不错！")
                elif total_value > 30000:
                    st.info("👍 还不错，小有收获")
                else:
                    st.warning("😅 收获一般，继续加油")
            else:
                st.error("😭 这趟跑空了...一无所获")
    
    with tab2:
        st.subheader("批量模拟统计")
        st.markdown("模拟多次跑刀，统计平均收益")
        
        sim_map2 = st.selectbox("选择地图", list(MAPS_DATA.keys()), key="sim_map2")
        sim_runs = st.slider("模拟次数", 10, 1000, 100)
        survival_rate = st.slider("预估存活率 (%)", 10, 100, 60)
        
        if st.button("🚀 开始批量模拟", type="primary"):
            loot_probs = LOOT_PROBABILITY[sim_map2]
            
            all_runs = []
            for run in range(sim_runs):
                survived = random.random() * 100 < survival_rate
                
                if survived:
                    run_value = 0
                    for item, prob in loot_probs.items():
                        if random.random() * 100 < prob:
                            if "高级" in item:
                                run_value += random.randint(50000, 150000)
                            elif "中级" in item:
                                run_value += random.randint(15000, 50000)
                            elif "钥匙卡" in item:
                                run_value += random.randint(80000, 200000)
                            elif "情报文件" in item:
                                run_value += random.randint(100000, 300000)
                            else:
                                run_value += random.randint(2000, 15000)
                    all_runs.append({"局数": run+1, "收益": run_value, "状态": "存活"})
                else:
                    all_runs.append({"局数": run+1, "收益": 0, "状态": "阵亡"})
            
            df_runs = pd.DataFrame(all_runs)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总局数", sim_runs)
            with col2:
                actual_survival = len(df_runs[df_runs["状态"] == "存活"]) / sim_runs * 100
                st.metric("实际存活率", f"{actual_survival:.1f}%")
            with col3:
                avg_profit = df_runs["收益"].mean()
                st.metric("场均收益", f"{avg_profit:,.0f}")
            with col4:
                total_profit = df_runs["收益"].sum()
                st.metric("总收益", f"{total_profit:,}")
            
            # 收益分布图
            fig = px.histogram(
                df_runs[df_runs["收益"] > 0],
                x="收益",
                nbins=30,
                title="收益分布图"
            )
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
            
            # 趋势图
            fig2 = px.line(
                df_runs,
                x="局数",
                y="收益",
                title="收益趋势图",
                markers=True
            )
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig2, use_container_width=True)

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
    "<p style='text-align: center; color: #666;'>🎮 三角洲战术终端 v3.0 | Built with Streamlit | 数据来源: TapTap社区 + 个人统计</p>",
    unsafe_allow_html=True
)
