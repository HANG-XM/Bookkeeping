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
                           AddLedgerDialog)
from dialogs import EditIncomeDialog, AddIncomeDialog, EditExpenseDialog, AddExpenseDialog
from ui_base_components import StyleHelper, MessageHelper, BaseAccountDialog
from chart_utils import ChartUtils

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


class EditAccountDialog(BaseAccountDialog):
    """编辑账户对话框"""
    
    def __init__(self, account_data, parent=None):
        super().__init__(parent)
        self.account_data = account_data
        self.setWindowTitle("编辑账户")
        self.setModal(True)
        self.setup_ui()
        self.load_account_data()
    
    def setup_ui(self):
        layout = self.setup_account_form()
        self.setLayout(layout)
    
    def load_account_data(self):
        """加载账户数据"""
        if self.account_data:
            (account_id, name, account_type, balance, bank, description) = self.account_data
            self.name_edit.setText(name)
            self.type_combo.setCurrentText(account_type)
            self.bank_edit.setText(bank or "")
            self.balance_spin.setValue(balance)
            self.description_edit.setPlainText(description or "")
    
    def get_data(self):
        data = super().get_account_data()
        data['id'] = self.account_data[0] if self.account_data else None
        return data


class AddAccountDialog(BaseAccountDialog):
    """添加账户对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加账户")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        layout = self.setup_account_form()
        self.setLayout(layout)


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
        
        transfer_date_label = QLabel("转账日期:")
        StyleHelper.apply_label_style(transfer_date_label)
        form_layout.addRow(transfer_date_label, self.date_edit)
        
        from_account_label = QLabel("转出账户:")
        StyleHelper.apply_label_style(from_account_label)
        form_layout.addRow(from_account_label, self.from_account_combo)
        
        to_account_label = QLabel("转入账户:")
        StyleHelper.apply_label_style(to_account_label)
        form_layout.addRow(to_account_label, self.to_account_combo)
        
        transfer_amount_label = QLabel("转账金额:")
        StyleHelper.apply_label_style(transfer_amount_label)
        form_layout.addRow(transfer_amount_label, self.amount_spin)
        
        transfer_note_label = QLabel("备注:")
        StyleHelper.apply_label_style(transfer_note_label)
        form_layout.addRow(transfer_note_label, self.description_edit)
        
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


class EditTransferDialog(QDialog):
    """编辑转账对话框"""
    
    def __init__(self, transfer_data, db_manager, parent=None):
        super().__init__(parent)
        self.transfer_data = transfer_data
        self.db_manager = db_manager
        self.setWindowTitle("编辑转账")
        self.setModal(True)
        self.setup_ui()
        self.load_accounts()
        self.load_transfer_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # 转账日期
        self.date_edit = QDateTimeEdit()
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
        
        transfer_date_label = QLabel("转账日期:")
        StyleHelper.apply_label_style(transfer_date_label)
        form_layout.addRow(transfer_date_label, self.date_edit)
        
        from_account_label = QLabel("转出账户:")
        StyleHelper.apply_label_style(from_account_label)
        form_layout.addRow(from_account_label, self.from_account_combo)
        
        to_account_label = QLabel("转入账户:")
        StyleHelper.apply_label_style(to_account_label)
        form_layout.addRow(to_account_label, self.to_account_combo)
        
        transfer_amount_label = QLabel("转账金额:")
        StyleHelper.apply_label_style(transfer_amount_label)
        form_layout.addRow(transfer_amount_label, self.amount_spin)
        
        transfer_note_label = QLabel("备注:")
        StyleHelper.apply_label_style(transfer_note_label)
        form_layout.addRow(transfer_note_label, self.description_edit)
        
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
    
    def load_transfer_data(self):
        """加载转账数据"""
        if self.transfer_data:
            (transfer_id, transfer_date, from_account, to_account, amount, description, created_time) = self.transfer_data
            self.date_edit.setDate(QDate.fromString(transfer_date, "yyyy-MM-dd"))
            
            # 设置转出账户
            for i in range(self.from_account_combo.count()):
                account_text = self.from_account_combo.itemText(i)
                if account_text.startswith(from_account):
                    self.from_account_combo.setCurrentIndex(i)
                    break
            
            # 设置转入账户
            for i in range(self.to_account_combo.count()):
                account_text = self.to_account_combo.itemText(i)
                if account_text.startswith(to_account):
                    self.to_account_combo.setCurrentIndex(i)
                    break
            
            self.amount_spin.setValue(amount)
            self.description_edit.setText(description or "")
    
    def get_data(self):
        # 提取账户名称（去掉余额信息）
        from_account = self.from_account_combo.currentText().split(" (余额:")[0]
        to_account = self.to_account_combo.currentText().split(" (余额:")[0]
        
        return {
            'id': self.transfer_data[0] if self.transfer_data else None,
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
        edit_transfer_btn = QPushButton("编辑转账")
        edit_transfer_btn.clicked.connect(self.edit_transfer)
        delete_transfer_btn = QPushButton("删除转账")
        delete_transfer_btn.clicked.connect(self.delete_transfer)
        transfer_btn_layout.addWidget(add_transfer_btn)
        transfer_btn_layout.addWidget(edit_transfer_btn)
        transfer_btn_layout.addWidget(delete_transfer_btn)
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
                MessageHelper.show_info(self, "成功", "账户添加成功！")
    
    def edit_account(self):
        current_row = self.account_table.currentRow()
        if current_row < 0:
            MessageHelper.show_warning(self, "警告", "请先选择要编辑的账户！")
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
            MessageHelper.show_warning(self, "警告", "找不到选中的账户数据！")
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
                MessageHelper.show_info(self, "成功", "账户修改成功！")
    
    def delete_account(self):
        current_row = self.account_table.currentRow()
        if current_row < 0:
            MessageHelper.show_warning(self, "警告", "请先选择要删除的账户！")
            return
        
        account_name = self.account_table.item(current_row, 0).text()
        accounts = self.db_manager.get_accounts()
        account_data = None
        for account in accounts:
            if account[1] == account_name:
                account_data = account
                break
        
        if not account_data:
            MessageHelper.show_warning(self, "警告", "找不到选中的账户数据！")
            return
        
        if not MessageHelper.ask_confirmation(self, "确认删除", 
                                   f"确定要删除账户 '{account_name}' 吗？删除后将无法恢复！"):
            self.db_manager.delete_account(account_data[0])
            self.load_accounts()
            # 刷新统计页面
            parent = self.parent()
            if parent and hasattr(parent, 'statistics_widget'):
                parent.statistics_widget.update_statistics()
            MessageHelper.show_info(self, "成功", "账户删除成功！")
    
    def add_transfer(self):
        dialog = TransferDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['from_account'] and data['to_account'] and data['amount'] > 0:
                if data['from_account'] == data['to_account']:
                    MessageHelper.show_warning(self, "警告", "转出账户和转入账户不能相同！")
                    return
                
                # 检查转出账户余额
                from_balance = self.db_manager.get_account_balance(data['from_account'])
                if from_balance < data['amount']:
                    MessageHelper.show_warning(self, "警告", f"转出账户余额不足！当前余额: ¥{from_balance:.2f}")
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
                MessageHelper.show_info(self, "成功", "转账记录添加成功！")
    
    def edit_transfer(self):
        current_row = self.transfer_table.currentRow()
        if current_row < 0:
            MessageHelper.show_warning(self, "警告", "请先选择要编辑的转账记录！")
            return
        
        # 获取选中的转账记录数据
        transfers = self.db_manager.get_transfers()
        if current_row >= len(transfers):
            MessageHelper.show_warning(self, "警告", "找不到选中的转账记录！")
            return
        
        transfer_data = transfers[current_row]
        
        dialog = EditTransferDialog(transfer_data, self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['from_account'] and data['to_account'] and data['amount'] > 0:
                if data['from_account'] == data['to_account']:
                    MessageHelper.show_warning(self, "警告", "转出账户和转入账户不能相同！")
                    return
                
                # 获取原始转账数据以计算余额变化
                old_from_account = transfer_data[2]
                old_to_account = transfer_data[3]
                old_amount = transfer_data[4]
                
                # 如果转出账户或金额发生变化，需要检查新转出账户的余额
                if old_from_account != data['from_account'] or old_amount != data['amount']:
                    # 先恢复原始转账对账户余额的影响
                    self.db_manager.update_account_balance(old_from_account, old_amount)
                    self.db_manager.update_account_balance(old_to_account, -old_amount)
                    
                    # 检查新转出账户余额
                    from_balance = self.db_manager.get_account_balance(data['from_account'])
                    if from_balance < data['amount']:
                        # 恢复原始转账记录
                        self.db_manager.update_account_balance(old_from_account, -old_amount)
                        self.db_manager.update_account_balance(old_to_account, old_amount)
                        MessageHelper.show_warning(self, "警告", f"转出账户余额不足！当前余额: ¥{from_balance:.2f}")
                        return
                
                    # 应用新的转账对账户余额的影响
                    self.db_manager.update_account_balance(data['from_account'], -data['amount'])
                    self.db_manager.update_account_balance(data['to_account'], data['amount'])
                elif old_to_account != data['to_account']:
                    # 只有转入账户发生变化
                    self.db_manager.update_account_balance(old_to_account, -old_amount)
                    self.db_manager.update_account_balance(data['to_account'], data['amount'])
                
                self.db_manager.update_transfer(
                    data['id'], data['transfer_date'], data['from_account'], 
                    data['to_account'], data['amount'], data['description']
                )
                self.load_accounts()
                self.load_transfers()
                # 刷新统计页面
                parent = self.parent()
                if parent and hasattr(parent, 'statistics_widget'):
                    parent.statistics_widget.update_statistics()
                MessageHelper.show_info(self, "成功", "转账记录修改成功！")
    
    def delete_transfer(self):
        current_row = self.transfer_table.currentRow()
        if current_row < 0:
            MessageHelper.show_warning(self, "警告", "请先选择要删除的转账记录！")
            return
        
        # 获取选中的转账记录数据
        transfers = self.db_manager.get_transfers()
        if current_row >= len(transfers):
            MessageHelper.show_warning(self, "警告", "找不到选中的转账记录！")
            return
        
        transfer_data = transfers[current_row]
        transfer_date = transfer_data[1]
        from_account = transfer_data[2]
        to_account = transfer_data[3]
        amount = transfer_data[4]
        description = transfer_data[5]
        
        if not MessageHelper.ask_confirmation(self, "确认删除", 
                                   f"确定要删除这条转账记录吗？\n"
                                   f"日期: {transfer_date}\n"
                                   f"转出账户: {from_account}\n"
                                   f"转入账户: {to_account}\n"
                                   f"金额: ¥{amount:.2f}\n"
                                   f"备注: {description or '无'}\n"
                                   f"删除后将无法恢复！"):
            # 恢复账户余额（删除转账需要反向操作）
            self.db_manager.update_account_balance(from_account, amount)
            self.db_manager.update_account_balance(to_account, -amount)
            
            self.db_manager.delete_transfer(transfer_data[0])
            self.load_accounts()
            self.load_transfers()
            # 刷新统计页面
            parent = self.parent()
            if parent and hasattr(parent, 'statistics_widget'):
                parent.statistics_widget.update_statistics()
            MessageHelper.show_info(self, "成功", "转账记录删除成功！")


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
        start_date_label = QLabel("起始日期:")
        StyleHelper.apply_label_style(start_date_label)
        custom_date_layout.addWidget(start_date_label)
        custom_date_layout.addWidget(self.start_date_edit)
        end_date_label = QLabel("结束日期:")
        StyleHelper.apply_label_style(end_date_label)
        custom_date_layout.addWidget(end_date_label)
        custom_date_layout.addWidget(self.end_date_edit)
        custom_date_layout.addLayout(quick_layout)
        self.custom_date_widget.setLayout(custom_date_layout)
        self.custom_date_widget.hide()
        
        view_type_label = QLabel("视图类型:")
        StyleHelper.apply_label_style(view_type_label)
        view_control_layout.addWidget(view_type_label)
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
        StyleHelper.apply_checkbox_style(self.show_chinese_check)
        self.show_chinese_check.toggled.connect(self.toggle_chinese_amount)
        
        self.category_level_combo = QComboBox()
        self.category_level_combo.addItems(["按主类别统计", "按子类别统计"])
        self.category_level_combo.currentTextChanged.connect(self.on_category_level_changed)
        
        options_layout.addWidget(self.show_chinese_check)
        category_stats_label = QLabel("类别统计:")
        StyleHelper.apply_label_style(category_stats_label)
        options_layout.addWidget(category_stats_label)
        options_layout.addWidget(self.category_level_combo)
        options_layout.addStretch()
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 统计结果区域
        stats_content = QWidget()
        stats_layout = QVBoxLayout()
        
        # 收支汇总卡片（居中分布）
        summary_cards_layout = QHBoxLayout()
        summary_cards_layout.setSpacing(15)
        summary_cards_layout.setContentsMargins(10, 5, 10, 5)

        # 使用左右及中间拉伸项使卡片在行内居中且均匀分布
        summary_cards_layout.addStretch()

        # 总收入卡片
        income_card = self.create_summary_card("总收入", "#4CAF50", "#E8F5E8")
        self.income_card_amount = income_card.findChild(QLabel, "card_amount")
        self.income_card_chinese = income_card.findChild(QLabel, "card_chinese")
        summary_cards_layout.addWidget(income_card)
        summary_cards_layout.addStretch()

        # 总支出卡片
        expense_card = self.create_summary_card("总支出", "#F44336", "#FFEBEE")
        self.expense_card_amount = expense_card.findChild(QLabel, "card_amount")
        self.expense_card_chinese = expense_card.findChild(QLabel, "card_chinese")
        summary_cards_layout.addWidget(expense_card)
        summary_cards_layout.addStretch()

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
                background-color: transparent;
                border-radius: 3px;
            }
        """)
        calculation_note.setWordWrap(True)
        stats_layout.addWidget(calculation_note)
        
        # 视图专属统计内容区域
        self.view_specific_widget = QWidget()
        self.view_specific_layout = QVBoxLayout(self.view_specific_widget)
        
        # 默认的收支结构和账户分布图表（月视图、年视图、自定义时间使用）
        self.default_charts_layout = QHBoxLayout()
        
        # 收入结构饼图
        self.income_structure_group = QGroupBox("收入结构")
        self.income_figure = Figure(figsize=(4, 3))
        self.income_canvas = FigureCanvas(self.income_figure)
        income_structure_layout = QVBoxLayout()
        income_structure_layout.addWidget(self.income_canvas)
        self.income_structure_group.setLayout(income_structure_layout)
        
        # 支出结构饼图
        self.expense_structure_group = QGroupBox("支出结构")
        self.expense_figure = Figure(figsize=(4, 3))
        self.expense_canvas = FigureCanvas(self.expense_figure)
        expense_structure_layout = QVBoxLayout()
        expense_structure_layout.addWidget(self.expense_canvas)
        self.expense_structure_group.setLayout(expense_structure_layout)
        
        # 账户分布饼图
        self.account_distribution_group = QGroupBox("账户分布")
        self.account_figure = Figure(figsize=(4, 3))
        self.account_canvas = FigureCanvas(self.account_figure)
        account_distribution_layout = QVBoxLayout()
        account_distribution_layout.addWidget(self.account_canvas)
        self.account_distribution_group.setLayout(account_distribution_layout)
        
        self.default_charts_layout.addWidget(self.income_structure_group)
        self.default_charts_layout.addWidget(self.expense_structure_group)
        self.default_charts_layout.addWidget(self.account_distribution_group)
        
        # 日视图专属内容
        self.day_view_widget = QWidget()
        day_view_layout = QVBoxLayout(self.day_view_widget)
        
        # 日视图排序选项
        day_sort_layout = QHBoxLayout()
        day_sort_label = QLabel("排序方式:")
        StyleHelper.apply_label_style(day_sort_label)
        self.day_sort_combo = QComboBox()
        self.day_sort_combo.addItems(["按时间排序", "按金额排序"])
        self.day_sort_combo.currentTextChanged.connect(self.update_day_view)
        day_sort_layout.addWidget(day_sort_label)
        day_sort_layout.addWidget(self.day_sort_combo)
        day_sort_layout.addStretch()
        day_view_layout.addLayout(day_sort_layout)
        
        # 当日详细记录表格
        self.day_table_widget = QWidget()
        day_table_layout = QVBoxLayout(self.day_table_widget)
        
        day_table_label = QLabel("当日记账记录明细")
        day_table_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        day_table_layout.addWidget(day_table_label)
        
        # 创建日视图表格
        self.day_transaction_table = QTableWidget()
        self.day_transaction_table.setColumnCount(6)
        self.day_transaction_table.setHorizontalHeaderLabels(["时间", "类别", "子类别", "金额", "账户", "备注"])
        self.day_transaction_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.day_transaction_table.setSortingEnabled(True)
        day_table_layout.addWidget(self.day_transaction_table)
        
        # 收支峰值时段标签
        self.peak_time_label = QLabel("")
        self.peak_time_label.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                border: 1px solid #2196F3;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
                color: #1976D2;
            }
        """)
        day_table_layout.addWidget(self.peak_time_label)
        
        day_view_layout.addWidget(self.day_table_widget)
        
        # 周视图专属内容
        self.week_view_widget = QWidget()
        week_view_layout = QVBoxLayout(self.week_view_widget)
        
        # 周视图折线图
        week_chart_label = QLabel("本周每日收支趋势")
        week_chart_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        week_view_layout.addWidget(week_chart_label)
        
        self.week_figure = Figure(figsize=(10, 6))
        self.week_canvas = FigureCanvas(self.week_figure)
        week_view_layout.addWidget(self.week_canvas)
        
        # 单日明细查看按钮区域
        week_detail_layout = QHBoxLayout()
        week_detail_label = QLabel("查看单日明细:")
        StyleHelper.apply_label_style(week_detail_label)
        week_detail_layout.addWidget(week_detail_label)
        
        self.week_day_combo = QComboBox()
        self.week_day_combo.currentTextChanged.connect(self.show_week_day_detail)
        week_detail_layout.addWidget(self.week_day_combo)
        
        week_detail_layout.addStretch()
        week_view_layout.addLayout(week_detail_layout)
        
        # 初始时显示默认图表
        self.default_charts_widget = QWidget()
        self.default_charts_widget.setLayout(self.default_charts_layout)
        self.view_specific_layout.addWidget(self.default_charts_widget)
        stats_layout.addWidget(self.view_specific_widget)
        
        # 核心字段关联统计
        core_stats_layout = QHBoxLayout()
        
        # 销账状态分布
        settlement_group = QGroupBox("销账状态分布")
        settlement_form_layout = QFormLayout()
        self.settled_amount_label = QLabel("¥0.00")
        StyleHelper.apply_label_style(self.settled_amount_label)
        self.unsettled_amount_label = QLabel("¥0.00")
        StyleHelper.apply_label_style(self.unsettled_amount_label)
        self.settled_ratio_label = QLabel("0%")
        StyleHelper.apply_label_style(self.settled_ratio_label)
        
        settled_amount_label = QLabel("已销账金额:")
        StyleHelper.apply_label_style(settled_amount_label)
        settlement_form_layout.addRow(settled_amount_label, self.settled_amount_label)
        
        unsettled_amount_label = QLabel("未销账金额:")
        StyleHelper.apply_label_style(unsettled_amount_label)
        settlement_form_layout.addRow(unsettled_amount_label, self.unsettled_amount_label)
        
        settled_ratio_label = QLabel("销账比例:")
        StyleHelper.apply_label_style(settled_ratio_label)
        settlement_form_layout.addRow(settled_ratio_label, self.settled_ratio_label)
        
        settlement_group.setLayout(settlement_form_layout)
        
        # 退款统计
        refund_group = QGroupBox("退款统计")
        refund_form_layout = QFormLayout()
        self.refund_amount_label = QLabel("¥0.00")
        StyleHelper.apply_label_style(self.refund_amount_label)
        self.refund_count_label = QLabel("0")
        StyleHelper.apply_label_style(self.refund_count_label)
        self.refund_ratio_label = QLabel("0%")
        StyleHelper.apply_label_style(self.refund_ratio_label)
        
        refund_total_label = QLabel("退款总额:")
        StyleHelper.apply_label_style(refund_total_label)
        refund_form_layout.addRow(refund_total_label, self.refund_amount_label)
        
        refund_count_text_label = QLabel("退款笔数:")
        StyleHelper.apply_label_style(refund_count_text_label)
        refund_form_layout.addRow(refund_count_text_label, self.refund_count_label)
        
        refund_ratio_text_label = QLabel("退款占比:")
        StyleHelper.apply_label_style(refund_ratio_text_label)
        refund_form_layout.addRow(refund_ratio_text_label, self.refund_ratio_label)
        
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
        
        # 切换视图专属内容
        self.switch_view_content()
        
        self.update_date_display()
        self.update_statistics()
    
    def switch_view_content(self):
        """切换视图专属内容"""
        # 清除当前视图内容
        for i in reversed(range(self.view_specific_layout.count())):
            child = self.view_specific_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 根据视图类型添加对应内容
        if self.current_view == "day":
            # 日视图：饼图 + 专属内容
            self.view_specific_layout.addWidget(self.default_charts_widget)
            self.view_specific_layout.addWidget(self.day_view_widget)
        elif self.current_view == "week":
            # 周视图：饼图 + 专属内容
            self.view_specific_layout.addWidget(self.default_charts_widget)
            self.view_specific_layout.addWidget(self.week_view_widget)
        else:  # month, year, custom
            # 其他视图：只显示饼图
            self.view_specific_layout.addWidget(self.default_charts_widget)
    
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
                padding: 12px;
                font-weight: bold;
            }}
        """)
        card.setFixedWidth(240)
        card.setFixedHeight(120)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(title)
        StyleHelper.apply_card_title_style(title_label, color)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 金额
        amount_label = QLabel("¥0.00")
        amount_label.setObjectName("card_amount")
        StyleHelper.apply_card_amount_style(amount_label, color)
        amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        amount_label.setWordWrap(True)
        amount_label.setMinimumHeight(35)
        layout.addWidget(amount_label)
        
        # 中文大写
        chinese_label = QLabel("")
        chinese_label.setObjectName("card_chinese")
        StyleHelper.apply_card_chinese_style(chinese_label, color)
        chinese_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chinese_label.setWordWrap(True)
        chinese_label.setMinimumHeight(20)
        layout.addWidget(chinese_label)
        
        card.setLayout(layout)
        return card
    
    def create_pie_chart(self, figure, data, labels, title, colors=None):
        """创建圆环图"""
        ChartUtils.create_pie_chart(figure, data, labels, title, colors)
    
    def update_statistics(self):
        """更新统计数据"""
        start_date, end_date = self.get_date_range()
        
        # 禁用UI更新以提高性能
        self.setUpdatesEnabled(False)
        
        try:
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
            
            # 批量获取统计数据以减少数据库连接
            income_stats = self.db_manager.get_category_statistics(start_date, end_date, "收入", self.category_level)
            expense_stats = self.db_manager.get_category_statistics(start_date, end_date, "支出", self.category_level)
            account_stats = self.db_manager.get_account_statistics(start_date, end_date)
            settlement_stats = self.db_manager.get_settlement_statistics(start_date, end_date)
            refund_stats = self.db_manager.get_refund_statistics(start_date, end_date)
            
            # 更新收入结构饼图
            if income_stats and summary['total_income'] > 0:
                income_labels = [item[0] for item in income_stats]
                income_data = [item[1] for item in income_stats]
                # 使用工具方法限制显示数量
                income_labels, income_data = ChartUtils.limit_data_display(income_labels, income_data, 8)
                self.create_pie_chart(self.income_figure, income_data, income_labels, "收入结构")
            else:
                self.create_pie_chart(self.income_figure, [], [], "收入结构")
            
            # 更新支出结构饼图
            if expense_stats and summary['total_expense'] > 0:
                expense_labels = [item[0] for item in expense_stats]
                expense_data = [item[1] for item in expense_stats]
                # 使用工具方法限制显示数量
                expense_labels, expense_data = ChartUtils.limit_data_display(expense_labels, expense_data, 8)
                self.create_pie_chart(self.expense_figure, expense_data, expense_labels, "支出结构")
            else:
                self.create_pie_chart(self.expense_figure, [], [], "支出结构")
            
            # 更新账户分布饼图
            if account_stats:
                account_labels = [item[0] for item in account_stats]
                account_data = [item[1] + item[2] for item in account_stats]  # 收入+支出
                # 使用工具方法限制显示数量
                account_labels, account_data = ChartUtils.limit_data_display(account_labels, account_data, 6)
                self.create_pie_chart(self.account_figure, account_data, account_labels, "账户分布")
            else:
                self.create_pie_chart(self.account_figure, [], [], "账户分布")
            
            # 使用工具方法安全刷新画布
            ChartUtils.safe_draw_canvas(self.income_canvas)
            ChartUtils.safe_draw_canvas(self.expense_canvas)
            ChartUtils.safe_draw_canvas(self.account_canvas)
            
            # 更新销账状态统计
            self.settled_amount_label.setText(f"¥{settlement_stats['settled_amount']:.2f}")
            self.unsettled_amount_label.setText(f"¥{settlement_stats['unsettled_amount']:.2f}")
            
            if settlement_stats['total_amount'] > 0:
                settled_ratio = (settlement_stats['settled_amount'] / settlement_stats['total_amount'] * 100)
                self.settled_ratio_label.setText(f"{settled_ratio:.1f}%")
            else:
                self.settled_ratio_label.setText("0%")
            
            # 更新退款统计
            self.refund_amount_label.setText(f"¥{refund_stats['total_refund']:.2f}")
            self.refund_count_label.setText(str(refund_stats['refund_count']))
            self.refund_ratio_label.setText(f"{refund_stats['refund_ratio']:.1f}%")
        
        finally:
            # 重新启用UI更新
            self.setUpdatesEnabled(True)
            self.update()
        
        # 更新视图专属内容
        self.update_view_specific_content()
    
    def update_view_specific_content(self):
        """更新视图专属的统计内容"""
        if self.current_view == "day":
            self.update_day_view()
        elif self.current_view == "week":
            self.update_week_view()
    
    def update_day_view(self):
        """更新日视图内容"""
        current_date_str = self.current_date.toString("yyyy-MM-dd")
        transactions = self.db_manager.get_day_transactions(current_date_str)
        
        # 更新表格数据
        self.day_transaction_table.setRowCount(len(transactions))
        
        sort_by_time = self.day_sort_combo.currentText() == "按时间排序"
        
        # 根据排序方式重新组织数据
        if not sort_by_time:
            # 按金额排序
            transactions_sorted = sorted(transactions, key=lambda x: abs(x[4]), reverse=True)
        else:
            transactions_sorted = transactions
        
        for row, trans in enumerate(transactions_sorted):
            (created_time, transaction_type, category, subcategory, amount, account, description) = trans
            # 只显示时间部分
            time_only = created_time.split(" ")[1][:5] if " " in created_time else created_time
            self.day_transaction_table.setItem(row, 0, QTableWidgetItem(time_only))
            self.day_transaction_table.setItem(row, 1, QTableWidgetItem(category))
            self.day_transaction_table.setItem(row, 2, QTableWidgetItem(subcategory))
            self.day_transaction_table.setItem(row, 3, QTableWidgetItem(f"¥{abs(amount):.2f}"))
            self.day_transaction_table.setItem(row, 4, QTableWidgetItem(account or ""))
            self.day_transaction_table.setItem(row, 5, QTableWidgetItem(description or ""))
        
        # 获取消费峰值时段
        peak_result = self.db_manager.get_peak_consumption_hours(current_date_str)
        if peak_result:
            time_period, total_amount, count = peak_result
            self.peak_time_label.setText(f"🔥 消费峰值时段：{time_period} 消费 ¥{total_amount:.2f}（{count}笔）")
        else:
            self.peak_time_label.setText("📊 当日暂无消费记录")
    
    def update_week_view(self):
        """更新周视图内容"""
        start_date, end_date = self.get_date_range()
        week_trends = self.db_manager.get_week_trends(start_date, end_date)
        
        if not week_trends:
            # 显示空图表
            self.week_figure.clear()
            ax = self.week_figure.add_subplot(111)
            ax.text(0.5, 0.5, '本周暂无数据', ha='center', va='center', fontsize=12)
            ax.set_title("本周每日收支趋势")
            ChartUtils.safe_draw_canvas(self.week_canvas)
            return
        
        # 准备数据
        dates = [item[0][5:] for item in week_trends]  # 只取MM-DD部分
        incomes = [item[1] for item in week_trends]
        expenses = [item[2] for item in week_trends]
        net_incomes = [income - expense for income, expense in zip(incomes, expenses)]
        
        # 创建折线图
        self.week_figure.clear()
        ax = self.week_figure.add_subplot(111)
        
        # 绘制收入和支出折线
        ax.plot(dates, incomes, marker='o', label='收入', color='#4CAF50', linewidth=2)
        ax.plot(dates, expenses, marker='s', label='支出', color='#F44336', linewidth=2)
        ax.plot(dates, net_incomes, marker='^', label='净收支', color='#2196F3', linewidth=2, linestyle='--')
        
        # 设置图表样式
        ax.set_title('本周每日收支趋势', fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('金额 (¥)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 格式化Y轴显示
        from matplotlib.ticker import FuncFormatter
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'¥{x:.0f}'))
        
        # 旋转X轴标签
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 调整布局
        self.week_figure.tight_layout()
        
        ChartUtils.safe_draw_canvas(self.week_canvas)
        
        # 更新日期选择下拉框
        self.week_day_combo.clear()
        for item in week_trends:
            date_str = item[0]
            display_text = f"{date_str[5:]} (收入: ¥{item[1]:.2f}, 支出: ¥{item[2]:.2f})"
            self.week_day_combo.addItem(display_text, date_str)
    
    def show_week_day_detail(self, display_text):
        """显示周视图中单日的详细记录"""
        selected_date = self.week_day_combo.currentData()
        if not selected_date:
            return
        
        # 获取选中日期的详细交易记录
        transactions = self.db_manager.get_day_transactions(selected_date)
        
        if not transactions:
            MessageHelper.show_info(self, "提示", f"{selected_date} 暂无交易记录")
            return
        
        # 创建详情对话框
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{selected_date} 详细记录")
        dialog.setModal(True)
        dialog.resize(800, 400)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(f"{selected_date} 交易记录明细")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 表格
        detail_table = QTableWidget()
        detail_table.setColumnCount(7)
        detail_table.setHorizontalHeaderLabels(["时间", "类型", "类别", "子类别", "金额", "账户", "备注"])
        detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        detail_table.setRowCount(len(transactions))
        for row, trans in enumerate(transactions):
            (created_time, transaction_type, category, subcategory, amount, account, description) = trans
            time_only = created_time.split(" ")[1] if " " in created_time else created_time
            detail_table.setItem(row, 0, QTableWidgetItem(time_only))
            detail_table.setItem(row, 1, QTableWidgetItem(transaction_type))
            detail_table.setItem(row, 2, QTableWidgetItem(category))
            detail_table.setItem(row, 3, QTableWidgetItem(subcategory))
            detail_table.setItem(row, 4, QTableWidgetItem(f"¥{abs(amount):.2f}"))
            detail_table.setItem(row, 5, QTableWidgetItem(account or ""))
            detail_table.setItem(row, 6, QTableWidgetItem(description or ""))
        
        layout.addWidget(detail_table)
        
        # 关闭按钮
        from PyQt6.QtWidgets import QPushButton
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.current_ledger_id = None
        self.ledgers = {}
        self.setup_ui()
        self.load_ledgers()
        self.apply_theme()
        
        # 尝试自动打开上次账本
        self.auto_open_last_ledger()
    
    def auto_open_last_ledger(self):
        """自动打开上次使用的账本"""
        from PyQt6.QtCore import QSettings
        settings = QSettings()
        
        auto_open = settings.value("auto_open_last_ledger", False, type=bool)
        if auto_open:
            last_ledger_id = settings.value("last_ledger_id", None, type=int)
            if last_ledger_id and last_ledger_id in self.ledgers:
                ledger_info = self.ledgers[last_ledger_id]
                self.current_ledger_label.setText(f"当前账本: {ledger_info['name']} ({ledger_info['type']})")
                self.current_ledger_id = last_ledger_id
                self.initialize_search_controls()
                self.load_transactions()
    
    def save_current_ledger(self):
        """保存当前账本信息"""
        if self.current_ledger_id and self.current_ledger_id in self.ledgers:
            from PyQt6.QtCore import QSettings
            settings = QSettings()
            
            ledger_info = self.ledgers[self.current_ledger_id]
            settings.setValue("last_ledger_id", self.current_ledger_id)
            settings.setValue("last_ledger_info", f"{ledger_info['name']} ({ledger_info['type']})")
    
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
        text = button.text()
        if "收入" in text:
            StyleHelper.apply_button_style(button, "income")
        elif "支出" in text:
            StyleHelper.apply_button_style(button, "expense")
        elif "删除" in text:
            StyleHelper.apply_button_style(button, "danger")
        else:
            StyleHelper.apply_button_style(button, "default")
    
    def update_table_theme(self, table):
        """更新表格主题"""
        StyleHelper.apply_table_style(table)
    
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
    
    def on_settings_changed(self):
        """设置变更后的处理"""
        # 可以在这里添加设置变更后的处理逻辑
        pass
    
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
        keyword_label = QLabel("关键词搜索:")
        StyleHelper.apply_label_style(keyword_label)
        basic_search_layout.addWidget(keyword_label)
        
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
        account_label = QLabel("账户:")
        StyleHelper.apply_label_style(account_label)
        basic_filter_layout.addWidget(account_label)
        self.account_search_combo = QComboBox()
        self.account_search_combo.setMinimumWidth(120)  # 设置组合框最小宽度
        self.account_search_combo.addItem("")
        basic_filter_layout.addWidget(self.account_search_combo)
        
        # 交易类型
        type_label = QLabel("类型:")
        StyleHelper.apply_label_style(type_label)
        basic_filter_layout.addWidget(type_label)
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.setMinimumWidth(80)  # 设置组合框最小宽度
        self.transaction_type_combo.addItems(["", "收入", "支出"])
        basic_filter_layout.addWidget(self.transaction_type_combo)
        
        # 分类筛选
        category_label = QLabel("分类:")
        StyleHelper.apply_label_style(category_label)
        basic_filter_layout.addWidget(category_label)
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
        settled_label = QLabel("销账:")
        StyleHelper.apply_label_style(settled_label)
        status_layout.addWidget(settled_label)
        self.settled_combo = QComboBox()
        self.settled_combo.setMinimumWidth(80)  # 设置组合框最小宽度
        self.settled_combo.addItems(["", "已销账", "未销账"])
        status_layout.addWidget(self.settled_combo)
        
        refund_label = QLabel("退款:")
        StyleHelper.apply_label_style(refund_label)
        status_layout.addWidget(refund_label)
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
        
        amount_to_label = QLabel("至")
        StyleHelper.apply_label_style(amount_to_label)
        amount_layout.addWidget(amount_to_label)
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
        
        to_label = QLabel("至")
        StyleHelper.apply_label_style(to_label)
        date_layout.addWidget(to_label)
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
            
            # 保存当前账本信息
            self.save_current_ledger()
    
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
            MessageHelper.show_warning(self, "警告", "请先选择账本！")
            return
        
        # 收集搜索条件
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
        
        # 检查是否有任何搜索条件
        has_search_conditions = any([
            keyword, category, subcategory, account, transaction_type,
            settled_status, refund_status, min_amount > 0, max_amount < 999999.99
        ])
        
        if not has_search_conditions:
            self.load_transactions()
            return
        
        # 构建SQL查询以提高性能
        conditions = []
        params = []
        
        conditions.append("ledger_id = ?")
        params.append(self.current_ledger_id)
        
        if keyword:
            conditions.append("(LOWER(description) LIKE ? OR LOWER(category) LIKE ? OR LOWER(subcategory) LIKE ? OR LOWER(account) LIKE ? OR LOWER(refund_reason) LIKE ?)")
            keyword_param = f"%{keyword}%"
            params.extend([keyword_param, keyword_param, keyword_param, keyword_param, keyword_param])
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if subcategory:
            conditions.append("subcategory = ?")
            params.append(subcategory)
        
        if account:
            conditions.append("account = ?")
            params.append(account)
        
        if transaction_type:
            conditions.append("transaction_type = ?")
            params.append(transaction_type)
        
        if settled_status:
            is_settled = settled_status == "已销账"
            conditions.append("is_settled = ?")
            params.append(is_settled)
        
        if refund_status:
            if refund_status == "有退款":
                conditions.append("refund_amount > 0")
            else:
                conditions.append("refund_amount = 0")
        
        if min_amount > 0:
            conditions.append("ABS(amount) >= ?")
            params.append(min_amount)
        
        if max_amount < 999999.99:
            conditions.append("ABS(amount) <= ?")
            params.append(max_amount)
        
        # 时间范围
        conditions.append("transaction_date BETWEEN ? AND ?")
        params.extend([start_date, end_date])
        
        # 执行查询
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT * FROM transactions 
                WHERE {' AND '.join(conditions)}
                ORDER BY transaction_date DESC, created_time DESC
            """
            cursor.execute(query, params)
            filtered_transactions = cursor.fetchall()
        
        # 显示筛选结果
        self.load_transactions(filtered_transactions)
        
        # 显示搜索结果数量
        result_count = len(filtered_transactions)
        total_count = len(self.db_manager.get_transactions(self.current_ledger_id))
        MessageHelper.show_info(self, "搜索结果", f"找到 {result_count} 条记录，共 {total_count} 条记录")
    
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
                MessageHelper.show_info(self, "成功", "账本添加成功！")
    
    def delete_ledger(self):
        current_item = self.ledger_list.currentItem()
        if not current_item:
            MessageHelper.show_warning(self, "警告", "请先选择要删除的账本！")
            return
        
        ledger_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        ledger_name = self.ledgers[ledger_id]['name']
        
        if not MessageHelper.ask_confirmation(self, "确认删除", 
                                   f"确定要删除账本 '{ledger_name}' 吗？\n删除后将同时删除该账本下的所有交易记录！"):
            self.db_manager.delete_ledger(ledger_id)
            self.load_ledgers()
            if self.current_ledger_id == ledger_id:
                self.current_ledger_id = None
                self.current_ledger_label.setText("请选择账本")
                self.transaction_table.setRowCount(0)
            MessageHelper.show_info(self, "成功", "账本删除成功！")
    
    def add_income(self):
        if not self.current_ledger_id:
            MessageHelper.show_warning(self, "警告", "请先选择账本！")
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
                        MessageHelper.show_info(self, "成功", "收入记录添加成功！")
                        # 刷新资产管理页面的账户信息
                        if hasattr(self, 'asset_widget'):
                            self.asset_widget.load_accounts()
                        break
                else:
                    MessageHelper.show_warning(self, "警告", "请填写必要的收入信息！")
                    break
            else:
                break
    
    def add_expense(self):
        if not self.current_ledger_id:
            MessageHelper.show_warning(self, "警告", "请先选择账本！")
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
                        MessageHelper.show_info(self, "成功", "支出记录添加成功！")
                        # 刷新资产管理页面的账户信息
                        if hasattr(self, 'asset_widget'):
                            self.asset_widget.load_accounts()
                        break
                else:
                    MessageHelper.show_warning(self, "警告", "请填写必要的支出信息！")
                    break
            else:
                break
    
    def edit_transaction(self):
        if not self.current_ledger_id:
            MessageHelper.show_warning(self, "警告", "请先选择账本！")
            return
        
        current_row = self.transaction_table.currentRow()
        if current_row < 0:
            MessageHelper.show_warning(self, "警告", "请先选择要编辑的交易记录！")
            return
        
        # 获取选中的交易记录数据
        transactions = self.db_manager.get_transactions(self.current_ledger_id)
        if current_row >= len(transactions):
            MessageHelper.show_warning(self, "警告", "找不到选中的交易记录！")
            return
        
        transaction_data = transactions[current_row]
        transaction_type = transaction_data[3]
        
        if transaction_type == "收入":
            dialog = EditIncomeDialog(self.db_manager, transaction_data, self)
        elif transaction_type == "支出":
            dialog = EditExpenseDialog(self.db_manager, transaction_data, self)
        else:
            MessageHelper.show_warning(self, "警告", "未知的交易类型！")
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
                
                MessageHelper.show_info(self, "成功", "交易记录修改成功！")
                # 刷新相关页面
                if hasattr(self, 'asset_widget'):
                    self.asset_widget.load_accounts()
                if hasattr(self, 'statistics_widget'):
                    self.statistics_widget.update_statistics()
    
    def delete_transaction(self):
        if not self.current_ledger_id:
            MessageHelper.show_warning(self, "警告", "请先选择账本！")
            return
        
        current_row = self.transaction_table.currentRow()
        if current_row < 0:
            MessageHelper.show_warning(self, "警告", "请先选择要删除的交易记录！")
            return
        
        # 获取选中的交易记录数据
        transactions = self.db_manager.get_transactions(self.current_ledger_id)
        if current_row >= len(transactions):
            MessageHelper.show_warning(self, "警告", "找不到选中的交易记录！")
            return
        
        transaction_data = transactions[current_row]
        transaction_date = transaction_data[2]
        transaction_type = transaction_data[3]
        category = transaction_data[4]
        subcategory = transaction_data[5]
        amount = transaction_data[6]
        account = transaction_data[7]
        
        if not MessageHelper.ask_confirmation(self, "确认删除", 
                                   f"确定要删除这条交易记录吗？\n"
                                   f"日期: {transaction_date}\n"
                                   f"类型: {transaction_type}\n"
                                   f"类别: {category} - {subcategory}\n"
                                   f"金额: ¥{abs(amount):.2f}\n"
                                   f"删除后将无法恢复！"):
            self.db_manager.delete_transaction(transaction_data[0])
            self.load_transactions()
            
            # 更新账户余额（删除记录需要反向操作）
            if account:
                self.db_manager.update_account_balance(account, -amount)
            
            MessageHelper.show_info(self, "成功", "交易记录删除成功！")
            # 刷新相关页面
            if hasattr(self, 'asset_widget'):
                self.asset_widget.load_accounts()
            if hasattr(self, 'statistics_widget'):
                self.statistics_widget.update_statistics()