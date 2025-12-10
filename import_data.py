"""
数据导入和修复工具
用于导入旧数据和修复缺失的CSV文件
"""

import sys
import os
from pathlib import Path

# 添加desktop目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'desktop'))

from data_manager import DataManager


def main():
    print("="*60)
    print("🔧 三角洲工具 - 数据导入修复工具")
    print("="*60)
    print()
    
    # 初始化数据管理器
    data_manager = DataManager()
    
    print(f"📁 数据目录: {data_manager.data_dir}")
    print()
    
    # 检查数据文件
    files_status = {
        "game_records.json": data_manager.records_file.exists(),
        "stats.json": data_manager.stats_file.exists(),
        "live_session.json": data_manager.live_session_file.exists(),
        "game_records_export.csv": data_manager.csv_export_file.exists(),
    }
    
    print("📊 文件状态:")
    for filename, exists in files_status.items():
        status = "✅ 存在" if exists else "❌ 缺失"
        print(f"  {filename}: {status}")
    print()
    
    # 显示记录数量
    print(f"📝 当前记录数: {len(data_manager.records)}")
    
    if data_manager.records:
        print("📋 记录列表:")
        for i, record in enumerate(data_manager.records, 1):
            map_name = record.get('map', '未知')
            mode = record.get('mode', '未知')
            profit = record.get('profit', 0)
            survived = "✅" if record.get('survived') else "❌"
            date = record.get('datetime', '未知')[:19]
            print(f"  {i}. [{date}] {map_name} - {mode} - {profit:,} 哈夫币 {survived}")
    print()
    
    # 修复选项
    print("🔧 可用操作:")
    print("  [1] 导出CSV文件（从现有JSON生成）")
    print("  [2] 创建空的实时会话文件")
    print("  [3] 重新计算统计数据")
    print("  [4] 全部修复（推荐）")
    print("  [5] 手动添加测试记录")
    print("  [0] 退出")
    print()
    
    choice = input("请选择操作 (0-5): ").strip()
    
    if choice == "1":
        print("\n🔄 正在导出CSV...")
        data_manager.export_to_csv()
        if data_manager.csv_export_file.exists():
            print(f"✅ CSV文件已生成: {data_manager.csv_export_file}")
        else:
            print("❌ CSV文件生成失败")
    
    elif choice == "2":
        print("\n🔄 正在创建实时会话文件...")
        data_manager.save_live_session()
        if data_manager.live_session_file.exists():
            print(f"✅ 实时会话文件已创建: {data_manager.live_session_file}")
        else:
            print("❌ 实时会话文件创建失败")
    
    elif choice == "3":
        print("\n🔄 正在重新计算统计数据...")
        # 重置统计
        data_manager.stats = {
            "total_games": 0,
            "total_profit": 0,
            "survived_games": 0,
            "last_update": None
        }
        # 重新计算
        for record in data_manager.records:
            data_manager.stats["total_games"] += 1
            if record.get("survived", False):
                data_manager.stats["survived_games"] += 1
                data_manager.stats["total_profit"] += record.get("profit", 0)
        
        data_manager.save_data()
        print(f"✅ 统计数据已更新:")
        print(f"   总局数: {data_manager.stats['total_games']}")
        print(f"   存活局数: {data_manager.stats['survived_games']}")
        print(f"   总收益: {data_manager.stats['total_profit']:,}")
    
    elif choice == "4":
        print("\n🔄 正在执行全部修复...")
        
        # 1. 导出CSV
        print("  1/3 导出CSV...")
        data_manager.export_to_csv()
        
        # 2. 创建实时会话
        print("  2/3 创建实时会话...")
        data_manager.save_live_session()
        
        # 3. 重新计算统计
        print("  3/3 重新计算统计...")
        data_manager.stats = {
            "total_games": 0,
            "total_profit": 0,
            "survived_games": 0,
            "last_update": None
        }
        for record in data_manager.records:
            data_manager.stats["total_games"] += 1
            if record.get("survived", False):
                data_manager.stats["survived_games"] += 1
                data_manager.stats["total_profit"] += record.get("profit", 0)
        
        data_manager.save_data()
        
        print("\n✅ 全部修复完成！")
        print(f"   CSV文件: {'✅' if data_manager.csv_export_file.exists() else '❌'}")
        print(f"   会话文件: {'✅' if data_manager.live_session_file.exists() else '❌'}")
        print(f"   统计数据: ✅")
    
    elif choice == "5":
        print("\n📝 添加测试记录...")
        print("地图选择: 1.大坝 2.长弓 3.巴克什 4.航天 5.监狱")
        map_choice = input("选择地图 (1-5): ").strip()
        map_names = ["", "大坝", "长弓", "巴克什", "航天", "监狱"]
        map_name = map_names[int(map_choice)] if map_choice in "12345" else "大坝"
        
        mode = input("模式 (普通/机密/绝密): ").strip() or "机密"
        spawn = input("出生地 (如：发电站): ").strip() or "发电站"
        profit = int(input("收益 (哈夫币): ").strip() or "350000")
        survived = input("是否撤离 (y/n): ").strip().lower() == 'y'
        
        record = {
            "datetime": __import__('datetime').datetime.now().isoformat(),
            "map": map_name,
            "mode": mode,
            "zone": spawn,
            "items": [],
            "profit": profit,
            "survived": survived
        }
        
        data_manager.add_record(record)
        print(f"✅ 记录已添加！")
        print(f"   地图: {map_name}")
        print(f"   出生地: {spawn}")
        print(f"   收益: {profit:,}")
        print(f"   结果: {'✅ 撤离' if survived else '❌ 阵亡'}")
    
    elif choice == "0":
        print("\n👋 再见！")
        return
    
    else:
        print("\n❌ 无效选项")
    
    print("\n" + "="*60)
    print("按回车键退出...")
    input()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n按回车键退出...")
        input()
