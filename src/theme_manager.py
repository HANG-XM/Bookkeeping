import json
import os
import matplotlib
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt


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