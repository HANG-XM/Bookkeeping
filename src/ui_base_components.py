"""
基础UI组件模块 - 提供通用的UI组件和功能
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QFormLayout, QLabel, QPushButton, QLineEdit, 
                            QTextEdit, QComboBox, QCheckBox, QDoubleSpinBox, 
                            QScrollArea, QWidget, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from theme_manager import theme_manager


class BaseTransactionDialog(QDialog):
    """交易对话框基类，封装通用的UI组件和方法"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.selected_category = None
        self.selected_subcategory = None
        self.subcategories = {}
        
    def create_basic_info_group(self):
        """创建基本信息组"""
        group = QGroupBox("基本信息")
        layout = QFormLayout()
        
        # 交易时间
        self.date_edit = self._create_date_edit()
        layout.addRow("交易时间:", self.date_edit)
        
        # 金额
        self.amount_spin = self._create_amount_spin()
        layout.addRow("金额:", self.amount_spin)
        
        # 账户
        self.account_combo = self._create_account_combo()
        layout.addRow("账户:", self.account_combo)
        
        group.setLayout(layout)
        return group
    
    def create_category_group(self, title):
        """创建类别选择组"""
        group = QGroupBox(title)
        layout = QVBoxLayout()
        
        # 主类别标签
        main_label = QLabel("主类别:")
        main_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        main_label.setStyleSheet("background-color: transparent;")
        layout.addWidget(main_label)
        
        # 主类别滚动区域
        self.main_category_scroll = self._create_category_scroll()
        self.main_category_content = QWidget()
        self.main_category_grid_layout = QVBoxLayout(self.main_category_content)
        self.main_category_scroll.setWidget(self.main_category_content)
        layout.addWidget(self.main_category_scroll)
        
        # 子类别标签
        self.subcategory_label = QLabel("子类别:")
        self.subcategory_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.subcategory_label.setStyleSheet("background-color: transparent;")
        self.subcategory_label.setVisible(False)
        layout.addWidget(self.subcategory_label)
        
        # 子类别滚动区域
        self.subcategory_scroll = self._create_category_scroll()
        self.subcategory_content = QWidget()
        self.subcategory_grid_layout = QVBoxLayout(self.subcategory_content)
        self.subcategory_scroll.setWidget(self.subcategory_content)
        self.subcategory_scroll.setVisible(False)
        layout.addWidget(self.subcategory_scroll)
        
        group.setLayout(layout)
        return group
    
    def create_other_info_group(self, include_settlement=True, include_refund=True):
        """创建其他信息组"""
        group = QGroupBox("其他信息")
        layout = QFormLayout()
        
        # 备注
        self.description_edit = QLineEdit()
        layout.addRow("备注:", self.description_edit)
        
        # 销账标记（仅支出）
        if include_settlement:
            self.settled_check = QCheckBox("已销账")
            self.settled_check.setStyleSheet("background-color: transparent;")
            layout.addRow("", self.settled_check)
        
        # 退款信息（仅支出）
        if include_refund:
            self.refund_amount_spin = self._create_amount_spin(0, 999999.99, "¥")
            layout.addRow("退款金额:", self.refund_amount_spin)
            
            self.refund_reason_edit = QLineEdit()
            layout.addRow("退款原因:", self.refund_reason_edit)
        
        group.setLayout(layout)
        return group
    
    def create_button_layout(self, include_add_more=False):
        """创建按钮布局"""
        layout = QHBoxLayout()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        if include_add_more:
            add_more_button = QPushButton("再记")
            add_more_button.clicked.connect(self.add_more)
            layout.addWidget(add_more_button)
            self.is_add_more = False
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)
        
        return layout
    
    def _create_date_edit(self):
        """创建日期编辑控件"""
        from PyQt6.QtWidgets import QDateTimeEdit
        from PyQt6.QtCore import QDateTime
        
        date_edit = QDateTimeEdit()
        date_edit.setDateTime(QDateTime.currentDateTime())
        date_edit.setDisplayFormat("yyyy-MM-dd")
        date_edit.setCalendarPopup(True)
        return date_edit
    
    def _create_amount_spin(self, min_val=0, max_val=999999.99, prefix="¥"):
        """创建金额输入控件"""
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setDecimals(2)
        spin.setPrefix(prefix)
        return spin
    
    def _create_account_combo(self):
        """创建账户选择控件"""
        combo = QComboBox()
        combo.addItem("")
        accounts = self.db_manager.get_accounts()
        for account in accounts:
            combo.addItem(account[1])
        return combo
    
    def _create_category_scroll(self):
        """创建类别滚动区域"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(80)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        return scroll
    
    def load_categories(self, transaction_type):
        """加载类别数据"""
        categories = self.db_manager.get_categories(transaction_type)
        
        # 按主类别分组
        self.subcategories = {}
        for parent, sub, cat_type in categories:
            if parent not in self.subcategories:
                self.subcategories[parent] = []
            self.subcategories[parent].append(sub)
        
        # 创建主类别按钮
        self._create_category_buttons(transaction_type)
    
    def _create_category_buttons(self, transaction_type):
        """创建类别按钮"""
        from gui_components import CategoryButton
        
        # 清除之前的按钮
        self._clear_layout(self.main_category_grid_layout)
        
        # 创建按钮行
        row_widget = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        category_type = "income" if transaction_type == "收入" else "expense"
        
        for category in self.subcategories.keys():
            btn = CategoryButton(category, category_type)
            btn.clicked.connect(lambda checked, cat=category: self.on_main_category_clicked(cat))
            row_layout.addWidget(btn)
        
        row_layout.addStretch()
        row_widget.setLayout(row_layout)
        self.main_category_grid_layout.addWidget(row_widget)
    
    def on_main_category_clicked(self, category):
        """主类别点击事件"""
        # 清除之前的选择
        self._clear_category_selection(self.main_category_grid_layout)
        
        # 设置当前选择
        sender = self.sender()
        if hasattr(sender, 'set_selected'):
            sender.set_selected(True)
        
        self.selected_category = category
        self.show_subcategories(category)
    
    def show_subcategories(self, category):
        """显示子类别"""
        from gui_components import CategoryButton
        
        # 清除之前的子类别按钮
        self._clear_layout(self.subcategory_grid_layout)
        
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
        
        # 显示子类别区域
        self.subcategory_label.setVisible(True)
        self.subcategory_scroll.setVisible(True)
    
    def on_subcategory_clicked(self, subcategory):
        """子类别点击事件"""
        # 清除之前的选择
        self._clear_category_selection(self.subcategory_grid_layout)
        
        # 设置当前选择
        sender = self.sender()
        if hasattr(sender, 'set_selected'):
            sender.set_selected(True)
        
        self.selected_subcategory = subcategory
    
    def _clear_layout(self, layout):
        """清除布局中的控件"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def _clear_category_selection(self, layout):
        """清除类别选择状态"""
        for i in range(layout.count()):
            row_widget = layout.itemAt(i).widget()
            if row_widget and row_widget.layout():
                for j in range(row_widget.layout().count()):
                    widget = row_widget.layout().itemAt(j).widget()
                    if hasattr(widget, 'set_selected'):
                        widget.set_selected(False)
    
    def add_more(self):
        """再记按钮点击事件"""
        self.is_add_more = True
        self.accept()


class BaseEditDialog(BaseTransactionDialog):
    """编辑对话框基类"""
    
    def __init__(self, db_manager, transaction_data, parent=None):
        super().__init__(db_manager, parent)
        self.transaction_data = transaction_data
        self.selected_category = None
        self.selected_subcategory = None
    
    def load_transaction_data(self, transaction_type):
        """加载交易数据"""
        if not self.transaction_data:
            return
        
        (trans_id, ledger_id, transaction_date, trans_type, category, subcategory, 
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
            if subcategory:
                self.selected_subcategory = subcategory
        
        # 支出特有字段
        if transaction_type == "支出" and hasattr(self, 'settled_check'):
            self.settled_check.setChecked(is_settled)
            self.refund_amount_spin.setValue(refund_amount)
            self.refund_reason_edit.setText(refund_reason or "")


class StyleHelper:
    """样式助手类，提供通用的样式设置方法"""
    
    @staticmethod
    def apply_button_style(button, button_type="default"):
        """应用按钮样式"""
        colors = theme_manager.get_current_theme()["colors"]
        text = button.text().lower()
        
        if button_type == "income" or "收入" in text:
            color = colors['income']
        elif button_type == "expense" or "支出" in text:
            color = colors['expense']
        elif button_type == "danger" or "删除" in text:
            color = colors['danger']
        else:
            color = colors['accent']
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {colors['hover']};
                border: 1px solid {color};
            }}
        """)
    
    @staticmethod
    def apply_table_style(table):
        """应用表格样式"""
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
    
    @staticmethod
    def apply_label_style(label, label_type="default"):
        """应用标签样式"""
        colors = theme_manager.get_current_theme()["colors"]
        label.setStyleSheet(f"""
            QLabel {{
                color: {colors['primary_text']};
                background-color: transparent;
            }}
        """)
    
    @staticmethod
    def apply_checkbox_style(checkbox):
        """应用复选框样式"""
        colors = theme_manager.get_current_theme()["colors"]
        checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {colors['primary_text']};
                background-color: transparent;
            }}
        """)
    
    @staticmethod
    def apply_card_title_style(label, color):
        """应用卡片标题样式"""
        label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold; background-color: transparent;")
    
    @staticmethod
    def apply_card_amount_style(label, color):
        """应用卡片金额样式"""
        label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; background-color: transparent;")
    
    @staticmethod
    def apply_card_chinese_style(label, color):
        """应用卡片中文样式"""
        label.setStyleSheet(f"color: {color}; font-size: 12px; background-color: transparent;")
    
    @staticmethod
    def apply_groupbox_style(groupbox):
        """应用组框样式"""
        colors = theme_manager.get_current_theme()["colors"]
        groupbox.setStyleSheet(f"""
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
        """)


class BaseAccountDialog(QDialog):
    """账户对话框基类，封装通用的账户表单UI"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.name_edit = None
        self.type_combo = None
        self.bank_edit = None
        self.balance_spin = None
        self.description_edit = None
    
    def setup_account_form(self):
        """设置账户表单"""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # 账户名称
        self.name_edit = QLineEdit()
        account_name_label = QLabel("账户名称:")
        StyleHelper.apply_label_style(account_name_label)
        form_layout.addRow(account_name_label, self.name_edit)
        
        # 账户类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(["现金", "银行卡", "电子支付", "其他"])
        account_type_label = QLabel("账户类型:")
        StyleHelper.apply_label_style(account_type_label)
        form_layout.addRow(account_type_label, self.type_combo)
        
        # 开户行
        self.bank_edit = QLineEdit()
        bank_label = QLabel("开户行:")
        StyleHelper.apply_label_style(bank_label)
        form_layout.addRow(bank_label, self.bank_edit)
        
        # 初始余额
        self.balance_spin = QDoubleSpinBox()
        self.balance_spin.setRange(0, 999999.99)
        self.balance_spin.setDecimals(2)
        self.balance_spin.setPrefix("¥")
        balance_label = QLabel("初始余额:")
        StyleHelper.apply_label_style(balance_label)
        form_layout.addRow(balance_label, self.balance_spin)
        
        # 备注
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        note_label = QLabel("备注:")
        StyleHelper.apply_label_style(note_label)
        form_layout.addRow(note_label, self.description_edit)
        
        # 按钮
        button_layout = self.create_button_layout()
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        return layout
    
    def create_button_layout(self):
        """创建按钮布局"""
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        StyleHelper.apply_button_style(ok_button)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        StyleHelper.apply_button_style(cancel_button)
        button_layout.addWidget(cancel_button)
        
        return button_layout
    
    def get_account_data(self):
        """获取表单数据"""
        return {
            'name': self.name_edit.text(),
            'type': self.type_combo.currentText(),
            'bank': self.bank_edit.text(),
            'balance': self.balance_spin.value(),
            'description': self.description_edit.toPlainText()
        }


class MessageHelper:
    """消息助手类，提供通用的消息显示方法"""
    
    @staticmethod
    def show_info(parent, title, message):
        """显示信息消息"""
        QMessageBox.information(parent, title, message)
    
    @staticmethod
    def show_warning(parent, title, message):
        """显示警告消息"""
        QMessageBox.warning(parent, title, message)
    
    @staticmethod
    def show_error(parent, title, message):
        """显示错误消息"""
        QMessageBox.critical(parent, title, message)
    
    @staticmethod
    def ask_confirmation(parent, title, message):
        """询问确认"""
        reply = QMessageBox.question(
            parent, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes