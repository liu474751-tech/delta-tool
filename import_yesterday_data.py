"""
快速导入昨天的游戏记录
根据截图数据自动生成
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# 昨天的游戏记录（2025-12-09）
records = [
    # 第一组截图的记录
    {"datetime": "2025-12-09T18:47:00", "map": "大坝", "mode": "机密", "zone": "优势方: 军营/栏杆(离主楼最近，TO出生点)", "items": "", "profit": -173183, "survived": False},
    {"datetime": "2025-12-09T18:38:00", "map": "大坝", "mode": "机密", "zone": "优势方: 军营/栏杆(离主楼最近，TO出生点)", "items": "灯", "profit": -89653, "survived": False},
    
    # 第二组截图的记录
    {"datetime": "2025-12-09T20:47:00", "map": "大坝", "mode": "机密", "zone": "优势方: 军营/栏杆(离主楼最近，TO出生点)", "items": "", "profit": -28218, "survived": True},
    {"datetime": "2025-12-09T20:35:00", "map": "大坝", "mode": "机密", "zone": "优势方: 军营/栏杆(离主楼最近，TO出生点)", "items": "", "profit": -960270, "survived": False},
    {"datetime": "2025-12-09T20:11:00", "map": "大坝", "mode": "机密", "zone": "劣势方: 水泥厂/后山(建议直接吃完水泥厂，架起前往中心的人)", "items": "扳手;炸药", "profit": -842501, "survived": False},
    {"datetime": "2025-12-09T19:51:00", "map": "大坝", "mode": "机密", "zone": "劣势方: 水泥厂/后山(建议直接吃完水泥厂，架起前往中心的人)", "items": "水壶", "profit": -145991, "survived": False},
    {"datetime": "2025-12-09T19:35:00", "map": "大坝", "mode": "机密", "zone": "优势方: 军营/栏杆(离主楼最近，TO出生点)", "items": "绷带;匕首;指南针", "profit": -228190, "survived": False},
    {"datetime": "2025-12-09T19:21:00", "map": "大坝", "mode": "机密", "zone": "优势方: 军营/栏杆(离主楼最近，TO出生点)", "items": "", "profit": -248343, "survived": False},
    {"datetime": "2025-12-09T19:03:00", "map": "大坝", "mode": "机密", "zone": "优势方: 军营/栏杆(离主楼最近，TO出生点)", "items": "文件", "profit": 122462, "survived": True},
]

def main():
    if not records:
        print("⚠️ 没有记录需要导入")
        return
    
    # 转换为DataFrame
    df = pd.DataFrame(records)
    
    # 保存到DeltaTool目录
    data_dir = Path.home() / "Documents" / "DeltaTool"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = data_dir / f"import_20251209_games_{timestamp}.csv"
    
    # 保存CSV
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    print("="*80)
    print("✅ 昨天的游戏数据导入成功！")
    print("="*80)
    print(f"\n📊 总共导入: {len(records)} 场游戏")
    print(f"📁 保存位置: {csv_file}")
    
    # 统计数据
    survived_count = sum(1 for r in records if r['survived'])
    died_count = len(records) - survived_count
    total_profit = sum(r['profit'] for r in records)
    
    print("\n📈 统计概览:")
    print(f"   ✅ 成功撤离: {survived_count} 场")
    print(f"   ❌ 阵亡: {died_count} 场")
    print(f"   💰 总盈亏: {total_profit:,} 哈夫币")
    print(f"   📊 平均盈亏: {total_profit//len(records):,} 哈夫币/局")
    
    print("\n📋 记录详情:")
    for i, record in enumerate(records, 1):
        status = "✅撤离" if record['survived'] else "❌阵亡"
        items = record['items'] if record['items'] else "无"
        print(f"   {i}. {record['datetime'][-5:]} | {status} | {record['profit']:>9,} | {items}")
    
    print("\n" + "="*80)
    print("🎮 下一步操作:")
    print("1. 在Streamlit应用中打开 '📈 数据管理' 页面")
    print("2. 选择 '文件上传' 标签")
    print(f"3. 上传文件: {csv_file.name}")
    print("   或者等待应用自动刷新数据（会自动加载新CSV文件）")
    print("="*80)

if __name__ == "__main__":
    main()
