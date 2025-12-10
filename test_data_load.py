import pandas as pd
from pathlib import Path
import json

data_dir = Path.home() / "Documents" / "DeltaTool"
print(f"数据目录: {data_dir}")
print(f"目录存在: {data_dir.exists()}")

if data_dir.exists():
    files = list(data_dir.glob("*"))
    print(f"\n文件列表:")
    for f in files:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")

# 测试JSON加载
json_file = data_dir / "game_records.json"
if json_file.exists():
    print(f"\n读取 {json_file.name}:")
    with open(json_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
        print(f"  记录数: {len(records)}")
        if records:
            print(f"  第一条: {records[0]}")

# 测试CSV加载
csv_file = data_dir / "game_records_export.csv"
if csv_file.exists():
    print(f"\n读取 {csv_file.name}:")
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    print(f"  行数: {len(df)}")
    print(f"  列名: {list(df.columns)}")
    print(f"\n内容:")
    print(df)
