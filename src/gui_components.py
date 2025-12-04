import sys
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

from theme_manager import theme_manager, number_to_chinese
from database_manager import DatabaseManager

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


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