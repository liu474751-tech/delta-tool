import streamlit as st
import pandas as pd
from pathlib import Path
import json

st.title("数据加载测试")

data_dir = Path.home() / "Documents" / "DeltaTool"
st.write(f"数据目录: {data_dir}")
st.write(f"目录存在: {data_dir.exists()}")

# 测试CSV加载
csv_file = data_dir / "game_records_export.csv"
if csv_file.exists():
    st.success("CSV文件存在")
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    st.write(f"记录数: {len(df)}")
    st.dataframe(df)
    
    # 转换
    records = []
    for _, row in df.iterrows():
        record = {
            "日期": str(row.get('datetime', '')),
            "地图": str(row.get('map', '未知')),
            "模式": str(row.get('mode', '未知')),
            "刷新点": str(row.get('zone', '')),
            "物资": str(row.get('items', '')),
            "价值": int(row.get('profit', 0)) if pd.notna(row.get('profit')) else 0,
            "撤离": "✅" if row.get('survived', True) else "❌"
        }
        records.append(record)
    
    st.write("转换后的记录:")
    st.write(records)
else:
    st.error("CSV文件不存在")
