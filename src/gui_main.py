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
from gui_components import (SystemSettingsDialog, ThemeSelectionDialog, CategoryButton, 
                           AddLedgerDialog, EditIncomeDialog, AddIncomeDialog)
from gui_components import EditExpenseDialog, AddExpenseDialog

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


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
                }}
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
            ledger_info = self.ledgers[ledger_id]
            self.current_ledger_label.setText(f"当前账本: {ledger_info['name']} ({ledger_info['type']})")
            self.current_ledger_id = ledger_id
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
                                   f"确定要删除这条交易记录吗？\n"
                                   f"日期: {transaction_date}\n"
                                   f"类型: {transaction_type}\n"
                                   f"类别: {category} - {subcategory}\n"
                                   f"金额: ¥{abs(amount):.2f}\n"
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