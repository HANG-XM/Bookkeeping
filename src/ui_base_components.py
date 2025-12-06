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


class BaseDialog(QDialog):
    """对话框基类，封装通用的UI创建方法"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_completed = False
    
    def create_form_layout(self):
        """创建表单布局"""
        return QFormLayout()
    
    def create_button_layout(self, include_add_more=False):
        """创建按钮布局"""
        layout = QHBoxLayout()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        StyleHelper.apply_button_style(ok_button)
        layout.addWidget(ok_button)
        
        if include_add_more:
            add_more_button = QPushButton("再记")
            add_more_button.clicked.connect(self.add_more)
            layout.addWidget(add_more_button)
            self.is_add_more = False
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        StyleHelper.apply_button_style(cancel_button)
        layout.addWidget(cancel_button)
        
        return layout
    
    def create_date_edit(self, display_format="yyyy-MM-dd"):
        """创建日期编辑控件"""
        from PyQt6.QtWidgets import QDateTimeEdit
        from PyQt6.QtCore import QDateTime
        
        date_edit = QDateTimeEdit()
        date_edit.setDateTime(QDateTime.currentDateTime())
        date_edit.setDisplayFormat(display_format)
        date_edit.setCalendarPopup(True)
        return date_edit
    
    def create_date_edit_simple(self):
        """创建简单日期编辑控件（QDateEdit）"""
        from PyQt6.QtWidgets import QDateEdit
        from PyQt6.QtCore import QDate
        
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        return date_edit
    
    def create_amount_spin(self, min_val=0, max_val=999999.99, prefix="¥", suffix=""):
        """创建金额输入控件"""
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setDecimals(2)
        spin.setPrefix(prefix)
        if suffix:
            spin.setSuffix(suffix)
        return spin
    
    def create_account_combo(self, db_manager, include_balance=False):
        """创建账户选择控件"""
        combo = QComboBox()
        combo.addItem("")
        
        if hasattr(db_manager, 'get_accounts'):
            accounts = db_manager.get_accounts()
            for account in accounts:
                if include_balance:
                    combo.addItem(f"{account[1]} (余额: ¥{account[3]:.2f})")
                else:
                    combo.addItem(account[1])
        
        return combo
    
    def create_combo_box(self, items):
        """创建下拉框控件"""
        combo = QComboBox()
        combo.addItems(items)
        return combo
    
    def create_line_edit(self, placeholder=""):
        """创建文本输入框"""
        edit = QLineEdit()
        if placeholder:
            edit.setPlaceholderText(placeholder)
        return edit
    
    def create_text_edit(self, max_height=None):
        """创建多行文本框"""
        edit = QTextEdit()
        if max_height:
            edit.setMaximumHeight(max_height)
        return edit
    
    def create_check_box(self, text):
        """创建复选框"""
        checkbox = QCheckBox(text)
        checkbox.setStyleSheet("background-color: transparent;")
        return checkbox
    
    def add_form_row(self, layout, label_text, widget):
        """添加表单行"""
        label = QLabel(label_text + ":")
        StyleHelper.apply_label_style(label)
        layout.addRow(label, widget)
    
    def add_more(self):
        """再记按钮点击事件（子类可重写）"""
        self.is_add_more = True
        self.accept()
    
    def show_dialog(self, title=None):
        """显示对话框"""
        if title:
            self.setWindowTitle(title)
        self.setModal(True)
        if not self.setup_completed:
            self.setup_completed = True
        return self.exec()


class BaseTransactionDialog(BaseDialog):
    """交易对话框基类，封装通用的UI组件和方法"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.selected_category = None
        self.selected_subcategory = None
        self.subcategories = {}
        self.date_edit = None
        self.amount_spin = None
        self.account_combo = None
        self.description_edit = None
        self.settled_check = None
        self.refund_amount_spin = None
        self.refund_reason_edit = None
        
    def create_basic_info_group(self):
        """创建基本信息组"""
        group = QGroupBox("基本信息")
        layout = self.create_form_layout()
        
        # 交易时间
        self.date_edit = self.create_date_edit()
        self.add_form_row(layout, "交易时间", self.date_edit)
        
        # 金额
        self.amount_spin = self.create_amount_spin()
        self.add_form_row(layout, "金额", self.amount_spin)
        
        # 账户
        self.account_combo = self.create_account_combo(self.db_manager)
        self.add_form_row(layout, "账户", self.account_combo)
        
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
        layout = self.create_form_layout()
        
        # 备注
        self.description_edit = self.create_line_edit()
        self.add_form_row(layout, "备注", self.description_edit)
        
        # 销账标记（仅支出）
        if include_settlement:
            self.settled_check = self.create_check_box("已销账")
            layout.addRow("", self.settled_check)
        
        # 退款信息（仅支出）
        if include_refund:
            self.refund_amount_spin = self.create_amount_spin()
            self.add_form_row(layout, "退款金额", self.refund_amount_spin)
            
            self.refund_reason_edit = self.create_line_edit()
            self.add_form_row(layout, "退款原因", self.refund_reason_edit)
        
        group.setLayout(layout)
        return group
    
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


class BaseAccountDialog(BaseDialog):
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
        form_layout = self.create_form_layout()
        
        # 账户名称
        self.name_edit = self.create_line_edit()
        self.add_form_row(form_layout, "账户名称", self.name_edit)
        
        # 账户类型
        self.type_combo = self.create_combo_box(["现金", "银行卡", "电子支付", "其他"])
        self.add_form_row(form_layout, "账户类型", self.type_combo)
        
        # 开户行
        self.bank_edit = self.create_line_edit()
        self.add_form_row(form_layout, "开户行", self.bank_edit)
        
        # 初始余额
        self.balance_spin = self.create_amount_spin()
        self.add_form_row(form_layout, "初始余额", self.balance_spin)
        
        # 备注
        self.description_edit = self.create_text_edit(80)
        self.add_form_row(form_layout, "备注", self.description_edit)
        
        # 按钮
        button_layout = self.create_button_layout()
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        return layout
    
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


class BaseTransferDialog(BaseDialog):
    """转账对话框基类"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.date_edit = None
        self.from_account_combo = None
        self.to_account_combo = None
        self.amount_spin = None
        self.description_edit = None
    
    def setup_transfer_form(self):
        """设置转账表单"""
        layout = QVBoxLayout()
        form_layout = self.create_form_layout()
        
        # 转账日期
        self.date_edit = self.create_date_edit()
        self.add_form_row(form_layout, "转账日期", self.date_edit)
        
        # 账户选择
        self.from_account_combo = self.create_account_combo(self.db_manager, include_balance=True)
        self.to_account_combo = self.create_account_combo(self.db_manager, include_balance=True)
        self.add_form_row(form_layout, "转出账户", self.from_account_combo)
        self.add_form_row(form_layout, "转入账户", self.to_account_combo)
        
        # 转账金额
        self.amount_spin = self.create_amount_spin()
        self.add_form_row(form_layout, "转账金额", self.amount_spin)
        
        # 备注
        self.description_edit = self.create_line_edit()
        self.add_form_row(form_layout, "备注", self.description_edit)
        
        # 按钮
        button_layout = self.create_button_layout()
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        return layout
    
    def get_data(self):
        """获取转账数据"""
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


class BaseBudgetDialog(BaseDialog):
    """预算对话框基类"""
    
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.category_combo = None
        self.budget_type_combo = None
        self.amount_spin = None
        self.threshold_spin = None
        self.start_date_edit = None
        self.end_date_edit = None
        self.end_date_check = None
    
    def setup_budget_form(self):
        """设置预算表单"""
        layout = QVBoxLayout()
        form_layout = self.create_form_layout()
        
        # 类别选择
        self.category_combo = self.create_combo_box(self.categories)
        self.add_form_row(form_layout, "支出类别", self.category_combo)
        
        # 预算类型
        self.budget_type_combo = self.create_combo_box(["月度预算", "年度预算"])
        self.budget_type_combo.currentTextChanged.connect(self.on_budget_type_changed)
        self.add_form_row(form_layout, "预算类型", self.budget_type_combo)
        
        # 预算金额
        self.amount_spin = self.create_amount_spin(suffix="元")
        self.add_form_row(form_layout, "预算金额", self.amount_spin)
        
        # 预警阈值
        self.threshold_spin = self.create_amount_spin(0, 100, "", "%")
        self.threshold_spin.setValue(80)
        self.add_form_row(form_layout, "预警阈值", self.threshold_spin)
        
        # 生效日期
        self.start_date_edit = self.create_date_edit_simple()
        self.add_form_row(form_layout, "生效日期", self.start_date_edit)
        
        # 结束日期（可选）
        self.end_date_edit = self.create_date_edit_simple()
        self.end_date_check = self.create_check_box("设置结束日期")
        self.end_date_check.toggled.connect(self.end_date_edit.setEnabled)
        self.end_date_edit.setEnabled(False)
        self.add_form_row(form_layout, "结束日期", self.end_date_check)
        form_layout.addRow("", self.end_date_edit)
        
        # 按钮
        button_layout = self.create_button_layout()
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        # 初始化日期
        self.on_budget_type_changed()
        
        return layout
    
    def on_budget_type_changed(self):
        """预算类型改变时的处理"""
        budget_type = self.budget_type_combo.currentText()
        current_date = QDate.currentDate()
        
        if "月度" in budget_type:
            self.start_date_edit.setDate(QDate(current_date.year(), current_date.month(), 1))
        else:  # 年度
            self.start_date_edit.setDate(QDate(current_date.year(), 1, 1))
    
    def get_data(self):
        """获取预算数据"""
        budget_type = 'monthly' if self.budget_type_combo.currentText() == "月度预算" else 'yearly'
        
        return {
            'category': self.category_combo.currentText(),
            'budget_type': budget_type,
            'amount': self.amount_spin.value(),
            'warning_threshold': self.threshold_spin.value(),
            'start_date': self.start_date_edit.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date_edit.date().toString("yyyy-MM-dd") if self.end_date_check.isChecked() else None
        }


class BaseReportDialog(BaseDialog):
    """报表对话框基类，预留用于将来的报表功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart_widget = None
        self.date_range_widget = None
    
    def setup_report_form(self):
        """设置报表表单，预留接口"""
        layout = QVBoxLayout()
        form_layout = self.create_form_layout()
        
        # 日期范围选择
        self.start_date_edit = self.create_date_edit_simple()
        self.end_date_edit = self.create_date_edit_simple()
        self.add_form_row(form_layout, "开始日期", self.start_date_edit)
        self.add_form_row(form_layout, "结束日期", self.end_date_edit)
        
        # 报表类型选择
        self.report_type_combo = self.create_combo_box(["收支汇总", "分类统计", "趋势分析"])
        self.add_form_row(form_layout, "报表类型", self.report_type_combo)
        
        layout.addLayout(form_layout)
        return layout


class BaseImportExportDialog(BaseDialog):
    """导入导出对话框基类，预留用于将来的数据导入导出功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path_edit = None
        self.format_combo = None
    
    def setup_import_export_form(self, is_import=True):
        """设置导入导出表单，预留接口"""
        layout = QVBoxLayout()
        form_layout = self.create_form_layout()
        
        # 文件路径
        self.file_path_edit = self.create_line_edit("选择文件...")
        self.add_form_row(form_layout, "文件路径", self.file_path_edit)
        
        # 文件格式
        formats = ["CSV", "Excel", "JSON"] if is_import else ["CSV", "Excel", "PDF"]
        self.format_combo = self.create_combo_box(formats)
        self.add_form_row(form_layout, "文件格式", self.format_combo)
        
        layout.addLayout(form_layout)
        return layout


# 扩展接口 - 预留给将来功能使用
class FeatureExtensionManager:
    """功能扩展管理器，预留用于插件系统或功能模块"""
    
    def __init__(self):
        self.plugins = {}
        self.hooks = {}
    
    def register_plugin(self, plugin_name, plugin_instance):
        """注册插件，预留接口"""
        self.plugins[plugin_name] = plugin_instance
    
    def register_hook(self, hook_name, callback):
        """注册钩子函数，预留接口"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def execute_hooks(self, hook_name, *args, **kwargs):
        """执行钩子函数，预留接口"""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                callback(*args, **kwargs)


# 全局扩展管理器实例
extension_manager = FeatureExtensionManager()


class DialogFactory:
    """对话框工厂类，统一管理对话框的创建"""
    
    @staticmethod
    def create_transaction_dialog(transaction_type, db_manager, ledger_id, parent=None, edit_data=None):
        """创建交易对话框工厂方法"""
        from dialogs import AddIncomeDialog, EditIncomeDialog, AddExpenseDialog, EditExpenseDialog
        
        if transaction_type == "收入":
            if edit_data:
                return EditIncomeDialog(db_manager, edit_data, parent)
            else:
                return AddIncomeDialog(db_manager, ledger_id, parent)
        elif transaction_type == "支出":
            if edit_data:
                return EditExpenseDialog(db_manager, edit_data, parent)
            else:
                return AddExpenseDialog(db_manager, ledger_id, parent)
        else:
            raise ValueError(f"未知的交易类型: {transaction_type}")
    
    @staticmethod
    def create_account_dialog(account_data=None, parent=None):
        """创建账户对话框工厂方法"""
        from gui_main import AddAccountDialog, EditAccountDialog
        
        if account_data:
            return EditAccountDialog(account_data, parent)
        else:
            return AddAccountDialog(parent)
    
    @staticmethod
    def create_transfer_dialog(transfer_data=None, db_manager=None, parent=None):
        """创建转账对话框工厂方法"""
        from gui_main import TransferDialog, EditTransferDialog
        
        if transfer_data:
            return EditTransferDialog(transfer_data, db_manager, parent)
        else:
            return TransferDialog(db_manager, parent)
    
    @staticmethod
    def create_budget_dialog(budget_data=None, categories=None, parent=None):
        """创建预算对话框工厂方法"""
        from gui_main import AddBudgetDialog, EditBudgetDialog
        
        if budget_data:
            return EditBudgetDialog(budget_data, categories, parent)
        else:
            return AddBudgetDialog(categories, parent)
    
    @staticmethod
    def create_ledger_dialog(ledger_data=None, parent=None):
        """创建账本对话框工厂方法"""
        from gui_components import AddLedgerDialog
        
        # 预留编辑账本的功能接口
        return AddLedgerDialog(parent)


class UIComponentFactory:
    """UI组件工厂类，统一管理UI组件的创建"""
    
    @staticmethod
    def create_category_button(text, category_type="normal", parent=None):
        """创建类别按钮"""
        from gui_components import CategoryButton
        return CategoryButton(text, category_type)
    
    @staticmethod
    def create_info_card(title, value, color, parent=None):
        """创建信息卡片，预留接口用于扩展"""
        from PyQt6.QtWidgets import QLabel, QVBoxLayout, QFrame
        
        card = QFrame(parent)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme_manager.get_current_theme()['colors']['card_background']};
                border: 1px solid {theme_manager.get_current_theme()['colors']['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        StyleHelper.apply_label_style(title_label)
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 18px;
                font-weight: bold;
                background-color: transparent;
            }}
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        
        return card


class ConfigManager:
    """配置管理器，统一管理应用配置"""
    
    def __init__(self):
        from PyQt6.QtCore import QSettings
        # 设置应用信息以便QSettings正常工作
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, ".")
        self.settings = QSettings("BookkeepingApp", "MultiLedgerSystem")
    
    def get_setting(self, key, default_value=None, value_type=None):
        """获取配置值"""
        if value_type is not None:
            return self.settings.value(key, default_value, type=value_type)
        return self.settings.value(key, default_value)
    
    def set_setting(self, key, value):
        """设置配置值"""
        self.settings.setValue(key, value)
    
    def get_auto_open_last_ledger(self):
        """获取是否自动打开上次账本"""
        return self.get_setting("auto_open_last_ledger", False, bool)
    
    def set_auto_open_last_ledger(self, value):
        """设置是否自动打开上次账本"""
        self.set_setting("auto_open_last_ledger", value)
    
    def get_auto_restore_stats_view(self):
        """获取是否自动恢复统计视图"""
        return self.get_setting("auto_restore_stats_view", False, bool)
    
    def set_auto_restore_stats_view(self, value):
        """设置是否自动恢复统计视图"""
        self.set_setting("auto_restore_stats_view", value)
    
    def get_last_ledger_info(self):
        """获取上次账本信息"""
        return self.get_setting("last_ledger_info", "")
    
    def set_last_ledger_info(self, info):
        """设置上次账本信息"""
        self.set_setting("last_ledger_info", info)
    
    def get_last_stats_view(self):
        """获取上次统计视图"""
        return self.get_setting("last_stats_view", "day")
    
    def set_last_stats_view(self, view):
        """设置上次统计视图"""
        self.set_setting("last_stats_view", view)
    
    def save_window_geometry(self, window):
        """保存窗口几何信息"""
        self.set_setting("geometry", window.saveGeometry())
        self.set_setting("windowState", window.saveState())
    
    def restore_window_geometry(self, window):
        """恢复窗口几何信息"""
        if self.settings.contains("geometry"):
            window.restoreGeometry(self.settings.value("geometry"))
        if self.settings.contains("windowState"):
            window.restoreState(self.settings.value("windowState"))


# 全局配置管理器实例
config_manager = ConfigManager()