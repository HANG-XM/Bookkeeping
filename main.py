import sys
import sqlite3
import json
import os
from datetime import datetime, date
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QLineEdit, QComboBox, 
                            QTableWidget, QTableWidgetItem, QTabWidget, QDialog,
                            QFormLayout, QTextEdit, QDateTimeEdit, QCheckBox,
                            QDoubleSpinBox, QMessageBox, QSplitter, QGroupBox,
                            QTreeWidget, QTreeWidgetItem, QHeaderView, QSpinBox,
                            QCalendarWidget, QDateEdit, QScrollArea, QGridLayout,
                            QFrame, QButtonGroup, QRadioButton)
from PyQt6.QtCore import Qt, QDateTime, QDate, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

class ThemeManager:
    """主题管理器"""
    
    THEMES = {
        "default": {
            "name": "日间主题",
            "description": "明亮配色，适合白天使用",
            "colors": {
                "background": "#FFFFFF",
                "secondary_background": "#F5F5F5",
                "card_background": "#FFFFFF",
                "primary_text": "#333333",
                "secondary_text": "#666666",
                "accent": "#2196F3",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "danger": "#F44336",
                "border": "#E0E0E0",
                "hover": "#F0F0F0",
                "income": "#4CAF50",
                "expense": "#FF6B6B",
                "chart_colors": ["#4CAF50", "#FF9800", "#2196F3", "#9C27B0", "#FF5722", "#795548", "#607D8B", "#E91E63"]
            }
        },
        "dark": {
            "name": "夜间主题",
            "description": "深色配色，适合夜间使用",
            "colors": {
                "background": "#1E1E1E",
                "secondary_background": "#2D2D2D",
                "card_background": "#252526",
                "primary_text": "#FFFFFF",
                "secondary_text": "#B0B0B0",
                "accent": "#64B5F6",
                "success": "#81C784",
                "warning": "#FFB74D",
                "danger": "#E57373",
                "border": "#404040",
                "hover": "#333333",
                "income": "#81C784",
                "expense": "#E57373",
                "chart_colors": ["#81C784", "#FFB74D", "#64B5F6", "#BA68C8", "#FF8A65", "#8D6E63", "#90A4AE", "#F06292"]
            }
        },
        "eye_care": {
            "name": "护眼主题",
            "description": "低蓝光配色，保护视力",
            "colors": {
                "background": "#F4F1E8",
                "secondary_background": "#E8E4D8",
                "card_background": "#FAF8F3",
                "primary_text": "#3D3D3D",
                "secondary_text": "#666666",
                "accent": "#8D6E63",
                "success": "#689F38",
                "warning": "#FFA726",
                "danger": "#EF5350",
                "border": "#D7CCC8",
                "hover": "#EFEBE9",
                "income": "#689F38",
                "expense": "#EF5350",
                "chart_colors": ["#689F38", "#FFA726", "#8D6E63", "#7E57C2", "#FF7043", "#8D6E63", "#A1887F", "#EC407A"]
            }
        },
        "cute": {
            "name": "可爱主题",
            "description": "淡粉色配色，温馨可爱",
            "colors": {
                "background": "#FFF5F7",
                "secondary_background": "#FCE4EC",
                "card_background": "#FFFFFF",
                "primary_text": "#4A4A4A",
                "secondary_text": "#7A7A7A",
                "accent": "#F48FB1",
                "success": "#AED581",
                "warning": "#FFD54F",
                "danger": "#FF8A80",
                "border": "#F8BBD0",
                "hover": "#FCE4EC",
                "income": "#AED581",
                "expense": "#FF8A80",
                "chart_colors": ["#F48FB1", "#AED581", "#FFD54F", "#81D4FA", "#CE93D8", "#FFCC80", "#A5D6A7", "#FFAB91"]
            }
        }
    }
    
    def __init__(self):
        self.current_theme = "default"
        self.settings_file = "theme_settings.json"
        self.load_settings()
    
    def load_settings(self):
        """加载主题设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get('theme', 'default')
            except:
                self.current_theme = "default"
    
    def save_settings(self):
        """保存主题设置"""
        settings = {'theme': self.current_theme}
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_current_theme(self):
        """获取当前主题"""
        return self.THEMES.get(self.current_theme, self.THEMES["default"])
    
    def set_theme(self, theme_name):
        """设置主题"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self.save_settings()
            return True
        return False
    
    def get_color(self, color_name):
        """获取当前主题的颜色"""
        theme = self.get_current_theme()
        return theme["colors"].get(color_name, "#000000")
    
    def apply_theme_to_widget(self, widget):
        """将主题应用到控件"""
        colors = self.get_current_theme()["colors"]
        
        # 设置样式表
        style = f"""
            QWidget {{
                background-color: {colors['background']};
                color: {colors['primary_text']};
                font-family: "Microsoft YaHei", "SimHei", Arial;
            }}
            
            QMainWindow {{
                background-color: {colors['background']};
            }}
            
            QGroupBox {{
                background-color: {colors['card_background']};
                border: 2px solid {colors['border']};
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {colors['primary_text']};
            }}
            
            QPushButton {{
                background-color: {colors['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            
            QPushButton:hover {{
                background-color: {colors['hover']};
                border: 1px solid {colors['accent']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['accent']};
            }}
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: {colors['card_background']};
                border: 2px solid {colors['border']};
                border-radius: 4px;
                padding: 6px;
                color: {colors['primary_text']};
            }}
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {colors['accent']};
            }}
            
            QTableWidget {{
                background-color: {colors['card_background']};
                alternate-background-color: {colors['secondary_background']};
                gridline-color: {colors['border']};
                selection-background-color: {colors['accent']};
            }}
            
            QTableWidget::item {{
                padding: 5px;
                color: {colors['primary_text']};
            }}
            
            QTableWidget::item:selected {{
                background-color: {colors['accent']};
                color: white;
            }}
            
            QHeaderView::section {{
                background-color: {colors['secondary_background']};
                color: {colors['primary_text']};
                padding: 5px;
                border: 1px solid {colors['border']};
                font-weight: bold;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                background-color: {colors['card_background']};
            }}
            
            QTabBar::tab {{
                background-color: {colors['secondary_background']};
                color: {colors['primary_text']};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors['accent']};
                color: white;
            }}
            
            QTabBar::tab:hover {{
                background-color: {colors['hover']};
            }}
            
            QScrollArea {{
                background-color: {colors['background']};
                border: none;
            }}
            
            QLabel {{
                color: {colors['primary_text']};
            }}
            
            QCheckBox {{
                color: {colors['primary_text']};
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {colors['border']};
                border-radius: 3px;
                background-color: {colors['card_background']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {colors['accent']};
                border-color: {colors['accent']};
            }}
            
            QTreeWidget {{
                background-color: {colors['card_background']};
                border: 1px solid {colors['border']};
                selection-background-color: {colors['accent']};
            }}
            
            QTreeWidget::item {{
                padding: 3px;
                color: {colors['primary_text']};
            }}
            
            QTreeWidget::item:selected {{
                background-color: {colors['accent']};
                color: white;
            }}
            
            QTreeWidget::item:hover {{
                background-color: {colors['hover']};
            }}
            
            QDateEdit, QDateTimeEdit {{
                background-color: {colors['card_background']};
                border: 2px solid {colors['border']};
                border-radius: 4px;
                padding: 6px;
                color: {colors['primary_text']};
            }}
            
            QCalendarWidget {{
                background-color: {colors['card_background']};
                color: {colors['primary_text']};
            }}
            
            QCalendarWidget QToolButton {{
                background-color: {colors['secondary_background']};
                color: {colors['primary_text']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                margin: 2px;
            }}
            
            QCalendarWidget QToolButton:hover {{
                background-color: {colors['accent']};
                color: white;
            }}
        """
        
        widget.setStyleSheet(style)
        
        # 更新matplotlib图表颜色
        self.update_matplotlib_colors()
    
    def update_matplotlib_colors(self):
        """更新matplotlib图表颜色"""
        colors = self.get_current_theme()["colors"]
        
        # 设置图表样式
        plt.style.use('default')  # 重置样式
        
        # 设置字体和颜色（只使用有效的参数）
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False
        
        # 尝试设置颜色参数，如果无效则跳过
        valid_params = {
            'figure.facecolor': colors['background'],
            'axes.facecolor': colors['background'],
            'axes.edgecolor': colors['border'],
            'axes.labelcolor': colors['primary_text'],
            'xtick.color': colors['primary_text'],
            'ytick.color': colors['primary_text'],
            'text.color': colors['primary_text'],
            'legend.facecolor': colors['card_background'],
            'legend.edgecolor': colors['border'],
            'legend.labelcolor': colors['primary_text']
        }
        
        for param, value in valid_params.items():
            try:
                matplotlib.rcParams[param] = value
            except KeyError:
                # 如果参数无效，跳过
                continue

# 全局主题管理器
theme_manager = ThemeManager()

def number_to_chinese(num):
    """将数字转换为中文大写"""
    if num == 0:
        return "零元整"
    
    digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    units = ['', '拾', '佰', '仟']
    big_units = ['', '万', '亿']
    
    # 处理小数部分
    integer_part = int(num)
    decimal_part = round((num - integer_part) * 100)
    
    if decimal_part >= 100:
        integer_part += decimal_part // 100
        decimal_part = decimal_part % 100
    
    result = ""
    
    # 处理整数部分
    if integer_part == 0:
        result = "零"
    else:
        str_num = str(integer_part)
        length = len(str_num)
        zero_flag = False
        
        for i, digit in enumerate(str_num):
            digit_int = int(digit)
            pos = length - i - 1
            
            if digit_int == 0:
                zero_flag = True
            else:
                if zero_flag and i > 0:
                    result += digits[0]
                result += digits[digit_int] + units[pos % 4]
                zero_flag = False
            
            if pos % 4 == 0 and pos > 0:
                if zero_flag:
                    result += digits[0]
                    zero_flag = False
                result += big_units[pos // 4]
    
    result += "元"
    
    # 处理小数部分
    if decimal_part == 0:
        result += "整"
    else:
        jiao = decimal_part // 10
        fen = decimal_part % 10
        
        if jiao > 0:
            result += digits[jiao] + "角"
        if fen > 0:
            result += digits[fen] + "分"
    
    return result

class SystemSettingsDialog(QDialog):
    """系统设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("系统设置")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("系统设置")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 设置选项
        settings_group = QGroupBox("设置选项")
        settings_layout = QVBoxLayout()
        
        # 主题设置按钮
        theme_btn = QPushButton("🎨 主题设置")
        theme_btn.clicked.connect(self.open_theme_settings)
        theme_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('accent')};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('hover')};
                border: 1px solid {theme_manager.get_color('accent')};
            }}
        """)
        settings_layout.addWidget(theme_btn)
        
        # 当前主题显示
        current_theme_layout = QHBoxLayout()
        current_theme_layout.addWidget(QLabel("当前主题:"))
        
        current_theme_label = QLabel(theme_manager.get_current_theme()["name"])
        current_theme_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('accent')};
                font-weight: bold;
            }}
        """)
        current_theme_layout.addWidget(current_theme_label)
        current_theme_layout.addStretch()
        
        settings_layout.addLayout(current_theme_layout)
        
        # 主题说明
        theme_info = QLabel("主题设置允许您更改应用的外观配色，包括日间、夜间、护眼和可爱四种预设主题。")
        theme_info.setWordWrap(True)
        theme_info.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('secondary_text')};
                font-size: 12px;
                padding: 10px;
                background-color: {theme_manager.get_color('secondary_background')};
                border-radius: 4px;
            }}
        """)
        settings_layout.addWidget(theme_info)
        
        # 其他设置（预留）
        other_settings_label = QLabel("其他设置功能正在开发中...")
        other_settings_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('secondary_text')};
                font-style: italic;
            }}
        """)
        settings_layout.addWidget(other_settings_label)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('accent')};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def open_theme_settings(self):
        """打开主题设置"""
        dialog = ThemeSelectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 主题已更改，重新应用样式
            if hasattr(self.parent(), 'apply_theme'):
                self.parent().apply_theme()
            QMessageBox.information(self, "成功", "主题已成功应用！")

class ThemeSelectionDialog(QDialog):
    """主题选择对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("主题设置")
        self.setModal(True)
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.load_current_theme()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("选择主题")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 主题卡片区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        card_layout = QGridLayout()
        
        self.theme_buttons = QButtonGroup()
        self.theme_cards = {}
        
        row, col = 0, 0
        for theme_id, theme_data in theme_manager.THEMES.items():
            card = self.create_theme_card(theme_id, theme_data)
            card_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 2:  # 每行2个卡片
                col = 0
                row += 1
        
        scroll_content.setLayout(card_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("恢复默认主题")
        reset_btn.clicked.connect(self.reset_to_default)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("应用")
        apply_btn.clicked.connect(self.apply_theme)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('accent')};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_theme_card(self, theme_id, theme_data):
        """创建主题预览卡片"""
        card = QFrame()
        card.setFixedSize(350, 200)
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme_data['colors']['card_background']};
                border: 2px solid {theme_data['colors']['border']};
                border-radius: 8px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # 主题标题和描述
        title_layout = QVBoxLayout()
        
        title_label = QLabel(theme_data['name'])
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {theme_data['colors']['primary_text']};")
        title_layout.addWidget(title_label)
        
        desc_label = QLabel(theme_data['description'])
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet(f"color: {theme_data['colors']['secondary_text']};")
        desc_label.setWordWrap(True)
        title_layout.addWidget(desc_label)
        
        layout.addLayout(title_layout)
        
        # 颜色预览
        preview_layout = QHBoxLayout()
        
        # 显示主要颜色
        colors_to_show = ['background', 'accent', 'success', 'danger', 'income', 'expense']
        for color_name in colors_to_show:
            color_widget = QWidget()
            color_widget.setFixedSize(30, 30)
            color_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme_data['colors'][color_name]};
                    border: 1px solid {theme_data['colors']['border']};
                    border-radius: 4px;
                }}
            """)
            preview_layout.addWidget(color_widget)
        
        preview_layout.addStretch()
        layout.addLayout(preview_layout)
        
        # 示例按钮
        example_layout = QHBoxLayout()
        
        income_btn = QPushButton("收入")
        income_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_data['colors']['income']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
            }}
        """)
        example_layout.addWidget(income_btn)
        
        expense_btn = QPushButton("支出")
        expense_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_data['colors']['expense']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
            }}
        """)
        example_layout.addWidget(expense_btn)
        
        example_layout.addStretch()
        layout.addLayout(example_layout)
        
        # 选择单选按钮
        radio = QRadioButton()
        radio.setStyleSheet(f"""
            QRadioButton {{
                color: {theme_data['colors']['primary_text']};
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {theme_data['colors']['border']};
                border-radius: 8px;
                background-color: {theme_data['colors']['card_background']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {theme_data['colors']['accent']};
                border-color: {theme_data['colors']['accent']};
            }}
        """)
        self.theme_buttons.addButton(radio)
        self.theme_buttons.setId(radio, len(self.theme_cards))
        self.theme_cards[radio] = theme_id
        
        # 如果是当前主题，标记为选中
        if theme_id == theme_manager.current_theme:
            radio.setChecked(True)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme_data['colors']['card_background']};
                    border: 3px solid {theme_data['colors']['accent']};
                    border-radius: 8px;
                    margin: 5px;
                }}
            """)
        
        # 将单选按钮和卡片组合
        card_layout = QHBoxLayout()
        card_layout.addLayout(layout)
        card_layout.addWidget(radio)
        
        card.setLayout(card_layout)
        
        # 点击卡片也可以选择
        card.mousePressEvent = lambda event: radio.setChecked(True)
        
        return card
    
    def load_current_theme(self):
        """加载当前主题"""
        pass  # 已在创建卡片时处理
    
    def reset_to_default(self):
        """恢复默认主题"""
        for radio, theme_id in self.theme_cards.items():
            if theme_id == "default":
                radio.setChecked(True)
                break
    
    def apply_theme(self):
        """应用选中的主题"""
        checked_radio = self.theme_buttons.checkedButton()
        if checked_radio and checked_radio in self.theme_cards:
            theme_id = self.theme_cards[checked_radio]
            if theme_manager.set_theme(theme_id):
                self.accept()
            else:
                QMessageBox.warning(self, "错误", "主题应用失败！")

class DatabaseManager:
    def __init__(self, db_path="bookkeeping.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建账本表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ledgers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_time TEXT NOT NULL,
                ledger_type TEXT NOT NULL,
                description TEXT
            )
        ''')
        
        # 创建收支类别表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_category TEXT NOT NULL,
                sub_category TEXT NOT NULL,
                type TEXT NOT NULL,
                UNIQUE(parent_category, sub_category)
            )
        ''')
        
        # 创建账户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,
                balance REAL DEFAULT 0.0,
                bank TEXT,
                description TEXT
            )
        ''')
        
        # 创建交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ledger_id INTEGER NOT NULL,
                transaction_date TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                amount REAL NOT NULL,
                account TEXT,
                description TEXT,
                is_settled BOOLEAN DEFAULT FALSE,
                refund_amount REAL DEFAULT 0.0,
                refund_reason TEXT,
                created_time TEXT NOT NULL,
                FOREIGN KEY (ledger_id) REFERENCES ledgers (id)
            )
        ''')
        
        # 创建资金流转表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transfer_date TEXT NOT NULL,
                from_account TEXT NOT NULL,
                to_account TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_time TEXT NOT NULL
            )
        ''')
        
        # 插入默认类别数据
        self.insert_default_categories()
        conn.commit()
        conn.close()
    
    def insert_default_categories(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 支出类别
        expense_categories = [
            ("餐饮", ["零食", "外卖", "食堂", "堂食", "水果", "饮料", "聚餐"]),
            ("休闲娱乐", ["电影", "游戏", "体育", "音乐", "旅游", "美妆", "宠物", "按摩", "健身", "会员"]),
            ("生活缴费", ["水电费", "物业费", "燃气费", "网费", "话费", "房贷", "房租", "取暖费", "车位费"]),
            ("交通", ["公交", "地铁", "共享单车", "共享电动车", "火车", "高铁", "飞机", "打车"]),
            ("教育", ["考试费", "培训费", "资料费", "文具"]),
            ("购物", ["服饰", "果蔬", "数码", "家电", "日用品", "家具"]),
            ("汽车", ["充电/油", "保养", "维修", "过路费", "停车费"]),
            ("医疗健康", ["药品", "住院", "体检", "保健品", "门诊", "疫苗接种"]),
            ("社交人情", ["红包", "礼物", "请客", "捐赠", "团建费"]),
            ("金融保险", ["保险", "投资", "贷款", "理财"]),
            ("其他", ["快递费", "党费", "罚款", "借款", "手续费", "维修费", "班费"]),
            ("儿童", ["母婴", "教育", "服装", "玩具", "医疗", "生活费"])
        ]
        
        # 收入类别
        income_categories = [
            ("薪资", ["工作薪资", "副业收入", "奖金补贴"]),
            ("生活费", ["家庭转账", "亲友资助"]),
            ("理财", ["股票基金", "存款利息", "借贷回款", "房产租金"]),
            ("人情往来", ["红包", "礼物"]),
            ("其他", ["闲置变卖", "商家奖励", "赛事奖金", "奖学金", "版权费"])
        ]
        
        for parent, subs in expense_categories:
            for sub in subs:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (parent_category, sub_category, type)
                    VALUES (?, ?, ?)
                ''', (parent, sub, "支出"))
        
        for parent, subs in income_categories:
            for sub in subs:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (parent_category, sub_category, type)
                    VALUES (?, ?, ?)
                ''', (parent, sub, "收入"))
        
        conn.commit()
        conn.close()
    
    def add_ledger(self, name, ledger_type, description):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO ledgers (name, created_time, ledger_type, description)
            VALUES (?, ?, ?, ?)
        ''', (name, created_time, ledger_type, description))
        
        # 获取新创建的账本ID
        ledger_id = cursor.lastrowid
        
        # 自动创建默认账户
        default_accounts = [
            ("现金", "现金", "个人", 0.0, "现金余额"),
            ("微信", "电子支付", "腾讯", 0.0, "微信支付")
        ]
        
        for account_name, account_type, bank, balance, account_desc in default_accounts:
            cursor.execute('''
                INSERT INTO accounts (name, type, balance, bank, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (account_name, account_type, balance, bank, account_desc))
        
        conn.commit()
        conn.close()
    
    def get_ledgers(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ledgers ORDER BY created_time')
        ledgers = cursor.fetchall()
        conn.close()
        return ledgers
    
    def delete_ledger(self, ledger_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE ledger_id = ?', (ledger_id,))
        cursor.execute('DELETE FROM ledgers WHERE id = ?', (ledger_id,))
        conn.commit()
        conn.close()
    
    def get_categories(self, category_type=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if category_type:
            cursor.execute('''
                SELECT DISTINCT parent_category, sub_category FROM categories 
                WHERE type = ? ORDER BY parent_category, sub_category
            ''', (category_type,))
        else:
            cursor.execute('''
                SELECT DISTINCT parent_category, sub_category FROM categories 
                ORDER BY parent_category, sub_category
            ''')
        categories = cursor.fetchall()
        conn.close()
        return categories
    
    def add_transaction(self, ledger_id, transaction_date, transaction_type, category, subcategory, 
                       amount, account, description, is_settled, refund_amount, refund_reason):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO transactions 
            (ledger_id, transaction_date, transaction_type, category, subcategory, amount, account, 
             description, is_settled, refund_amount, refund_reason, created_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ledger_id, transaction_date, transaction_type, category, subcategory, amount, account,
              description, is_settled, refund_amount, refund_reason, created_time))
        conn.commit()
        conn.close()
    
    def get_transactions(self, ledger_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions WHERE ledger_id = ? 
            ORDER BY transaction_date DESC, created_time DESC
        ''', (ledger_id,))
        transactions = cursor.fetchall()
        conn.close()
        return transactions
    
    def add_account(self, name, account_type, balance=0.0, bank=None, description=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO accounts (name, type, balance, bank, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, account_type, balance, bank, description))
        conn.commit()
        conn.close()
    
    def add_account_without_ledger(self, name, account_type, balance=0.0, bank=None, description=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO accounts (name, type, balance, bank, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, account_type, balance, bank, description))
        conn.commit()
        conn.close()
    
    def update_account(self, account_id, name, account_type, balance, bank, description):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE accounts SET name = ?, type = ?, balance = ?, bank = ?, description = ?
            WHERE id = ?
        ''', (name, account_type, balance, bank, description, account_id))
        conn.commit()
        conn.close()
    
    def delete_account(self, account_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        conn.commit()
        conn.close()
    
    def update_transaction(self, transaction_id, transaction_date, transaction_type, category, 
                         subcategory, amount, account, description, is_settled, refund_amount, refund_reason):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions SET 
                transaction_date = ?, transaction_type = ?, category = ?, subcategory = ?,
                amount = ?, account = ?, description = ?, is_settled = ?, 
                refund_amount = ?, refund_reason = ?
            WHERE id = ?
        ''', (transaction_date, transaction_type, category, subcategory, amount, account,
              description, is_settled, refund_amount, refund_reason, transaction_id))
        conn.commit()
        conn.close()
    
    def delete_transaction(self, transaction_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        conn.commit()
        conn.close()
    
    def get_accounts(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts ORDER BY name')
        accounts = cursor.fetchall()
        conn.close()
        return accounts
    
    def update_account_balance(self, account_name, amount_change):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE accounts SET balance = balance + ? WHERE name = ?
        ''', (amount_change, account_name))
        conn.commit()
        conn.close()
    
    def get_account_balance(self, account_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM accounts WHERE name = ?', (account_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0.0
    
    def add_transfer(self, transfer_date, from_account, to_account, amount, description):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 添加转账记录
        cursor.execute('''
            INSERT INTO transfers (transfer_date, from_account, to_account, amount, description, created_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transfer_date, from_account, to_account, amount, description, created_time))
        
        # 更新账户余额
        cursor.execute('''
            UPDATE accounts SET balance = balance - ? WHERE name = ?
        ''', (amount, from_account))
        
        cursor.execute('''
            UPDATE accounts SET balance = balance + ? WHERE name = ?
        ''', (amount, to_account))
        
        conn.commit()
        conn.close()
    
    def get_transfers(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transfers ORDER BY transfer_date DESC, created_time DESC
        ''')
        transfers = cursor.fetchall()
        conn.close()
        return transfers
    
    def get_transactions_by_date_range(self, start_date, end_date, ledger_id=None):
        """获取指定日期范围内的交易记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if ledger_id:
            cursor.execute('''
                SELECT * FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND ledger_id = ?
                ORDER BY transaction_date DESC, created_time DESC
            ''', (start_date, end_date, ledger_id))
        else:
            cursor.execute('''
                SELECT * FROM transactions 
                WHERE transaction_date BETWEEN ? AND ?
                ORDER BY transaction_date DESC, created_time DESC
            ''', (start_date, end_date))
        
        transactions = cursor.fetchall()
        conn.close()
        return transactions
    
    def get_statistics_summary(self, start_date, end_date, ledger_id=None):
        """获取收支汇总统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if ledger_id:
            # 获取收入总额和退款
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN transaction_type = "收入" THEN amount ELSE 0 END) as gross_income,
                    SUM(CASE WHEN transaction_type = "收入" THEN refund_amount ELSE 0 END) as total_refund
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND ledger_id = ?
            ''', (start_date, end_date, ledger_id))
            
            income_result = cursor.fetchone()
            gross_income = income_result[0] or 0.0
            total_refund = income_result[1] or 0.0
            
            # 获取支出总额和退款报销
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN transaction_type = "支出" THEN amount ELSE 0 END) as gross_expense,
                    SUM(CASE WHEN transaction_type = "支出" THEN refund_amount ELSE 0 END) as expense_refund
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND ledger_id = ?
            ''', (start_date, end_date, ledger_id))
            
            expense_result = cursor.fetchone()
            gross_expense = expense_result[0] or 0.0
            expense_refund = expense_result[1] or 0.0
        else:
            # 获取收入总额和退款
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN transaction_type = "收入" THEN amount ELSE 0 END) as gross_income,
                    SUM(CASE WHEN transaction_type = "收入" THEN refund_amount ELSE 0 END) as total_refund
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            income_result = cursor.fetchone()
            gross_income = income_result[0] or 0.0
            total_refund = income_result[1] or 0.0
            
            # 获取支出总额和退款报销
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN transaction_type = "支出" THEN amount ELSE 0 END) as gross_expense,
                    SUM(CASE WHEN transaction_type = "支出" THEN refund_amount ELSE 0 END) as expense_refund
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            expense_result = cursor.fetchone()
            gross_expense = expense_result[0] or 0.0
            expense_refund = expense_result[1] or 0.0
        
        conn.close()
        
        # 实际收入 = 收入总额 - 退款总额
        actual_income = gross_income - total_refund
        # 实际支出 = 支出总额 - 退款报销总额
        actual_expense = gross_expense - expense_refund
        # 净收入 = 实际收入 - 实际支出
        net_income = actual_income - actual_expense
        
        return {
            'gross_income': gross_income,
            'total_refund': total_refund,
            'actual_income': actual_income,
            'gross_expense': gross_expense,
            'expense_refund': expense_refund,
            'actual_expense': actual_expense,
            'net_income': net_income,
            'total_income': actual_income,  # 保持向后兼容
            'total_expense': actual_expense  # 保持向后兼容
        }
    
    def get_category_statistics(self, start_date, end_date, transaction_type, level="parent", ledger_id=None):
        """获取类别统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if level == "parent":
            category_field = "category"
        else:
            category_field = "subcategory"
        
        if ledger_id:
            cursor.execute(f'''
                SELECT {category_field}, SUM(ABS(amount)) as amount, COUNT(*) as count
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND ledger_id = ? AND transaction_type = ?
                GROUP BY {category_field}
                ORDER BY amount DESC
            ''', (start_date, end_date, ledger_id, transaction_type))
        else:
            cursor.execute(f'''
                SELECT {category_field}, SUM(ABS(amount)) as amount, COUNT(*) as count
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND transaction_type = ?
                GROUP BY {category_field}
                ORDER BY amount DESC
            ''', (start_date, end_date, transaction_type))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_account_statistics(self, start_date, end_date, ledger_id=None):
        """获取账户统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if ledger_id:
            cursor.execute('''
                SELECT account, 
                       SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
                       SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expense,
                       COUNT(*) as count
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND ledger_id = ? AND account IS NOT NULL AND account != ''
                GROUP BY account
                ORDER BY (income + expense) DESC
            ''', (start_date, end_date, ledger_id))
        else:
            cursor.execute('''
                SELECT account, 
                       SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
                       SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expense,
                       COUNT(*) as count
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND account IS NOT NULL AND account != ''
                GROUP BY account
                ORDER BY (income + expense) DESC
            ''', (start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_settlement_statistics(self, start_date, end_date, ledger_id=None):
        """获取销账状态统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if ledger_id:
            cursor.execute('''
                SELECT 
                    is_settled,
                    SUM(ABS(amount)) as amount,
                    COUNT(*) as count
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND ledger_id = ? AND transaction_type = '支出'
                GROUP BY is_settled
            ''', (start_date, end_date, ledger_id))
        else:
            cursor.execute('''
                SELECT 
                    is_settled,
                    SUM(ABS(amount)) as amount,
                    COUNT(*) as count
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND transaction_type = '支出'
                GROUP BY is_settled
            ''', (start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        
        settled_amount = 0.0
        unsettled_amount = 0.0
        
        for row in results:
            if row[0] == 1:  # 已销账
                settled_amount = row[1]
            else:  # 未销账
                unsettled_amount = row[1]
        
        return {
            'settled_amount': settled_amount,
            'unsettled_amount': unsettled_amount,
            'total_amount': settled_amount + unsettled_amount
        }
    
    def get_refund_statistics(self, start_date, end_date, ledger_id=None):
        """获取退款统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if ledger_id:
            cursor.execute('''
                SELECT 
                    SUM(refund_amount) as total_refund,
                    COUNT(CASE WHEN refund_amount > 0 THEN 1 END) as refund_count,
                    SUM(ABS(amount)) as total_amount,
                    COUNT(*) as total_count
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND ledger_id = ? AND transaction_type = '支出'
            ''', (start_date, end_date, ledger_id))
        else:
            cursor.execute('''
                SELECT 
                    SUM(refund_amount) as total_refund,
                    COUNT(CASE WHEN refund_amount > 0 THEN 1 END) as refund_count,
                    SUM(ABS(amount)) as total_amount,
                    COUNT(*) as total_count
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? AND transaction_type = '支出'
            ''', (start_date, end_date))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return {
                'total_refund': result[0],
                'refund_count': result[1],
                'total_amount': result[2],
                'total_count': result[3],
                'refund_ratio': (result[0] / result[2] * 100) if result[2] > 0 else 0
            }
        else:
            return {
                'total_refund': 0.0,
                'refund_count': 0,
                'total_amount': 0.0,
                'total_count': 0,
                'refund_ratio': 0.0
            }

class AddLedgerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加账本")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["个人", "家庭", "专项"])
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        
        form_layout.addRow("账本名称:", self.name_edit)
        form_layout.addRow("账本类型:", self.type_combo)
        form_layout.addRow("备注:", self.description_edit)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'name': self.name_edit.text(),
            'type': self.type_combo.currentText(),
            'description': self.description_edit.toPlainText()
        }

class CategoryButton(QPushButton):
    def __init__(self, text, category_type="normal"):
        super().__init__(text)
        self.category_type = category_type
        self.is_selected = False
        self.setup_style()
    
    def setup_style(self):
        self.update_style()
    
    def update_style(self):
        # 获取主题颜色
        colors = theme_manager.get_current_theme()["colors"]
        
        if self.is_selected:
            # 选中状态
            if self.category_type == "income":
                self.setStyleSheet(f"""
                    QPushButton {{
                        border: 2px solid {colors['income']};
                        border-radius: 6px;
                        padding: 6px 10px;
                        background-color: {colors['income']};
                        color: white;
                        font-size: 11px;
                        font-weight: bold;
                        min-height: 25px;
                        max-height: 25px;
                        min-width: 60px;
                        max-width: 100px;
                    }}
                """)
            elif self.category_type == "expense":
                self.setStyleSheet(f"""
                    QPushButton {{
                        border: 2px solid {colors['expense']};
                        border-radius: 6px;
                        padding: 6px 10px;
                        background-color: {colors['expense']};
                        color: white;
                        font-size: 11px;
                        font-weight: bold;
                        min-height: 25px;
                        max-height: 25px;
                        min-width: 60px;
                        max-width: 100px;
                    }}
                """)
            else:
                self.setStyleSheet(f"""
                    QPushButton {{
                        border: 2px solid {colors['expense']};
                        border-radius: 6px;
                        padding: 6px 10px;
                        background-color: {colors['expense']};
                        color: white;
                        font-size: 11px;
                        font-weight: bold;
                        min-height: 25px;
                        max-height: 25px;
                        min-width: 60px;
                        max-width: 100px;
                    }}
                """)
        else:
            # 未选中状态
            if self.category_type == "income":
                self.setStyleSheet(f"""
                    QPushButton {{
                        border: 2px solid {colors['income']};
                        border-radius: 6px;
                        padding: 6px 10px;
                        background-color: {colors['card_background']};
                        color: {colors['primary_text']};
                        font-size: 11px;
                        font-weight: bold;
                        min-height: 25px;
                        max-height: 25px;
                        min-width: 60px;
                        max-width: 100px;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['hover']};
                        border-color: {colors['income']};
                    }}
                """)
            elif self.category_type == "expense":
                self.setStyleSheet(f"""
                    QPushButton {{
                        border: 2px solid {colors['expense']};
                        border-radius: 6px;
                        padding: 6px 10px;
                        background-color: {colors['card_background']};
                        color: {colors['primary_text']};
                        font-size: 11px;
                        font-weight: bold;
                        min-height: 25px;
                        max-height: 25px;
                        min-width: 60px;
                        max-width: 100px;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['hover']};
                        border-color: {colors['expense']};
                    }}
                """)
            else:
                self.setStyleSheet(f"""
                    QPushButton {{
                        border: 2px solid {colors['expense']};
                        border-radius: 6px;
                        padding: 6px 10px;
                        background-color: {colors['card_background']};
                        color: {colors['primary_text']};
                        font-size: 11px;
                        font-weight: bold;
                        min-height: 25px;
                        max-height: 25px;
                        min-width: 60px;
                        max-width: 100px;
                    }}
                    QPushButton:hover {{
                        background-color: {colors['hover']};
                        border-color: {colors['expense']};
                    }}
                """)
    
    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

class EditIncomeDialog(QDialog):
    def __init__(self, db_manager, transaction_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.transaction_data = transaction_data
        self.setWindowTitle("编辑收入记录")
        self.setModal(True)
        self.selected_category = None
        self.selected_subcategory = None
        self.transaction_type = "收入"
        self.setup_ui()
        self.load_income_categories()
        self.load_transaction_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息区域
        basic_info_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        
        # 交易时间
        self.date_edit = QDateTimeEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        # 金额
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("¥")
        
        # 账户
        self.account_combo = QComboBox()
        self.load_accounts()
        
        basic_layout.addRow("交易时间:", self.date_edit)
        basic_layout.addRow("金额:", self.amount_spin)
        basic_layout.addRow("账户:", self.account_combo)
        
        basic_info_group.setLayout(basic_layout)
        layout.addWidget(basic_info_group)
        
        # 类别选择区域
        category_group = QGroupBox("收入类别选择")
        category_layout = QVBoxLayout()
        
        # 主类别卡片区域
        main_category_label = QLabel("主类别:")
        main_category_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        category_layout.addWidget(main_category_label)
        
        # 创建滚动区域
        self.main_category_scroll = QScrollArea()
        self.main_category_scroll.setWidgetResizable(True)
        self.main_category_scroll.setMaximumHeight(60)
        self.main_category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.main_category_content = QWidget()
        self.main_category_grid_layout = QVBoxLayout()
        self.main_category_content.setLayout(self.main_category_grid_layout)
        self.main_category_scroll.setWidget(self.main_category_content)
        
        category_layout.addWidget(self.main_category_scroll)
        
        # 子类别卡片区域
        self.subcategory_label = QLabel("子类别:")
        self.subcategory_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.subcategory_label.setVisible(False)
        category_layout.addWidget(self.subcategory_label)
        
        self.subcategory_scroll = QScrollArea()
        self.subcategory_scroll.setWidgetResizable(True)
        self.subcategory_scroll.setMaximumHeight(60)
        self.subcategory_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.subcategory_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.subcategory_content = QWidget()
        self.subcategory_grid_layout = QVBoxLayout()
        self.subcategory_content.setLayout(self.subcategory_grid_layout)
        self.subcategory_scroll.setWidget(self.subcategory_content)
        self.subcategory_scroll.setVisible(False)
        
        category_layout.addWidget(self.subcategory_scroll)
        
        category_group.setLayout(category_layout)
        layout.addWidget(category_group)
        
        # 其他信息区域
        other_info_group = QGroupBox("其他信息")
        other_layout = QFormLayout()
        
        # 备注
        self.description_edit = QLineEdit()
        
        other_layout.addRow("备注:", self.description_edit)
        
        other_info_group.setLayout(other_layout)
        layout.addWidget(other_info_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_income_categories(self):
        categories = self.db_manager.get_categories("收入")
        
        # 按主类别分组
        income_categories = {}
        for parent, sub in categories:
            if parent not in income_categories:
                income_categories[parent] = []
            income_categories[parent].append(sub)
        
        # 创建主类别按钮 - 使用网格布局
        from PyQt6.QtWidgets import QGridLayout
        
        # 收入类别行
        income_row_widget = QWidget()
        income_row_layout = QHBoxLayout()
        income_row_layout.setSpacing(5)
        income_row_layout.setContentsMargins(0, 0, 0, 0)
        
        for category in income_categories.keys():
            btn = CategoryButton(category, "income")
            btn.clicked.connect(lambda checked, cat=category: self.on_main_category_clicked(cat))
            income_row_layout.addWidget(btn)
        
        income_row_layout.addStretch()
        income_row_widget.setLayout(income_row_layout)
        self.main_category_grid_layout.addWidget(income_row_widget)
        
        # 存储子类别数据
        self.subcategories = income_categories
    
    def load_accounts(self):
        accounts = self.db_manager.get_accounts()
        self.account_combo.addItem("")
        for account in accounts:
            self.account_combo.addItem(account[1])
    
    def load_transaction_data(self):
        if self.transaction_data:
            (trans_id, ledger_id, transaction_date, transaction_type, category, subcategory, 
             amount, account, description, is_settled, refund_amount, 
             refund_reason, created_time) = self.transaction_data
            
            self.date_edit.setDate(QDate.fromString(transaction_date, "yyyy-MM-dd"))
            self.amount_spin.setValue(abs(amount))
            self.account_combo.setCurrentText(account or "")
            self.description_edit.setText(description or "")
            
            # 设置类别
            if category:
                self.selected_category = category
                self.show_subcategories(category)
                # 设置子类别
                if subcategory:
                    self.selected_subcategory = subcategory
    
    def on_main_category_clicked(self, category):
        # 清除之前的选择
        for i in range(self.main_category_grid_layout.count()):
            row_widget = self.main_category_grid_layout.itemAt(i).widget()
            if row_widget:
                for j in range(row_widget.layout().count()):
                    widget = row_widget.layout().itemAt(j).widget()
                    if isinstance(widget, CategoryButton):
                        widget.set_selected(False)
        
        # 设置当前选择
        sender = self.sender()
        if isinstance(sender, CategoryButton):
            sender.set_selected(True)
            self.selected_category = category
            
            # 显示子类别
            self.show_subcategories(category)
    
    def show_subcategories(self, category):
        # 清除之前的子类别按钮
        for i in reversed(range(self.subcategory_grid_layout.count())):
            child = self.subcategory_grid_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加新的子类别按钮 - 使用横向布局
        if category in self.subcategories:
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            for subcategory in self.subcategories[category]:
                btn = CategoryButton(subcategory, "expense")
                btn.clicked.connect(lambda checked, sub=subcategory: self.on_subcategory_clicked(sub))
                row_layout.addWidget(btn)
            
            row_layout.addStretch()
            row_widget.setLayout(row_layout)
            self.subcategory_grid_layout.addWidget(row_widget)
        
        # 确保子类别内容被正确设置到滚动区域
        self.subcategory_scroll.setWidget(self.subcategory_content)
        
        # 显示子类别区域
        self.subcategory_label.setVisible(True)
        self.subcategory_scroll.setVisible(True)
    
    def on_subcategory_clicked(self, subcategory):
        # 清除之前的选择
        for i in range(self.subcategory_grid_layout.count()):
            row_widget = self.subcategory_grid_layout.itemAt(i).widget()
            if row_widget:
                for j in range(row_widget.layout().count()):
                    widget = row_widget.layout().itemAt(j).widget()
                    if isinstance(widget, CategoryButton):
                        widget.set_selected(False)
        
        # 设置当前选择
        sender = self.sender()
        if isinstance(sender, CategoryButton):
            sender.set_selected(True)
            self.selected_subcategory = subcategory
    
    def get_data(self):
        return {
            'id': self.transaction_data[0] if self.transaction_data else None,
            'transaction_date': self.date_edit.date().toString("yyyy-MM-dd"),
            'transaction_type': self.transaction_type,
            'category': self.selected_category or "",
            'subcategory': self.selected_subcategory or "",
            'amount': self.amount_spin.value(),
            'account': self.account_combo.currentText(),
            'description': self.description_edit.text(),
            'is_settled': False,
            'refund_amount': 0.0,
            'refund_reason': ""
        }

class AddIncomeDialog(QDialog):
    def __init__(self, db_manager, ledger_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.ledger_id = ledger_id
        self.setWindowTitle("添加收入记录")
        self.setModal(True)
        self.selected_category = None
        self.selected_subcategory = None
        self.transaction_type = "收入"
        self.setup_ui()
        self.load_income_categories()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息区域
        basic_info_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        
        # 交易时间
        self.date_edit = QDateTimeEdit()
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        # 金额
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("¥")
        
        # 账户
        self.account_combo = QComboBox()
        self.load_accounts()
        
        basic_layout.addRow("交易时间:", self.date_edit)
        basic_layout.addRow("金额:", self.amount_spin)
        basic_layout.addRow("账户:", self.account_combo)
        
        basic_info_group.setLayout(basic_layout)
        layout.addWidget(basic_info_group)
        
        # 类别选择区域
        category_group = QGroupBox("收入类别选择")
        category_layout = QVBoxLayout()
        
        # 主类别卡片区域
        main_category_label = QLabel("主类别:")
        main_category_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        category_layout.addWidget(main_category_label)
        
        # 创建滚动区域
        self.main_category_scroll = QScrollArea()
        self.main_category_scroll.setWidgetResizable(True)
        self.main_category_scroll.setMaximumHeight(60)
        self.main_category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.main_category_content = QWidget()
        self.main_category_grid_layout = QVBoxLayout()
        self.main_category_content.setLayout(self.main_category_grid_layout)
        self.main_category_scroll.setWidget(self.main_category_content)
        
        category_layout.addWidget(self.main_category_scroll)
        
        # 子类别卡片区域
        self.subcategory_label = QLabel("子类别:")
        self.subcategory_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.subcategory_label.setVisible(False)
        category_layout.addWidget(self.subcategory_label)
        
        self.subcategory_scroll = QScrollArea()
        self.subcategory_scroll.setWidgetResizable(True)
        self.subcategory_scroll.setMaximumHeight(60)
        self.subcategory_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.subcategory_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.subcategory_content = QWidget()
        self.subcategory_grid_layout = QVBoxLayout()
        self.subcategory_content.setLayout(self.subcategory_grid_layout)
        self.subcategory_scroll.setWidget(self.subcategory_content)
        self.subcategory_scroll.setVisible(False)
        
        category_layout.addWidget(self.subcategory_scroll)
        
        category_group.setLayout(category_layout)
        layout.addWidget(category_group)
        
        # 其他信息区域
        other_info_group = QGroupBox("其他信息")
        other_layout = QFormLayout()
        
        # 备注
        self.description_edit = QLineEdit()
        
        other_layout.addRow("备注:", self.description_edit)
        
        other_info_group.setLayout(other_layout)
        layout.addWidget(other_info_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        add_more_button = QPushButton("再记")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        add_more_button.clicked.connect(self.add_more)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(add_more_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # 标记是否是"再记"操作
        self.is_add_more = False
    
    def load_income_categories(self):
        categories = self.db_manager.get_categories("收入")
        
        # 按主类别分组
        income_categories = {}
        for parent, sub in categories:
            if parent not in income_categories:
                income_categories[parent] = []
            income_categories[parent].append(sub)
        
        # 创建主类别按钮 - 使用网格布局
        from PyQt6.QtWidgets import QGridLayout
        
        # 收入类别行
        income_row_widget = QWidget()
        income_row_layout = QHBoxLayout()
        income_row_layout.setSpacing(5)
        income_row_layout.setContentsMargins(0, 0, 0, 0)
        
        for category in income_categories.keys():
            btn = CategoryButton(category, "income")
            btn.clicked.connect(lambda checked, cat=category: self.on_main_category_clicked(cat))
            income_row_layout.addWidget(btn)
        
        income_row_layout.addStretch()
        income_row_widget.setLayout(income_row_layout)
        self.main_category_grid_layout.addWidget(income_row_widget)
        
        # 存储子类别数据
        self.subcategories = income_categories
    
    def load_accounts(self):
        accounts = self.db_manager.get_accounts()
        self.account_combo.addItem("")
        for account in accounts:
            self.account_combo.addItem(account[1])
    
    def on_main_category_clicked(self, category):
        # 清除之前的选择
        for i in range(self.main_category_grid_layout.count()):
            row_widget = self.main_category_grid_layout.itemAt(i).widget()
            if row_widget:
                for j in range(row_widget.layout().count()):
                    widget = row_widget.layout().itemAt(j).widget()
                    if isinstance(widget, CategoryButton):
                        widget.set_selected(False)
        
        # 设置当前选择
        sender = self.sender()
        if isinstance(sender, CategoryButton):
            sender.set_selected(True)
            self.selected_category = category
            
            # 显示子类别
            self.show_subcategories(category)
    
    def show_subcategories(self, category):
        # 清除之前的子类别按钮
        for i in reversed(range(self.subcategory_grid_layout.count())):
            child = self.subcategory_grid_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加新的子类别按钮 - 使用横向布局
        if category in self.subcategories:
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            for subcategory in self.subcategories[category]:
                btn = CategoryButton(subcategory, "expense")
                btn.clicked.connect(lambda checked, sub=subcategory: self.on_subcategory_clicked(sub))
                row_layout.addWidget(btn)
            
            row_layout.addStretch()
            row_widget.setLayout(row_layout)
            self.subcategory_grid_layout.addWidget(row_widget)
        
        # 确保子类别内容被正确设置到滚动区域
        self.subcategory_scroll.setWidget(self.subcategory_content)
        
        # 显示子类别区域
        self.subcategory_label.setVisible(True)
        self.subcategory_scroll.setVisible(True)
    
    def on_subcategory_clicked(self, subcategory):
        # 清除之前的选择
        for i in range(self.subcategory_grid_layout.count()):
            row_widget = self.subcategory_grid_layout.itemAt(i).widget()
            if row_widget:
                for j in range(row_widget.layout().count()):
                    widget = row_widget.layout().itemAt(j).widget()
                    if isinstance(widget, CategoryButton):
                        widget.set_selected(False)
        
        # 设置当前选择
        sender = self.sender()
        if isinstance(sender, CategoryButton):
            sender.set_selected(True)
            self.selected_subcategory = subcategory
    
    def add_more(self):
        self.is_add_more = True
        self.accept()
    
    def get_data(self):
        return {
            'transaction_date': self.date_edit.date().toString("yyyy-MM-dd"),
            'transaction_type': self.transaction_type,
            'category': self.selected_category or "",
            'subcategory': self.selected_subcategory or "",
            'amount': self.amount_spin.value(),
            'account': self.account_combo.currentText(),
            'description': self.description_edit.text(),
            'is_settled': False,
            'refund_amount': 0.0,
            'refund_reason': ""
        }

class EditExpenseDialog(QDialog):
    def __init__(self, db_manager, transaction_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.transaction_data = transaction_data
        self.setWindowTitle("编辑支出记录")
        self.setModal(True)
        self.selected_category = None
        self.selected_subcategory = None
        self.transaction_type = "支出"
        self.setup_ui()
        self.load_expense_categories()
        self.load_transaction_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息区域
        basic_info_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        
        # 交易时间
        self.date_edit = QDateTimeEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        # 金额
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("¥")
        
        # 账户
        self.account_combo = QComboBox()
        self.load_accounts()
        
        basic_layout.addRow("交易时间:", self.date_edit)
        basic_layout.addRow("金额:", self.amount_spin)
        basic_layout.addRow("账户:", self.account_combo)
        
        basic_info_group.setLayout(basic_layout)
        layout.addWidget(basic_info_group)
        
        # 类别选择区域
        category_group = QGroupBox("支出类别选择")
        category_layout = QVBoxLayout()
        
        # 主类别卡片区域
        main_category_label = QLabel("主类别:")
        main_category_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        category_layout.addWidget(main_category_label)
        
        # 创建滚动区域
        self.main_category_scroll = QScrollArea()
        self.main_category_scroll.setWidgetResizable(True)
        self.main_category_scroll.setMaximumHeight(80)
        self.main_category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.main_category_content = QWidget()
        self.main_category_grid_layout = QVBoxLayout()
        self.main_category_content.setLayout(self.main_category_grid_layout)
        self.main_category_scroll.setWidget(self.main_category_content)
        
        category_layout.addWidget(self.main_category_scroll)
        
        # 子类别卡片区域
        self.subcategory_label = QLabel("子类别:")
        self.subcategory_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.subcategory_label.setVisible(False)
        category_layout.addWidget(self.subcategory_label)
        
        self.subcategory_scroll = QScrollArea()
        self.subcategory_scroll.setWidgetResizable(True)
        self.subcategory_scroll.setMaximumHeight(60)
        self.subcategory_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.subcategory_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.subcategory_content = QWidget()
        self.subcategory_grid_layout = QVBoxLayout()
        self.subcategory_content.setLayout(self.subcategory_grid_layout)
        self.subcategory_scroll.setWidget(self.subcategory_content)
        self.subcategory_scroll.setVisible(False)
        
        category_layout.addWidget(self.subcategory_scroll)
        
        category_group.setLayout(category_layout)
        layout.addWidget(category_group)
        
        # 其他信息区域
        other_info_group = QGroupBox("其他信息")
        other_layout = QFormLayout()
        
        # 备注
        self.description_edit = QLineEdit()
        
        # 销账标记
        self.settled_check = QCheckBox("已销账")
        
        # 退款信息
        self.refund_amount_spin = QDoubleSpinBox()
        self.refund_amount_spin.setRange(0, 999999.99)
        self.refund_amount_spin.setDecimals(2)
        self.refund_amount_spin.setPrefix("¥")
        self.refund_reason_edit = QLineEdit()
        
        other_layout.addRow("备注:", self.description_edit)
        other_layout.addRow("", self.settled_check)
        other_layout.addRow("退款金额:", self.refund_amount_spin)
        other_layout.addRow("退款原因:", self.refund_reason_edit)
        
        other_info_group.setLayout(other_layout)
        layout.addWidget(other_info_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_expense_categories(self):
        categories = self.db_manager.get_categories("支出")
        
        # 按主类别分组
        expense_categories = {}
        for parent, sub in categories:
            if parent not in expense_categories:
                expense_categories[parent] = []
            expense_categories[parent].append(sub)
        
        # 创建主类别按钮 - 使用网格布局
        from PyQt6.QtWidgets import QGridLayout
        
        # 支出类别行
        expense_row_widget = QWidget()
        expense_row_layout = QHBoxLayout()
        expense_row_layout.setSpacing(5)
        expense_row_layout.setContentsMargins(0, 0, 0, 0)
        
        for category in expense_categories.keys():
            btn = CategoryButton(category, "expense")
            btn.clicked.connect(lambda checked, cat=category: self.on_main_category_clicked(cat))
            expense_row_layout.addWidget(btn)
        
        expense_row_layout.addStretch()
        expense_row_widget.setLayout(expense_row_layout)
        self.main_category_grid_layout.addWidget(expense_row_widget)
        
        # 存储子类别数据
        self.subcategories = expense_categories
    
    def load_accounts(self):
        accounts = self.db_manager.get_accounts()
        self.account_combo.addItem("")
        for account in accounts:
            self.account_combo.addItem(account[1])
    
    def load_transaction_data(self):
        if self.transaction_data:
            (trans_id, ledger_id, transaction_date, transaction_type, category, subcategory, 
             amount, account, description, is_settled, refund_amount, 
             refund_reason, created_time) = self.transaction_data
            
            self.date_edit.setDate(QDate.fromString(transaction_date, "yyyy-MM-dd"))
            self.amount_spin.setValue(abs(amount))
            self.account_combo.setCurrentText(account or "")
            self.description_edit.setText(description or "")
            self.settled_check.setChecked(is_settled)
            self.refund_amount_spin.setValue(refund_amount)
            self.refund_reason_edit.setText(refund_reason or "")
            
            # 设置类别
            if category:
                self.selected_category = category
                self.show_subcategories(category)
                # 设置子类别
                if subcategory:
                    self.selected_subcategory = subcategory
    
    def on_main_category_clicked(self, category):
        # 清除之前的选择
        for i in range(self.main_category_grid_layout.count()):
            row_widget = self.main_category_grid_layout.itemAt(i).widget()
            if row_widget:
                for j in range(row_widget.layout().count()):
                    widget = row_widget.layout().itemAt(j).widget()
                    if isinstance(widget, CategoryButton):
                        widget.set_selected(False)
        
        # 设置当前选择
        sender = self.sender()
        if isinstance(sender, CategoryButton):
            sender.set_selected(True)
            self.selected_category = category
            
            # 显示子类别
            self.show_subcategories(category)
    
    def show_subcategories(self, category):
        # 清除之前的子类别按钮
        for i in reversed(range(self.subcategory_grid_layout.count())):
            child = self.subcategory_grid_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加新的子类别按钮 - 使用横向布局
        if category in self.subcategories:
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            for subcategory in self.subcategories[category]:
                btn = CategoryButton(subcategory, "expense")
                btn.clicked.connect(lambda checked, sub=subcategory: self.on_subcategory_clicked(sub))
                row_layout.addWidget(btn)
            
            row_layout.addStretch()
            row_widget.setLayout(row_layout)
            self.subcategory_grid_layout.addWidget(row_widget)
        
        # 确保子类别内容被正确设置到滚动区域
        self.subcategory_scroll.setWidget(self.subcategory_content)
        
        # 显示子类别区域
        self.subcategory_label.setVisible(True)
        self.subcategory_scroll.setVisible(True)
    
    def on_subcategory_clicked(self, subcategory):
        # 清除之前的选择
        for i in range(self.subcategory_grid_layout.count()):
            row_widget = self.subcategory_grid_layout.itemAt(i).widget()
            if row_widget:
                for j in range(row_widget.layout().count()):
                    widget = row_widget.layout().itemAt(j).widget()
                    if isinstance(widget, CategoryButton):
                        widget.set_selected(False)
        
        # 设置当前选择
        sender = self.sender()
        if isinstance(sender, CategoryButton):
            sender.set_selected(True)
            self.selected_subcategory = subcategory
    
    def get_data(self):
        return {
            'id': self.transaction_data[0] if self.transaction_data else None,
            'transaction_date': self.date_edit.date().toString("yyyy-MM-dd"),
            'transaction_type': self.transaction_type,
            'category': self.selected_category or "",
            'subcategory': self.selected_subcategory or "",
            'amount': -self.amount_spin.value(),  # 支出为负数
            'account': self.account_combo.currentText(),
            'description': self.description_edit.text(),
            'is_settled': self.settled_check.isChecked(),
            'refund_amount': self.refund_amount_spin.value(),
            'refund_reason': self.refund_reason_edit.text()
        }

class AddExpenseDialog(QDialog):
    def __init__(self, db_manager, ledger_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.ledger_id = ledger_id
        self.setWindowTitle("添加支出记录")
        self.setModal(True)
        self.selected_category = None
        self.selected_subcategory = None
        self.transaction_type = "支出"
        self.setup_ui()
        self.load_expense_categories()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息区域
        basic_info_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        
        # 交易时间
        self.date_edit = QDateTimeEdit()
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        # 金额
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("¥")
        
        # 账户
        self.account_combo = QComboBox()
        self.load_accounts()
        
        basic_layout.addRow("交易时间:", self.date_edit)
        basic_layout.addRow("金额:", self.amount_spin)
        basic_layout.addRow("账户:", self.account_combo)
        
        basic_info_group.setLayout(basic_layout)
        layout.addWidget(basic_info_group)
        
        # 类别选择区域
        category_group = QGroupBox("支出类别选择")
        category_layout = QVBoxLayout()
        
        # 主类别卡片区域
        main_category_label = QLabel("主类别:")
        main_category_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        category_layout.addWidget(main_category_label)
        
        # 创建滚动区域
        self.main_category_scroll = QScrollArea()
        self.main_category_scroll.setWidgetResizable(True)
        self.main_category_scroll.setMaximumHeight(80)
        self.main_category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.main_category_content = QWidget()
        self.main_category_grid_layout = QVBoxLayout()
        self.main_category_content.setLayout(self.main_category_grid_layout)
        self.main_category_scroll.setWidget(self.main_category_content)
        
        category_layout.addWidget(self.main_category_scroll)
        
        # 子类别卡片区域
        self.subcategory_label = QLabel("子类别:")
        self.subcategory_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.subcategory_label.setVisible(False)
        category_layout.addWidget(self.subcategory_label)
        
        self.subcategory_scroll = QScrollArea()
        self.subcategory_scroll.setWidgetResizable(True)
        self.subcategory_scroll.setMaximumHeight(60)
        self.subcategory_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.subcategory_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.subcategory_content = QWidget()
        self.subcategory_grid_layout = QVBoxLayout()
        self.subcategory_content.setLayout(self.subcategory_grid_layout)
        self.subcategory_scroll.setVisible(False)
        
        category_layout.addWidget(self.subcategory_scroll)
        
        category_group.setLayout(category_layout)
        layout.addWidget(category_group)
        
        # 其他信息区域
        other_info_group = QGroupBox("其他信息")
        other_layout = QFormLayout()
        
        # 备注
        self.description_edit = QLineEdit()
        
        # 销账标记
        self.settled_check = QCheckBox("已销账")
        
        # 退款信息
        self.refund_amount_spin = QDoubleSpinBox()
        self.refund_amount_spin.setRange(0, 999999.99)
        self.refund_amount_spin.setDecimals(2)
        self.refund_amount_spin.setPrefix("¥")
        self.refund_reason_edit = QLineEdit()
        
        other_layout.addRow("备注:", self.description_edit)
        other_layout.addRow("", self.settled_check)
        other_layout.addRow("退款金额:", self.refund_amount_spin)
        other_layout.addRow("退款原因:", self.refund_reason_edit)
        
        other_info_group.setLayout(other_layout)
        layout.addWidget(other_info_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        add_more_button = QPushButton("再记")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        add_more_button.clicked.connect(self.add_more)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(add_more_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # 标记是否是"再记"操作
        self.is_add_more = False
    
    def load_expense_categories(self):
        categories = self.db_manager.get_categories("支出")
        
        # 按主类别分组
        expense_categories = {}
        for parent, sub in categories:
            if parent not in expense_categories:
                expense_categories[parent] = []
            expense_categories[parent].append(sub)
        
        # 创建主类别按钮 - 使用网格布局
        from PyQt6.QtWidgets import QGridLayout
        
        # 支出类别行
        expense_row_widget = QWidget()
        expense_row_layout = QHBoxLayout()
        expense_row_layout.setSpacing(5)
        expense_row_layout.setContentsMargins(0, 0, 0, 0)
        
        for category in expense_categories.keys():
            btn = CategoryButton(category, "expense")
            btn.clicked.connect(lambda checked, cat=category: self.on_main_category_clicked(cat))
            expense_row_layout.addWidget(btn)
        
        expense_row_layout.addStretch()
        expense_row_widget.setLayout(expense_row_layout)
        self.main_category_grid_layout.addWidget(expense_row_widget)
        
        # 存储子类别数据
        self.subcategories = expense_categories
    
    def load_accounts(self):
        accounts = self.db_manager.get_accounts()
        self.account_combo.addItem("")
        for account in accounts:
            self.account_combo.addItem(account[1])
    
    def on_main_category_clicked(self, category):
        # 清除之前的选择
        for i in range(self.main_category_grid_layout.count()):
            row_widget = self.main_category_grid_layout.itemAt(i).widget()
            if row_widget:
                for j in range(row_widget.layout().count()):
                    widget = row_widget.layout().itemAt(j).widget()
                    if isinstance(widget, CategoryButton):
                        widget.set_selected(False)
        
        # 设置当前选择
        sender = self.sender()
        if isinstance(sender, CategoryButton):
            sender.set_selected(True)
            self.selected_category = category
            
            # 显示子类别
            self.show_subcategories(category)
    
    def show_subcategories(self, category):
        # 清除之前的子类别按钮
        for i in reversed(range(self.subcategory_grid_layout.count())):
            child = self.subcategory_grid_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加新的子类别按钮 - 使用横向布局
        if category in self.subcategories:
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            for subcategory in self.subcategories[category]:
                btn = CategoryButton(subcategory, "expense")
                btn.clicked.connect(lambda checked, sub=subcategory: self.on_subcategory_clicked(sub))
                row_layout.addWidget(btn)
            
            row_layout.addStretch()
            row_widget.setLayout(row_layout)
            self.subcategory_grid_layout.addWidget(row_widget)
        
        # 确保子类别内容被正确设置到滚动区域
        self.subcategory_scroll.setWidget(self.subcategory_content)
        
        # 显示子类别区域
        self.subcategory_label.setVisible(True)
        self.subcategory_scroll.setVisible(True)
    
    def on_subcategory_clicked(self, subcategory):
        # 清除之前的选择
        for i in range(self.subcategory_grid_layout.count()):
            row_widget = self.subcategory_grid_layout.itemAt(i).widget()
            if row_widget:
                for j in range(row_widget.layout().count()):
                    widget = row_widget.layout().itemAt(j).widget()
                    if isinstance(widget, CategoryButton):
                        widget.set_selected(False)
        
        # 设置当前选择
        sender = self.sender()
        if isinstance(sender, CategoryButton):
            sender.set_selected(True)
            self.selected_subcategory = subcategory
    
    def add_more(self):
        self.is_add_more = True
        self.accept()
    
    def get_data(self):
        return {
            'transaction_date': self.date_edit.date().toString("yyyy-MM-dd"),
            'transaction_type': self.transaction_type,
            'category': self.selected_category or "",
            'subcategory': self.selected_subcategory or "",
            'amount': -self.amount_spin.value(),  # 支出为负数
            'account': self.account_combo.currentText(),
            'description': self.description_edit.text(),
            'is_settled': self.settled_check.isChecked(),
            'refund_amount': self.refund_amount_spin.value(),
            'refund_reason': self.refund_reason_edit.text()
        }

class EditAccountDialog(QDialog):
    def __init__(self, account_data, parent=None):
        super().__init__(parent)
        self.account_data = account_data
        self.setWindowTitle("编辑账户")
        self.setModal(True)
        self.setup_ui()
        self.load_account_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["现金", "银行卡", "电子支付", "其他"])
        self.bank_edit = QLineEdit()
        self.balance_spin = QDoubleSpinBox()
        self.balance_spin.setRange(0, 999999.99)
        self.balance_spin.setDecimals(2)
        self.balance_spin.setPrefix("¥")
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        
        form_layout.addRow("账户名称:", self.name_edit)
        form_layout.addRow("账户类型:", self.type_combo)
        form_layout.addRow("开户行:", self.bank_edit)
        form_layout.addRow("初始余额:", self.balance_spin)
        form_layout.addRow("备注:", self.description_edit)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_account_data(self):
        if self.account_data:
            (account_id, name, account_type, balance, bank, description) = self.account_data
            self.name_edit.setText(name)
            self.type_combo.setCurrentText(account_type)
            self.bank_edit.setText(bank or "")
            self.balance_spin.setValue(balance)
            self.description_edit.setPlainText(description or "")
    
    def get_data(self):
        return {
            'id': self.account_data[0] if self.account_data else None,
            'name': self.name_edit.text(),
            'type': self.type_combo.currentText(),
            'bank': self.bank_edit.text(),
            'balance': self.balance_spin.value(),
            'description': self.description_edit.toPlainText()
        }

class AddAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加账户")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["现金", "银行卡", "电子支付", "其他"])
        self.bank_edit = QLineEdit()
        self.balance_spin = QDoubleSpinBox()
        self.balance_spin.setRange(0, 999999.99)
        self.balance_spin.setDecimals(2)
        self.balance_spin.setPrefix("¥")
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        
        form_layout.addRow("账户名称:", self.name_edit)
        form_layout.addRow("账户类型:", self.type_combo)
        form_layout.addRow("开户行:", self.bank_edit)
        form_layout.addRow("初始余额:", self.balance_spin)
        form_layout.addRow("备注:", self.description_edit)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'name': self.name_edit.text(),
            'type': self.type_combo.currentText(),
            'bank': self.bank_edit.text(),
            'balance': self.balance_spin.value(),
            'description': self.description_edit.toPlainText()
        }

class TransferDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("资金流转")
        self.setModal(True)
        self.setup_ui()
        self.load_accounts()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # 转账日期
        self.date_edit = QDateTimeEdit()
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        # 转出账户
        self.from_account_combo = QComboBox()
        
        # 转入账户
        self.to_account_combo = QComboBox()
        
        # 转账金额
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("¥")
        
        # 备注
        self.description_edit = QLineEdit()
        
        form_layout.addRow("转账日期:", self.date_edit)
        form_layout.addRow("转出账户:", self.from_account_combo)
        form_layout.addRow("转入账户:", self.to_account_combo)
        form_layout.addRow("转账金额:", self.amount_spin)
        form_layout.addRow("备注:", self.description_edit)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_accounts(self):
        accounts = self.db_manager.get_accounts()
        self.from_account_combo.clear()
        self.to_account_combo.clear()
        
        for account in accounts:
            self.from_account_combo.addItem(f"{account[1]} (余额: ¥{account[3]:.2f})")
            self.to_account_combo.addItem(f"{account[1]} (余额: ¥{account[3]:.2f})")
    
    def get_data(self):
        # 提取账户名称（去掉余额信息）
        from_account = self.from_account_combo.currentText().split(" (余额:")[0]
        to_account = self.to_account_combo.currentText().split(" (余额:")[0]
        
        return {
            'transfer_date': self.date_edit.date().toString("yyyy-MM-dd"),
            'from_account': from_account,
            'to_account': to_account,
            'amount': self.amount_spin.value(),
            'description': self.description_edit.text()
        }

class AssetManagementWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.load_accounts()
        self.load_transfers()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 账户管理区域
        account_group = QGroupBox("账户管理")
        account_layout = QVBoxLayout()
        
        # 账户操作按钮
        account_btn_layout = QHBoxLayout()
        add_account_btn = QPushButton("添加账户")
        add_account_btn.clicked.connect(self.add_account)
        edit_account_btn = QPushButton("编辑账户")
        edit_account_btn.clicked.connect(self.edit_account)
        delete_account_btn = QPushButton("删除账户")
        delete_account_btn.clicked.connect(self.delete_account)
        account_btn_layout.addWidget(add_account_btn)
        account_btn_layout.addWidget(edit_account_btn)
        account_btn_layout.addWidget(delete_account_btn)
        account_btn_layout.addStretch()
        account_layout.addLayout(account_btn_layout)
        
        # 账户表格
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(5)
        self.account_table.setHorizontalHeaderLabels(["账户名称", "类型", "开户行", "余额", "备注"])
        self.account_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        account_layout.addWidget(self.account_table)
        
        account_group.setLayout(account_layout)
        layout.addWidget(account_group)
        
        # 资金流转区域
        transfer_group = QGroupBox("资金流转")
        transfer_layout = QVBoxLayout()
        
        # 转账按钮
        transfer_btn_layout = QHBoxLayout()
        add_transfer_btn = QPushButton("新增转账")
        add_transfer_btn.clicked.connect(self.add_transfer)
        transfer_btn_layout.addWidget(add_transfer_btn)
        transfer_btn_layout.addStretch()
        transfer_layout.addLayout(transfer_btn_layout)
        
        # 转账记录表格
        self.transfer_table = QTableWidget()
        self.transfer_table.setColumnCount(5)
        self.transfer_table.setHorizontalHeaderLabels(["转账日期", "转出账户", "转入账户", "金额", "备注"])
        self.transfer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        transfer_layout.addWidget(self.transfer_table)
        
        transfer_group.setLayout(transfer_layout)
        layout.addWidget(transfer_group)
        
        self.setLayout(layout)
    
    def load_accounts(self):
        accounts = self.db_manager.get_accounts()
        self.account_table.setRowCount(len(accounts))
        
        for row, account in enumerate(accounts):
            (account_id, name, account_type, balance, bank, description) = account
            self.account_table.setItem(row, 0, QTableWidgetItem(name))
            self.account_table.setItem(row, 1, QTableWidgetItem(account_type))
            self.account_table.setItem(row, 2, QTableWidgetItem(bank or ""))
            self.account_table.setItem(row, 3, QTableWidgetItem(f"¥{balance:.2f}"))
            self.account_table.setItem(row, 4, QTableWidgetItem(description or ""))
    
    def load_transfers(self):
        transfers = self.db_manager.get_transfers()
        self.transfer_table.setRowCount(len(transfers))
        
        for row, transfer in enumerate(transfers):
            (transfer_id, transfer_date, from_account, to_account, amount, description, created_time) = transfer
            self.transfer_table.setItem(row, 0, QTableWidgetItem(transfer_date))
            self.transfer_table.setItem(row, 1, QTableWidgetItem(from_account))
            self.transfer_table.setItem(row, 2, QTableWidgetItem(to_account))
            self.transfer_table.setItem(row, 3, QTableWidgetItem(f"¥{amount:.2f}"))
            self.transfer_table.setItem(row, 4, QTableWidgetItem(description or ""))
    
    def add_account(self):
        dialog = AddAccountDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['name']:
                self.db_manager.add_account(
                    data['name'], data['type'], data['balance'], 
                    data['bank'], data['description']
                )
                self.load_accounts()
                # 刷新统计页面
                parent = self.parent()
                if parent and hasattr(parent, 'statistics_widget'):
                    parent.statistics_widget.update_statistics()
                QMessageBox.information(self, "成功", "账户添加成功！")
    
    def edit_account(self):
        current_row = self.account_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的账户！")
            return
        
        # 获取选中的账户数据
        account_name = self.account_table.item(current_row, 0).text()
        accounts = self.db_manager.get_accounts()
        account_data = None
        for account in accounts:
            if account[1] == account_name:
                account_data = account
                break
        
        if not account_data:
            QMessageBox.warning(self, "警告", "找不到选中的账户数据！")
            return
        
        dialog = EditAccountDialog(account_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['name']:
                self.db_manager.update_account(
                    data['id'], data['name'], data['type'], data['balance'],
                    data['bank'], data['description']
                )
                self.load_accounts()
                # 刷新统计页面
                parent = self.parent()
                if parent and hasattr(parent, 'statistics_widget'):
                    parent.statistics_widget.update_statistics()
                QMessageBox.information(self, "成功", "账户修改成功！")
    
    def delete_account(self):
        current_row = self.account_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的账户！")
            return
        
        account_name = self.account_table.item(current_row, 0).text()
        accounts = self.db_manager.get_accounts()
        account_data = None
        for account in accounts:
            if account[1] == account_name:
                account_data = account
                break
        
        if not account_data:
            QMessageBox.warning(self, "警告", "找不到选中的账户数据！")
            return
        
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除账户 '{account_name}' 吗？删除后将无法恢复！",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_account(account_data[0])
            self.load_accounts()
            # 刷新统计页面
            parent = self.parent()
            if parent and hasattr(parent, 'statistics_widget'):
                parent.statistics_widget.update_statistics()
            QMessageBox.information(self, "成功", "账户删除成功！")
    
    def add_transfer(self):
        dialog = TransferDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['from_account'] and data['to_account'] and data['amount'] > 0:
                if data['from_account'] == data['to_account']:
                    QMessageBox.warning(self, "警告", "转出账户和转入账户不能相同！")
                    return
                
                # 检查转出账户余额
                from_balance = self.db_manager.get_account_balance(data['from_account'])
                if from_balance < data['amount']:
                    QMessageBox.warning(self, "警告", f"转出账户余额不足！当前余额: ¥{from_balance:.2f}")
                    return
                
                self.db_manager.add_transfer(
                    data['transfer_date'], data['from_account'], 
                    data['to_account'], data['amount'], data['description']
                )
                self.load_accounts()
                self.load_transfers()
                # 刷新统计页面
                parent = self.parent()
                if parent and hasattr(parent, 'statistics_widget'):
                    parent.statistics_widget.update_statistics()
                QMessageBox.information(self, "成功", "转账记录添加成功！")

class StatisticsWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_view = "day"  # day, week, month, year, custom
        self.current_date = QDate.currentDate()
        self.show_chinese_amount = False
        self.category_level = "parent"  # parent, subcategory
        self.setup_ui()
        self.update_statistics()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 视图切换区域
        view_control_group = QGroupBox("视图控制")
        view_control_layout = QHBoxLayout()
        
        # 视图类型选择
        self.view_combo = QComboBox()
        self.view_combo.addItems(["日视图", "周视图", "月视图", "年视图", "自定义时间"])
        self.view_combo.currentTextChanged.connect(self.on_view_changed)
        
        # 日期导航按钮
        self.prev_btn = QPushButton("◀")
        self.prev_btn.clicked.connect(self.prev_period)
        self.current_date_label = QLabel()
        self.next_btn = QPushButton("▶")
        self.next_btn.clicked.connect(self.next_period)
        
        # 自定义日期选择器（默认隐藏）
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.start_date_edit.setDateRange(QDate(2000, 1, 1), QDate.currentDate())
        self.start_date_edit.dateChanged.connect(self.on_custom_date_changed)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDateRange(QDate(2000, 1, 1), QDate.currentDate())
        self.end_date_edit.dateChanged.connect(self.on_custom_date_changed)
        
        # 快捷选择按钮
        quick_layout = QVBoxLayout()
        recent_7_btn = QPushButton("近7天")
        recent_7_btn.clicked.connect(lambda: self.set_quick_range(7))
        recent_30_btn = QPushButton("近30天")
        recent_30_btn.clicked.connect(lambda: self.set_quick_range(30))
        recent_90_btn = QPushButton("近90天")
        recent_90_btn.clicked.connect(lambda: self.set_quick_range(90))
        
        quick_btn_layout = QHBoxLayout()
        quick_btn_layout.addWidget(recent_7_btn)
        quick_btn_layout.addWidget(recent_30_btn)
        quick_btn_layout.addWidget(recent_90_btn)
        quick_layout.addLayout(quick_btn_layout)
        
        self.custom_date_widget = QWidget()
        custom_date_layout = QHBoxLayout()
        custom_date_layout.addWidget(QLabel("起始日期:"))
        custom_date_layout.addWidget(self.start_date_edit)
        custom_date_layout.addWidget(QLabel("结束日期:"))
        custom_date_layout.addWidget(self.end_date_edit)
        custom_date_layout.addLayout(quick_layout)
        self.custom_date_widget.setLayout(custom_date_layout)
        self.custom_date_widget.hide()
        
        view_control_layout.addWidget(QLabel("视图类型:"))
        view_control_layout.addWidget(self.view_combo)
        view_control_layout.addWidget(self.prev_btn)
        view_control_layout.addWidget(self.current_date_label)
        view_control_layout.addWidget(self.next_btn)
        view_control_layout.addStretch()
        
        view_control_group_layout = QVBoxLayout()
        view_control_group_layout.addLayout(view_control_layout)
        view_control_group_layout.addWidget(self.custom_date_widget)
        view_control_group.setLayout(view_control_group_layout)
        
        layout.addWidget(view_control_group)
        
        # 统计选项
        options_group = QGroupBox("统计选项")
        options_layout = QHBoxLayout()
        
        self.show_chinese_check = QCheckBox("显示金额大写")
        self.show_chinese_check.toggled.connect(self.toggle_chinese_amount)
        
        self.category_level_combo = QComboBox()
        self.category_level_combo.addItems(["按主类别统计", "按子类别统计"])
        self.category_level_combo.currentTextChanged.connect(self.on_category_level_changed)
        
        options_layout.addWidget(self.show_chinese_check)
        options_layout.addWidget(QLabel("类别统计:"))
        options_layout.addWidget(self.category_level_combo)
        options_layout.addStretch()
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 统计结果区域
        stats_content = QWidget()
        stats_layout = QVBoxLayout()
        
        # 收支汇总卡片
        summary_cards_layout = QHBoxLayout()
        
        # 总收入卡片
        income_card = self.create_summary_card("总收入", "#4CAF50", "#E8F5E8")
        self.income_card_amount = income_card.findChild(QLabel, "card_amount")
        self.income_card_chinese = income_card.findChild(QLabel, "card_chinese")
        summary_cards_layout.addWidget(income_card)
        
        # 总支出卡片
        expense_card = self.create_summary_card("总支出", "#F44336", "#FFEBEE")
        self.expense_card_amount = expense_card.findChild(QLabel, "card_amount")
        self.expense_card_chinese = expense_card.findChild(QLabel, "card_chinese")
        summary_cards_layout.addWidget(expense_card)
        
        # 净收支卡片
        net_card = self.create_summary_card("净收支", "#2196F3", "#E3F2FD")
        self.net_card_amount = net_card.findChild(QLabel, "card_amount")
        self.net_card_chinese = net_card.findChild(QLabel, "card_chinese")
        summary_cards_layout.addWidget(net_card)
        
        summary_cards_layout.addStretch()
        stats_layout.addLayout(summary_cards_layout)
        
        # 添加计算说明
        calculation_note = QLabel("注：总收入=收入总额-退款总额；总支出=支出总额-报销总额；净收支=实际收入-实际支出")
        calculation_note.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 5px;
                background-color: #f5f5f5;
                border-radius: 3px;
            }
        """)
        calculation_note.setWordWrap(True)
        stats_layout.addWidget(calculation_note)
        
        # 收支结构和账户分布图表
        charts_layout = QHBoxLayout()
        
        # 收入结构饼图
        income_structure_group = QGroupBox("收入结构")
        self.income_figure = Figure(figsize=(4, 3))
        self.income_canvas = FigureCanvas(self.income_figure)
        income_structure_layout = QVBoxLayout()
        income_structure_layout.addWidget(self.income_canvas)
        income_structure_group.setLayout(income_structure_layout)
        
        # 支出结构饼图
        expense_structure_group = QGroupBox("支出结构")
        self.expense_figure = Figure(figsize=(4, 3))
        self.expense_canvas = FigureCanvas(self.expense_figure)
        expense_structure_layout = QVBoxLayout()
        expense_structure_layout.addWidget(self.expense_canvas)
        expense_structure_group.setLayout(expense_structure_layout)
        
        # 账户分布饼图
        account_distribution_group = QGroupBox("账户分布")
        self.account_figure = Figure(figsize=(4, 3))
        self.account_canvas = FigureCanvas(self.account_figure)
        account_distribution_layout = QVBoxLayout()
        account_distribution_layout.addWidget(self.account_canvas)
        account_distribution_group.setLayout(account_distribution_layout)
        
        charts_layout.addWidget(income_structure_group)
        charts_layout.addWidget(expense_structure_group)
        charts_layout.addWidget(account_distribution_group)
        
        stats_layout.addLayout(charts_layout)
        
        # 核心字段关联统计
        core_stats_layout = QHBoxLayout()
        
        # 销账状态分布
        settlement_group = QGroupBox("销账状态分布")
        settlement_form_layout = QFormLayout()
        self.settled_amount_label = QLabel("¥0.00")
        self.unsettled_amount_label = QLabel("¥0.00")
        self.settled_ratio_label = QLabel("0%")
        
        settlement_form_layout.addRow("已销账金额:", self.settled_amount_label)
        settlement_form_layout.addRow("未销账金额:", self.unsettled_amount_label)
        settlement_form_layout.addRow("销账比例:", self.settled_ratio_label)
        
        settlement_group.setLayout(settlement_form_layout)
        
        # 退款统计
        refund_group = QGroupBox("退款统计")
        refund_form_layout = QFormLayout()
        self.refund_amount_label = QLabel("¥0.00")
        self.refund_count_label = QLabel("0")
        self.refund_ratio_label = QLabel("0%")
        
        refund_form_layout.addRow("退款总额:", self.refund_amount_label)
        refund_form_layout.addRow("退款笔数:", self.refund_count_label)
        refund_form_layout.addRow("退款占比:", self.refund_ratio_label)
        
        refund_group.setLayout(refund_form_layout)
        
        core_stats_layout.addWidget(settlement_group)
        core_stats_layout.addWidget(refund_group)
        
        stats_layout.addLayout(core_stats_layout)
        stats_content.setLayout(stats_layout)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(stats_content)
        
        layout.addWidget(scroll_area)
        self.setLayout(layout)
        
        # 初始化显示
        self.update_date_display()
    
    def on_view_changed(self, view_text):
        """视图类型改变"""
        view_map = {
            "日视图": "day",
            "周视图": "week", 
            "月视图": "month",
            "年视图": "year",
            "自定义时间": "custom"
        }
        self.current_view = view_map[view_text]
        
        if self.current_view == "custom":
            self.custom_date_widget.show()
            self.prev_btn.hide()
            self.next_btn.hide()
        else:
            self.custom_date_widget.hide()
            self.prev_btn.show()
            self.next_btn.show()
        
        self.update_date_display()
        self.update_statistics()
    
    def update_date_display(self):
        """更新日期显示"""
        if self.current_view == "day":
            self.current_date_label.setText(self.current_date.toString("yyyy年MM月dd日"))
        elif self.current_view == "week":
            # 获取周一和周日
            monday = self.current_date.addDays(-self.current_date.dayOfWeek() + 1)
            sunday = monday.addDays(6)
            self.current_date_label.setText(f"{monday.toString('MM.dd')} - {sunday.toString('MM.dd')}")
        elif self.current_view == "month":
            self.current_date_label.setText(self.current_date.toString("yyyy年MM月"))
        elif self.current_view == "year":
            self.current_date_label.setText(self.current_date.toString("yyyy年"))
    
    def get_date_range(self):
        """获取当前视图的日期范围"""
        if self.current_view == "day":
            start_date = self.current_date.toString("yyyy-MM-dd")
            end_date = self.current_date.toString("yyyy-MM-dd")
        elif self.current_view == "week":
            monday = self.current_date.addDays(-self.current_date.dayOfWeek() + 1)
            sunday = monday.addDays(6)
            start_date = monday.toString("yyyy-MM-dd")
            end_date = sunday.toString("yyyy-MM-dd")
        elif self.current_view == "month":
            start_date = self.current_date.toString("yyyy-MM-01")
            end_date = self.current_date.toString(f"yyyy-MM-{self.current_date.daysInMonth()}")
        elif self.current_view == "year":
            start_date = self.current_date.toString("yyyy-01-01")
            end_date = self.current_date.toString("yyyy-12-31")
        elif self.current_view == "custom":
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        else:
            start_date = end_date = self.current_date.toString("yyyy-MM-dd")
        
        return start_date, end_date
    
    def prev_period(self):
        """切换到上一个时间段"""
        if self.current_view == "day":
            self.current_date = self.current_date.addDays(-1)
        elif self.current_view == "week":
            self.current_date = self.current_date.addDays(-7)
        elif self.current_view == "month":
            self.current_date = self.current_date.addMonths(-1)
        elif self.current_view == "year":
            self.current_date = self.current_date.addYears(-1)
        
        self.update_date_display()
        self.update_statistics()
    
    def next_period(self):
        """切换到下一个时间段"""
        if self.current_view == "day":
            self.current_date = self.current_date.addDays(1)
        elif self.current_view == "week":
            self.current_date = self.current_date.addDays(7)
        elif self.current_view == "month":
            self.current_date = self.current_date.addMonths(1)
        elif self.current_view == "year":
            self.current_date = self.current_date.addYears(1)
        
        self.update_date_display()
        self.update_statistics()
    
    def on_custom_date_changed(self):
        """自定义日期改变"""
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()
        
        # 确保起始日期不大于结束日期
        if start_date > end_date:
            self.end_date_edit.setDate(start_date)
        
        self.update_statistics()
    
    def set_quick_range(self, days):
        """设置快捷时间范围"""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-days + 1)
        
        self.start_date_edit.setDate(start_date)
        self.end_date_edit.setDate(end_date)
        self.update_statistics()
    
    def toggle_chinese_amount(self, checked):
        """切换中文大写显示"""
        self.show_chinese_amount = checked
        self.update_statistics()
    
    def on_category_level_changed(self, text):
        """类别统计层级改变"""
        self.category_level = "subcategory" if "子类别" in text else "parent"
        self.update_statistics()
    
    def create_summary_card(self, title, color, bg_color):
        """创建汇总卡片"""
        # 使用主题颜色
        colors = theme_manager.get_current_theme()["colors"]
        
        card = QGroupBox()
        card.setStyleSheet(f"""
            QGroupBox {{
                background-color: {bg_color};
                border: 2px solid {color};
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }}
        """)
        card.setFixedWidth(200)
        card.setFixedHeight(100)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 金额
        amount_label = QLabel("¥0.00")
        amount_label.setObjectName("card_amount")
        amount_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")
        amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(amount_label)
        
        # 中文大写
        chinese_label = QLabel("")
        chinese_label.setObjectName("card_chinese")
        chinese_label.setStyleSheet(f"color: {color}; font-size: 10px;")
        chinese_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chinese_label.setWordWrap(True)
        layout.addWidget(chinese_label)
        
        card.setLayout(layout)
        return card
    
    def create_pie_chart(self, figure, data, labels, title, colors=None):
        """创建圆环图"""
        figure.clear()
        ax = figure.add_subplot(111)
        
        # 获取主题颜色
        theme_colors = theme_manager.get_color('chart_colors')
        theme_bg = theme_manager.get_color('background')
        theme_text = theme_manager.get_color('primary_text')
        theme_border = theme_manager.get_color('border')
        
        if not data or sum(data) == 0:
            ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=ax.transAxes, 
                   fontsize=12, color=theme_text)
            ax.set_title(title, fontsize=14, fontweight='bold', color=theme_text)
            return
        
        # 设置颜色
        if colors is None:
            # 使用主题图表颜色
            import matplotlib.colors as mcolors
            colors = []
            for i in range(len(data)):
                if i < len(theme_colors):
                    # 解析十六进制颜色
                    hex_color = theme_colors[i].lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
                    colors.append(rgb)
                else:
                    colors.append(plt.cm.Set3(i))
        
        # 创建圆环图（通过设置wedgeprops来实现）
        wedges, texts, autotexts = ax.pie(data, labels=labels, colors=colors, autopct='%1.1f%%', 
                                         startangle=90, textprops={'fontsize': 9, 'color': theme_text},
                                         wedgeprops=dict(width=0.6, edgecolor=theme_bg, linewidth=2))
        
        # 在中心添加圆圈形成圆环效果
        centre_circle = plt.Circle((0, 0), 0.40, fc=theme_bg, linewidth=2, edgecolor=theme_border)
        ax.add_artist(centre_circle)
        
        # 设置标题
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20, color=theme_text)
        
        # 确保圆环图是圆形
        ax.axis('equal')
        
        # 设置背景色
        figure.patch.set_facecolor(theme_bg)
        ax.set_facecolor(theme_bg)
        
        figure.tight_layout()
    
    def update_statistics(self):
        """更新统计数据"""
        start_date, end_date = self.get_date_range()
        
        # 获取收支汇总
        summary = self.db_manager.get_statistics_summary(start_date, end_date)
        
        # 更新卡片显示
        self.income_card_amount.setText(f"¥{summary['total_income']:.2f}")
        self.expense_card_amount.setText(f"¥{summary['total_expense']:.2f}")
        self.net_card_amount.setText(f"¥{summary['net_income']:.2f}")
        
        if self.show_chinese_amount:
            self.income_card_chinese.setText(number_to_chinese(summary['total_income']))
            self.expense_card_chinese.setText(number_to_chinese(summary['total_expense']))
            self.net_card_chinese.setText(number_to_chinese(abs(summary['net_income'])))
        else:
            self.income_card_chinese.setText("")
            self.expense_card_chinese.setText("")
            self.net_card_chinese.setText("")
        
        # 更新收入结构饼图
        income_stats = self.db_manager.get_category_statistics(start_date, end_date, "收入", self.category_level)
        if income_stats and summary['total_income'] > 0:
            income_labels = [item[0] for item in income_stats]
            income_data = [item[1] for item in income_stats]
            # 限制显示前8个类别，其余合并为"其他"
            if len(income_labels) > 8:
                other_amount = sum(income_data[8:])
                income_labels = income_labels[:8] + ["其他"]
                income_data = income_data[:8] + [other_amount]
            self.create_pie_chart(self.income_figure, income_data, income_labels, "收入结构")
        else:
            self.create_pie_chart(self.income_figure, [], [], "收入结构")
        
        # 更新支出结构饼图
        expense_stats = self.db_manager.get_category_statistics(start_date, end_date, "支出", self.category_level)
        if expense_stats and summary['total_expense'] > 0:
            expense_labels = [item[0] for item in expense_stats]
            expense_data = [item[1] for item in expense_stats]
            # 限制显示前8个类别，其余合并为"其他"
            if len(expense_labels) > 8:
                other_amount = sum(expense_data[8:])
                expense_labels = expense_labels[:8] + ["其他"]
                expense_data = expense_data[:8] + [other_amount]
            self.create_pie_chart(self.expense_figure, expense_data, expense_labels, "支出结构")
        else:
            self.create_pie_chart(self.expense_figure, [], [], "支出结构")
        
        # 更新账户分布饼图
        account_stats = self.db_manager.get_account_statistics(start_date, end_date)
        if account_stats:
            account_labels = [item[0] for item in account_stats]
            account_data = [item[1] + item[2] for item in account_stats]  # 收入+支出
            # 限制显示前6个账户，其余合并为"其他"
            if len(account_labels) > 6:
                other_amount = sum(account_data[6:])
                account_labels = account_labels[:6] + ["其他"]
                account_data = account_data[:6] + [other_amount]
            self.create_pie_chart(self.account_figure, account_data, account_labels, "账户分布")
        else:
            self.create_pie_chart(self.account_figure, [], [], "账户分布")
        
        # 刷新画布
        self.income_canvas.draw()
        self.expense_canvas.draw()
        self.account_canvas.draw()
        
        # 更新销账状态统计
        settlement_stats = self.db_manager.get_settlement_statistics(start_date, end_date)
        self.settled_amount_label.setText(f"¥{settlement_stats['settled_amount']:.2f}")
        self.unsettled_amount_label.setText(f"¥{settlement_stats['unsettled_amount']:.2f}")
        
        if settlement_stats['total_amount'] > 0:
            settled_ratio = (settlement_stats['settled_amount'] / settlement_stats['total_amount'] * 100)
            self.settled_ratio_label.setText(f"{settled_ratio:.1f}%")
        else:
            self.settled_ratio_label.setText("0%")
        
        # 更新退款统计
        refund_stats = self.db_manager.get_refund_statistics(start_date, end_date)
        self.refund_amount_label.setText(f"¥{refund_stats['total_refund']:.2f}")
        self.refund_count_label.setText(str(refund_stats['refund_count']))
        self.refund_ratio_label.setText(f"{refund_stats['refund_ratio']:.1f}%")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.current_ledger_id = None
        self.ledgers = {}
        self.setup_ui()
        self.load_ledgers()
        self.apply_theme()
    
    def apply_theme(self):
        """应用主题到整个应用"""
        theme_manager.apply_theme_to_widget(self)
        
        # 更新所有子控件的主题
        self.update_children_theme(self)
    
    def update_children_theme(self, widget):
        """递归更新子控件主题"""
        for child in widget.children():
            if hasattr(child, 'setStyleSheet'):
                # 特殊处理某些控件
                if isinstance(child, QPushButton):
                    self.update_button_theme(child)
                elif isinstance(child, QTableWidget):
                    self.update_table_theme(child)
                elif hasattr(child, 'children'):
                    self.update_children_theme(child)
    
    def update_button_theme(self, button):
        """更新按钮主题"""
        colors = theme_manager.get_current_theme()["colors"]
        text = button.text()
        
        # 根据按钮文本设置不同颜色
        if "收入" in text:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['income']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {colors['hover']};
                    border: 1px solid {colors['income']};
                }}
            """)
        elif "支出" in text:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['expense']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {colors['hover']};
                    border: 1px solid {colors['expense']};
                }}4
            """)
        elif "删除" in text:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['danger']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {colors['hover']};
                    border: 1px solid {colors['danger']};
                }}
            """)
        else:
            # 默认按钮样式
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['accent']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {colors['hover']};
                    border: 1px solid {colors['accent']};
                }}
            """)
    
    def update_table_theme(self, table):
        """更新表格主题"""
        colors = theme_manager.get_current_theme()["colors"]
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {colors['card_background']};
                alternate-background-color: {colors['secondary_background']};
                gridline-color: {colors['border']};
                selection-background-color: {colors['accent']};
            }}
            QTableWidget::item {{
                padding: 5px;
                color: {colors['primary_text']};
            }}
            QTableWidget::item:selected {{
                background-color: {colors['accent']};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {colors['secondary_background']};
                color: {colors['primary_text']};
                padding: 5px;
                border: 1px solid {colors['border']};
                font-weight: bold;
            }}
        """)
    
    def showEvent(self, event):
        """窗口显示时应用主题"""
        super().showEvent(event)
        self.apply_theme()
        
    def setup_ui(self):
        self.setWindowTitle("多账本记账系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        
        # 左侧账本管理
        left_widget = self.create_ledger_panel()
        
        # 右侧交易记录
        right_widget = self.create_transaction_panel()
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置")
        
        # 系统设置动作
        system_settings_action = settings_menu.addAction("系统设置")
        system_settings_action.triggered.connect(self.open_system_settings)
        
        # 主题设置动作
        theme_settings_action = settings_menu.addAction("主题设置")
        theme_settings_action.triggered.connect(self.open_theme_settings)
        
        settings_menu.addSeparator()
        
        # 退出动作
        exit_action = settings_menu.addAction("退出")
        exit_action.triggered.connect(self.close)
    
    def open_system_settings(self):
        """打开系统设置"""
        dialog = SystemSettingsDialog(self)
        dialog.exec()
        self.apply_theme()  # 重新应用主题
    
    def open_theme_settings(self):
        """打开主题设置"""
        dialog = ThemeSelectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_theme()
            QMessageBox.information(self, "成功", "主题已成功应用！")
    
    def create_ledger_panel(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 账本管理标题
        title_label = QLabel("账本管理")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 添加账本按钮
        add_ledger_btn = QPushButton("添加账本")
        add_ledger_btn.clicked.connect(self.add_ledger)
        layout.addWidget(add_ledger_btn)
        
        # 账本列表
        self.ledger_list = QTreeWidget()
        self.ledger_list.setHeaderLabel("账本列表")
        self.ledger_list.itemClicked.connect(self.on_ledger_selected)
        layout.addWidget(self.ledger_list)
        
        # 账本操作按钮
        ledger_btn_layout = QHBoxLayout()
        delete_ledger_btn = QPushButton("删除账本")
        delete_ledger_btn.clicked.connect(self.delete_ledger)
        ledger_btn_layout.addWidget(delete_ledger_btn)
        layout.addLayout(ledger_btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_transaction_panel(self):
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 交易记录标签页
        transaction_widget = QWidget()
        transaction_layout = QVBoxLayout()
        
        # 当前账本标题
        self.current_ledger_label = QLabel("请选择账本")
        self.current_ledger_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        transaction_layout.addWidget(self.current_ledger_label)
        
        # 交易操作按钮
        transaction_btn_layout = QHBoxLayout()
        add_income_btn = QPushButton("添加收入")
        add_income_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_income_btn.clicked.connect(self.add_income)
        
        add_expense_btn = QPushButton("添加支出")
        add_expense_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        add_expense_btn.clicked.connect(self.add_expense)
        
        transaction_btn_layout.addWidget(add_income_btn)
        transaction_btn_layout.addWidget(add_expense_btn)
        edit_transaction_btn = QPushButton("编辑记录")
        edit_transaction_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        edit_transaction_btn.clicked.connect(self.edit_transaction)
        delete_transaction_btn = QPushButton("删除记录")
        delete_transaction_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        delete_transaction_btn.clicked.connect(self.delete_transaction)
        transaction_btn_layout.addWidget(edit_transaction_btn)
        transaction_btn_layout.addWidget(delete_transaction_btn)
        transaction_btn_layout.addStretch()
        transaction_layout.addLayout(transaction_btn_layout)
        
        # 搜索区域
        search_group = QGroupBox("搜索功能")
        search_layout = QVBoxLayout()
        
        # 基础搜索
        basic_search_layout = QHBoxLayout()
        basic_search_layout.addWidget(QLabel("关键词搜索:"))
        
        self.keyword_search_edit = QLineEdit()
        self.keyword_search_edit.setPlaceholderText("输入关键词搜索备注、类别、账户、退款原因...")
        self.keyword_search_edit.returnPressed.connect(self.search_transactions)
        basic_search_layout.addWidget(self.keyword_search_edit)
        
        search_btn = QPushButton("🔍 搜索")
        search_btn.clicked.connect(self.search_transactions)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        basic_search_layout.addWidget(search_btn)
        
        clear_btn = QPushButton("清除")
        clear_btn.clicked.connect(self.clear_search)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        basic_search_layout.addWidget(clear_btn)
        
        # 高级筛选按钮
        self.advanced_toggle_btn = QPushButton("🔧 高级筛选")
        self.advanced_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.advanced_toggle_btn.clicked.connect(self.toggle_advanced_search)
        basic_search_layout.addWidget(self.advanced_toggle_btn)
        
        basic_search_layout.addStretch()
        search_layout.addLayout(basic_search_layout)
        
        # 进阶搜索（默认隐藏）
        self.advanced_search_widget = QWidget()
        self.advanced_search_widget.setVisible(False)
        advanced_search_layout = QVBoxLayout(self.advanced_search_widget)
        
        # 第一行：基础筛选
        row1_layout = QHBoxLayout()
        
        # 基础筛选组（包含账户、类型、分类）
        basic_filter_group = QGroupBox("基础筛选")
        basic_filter_group.setMinimumWidth(400)  # 设置分组框最小宽度
        basic_filter_layout = QHBoxLayout()
        
        # 账户筛选
        basic_filter_layout.addWidget(QLabel("账户:"))
        self.account_search_combo = QComboBox()
        self.account_search_combo.setMinimumWidth(120)  # 设置组合框最小宽度
        self.account_search_combo.addItem("")
        basic_filter_layout.addWidget(self.account_search_combo)
        
        # 交易类型
        basic_filter_layout.addWidget(QLabel("类型:"))
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.setMinimumWidth(80)  # 设置组合框最小宽度
        self.transaction_type_combo.addItems(["", "收入", "支出"])
        basic_filter_layout.addWidget(self.transaction_type_combo)
        
        # 分类筛选
        basic_filter_layout.addWidget(QLabel("分类:"))
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(100)  # 设置组合框最小宽度
        self.category_combo.addItem("")
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        basic_filter_layout.addWidget(self.category_combo)
        
        self.subcategory_combo = QComboBox()
        self.subcategory_combo.setMinimumWidth(100)  # 设置组合框最小宽度
        self.subcategory_combo.addItem("")
        basic_filter_layout.addWidget(self.subcategory_combo)
        
        basic_filter_group.setLayout(basic_filter_layout)
        row1_layout.addWidget(basic_filter_group)
        
        # 状态筛选组
        status_group = QGroupBox("状态筛选")
        status_group.setMinimumWidth(200)  # 设置分组框最小宽度
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("销账:"))
        self.settled_combo = QComboBox()
        self.settled_combo.setMinimumWidth(80)  # 设置组合框最小宽度
        self.settled_combo.addItems(["", "已销账", "未销账"])
        status_layout.addWidget(self.settled_combo)
        
        status_layout.addWidget(QLabel("退款:"))
        self.refund_combo = QComboBox()
        self.refund_combo.setMinimumWidth(80)  # 设置组合框最小宽度
        self.refund_combo.addItems(["", "有退款", "无退款"])
        status_layout.addWidget(self.refund_combo)
        status_group.setLayout(status_layout)
        row1_layout.addWidget(status_group)
        
        row1_layout.addStretch()
        advanced_search_layout.addLayout(row1_layout)
        
        # 第三行：金额和时间范围
        row3_layout = QHBoxLayout()
        
        # 金额范围组
        amount_group = QGroupBox("金额范围")
        amount_group.setMinimumWidth(250)  # 设置分组框最小宽度
        amount_layout = QHBoxLayout()
        self.min_amount_spin = QDoubleSpinBox()
        self.min_amount_spin.setRange(0, 999999.99)
        self.min_amount_spin.setDecimals(2)
        self.min_amount_spin.setPrefix("¥")
        self.min_amount_spin.setSpecialValueText("最小")
        self.min_amount_spin.setValue(0)
        self.min_amount_spin.setMinimumWidth(100)  # 设置输入框最小宽度
        amount_layout.addWidget(self.min_amount_spin)
        
        amount_layout.addWidget(QLabel("至"))
        self.max_amount_spin = QDoubleSpinBox()
        self.max_amount_spin.setRange(0, 999999.99)
        self.max_amount_spin.setDecimals(2)
        self.max_amount_spin.setPrefix("¥")
        self.max_amount_spin.setSpecialValueText("最大")
        self.max_amount_spin.setMaximum(999999.99)
        self.max_amount_spin.setMinimumWidth(100)  # 设置输入框最小宽度
        amount_layout.addWidget(self.max_amount_spin)
        amount_group.setLayout(amount_layout)
        row3_layout.addWidget(amount_group)
        
        # 时间范围组
        date_group = QGroupBox("时间范围")
        date_group.setMinimumWidth(300)  # 设置分组框最小宽度
        date_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setMinimumWidth(120)  # 设置日期选择器最小宽度
        date_layout.addWidget(self.start_date_edit)
        
        date_layout.addWidget(QLabel("至"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setMinimumWidth(120)  # 设置日期选择器最小宽度
        date_layout.addWidget(self.end_date_edit)
        date_group.setLayout(date_layout)
        row3_layout.addWidget(date_group)
        
        row3_layout.addStretch()
        advanced_search_layout.addLayout(row3_layout)
        
        search_layout.addWidget(self.advanced_search_widget)
        search_group.setLayout(search_layout)
        transaction_layout.addWidget(search_group)
        
        # 交易记录表格
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(11)
        self.transaction_table.setHorizontalHeaderLabels([
            "日期", "类型", "主类别", "子类别", "金额", "账户", "备注", "销账", "退款金额", "退款原因", "创建时间"
        ])
        self.transaction_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        transaction_layout.addWidget(self.transaction_table)
        
        transaction_widget.setLayout(transaction_layout)
        tab_widget.addTab(transaction_widget, "交易记录")
        
        # 资产管理标签页
        self.asset_widget = AssetManagementWidget(self.db_manager)
        tab_widget.addTab(self.asset_widget, "资产管理")
        
        # 统计分析标签页
        self.statistics_widget = StatisticsWidget(self.db_manager)
        tab_widget.addTab(self.statistics_widget, "统计分析")
        
        return tab_widget
    
    def load_ledgers(self):
        ledgers = self.db_manager.get_ledgers()
        self.ledger_list.clear()
        self.ledgers = {}
        
        for ledger in ledgers:
            ledger_id, name, created_time, ledger_type, description = ledger
            self.ledgers[ledger_id] = {
                'name': name,
                'type': ledger_type,
                'description': description,
                'created_time': created_time
            }
            
            item = QTreeWidgetItem(self.ledger_list)
            item.setText(0, f"{name} ({ledger_type})")
            item.setData(0, Qt.ItemDataRole.UserRole, ledger_id)
    
    def on_ledger_selected(self, item, column):
        ledger_id = item.data(0, Qt.ItemDataRole.UserRole)
        if ledger_id:
            self.current_ledger_id = ledger_id
            ledger_info = self.ledgers[ledger_id]
            self.current_ledger_label.setText(f"当前账本: {ledger_info['name']} ({ledger_info['type']})")
            self.initialize_search_controls()
            self.load_transactions()
    
    def load_transactions(self, filtered_transactions=None):
        if not self.current_ledger_id:
            return
        
        if filtered_transactions is not None:
            transactions = filtered_transactions
        else:
            transactions = self.db_manager.get_transactions(self.current_ledger_id)
            
        self.transaction_table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            (trans_id, ledger_id, transaction_date, transaction_type, category, subcategory, 
             amount, account, description, is_settled, refund_amount, 
             refund_reason, created_time) = transaction
            
            self.transaction_table.setItem(row, 0, QTableWidgetItem(transaction_date))
            self.transaction_table.setItem(row, 1, QTableWidgetItem(transaction_type))
            self.transaction_table.setItem(row, 2, QTableWidgetItem(category))
            self.transaction_table.setItem(row, 3, QTableWidgetItem(subcategory))
            self.transaction_table.setItem(row, 4, QTableWidgetItem(f"¥{abs(amount):.2f}"))
            self.transaction_table.setItem(row, 5, QTableWidgetItem(account or ""))
            self.transaction_table.setItem(row, 6, QTableWidgetItem(description or ""))
            self.transaction_table.setItem(row, 7, QTableWidgetItem("是" if is_settled else "否"))
            self.transaction_table.setItem(row, 8, QTableWidgetItem(f"¥{refund_amount:.2f}" if refund_amount > 0 else ""))
            self.transaction_table.setItem(row, 9, QTableWidgetItem(refund_reason or ""))
            self.transaction_table.setItem(row, 10, QTableWidgetItem(created_time))
    
    def initialize_search_controls(self):
        """初始化搜索控件的选项"""
        # 加载类别选项
        categories = self.db_manager.get_categories()
        category_set = set()
        for parent, sub in categories:
            category_set.add(parent)
        
        self.category_combo.clear()
        self.category_combo.addItem("")
        self.category_combo.addItems(sorted(category_set))
        
        # 加载账户选项
        accounts = self.db_manager.get_accounts()
        self.account_search_combo.clear()
        self.account_search_combo.addItem("")
        for account in accounts:
            self.account_search_combo.addItem(account[1])
    
    def on_category_changed(self, category):
        """类别改变时更新子类别选项"""
        self.subcategory_combo.clear()
        self.subcategory_combo.addItem("")
        
        if category:
            categories = self.db_manager.get_categories()
            subcategories = set()
            for parent, sub in categories:
                if parent == category:
                    subcategories.add(sub)
            self.subcategory_combo.addItems(sorted(subcategories))
    
    def search_transactions(self):
        """执行搜索"""
        if not self.current_ledger_id:
            QMessageBox.warning(self, "警告", "请先选择账本！")
            return
        
        # 获取所有交易记录
        all_transactions = self.db_manager.get_transactions(self.current_ledger_id)
        filtered_transactions = []
        
        keyword = self.keyword_search_edit.text().strip().lower()
        category = self.category_combo.currentText()
        subcategory = self.subcategory_combo.currentText()
        account = self.account_search_combo.currentText()
        transaction_type = self.transaction_type_combo.currentText()
        settled_status = self.settled_combo.currentText()
        refund_status = self.refund_combo.currentText()
        min_amount = self.min_amount_spin.value()
        max_amount = self.max_amount_spin.value()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        for transaction in all_transactions:
            (trans_id, ledger_id, transaction_date, trans_type, trans_category, trans_subcategory, 
             amount, trans_account, description, is_settled, refund_amount, 
             refund_reason, created_time) = transaction
            
            # 关键词搜索
            if keyword:
                searchable_text = f"{description or ''} {trans_category} {trans_subcategory} {trans_account or ''} {refund_reason or ''}".lower()
                if keyword not in searchable_text:
                    continue
            
            # 类别搜索
            if category and trans_category != category:
                continue
            
            if subcategory and trans_subcategory != subcategory:
                continue
            
            # 账户搜索
            if account and trans_account != account:
                continue
            
            # 收支类型搜索
            if transaction_type and trans_type != transaction_type:
                continue
            
            # 销账状态搜索
            if settled_status:
                if settled_status == "已销账" and not is_settled:
                    continue
                elif settled_status == "未销账" and is_settled:
                    continue
            
            # 退款状态搜索
            if refund_status:
                if refund_status == "有退款" and refund_amount <= 0:
                    continue
                elif refund_status == "无退款" and refund_amount > 0:
                    continue
            
            # 金额范围搜索
            abs_amount = abs(amount)
            if min_amount > 0 and abs_amount < min_amount:
                continue
            if max_amount < 999999.99 and abs_amount > max_amount:
                continue
            
            # 时间范围搜索
            if transaction_date < start_date or transaction_date > end_date:
                continue
            
            # 通过所有筛选条件
            filtered_transactions.append(transaction)
        
        # 显示筛选结果
        self.load_transactions(filtered_transactions)
        
        # 显示搜索结果数量
        result_count = len(filtered_transactions)
        total_count = len(all_transactions)
        if keyword or category or subcategory or account or transaction_type or settled_status or refund_status or min_amount > 0 or max_amount < 999999.99:
            QMessageBox.information(self, "搜索结果", f"找到 {result_count} 条记录，共 {total_count} 条记录")
    
    def toggle_advanced_search(self):
        """切换高级搜索的显示/隐藏"""
        is_visible = self.advanced_search_widget.isVisible()
        self.advanced_search_widget.setVisible(not is_visible)
        
        if not is_visible:
            self.advanced_toggle_btn.setText("🔧 收起筛选")
            self.advanced_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
            """)
        else:
            self.advanced_toggle_btn.setText("🔧 高级筛选")
            self.advanced_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
    
    def clear_search(self):
        """清除搜索条件"""
        self.keyword_search_edit.clear()
        self.category_combo.setCurrentIndex(0)
        self.subcategory_combo.clear()
        self.subcategory_combo.addItem("")
        self.account_search_combo.setCurrentIndex(0)
        self.transaction_type_combo.setCurrentIndex(0)
        self.settled_combo.setCurrentIndex(0)
        self.refund_combo.setCurrentIndex(0)
        self.min_amount_spin.setValue(0)
        self.max_amount_spin.setValue(999999.99)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.end_date_edit.setDate(QDate.currentDate())
        
        # 重新加载所有交易记录
        self.load_transactions()
    
    def add_ledger(self):
        dialog = AddLedgerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['name']:
                self.db_manager.add_ledger(data['name'], data['type'], data['description'])
                self.load_ledgers()
                QMessageBox.information(self, "成功", "账本添加成功！")
    
    def delete_ledger(self):
        current_item = self.ledger_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的账本！")
            return
        
        ledger_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        ledger_name = self.ledgers[ledger_id]['name']
        
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除账本 '{ledger_name}' 吗？\n删除后将同时删除该账本下的所有交易记录！",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_ledger(ledger_id)
            self.load_ledgers()
            if self.current_ledger_id == ledger_id:
                self.current_ledger_id = None
                self.current_ledger_label.setText("请选择账本")
                self.transaction_table.setRowCount(0)
            QMessageBox.information(self, "成功", "账本删除成功！")
    
    def add_income(self):
        if not self.current_ledger_id:
            QMessageBox.warning(self, "警告", "请先选择账本！")
            return
        
        while True:
            dialog = AddIncomeDialog(self.db_manager, self.current_ledger_id, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if data['category'] and data['subcategory'] and data['amount'] > 0:
                    self.db_manager.add_transaction(
                        self.current_ledger_id, data['transaction_date'], data['transaction_type'],
                        data['category'], data['subcategory'], data['amount'], data['account'], data['description'],
                        data['is_settled'], data['refund_amount'], data['refund_reason']
                    )
                    self.load_transactions()
                    
                    # 更新账户余额
                    if data['account']:
                        self.db_manager.update_account_balance(data['account'], data['amount'])
                    
                    if dialog.is_add_more:
                        # 继续添加下一条记录
                        continue
                    else:
                        QMessageBox.information(self, "成功", "收入记录添加成功！")
                        # 刷新资产管理页面的账户信息
                        if hasattr(self, 'asset_widget'):
                            self.asset_widget.load_accounts()
                        break
                else:
                    QMessageBox.warning(self, "警告", "请填写必要的收入信息！")
                    break
            else:
                break
    
    def add_expense(self):
        if not self.current_ledger_id:
            QMessageBox.warning(self, "警告", "请先选择账本！")
            return
        
        while True:
            dialog = AddExpenseDialog(self.db_manager, self.current_ledger_id, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if data['category'] and data['subcategory'] and data['amount'] < 0:
                    self.db_manager.add_transaction(
                        self.current_ledger_id, data['transaction_date'], data['transaction_type'],
                        data['category'], data['subcategory'], data['amount'], data['account'], data['description'],
                        data['is_settled'], data['refund_amount'], data['refund_reason']
                    )
                    self.load_transactions()
                    
                    # 更新账户余额（支出为负数）
                    if data['account']:
                        self.db_manager.update_account_balance(data['account'], data['amount'])
                    
                    if dialog.is_add_more:
                        # 继续添加下一条记录
                        continue
                    else:
                        QMessageBox.information(self, "成功", "支出记录添加成功！")
                        # 刷新资产管理页面的账户信息
                        if hasattr(self, 'asset_widget'):
                            self.asset_widget.load_accounts()
                        break
                else:
                    QMessageBox.warning(self, "警告", "请填写必要的支出信息！")
                    break
            else:
                break
    
    def edit_transaction(self):
        if not self.current_ledger_id:
            QMessageBox.warning(self, "警告", "请先选择账本！")
            return
        
        current_row = self.transaction_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的交易记录！")
            return
        
        # 获取选中的交易记录数据
        transactions = self.db_manager.get_transactions(self.current_ledger_id)
        if current_row >= len(transactions):
            QMessageBox.warning(self, "警告", "找不到选中的交易记录！")
            return
        
        transaction_data = transactions[current_row]
        transaction_type = transaction_data[3]
        
        if transaction_type == "收入":
            dialog = EditIncomeDialog(self.db_manager, transaction_data, self)
        elif transaction_type == "支出":
            dialog = EditExpenseDialog(self.db_manager, transaction_data, self)
        else:
            QMessageBox.warning(self, "警告", "未知的交易类型！")
            return
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['category'] and data['subcategory']:
                # 计算余额变化
                old_amount = transaction_data[6]
                new_amount = data['amount']
                balance_change = new_amount - old_amount
                
                self.db_manager.update_transaction(
                    data['id'], data['transaction_date'], data['transaction_type'],
                    data['category'], data['subcategory'], data['amount'], data['account'], data['description'],
                    data['is_settled'], data['refund_amount'], data['refund_reason']
                )
                self.load_transactions()
                
                # 更新账户余额
                if data['account']:
                    self.db_manager.update_account_balance(data['account'], balance_change)
                
                QMessageBox.information(self, "成功", "交易记录修改成功！")
                # 刷新相关页面
                if hasattr(self, 'asset_widget'):
                    self.asset_widget.load_accounts()
                if hasattr(self, 'statistics_widget'):
                    self.statistics_widget.update_statistics()
    
    def delete_transaction(self):
        if not self.current_ledger_id:
            QMessageBox.warning(self, "警告", "请先选择账本！")
            return
        
        current_row = self.transaction_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的交易记录！")
            return
        
        # 获取选中的交易记录数据
        transactions = self.db_manager.get_transactions(self.current_ledger_id)
        if current_row >= len(transactions):
            QMessageBox.warning(self, "警告", "找不到选中的交易记录！")
            return
        
        transaction_data = transactions[current_row]
        transaction_date = transaction_data[2]
        transaction_type = transaction_data[3]
        category = transaction_data[4]
        subcategory = transaction_data[5]
        amount = transaction_data[6]
        account = transaction_data[7]
        
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除这条交易记录吗？"
                                   f"日期: {transaction_date}"
                                   f"类型: {transaction_type}"
                                   f"类别: {category} - {subcategory}"
                                   f"金额: ¥{abs(amount):.2f}"
                                   f"删除后将无法恢复！",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_transaction(transaction_data[0])
            self.load_transactions()
            
            # 更新账户余额（删除记录需要反向操作）
            if account:
                self.db_manager.update_account_balance(account, -amount)
            
            QMessageBox.information(self, "成功", "交易记录删除成功！")
            # 刷新相关页面
            if hasattr(self, 'asset_widget'):
                self.asset_widget.load_accounts()
            if hasattr(self, 'statistics_widget'):
                self.statistics_widget.update_statistics()

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()