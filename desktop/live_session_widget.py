"""
实时会话显示组件
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QTableWidget, QTableWidgetItem, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class LiveSessionWidget(QWidget):
    """实时会话显示组件"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.setup_ui()
        
        # 定时器更新会话信息
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_session_display)
        self.update_timer.start(1000)  # 每秒更新
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 会话状态组
        status_group = QGroupBox("当前会话状态")
        status_layout = QVBoxLayout(status_group)
        
        # 状态信息
        info_layout = QHBoxLayout()
        
        self.status_label = QLabel("状态: 准备中")
        self.status_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #FFD700;")
        info_layout.addWidget(self.status_label)
        
        info_layout.addStretch()
        
        self.spawn_label = QLabel("出生地: --")
        self.spawn_label.setStyleSheet("font-size: 12pt; color: #4169E1;")
        info_layout.addWidget(self.spawn_label)
        
        self.map_label = QLabel("地图: --")
        self.map_label.setStyleSheet("font-size: 12pt; color: #FFD700;")
        info_layout.addWidget(self.map_label)
        
        self.mode_label = QLabel("模式: --")
        self.mode_label.setStyleSheet("font-size: 12pt; color: #00CED1;")
        info_layout.addWidget(self.mode_label)
        
        status_layout.addLayout(info_layout)
        
        # 总价值显示
        value_layout = QHBoxLayout()
        self.total_value_label = QLabel("当前价值: ¥0")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.total_value_label.setFont(font)
        self.total_value_label.setStyleSheet("color: #00FF00;")
        self.total_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_layout.addWidget(self.total_value_label)
        
        status_layout.addLayout(value_layout)
        
        layout.addWidget(status_group)
        
        # 物品列表组
        items_group = QGroupBox("收集物品")
        items_layout = QVBoxLayout(items_group)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["时间", "物品", "类别", "价值"])
        self.items_table.setColumnWidth(0, 100)
        self.items_table.setColumnWidth(1, 200)
        self.items_table.setColumnWidth(2, 100)
        self.items_table.setColumnWidth(3, 120)
        items_layout.addWidget(self.items_table)
        
        layout.addWidget(items_group, 1)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        
        self.start_session_btn = QPushButton("🎮 开始新会话")
        self.start_session_btn.clicked.connect(self.start_new_session)
        btn_layout.addWidget(self.start_session_btn)
        
        self.survived_btn = QPushButton("✅ 成功撤离")
        self.survived_btn.clicked.connect(self.end_session_survived)
        self.survived_btn.setStyleSheet("background-color: #28a745;")
        btn_layout.addWidget(self.survived_btn)
        
        self.died_btn = QPushButton("❌ 阵亡")
        self.died_btn.clicked.connect(self.end_session_died)
        self.died_btn.setStyleSheet("background-color: #dc3545;")
        btn_layout.addWidget(self.died_btn)
        
        layout.addLayout(btn_layout)
    
    def update_session_display(self):
        """更新显示"""
        session = self.data_manager.get_current_session()
        
        # 更新状态
        status = session.get("status", "准备中")
        self.status_label.setText(f"状态: {status}")
        
        # 根据状态改变颜色
        if status == "进行中":
            self.status_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #00FF00;")
        elif status == "已撤离":
            self.status_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #FFD700;")
        elif status == "已阵亡":
            self.status_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #FF0000;")
        else:
            self.status_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #808080;")
        
        # 更新信息
        spawn = session.get("spawn_point", "--")
        self.spawn_label.setText(f"出生地: {spawn}")
        
        map_name = session.get("map", "--")
        self.map_label.setText(f"地图: {map_name}")
        
        mode = session.get("mode", "--")
        self.mode_label.setText(f"模式: {mode}")
        
        # 更新总价值
        total_value = session.get("total_value", 0)
        self.total_value_label.setText(f"当前价值: ¥{total_value:,}")
        
        # 更新物品列表
        items = session.get("items_collected", [])
        self.items_table.setRowCount(len(items))
        
        for i, item in enumerate(items):
            # 时间
            time_str = item.get("time", "")[-8:]  # 只显示时:分:秒
            self.items_table.setItem(i, 0, QTableWidgetItem(time_str))
            
            # 物品名
            name = item.get("name", "")
            self.items_table.setItem(i, 1, QTableWidgetItem(name))
            
            # 类别
            category = item.get("category", "")
            self.items_table.setItem(i, 2, QTableWidgetItem(category))
            
            # 价值
            value = item.get("value", 0)
            value_item = QTableWidgetItem(f"¥{value:,}")
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.items_table.setItem(i, 3, value_item)
    
    def start_new_session(self):
        """开始新会话"""
        self.data_manager.start_new_session()
        self.update_session_display()
    
    def end_session_survived(self):
        """成功撤离"""
        self.data_manager.end_session(survived=True)
        self.update_session_display()
    
    def end_session_died(self):
        """阵亡"""
        self.data_manager.end_session(survived=False)
        self.update_session_display()
