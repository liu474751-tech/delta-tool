"""
数据管理模块
负责存储和管理游戏记录
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path


class DataManager:
    """数据管理器"""
    
    def __init__(self, data_dir=None):
        if data_dir is None:
            # 默认存储在用户文档目录
            data_dir = Path.home() / "Documents" / "DeltaTool"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.records_file = self.data_dir / "game_records.json"
        self.stats_file = self.data_dir / "stats.json"
        self.settings_file = self.data_dir / "settings.json"
        
        self.records = []
        self.stats = {
            "total_games": 0,
            "total_profit": 0,
            "survived_games": 0,
            "last_update": None
        }
        
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        # 加载游戏记录
        if self.records_file.exists():
            try:
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
            except:
                self.records = []
        
        # 加载统计数据
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except:
                pass
    
    def save_data(self):
        """保存数据"""
        # 保存游戏记录
        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
        
        # 保存统计数据
        self.stats["last_update"] = datetime.now().isoformat()
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def add_record(self, record):
        """
        添加游戏记录
        
        Args:
            record: dict {
                "datetime": 日期时间,
                "map": 地图,
                "mode": 模式,
                "zone": 刷新点,
                "items": 物品列表,
                "profit": 收益,
                "survived": 是否撤离
            }
        """
        if "datetime" not in record:
            record["datetime"] = datetime.now().isoformat()
        
        self.records.append(record)
        
        # 更新统计
        self.stats["total_games"] += 1
        if record.get("survived", False):
            self.stats["survived_games"] += 1
            self.stats["total_profit"] += record.get("profit", 0)
        
        self.save_data()
        return True
    
    def get_records(self, filters=None):
        """
        获取记录
        
        Args:
            filters: dict {
                "map": 地图筛选,
                "mode": 模式筛选,
                "date_from": 开始日期,
                "date_to": 结束日期,
                "survived": 是否撤离
            }
        """
        if filters is None:
            return self.records
        
        filtered = self.records.copy()
        
        if filters.get("map"):
            filtered = [r for r in filtered if r.get("map") == filters["map"]]
        
        if filters.get("mode"):
            filtered = [r for r in filtered if r.get("mode") == filters["mode"]]
        
        if filters.get("survived") is not None:
            filtered = [r for r in filtered if r.get("survived") == filters["survived"]]
        
        return filtered
    
    def get_stats(self):
        """获取统计数据"""
        if not self.records:
            return {
                "total_games": 0,
                "survival_rate": 0,
                "total_profit": 0,
                "avg_profit": 0,
                "best_game": 0,
                "map_stats": {},
                "mode_stats": {}
            }
        
        total = len(self.records)
        survived = len([r for r in self.records if r.get("survived")])
        profits = [r.get("profit", 0) for r in self.records if r.get("survived")]
        
        # 地图统计
        map_stats = {}
        for record in self.records:
            map_name = record.get("map", "未知")
            if map_name not in map_stats:
                map_stats[map_name] = {"games": 0, "survived": 0, "profit": 0}
            map_stats[map_name]["games"] += 1
            if record.get("survived"):
                map_stats[map_name]["survived"] += 1
                map_stats[map_name]["profit"] += record.get("profit", 0)
        
        # 模式统计
        mode_stats = {}
        for record in self.records:
            mode_name = record.get("mode", "未知")
            if mode_name not in mode_stats:
                mode_stats[mode_name] = {"games": 0, "survived": 0, "profit": 0}
            mode_stats[mode_name]["games"] += 1
            if record.get("survived"):
                mode_stats[mode_name]["survived"] += 1
                mode_stats[mode_name]["profit"] += record.get("profit", 0)
        
        return {
            "total_games": total,
            "survival_rate": survived / total * 100 if total > 0 else 0,
            "total_profit": sum(profits),
            "avg_profit": sum(profits) / len(profits) if profits else 0,
            "best_game": max(profits) if profits else 0,
            "map_stats": map_stats,
            "mode_stats": mode_stats
        }
    
    def export_csv(self, filepath):
        """导出为CSV"""
        if not self.records:
            return False
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 表头
            headers = ["日期时间", "地图", "模式", "刷新点", "物品", "收益", "是否撤离"]
            writer.writerow(headers)
            
            # 数据
            for record in self.records:
                items_str = ", ".join([
                    f"{item['name']}x{item.get('count', 1)}" 
                    for item in record.get("items", [])
                ])
                
                row = [
                    record.get("datetime", ""),
                    record.get("map", ""),
                    record.get("mode", ""),
                    record.get("zone", ""),
                    items_str,
                    record.get("profit", 0),
                    "是" if record.get("survived") else "否"
                ]
                writer.writerow(row)
        
        return True
    
    def import_csv(self, filepath):
        """从CSV导入"""
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    record = {
                        "datetime": row.get("日期时间", datetime.now().isoformat()),
                        "map": row.get("地图", ""),
                        "mode": row.get("模式", ""),
                        "zone": row.get("刷新点", ""),
                        "items": [],
                        "profit": int(row.get("收益", 0) or 0),
                        "survived": row.get("是否撤离", "否") == "是"
                    }
                    self.records.append(record)
            
            self.save_data()
            return True
        except Exception as e:
            print(f"导入失败: {e}")
            return False
    
    def clear_records(self):
        """清空记录"""
        self.records = []
        self.stats = {
            "total_games": 0,
            "total_profit": 0,
            "survived_games": 0,
            "last_update": None
        }
        self.save_data()
    
    def backup(self):
        """备份数据"""
        backup_dir = self.data_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump({
                "records": self.records,
                "stats": self.stats
            }, f, ensure_ascii=False, indent=2)
        
        return backup_file


class SyncManager:
    """数据同步管理器 - 与网页版同步"""
    
    def __init__(self, api_url=None):
        self.api_url = api_url
    
    def sync_to_cloud(self, data):
        """同步到云端"""
        if not self.api_url:
            return False
        
        try:
            import requests
            response = requests.post(
                f"{self.api_url}/sync",
                json=data,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def sync_from_cloud(self):
        """从云端同步"""
        if not self.api_url:
            return None
        
        try:
            import requests
            response = requests.get(
                f"{self.api_url}/data",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None


if __name__ == "__main__":
    # 测试
    dm = DataManager()
    
    # 添加测试记录
    dm.add_record({
        "map": "大坝",
        "mode": "机密",
        "zone": "控制室",
        "items": [{"name": "M4A1", "value": 80000, "count": 1}],
        "profit": 150000,
        "survived": True
    })
    
    print("统计:", dm.get_stats())
    print("记录数:", len(dm.get_records()))
