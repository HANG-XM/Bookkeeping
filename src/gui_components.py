"""
GUI组件模块 - 重构后的GUI组件，移除重复代码
"""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QLineEdit, QComboBox, 
                            QTableWidget, QTableWidgetItem, QTabWidget, QDialog,
                            QFormLayout, QTextEdit, QDateTimeEdit, QCheckBox,
                            QDoubleSpinBox, QMessageBox, QSplitter, QGroupBox,
                            QTreeWidget, QTreeWidgetItem, QHeaderView, QSpinBox,
                            QCalendarWidget, QDateEdit, QScrollArea, QGridLayout,
                            QFrame, QButtonGroup, QRadioButton, QColorDialog)
from PyQt6.QtCore import Qt, QDateTime, QDate, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib

from theme_manager import theme_manager, number_to_chinese
from database_manager import DatabaseManager
from ui_base_components import StyleHelper, MessageHelper, BaseDialog
from chart_utils import ChartUtils

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 对话框类已移至 dialogs.py 模块


class SystemSettingsDialog(BaseDialog):
    """系统设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("系统设置")
        self.setFixedSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("系统设置")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        StyleHelper.apply_label_style(title_label)
        layout.addWidget(title_label)
        
        # 设置选项
        settings_group = QGroupBox("设置选项")
        StyleHelper.apply_groupbox_style(settings_group)
        settings_layout = QVBoxLayout()
        
        # 主题设置按钮
        theme_btn = QPushButton("🎨 主题设置")
        theme_btn.clicked.connect(self.open_theme_settings)
        StyleHelper.apply_button_style(theme_btn)
        settings_layout.addWidget(theme_btn)
        
        # 当前主题显示
        current_theme_layout = QHBoxLayout()
        current_theme_label = QLabel("当前主题:")
        StyleHelper.apply_label_style(current_theme_label)
        current_theme_layout.addWidget(current_theme_label)
        
        current_theme_name = QLabel(theme_manager.get_current_theme()["name"])
        current_theme_name.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('accent')};
                font-weight: bold;
                background-color: transparent;
            }}
        """)
        current_theme_layout.addWidget(current_theme_name)
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
        
        # 账本设置
        ledger_separator = QFrame()
        ledger_separator.setFrameShape(QFrame.Shape.HLine)
        ledger_separator.setStyleSheet(f"color: {theme_manager.get_color('border')};")
        settings_layout.addWidget(ledger_separator)
        
        # 自动打开上次账本
        ledger_settings_layout = QVBoxLayout()
        self.auto_open_check = QCheckBox("启动时自动打开上次使用的账本")
        self.auto_open_check.setStyleSheet(f"""
            QCheckBox {{
                color: {theme_manager.get_color('primary_text')};
                background-color: transparent;
                font-size: 14px;
            }}
        """)
        
        # 获取设置状态
        from ui_base_components import config_manager
        auto_open = config_manager.get_auto_open_last_ledger()
        self.auto_open_check.setChecked(auto_open)
        
        # 上次账本信息
        last_ledger_info = config_manager.get_last_ledger_info()
        if last_ledger_info:
            self.last_ledger_label = QLabel(f"上次账本: {last_ledger_info}")
        else:
            self.last_ledger_label = QLabel("尚未保存账本信息")
        self.last_ledger_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('secondary_text')};
                font-size: 12px;
                font-style: italic;
                background-color: transparent;
                padding: 5px 0;
            }}
        """)
        
        ledger_settings_layout.addWidget(self.auto_open_check)
        ledger_settings_layout.addWidget(self.last_ledger_label)
        
        # 账本设置说明
        ledger_info = QLabel("启用此功能后，程序启动时会自动打开上次使用的账本，省去手动选择的步骤。")
        ledger_info.setWordWrap(True)
        ledger_info.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('secondary_text')};
                font-size: 12px;
                padding: 10px;
                background-color: {theme_manager.get_color('secondary_background')};
                border-radius: 4px;
            }}
        """)
        ledger_settings_layout.addWidget(ledger_info)
        
        settings_layout.addLayout(ledger_settings_layout)
        
        # 统计设置分隔符
        stats_separator = QFrame()
        stats_separator.setFrameShape(QFrame.Shape.HLine)
        stats_separator.setStyleSheet(f"color: {theme_manager.get_color('border')};")
        settings_layout.addWidget(stats_separator)
        
        # 统计设置
        stats_settings_layout = QVBoxLayout()
        self.auto_restore_stats_view_check = QCheckBox("启动时自动恢复上次统计视图")
        self.auto_restore_stats_view_check.setStyleSheet(f"""
            QCheckBox {{
                color: {theme_manager.get_color('primary_text')};
                background-color: transparent;
                font-size: 14px;
            }}
        """)
        
        # 获取设置状态
        auto_restore_stats_view = config_manager.get_auto_restore_stats_view()
        self.auto_restore_stats_view_check.setChecked(auto_restore_stats_view)
        
        # 上次统计视图信息
        last_stats_view = config_manager.get_last_stats_view()
        view_names = {"day": "日视图", "week": "周视图", "month": "月视图", "year": "年视图", "custom": "自定义时间"}
        self.last_stats_view_label = QLabel(f"上次视图: {view_names.get(last_stats_view, '日视图')}")
        self.last_stats_view_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('secondary_text')};
                font-size: 12px;
                font-style: italic;
                background-color: transparent;
                padding: 5px 0;
            }}
        """)
        
        stats_settings_layout.addWidget(self.auto_restore_stats_view_check)
        stats_settings_layout.addWidget(self.last_stats_view_label)
        
        # 统计设置说明
        stats_info = QLabel("启用此功能后，程序启动时统计分析页面会自动恢复到上次使用的视图类型。")
        stats_info.setWordWrap(True)
        stats_info.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('secondary_text')};
                font-size: 12px;
                padding: 10px;
                background-color: {theme_manager.get_color('secondary_background')};
                border-radius: 4px;
            }}
        """)
        stats_settings_layout.addWidget(stats_info)
        
        settings_layout.addLayout(stats_settings_layout)
        
        # 数据管理设置分隔符
        data_separator = QFrame()
        data_separator.setFrameShape(QFrame.Shape.HLine)
        data_separator.setStyleSheet(f"color: {theme_manager.get_color('border')};")
        settings_layout.addWidget(data_separator)
        
        # 数据管理设置
        data_settings_layout = QVBoxLayout()
        
        # 数据管理按钮
        data_management_btn = QPushButton("📊 数据管理")
        data_management_btn.clicked.connect(self.open_data_management)
        StyleHelper.apply_button_style(data_management_btn)
        data_settings_layout.addWidget(data_management_btn)
        
        # 数据管理说明
        data_info = QLabel("数据管理提供导出导入功能，支持Excel和CSV格式，可导出记账记录、预算配置和账户信息。")
        data_info.setWordWrap(True)
        data_info.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('secondary_text')};
                font-size: 12px;
                padding: 10px;
                background-color: {theme_manager.get_color('secondary_background')};
                border-radius: 4px;
            }}
        """)
        data_settings_layout.addWidget(data_info)
        
        settings_layout.addLayout(data_settings_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        StyleHelper.apply_button_style(save_btn)
        button_layout.addWidget(save_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        StyleHelper.apply_button_style(close_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def save_settings(self):
        """保存设置"""
        from ui_base_components import config_manager
        
        # 保存自动打开账本设置
        config_manager.set_auto_open_last_ledger(self.auto_open_check.isChecked())
        
        # 保存自动恢复统计视图设置
        config_manager.set_auto_restore_stats_view(self.auto_restore_stats_view_check.isChecked())
        
        # 通知父窗口（如果需要）
        if hasattr(self.parent(), 'on_settings_changed'):
            self.parent().on_settings_changed()
        
        MessageHelper.show_info(self, "成功", "设置已保存！")
        self.accept()
    
    def open_theme_settings(self):
        """打开主题设置"""
        # ThemeSelectionDialog 在本模块中定义，直接使用以避免循环导入
        dialog = ThemeSelectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 主题已更改，重新应用样式
            if hasattr(self.parent(), 'apply_theme'):
                self.parent().apply_theme()
            MessageHelper.show_info(self, "成功", "主题已成功应用！")
    
    def open_data_management(self):
        """打开数据管理"""
        try:
            from data_import_export import DataManagementDialog
            # 获取数据库管理器实例
            if hasattr(self.parent(), 'db_manager'):
                db_manager = self.parent().db_manager
            else:
                # 如果父窗口没有db_manager，创建新实例
                db_manager = DatabaseManager()
            
            dialog = DataManagementDialog(db_manager, self)
            dialog.exec()
        except Exception as e:
            MessageHelper.show_error(self, "错误", f"无法打开数据管理：{str(e)}")


class ThemeSelectionDialog(BaseDialog):
    """主题选择对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("主题设置")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.load_current_theme()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("选择主题")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        StyleHelper.apply_label_style(title_label)
        layout.addWidget(title_label)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        create_theme_btn = QPushButton("创建自定义主题")
        create_theme_btn.clicked.connect(self.create_custom_theme)
        StyleHelper.apply_button_style(create_theme_btn)
        toolbar_layout.addWidget(create_theme_btn)
        
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 主题卡片区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.card_layout = QGridLayout()
        
        self.theme_buttons = QButtonGroup()
        self.theme_cards = {}
        
        row, col = 0, 0
        for theme_id, theme_data in theme_manager.THEMES.items():
            card = self.create_theme_card(theme_id, theme_data)
            self.card_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 2:  # 每行2个卡片
                col = 0
                row += 1
        
        scroll_content.setLayout(self.card_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("恢复默认主题")
        reset_btn.clicked.connect(self.reset_to_default)
        StyleHelper.apply_button_style(reset_btn)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        StyleHelper.apply_button_style(cancel_btn)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("应用")
        apply_btn.clicked.connect(self.apply_theme)
        StyleHelper.apply_button_style(apply_btn)
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
        
        # 检查是否为自定义主题
        is_custom = theme_id.startswith('custom_')
        
        layout = QVBoxLayout()
        
        # 主题标题和描述
        title_layout = QVBoxLayout()
        
        title_label = QLabel(theme_data['name'])
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {theme_data['colors']['primary_text']}; background-color: transparent;")
        title_layout.addWidget(title_label)
        
        desc_label = QLabel(theme_data['description'])
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet(f"color: {theme_data['colors']['secondary_text']}; background-color: transparent;")
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
                background-color: transparent;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {theme_data['colors']['border']};
                border-radius: 8px;
                background-color: transparent;
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
        
        # 如果是自定义主题，添加删除按钮
        if is_custom:
            delete_btn = QPushButton("删除")
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme_data['colors']['danger']};
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: #d32f2f;
                }}
            """)
            delete_btn.clicked.connect(lambda _, tid=theme_id: self.delete_custom_theme(tid))
            card_layout.addWidget(delete_btn)
        
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
    
    def create_custom_theme(self):
        """创建自定义主题"""
        dialog = CustomThemeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 重新加载主题列表
            self.refresh_theme_list()
    
    def delete_custom_theme(self, theme_id):
        """删除自定义主题"""
        theme_name = theme_manager.THEMES[theme_id].get('name', theme_id)
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除自定义主题 '{theme_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if theme_manager.delete_custom_theme(theme_id):
                MessageHelper.show_info(self, "成功", "主题已删除")
                self.refresh_theme_list()
            else:
                MessageHelper.show_error(self, "错误", "删除主题失败")
    
    def refresh_theme_list(self):
        """刷新主题列表"""
        # 清除现有的主题卡片
        for i in reversed(range(self.card_layout.count())):
            child = self.card_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 重新创建主题卡片
        self.theme_cards = {}
        self.theme_buttons = QButtonGroup()
        
        row, col = 0, 0
        for theme_id, theme_data in theme_manager.THEMES.items():
            card = self.create_theme_card(theme_id, theme_data)
            self.card_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 2:  # 每行2个卡片
                col = 0
                row += 1
        
        # 重新加载当前主题选择
        self.load_current_theme()
    
    def apply_theme(self):
        """应用选中的主题"""
        checked_radio = self.theme_buttons.checkedButton()
        if checked_radio and checked_radio in self.theme_cards:
            theme_id = self.theme_cards[checked_radio]
            if theme_manager.set_theme(theme_id):
                self.accept()
            else:
                MessageHelper.show_warning(self, "错误", "主题应用失败！")


class CustomThemeDialog(BaseDialog):
    """自定义主题创建对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义主题")
        self.setFixedSize(900, 700)
        self.color_inputs = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("创建自定义主题")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        StyleHelper.apply_label_style(title_label)
        layout.addWidget(title_label)
        
        # 主题名称输入
        name_group = QGroupBox("主题信息")
        name_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入主题名称")
        name_layout.addRow("主题名称:", self.name_input)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("请输入主题描述")
        self.desc_input.setMaximumHeight(60)
        name_layout.addRow("主题描述:", self.desc_input)
        
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # 颜色配置区域
        color_group = QGroupBox("颜色配置")
        color_layout = QVBoxLayout()
        
        # 创建颜色配置表格
        self.color_table = QTableWidget()
        self.color_table.setColumnCount(3)
        self.color_table.setHorizontalHeaderLabels(["颜色名称", "颜色预览", "操作"])
        self.color_table.horizontalHeader().setStretchLastSection(True)
        
        # 定义颜色配置项
        self.color_configs = [
            ("background", "背景色", "#FFFFFF"),
            ("secondary_background", "次要背景色", "#F5F5F5"),
            ("card_background", "卡片背景色", "#FFFFFF"),
            ("primary_text", "主要文字色", "#333333"),
            ("secondary_text", "次要文字色", "#666666"),
            ("accent", "主题色", "#2196F3"),
            ("success", "成功色", "#4CAF50"),
            ("warning", "警告色", "#FF9800"),
            ("danger", "危险色", "#F44336"),
            ("border", "边框色", "#E0E0E0"),
            ("hover", "悬停色", "#F0F0F0"),
            ("income", "收入色", "#4CAF50"),
            ("expense", "支出色", "#FF6B6B")
        ]
        
        self.color_table.setRowCount(len(self.color_configs))
        
        for row, (color_key, color_name, default_color) in enumerate(self.color_configs):
            # 颜色名称
            name_item = QTableWidgetItem(color_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.color_table.setItem(row, 0, name_item)
            
            # 颜色预览
            color_label = QLabel()
            color_label.setFixedSize(80, 25)
            color_label.setStyleSheet(f"background-color: {default_color}; border: 1px solid #ccc;")
            self.color_table.setCellWidget(row, 1, color_label)
            
            # 选择颜色按钮
            color_btn = QPushButton("选择颜色")
            color_btn.clicked.connect(lambda _, r=row, c=color_key: self.choose_color(r, c))
            color_btn.setFixedSize(100, 25)
            self.color_table.setCellWidget(row, 2, color_btn)
            
            # 保存颜色值和控件引用
            self.color_inputs[color_key] = {
                'label': color_label,
                'button': color_btn,
                'value': default_color
            }
        
        # 设置表格行高
        self.color_table.verticalHeader().setDefaultSectionSize(30)
        
        color_layout.addWidget(self.color_table)
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # 预览区域
        preview_group = QGroupBox("预览效果")
        preview_layout = QVBoxLayout()
        preview_content = self.create_preview_widget()
        preview_layout.addWidget(preview_content)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 预设主题按钮
        preset_layout = QHBoxLayout()
        preset_label = QLabel("快速应用预设:")
        preset_layout.addWidget(preset_label)
        
        presets = [
            ("日间风格", {
                "background": "#FFFFFF", "secondary_background": "#F5F5F5", "card_background": "#FFFFFF",
                "primary_text": "#333333", "secondary_text": "#666666", "accent": "#2196F3",
                "success": "#4CAF50", "warning": "#FF9800", "danger": "#F44336", "border": "#E0E0E0",
                "hover": "#F0F0F0", "income": "#4CAF50", "expense": "#FF6B6B"
            }),
            ("暗夜风格", {
                "background": "#1E1E1E", "secondary_background": "#2D2D2D", "card_background": "#252526",
                "primary_text": "#FFFFFF", "secondary_text": "#B0B0B0", "accent": "#64B5F6",
                "success": "#81C784", "warning": "#FFB74D", "danger": "#E57373", "border": "#404040",
                "hover": "#333333", "income": "#81C784", "expense": "#E57373"
            }),
            ("护眼风格", {
                "background": "#F4F1E8", "secondary_background": "#E8E4D8", "card_background": "#FAF8F3",
                "primary_text": "#3D3D3D", "secondary_text": "#666666", "accent": "#8D6E63",
                "success": "#689F38", "warning": "#FFA726", "danger": "#EF5350", "border": "#D7CCC8",
                "hover": "#EFEBE9", "income": "#689F38", "expense": "#EF5350"
            }),
            ("科技风格", {
                "background": "#0F0F23", "secondary_background": "#1A1A2E", "card_background": "#16213E",
                "primary_text": "#E8E8E8", "secondary_text": "#B8B8B8", "accent": "#00FF88",
                "success": "#00C851", "warning": "#FFB300", "danger": "#FF4444", "border": "#2C3E50",
                "hover": "#1E3A5F", "income": "#00C851", "expense": "#FF4444"
            })
        ]
        
        for preset_name, preset_colors in presets:
            btn = QPushButton(preset_name)
            btn.clicked.connect(lambda _, colors=preset_colors: self.apply_preset(colors))
            btn.setMaximumWidth(80)
            preset_layout.addWidget(btn)
        
        preset_layout.addStretch()
        layout.addLayout(preset_layout)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        StyleHelper.apply_button_style(cancel_btn)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存主题")
        save_btn.clicked.connect(self.save_custom_theme)
        StyleHelper.apply_button_style(save_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def choose_color(self, row, color_key):
        """选择颜色"""
        current_color = self.color_inputs[color_key]['value']
        color = QColorDialog.getColor(QColor(current_color), self, f"选择{self.color_configs[row][1]}")
        if color.isValid():
            hex_color = color.name()
            self.update_color(color_key, hex_color)
    
    def update_color(self, color_key, hex_color):
        """更新颜色"""
        if color_key in self.color_inputs:
            self.color_inputs[color_key]['value'] = hex_color
            self.color_inputs[color_key]['label'].setStyleSheet(
                f"background-color: {hex_color}; border: 1px solid #ccc;"
            )
            # 更新预览
            self.update_preview()
    
    def apply_preset(self, preset_colors):
        """应用预设颜色"""
        for color_key, hex_color in preset_colors.items():
            self.update_color(color_key, hex_color)
    
    def create_preview_widget(self):
        """创建预览控件"""
        self.preview_widget = QWidget()
        layout = QVBoxLayout()
        
        # 预览标题
        title = QLabel("主题预览")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 预览内容
        preview_content = QWidget()
        preview_layout = QVBoxLayout()
        
        # 示例文本
        self.preview_text = QLabel("这是一段示例文本，用于预览主题效果")
        self.preview_text.setWordWrap(True)
        preview_layout.addWidget(self.preview_text)
        
        # 示例按钮
        button_layout = QHBoxLayout()
        self.preview_income_btn = QPushButton("收入按钮")
        self.preview_expense_btn = QPushButton("支出按钮")
        self.preview_normal_btn = QPushButton("普通按钮")
        
        button_layout.addWidget(self.preview_income_btn)
        button_layout.addWidget(self.preview_expense_btn)
        button_layout.addWidget(self.preview_normal_btn)
        preview_layout.addLayout(button_layout)
        
        preview_content.setLayout(preview_layout)
        layout.addWidget(preview_content)
        
        self.preview_widget.setLayout(layout)
        self.update_preview()
        
        return self.preview_widget
    
    def update_preview(self):
        """更新预览效果"""
        colors = {k: v['value'] for k, v in self.color_inputs.items()}
        
        # 应用预览样式
        self.preview_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['background']};
                color: {colors['primary_text']};
            }}
            QLabel {{
                color: {colors['primary_text']};
            }}
            QPushButton {{
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
        """)
        
        self.preview_income_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['income']};
                color: white;
            }}
        """)
        
        self.preview_expense_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['expense']};
                color: white;
            }}
        """)
        
        self.preview_normal_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['accent']};
                color: white;
            }}
        """)
    
    def save_custom_theme(self):
        """保存自定义主题"""
        name = self.name_input.text().strip()
        if not name:
            MessageHelper.show_warning(self, "提示", "请输入主题名称！")
            return
        
        # 检查名称是否重复
        for theme_id, theme_data in theme_manager.THEMES.items():
            if theme_data.get('name') == name:
                MessageHelper.show_warning(self, "提示", "主题名称已存在！")
                return
        
        # 构建主题数据
        colors = {k: v['value'] for k, v in self.color_inputs.items()}
        description = self.desc_input.toPlainText().strip() or f"用户自定义主题：{name}"
        
        # 生成主题ID
        theme_id = f"custom_{name}_{hash(name)}"
        
        theme_data = {
            "name": name,
            "description": description,
            "colors": colors
        }
        
        # 保存主题
        theme_manager.add_custom_theme(theme_id, theme_data)
        
        MessageHelper.show_info(self, "成功", f"主题 '{name}' 已成功保存！")
        self.accept()


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
                button_color = colors['income']
            elif self.category_type == "expense":
                button_color = colors['expense']
            else:
                button_color = colors['expense']
                
            self.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid {button_color};
                    border-radius: 6px;
                    padding: 6px 10px;
                    background-color: {button_color};
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
                border_color = colors['income']
            elif self.category_type == "expense":
                border_color = colors['expense']
            else:
                border_color = colors['expense']
                
            self.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid {border_color};
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
                    border-color: {border_color};
                }}
            """)
    
    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()


class AddLedgerDialog(BaseDialog):
    """添加账本对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加账本")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = self.create_form_layout()
        
        # 账本名称
        self.name_edit = self.create_line_edit()
        self.add_form_row(form_layout, "账本名称", self.name_edit)
        
        # 账本类型
        self.type_combo = self.create_combo_box(["个人", "家庭", "专项"])
        self.add_form_row(form_layout, "账本类型", self.type_combo)
        
        # 备注
        self.description_edit = self.create_text_edit(80)
        self.add_form_row(form_layout, "备注", self.description_edit)
        
        # 按钮
        button_layout = self.create_button_layout()
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'name': self.name_edit.text(),
            'type': self.type_combo.currentText(),
            'description': self.description_edit.toPlainText()
        }