"""
对话框模块 - 重构后的对话框类，使用基类减少重复代码
"""
from ui_base_components import BaseTransactionDialog, BaseEditDialog
from theme_manager import theme_manager
from PyQt6.QtWidgets import QVBoxLayout

class AddIncomeDialog(BaseTransactionDialog):
    """添加收入对话框"""
    
    def __init__(self, db_manager, ledger_id, parent=None):
        super().__init__(db_manager, parent)
        self.ledger_id = ledger_id
        self.transaction_type = "收入"
        self.setup_ui()
        self.load_categories("收入")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息
        layout.addWidget(self.create_basic_info_group())
        
        # 类别选择
        layout.addWidget(self.create_category_group("收入类别选择"))
        
        # 其他信息
        layout.addWidget(self.create_other_info_group(include_settlement=False, include_refund=False))
        
        # 按钮
        layout.addLayout(self.create_button_layout(include_add_more=True))
        
        self.setLayout(layout)
        self.setWindowTitle("添加收入记录")
        self.setModal(True)
    
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


class EditIncomeDialog(BaseEditDialog):
    """编辑收入对话框"""
    
    def __init__(self, db_manager, transaction_data, parent=None):
        super().__init__(db_manager, transaction_data, parent)
        self.transaction_type = "收入"
        self.setup_ui()
        self.load_categories("收入")
        self.load_transaction_data("收入")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息
        layout.addWidget(self.create_basic_info_group())
        
        # 类别选择
        layout.addWidget(self.create_category_group("收入类别选择"))
        
        # 其他信息
        layout.addWidget(self.create_other_info_group(include_settlement=False, include_refund=False))
        
        # 按钮
        layout.addLayout(self.create_button_layout())
        
        self.setLayout(layout)
        self.setWindowTitle("编辑收入记录")
        self.setModal(True)
    
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


class AddExpenseDialog(BaseTransactionDialog):
    """添加支出对话框"""
    
    def __init__(self, db_manager, ledger_id, parent=None):
        super().__init__(db_manager, parent)
        self.ledger_id = ledger_id
        self.transaction_type = "支出"
        self.setup_ui()
        self.load_categories("支出")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息
        layout.addWidget(self.create_basic_info_group())
        
        # 类别选择
        layout.addWidget(self.create_category_group("支出类别选择"))
        
        # 其他信息
        layout.addWidget(self.create_other_info_group(include_settlement=True, include_refund=True))
        
        # 按钮
        layout.addLayout(self.create_button_layout(include_add_more=True))
        
        self.setLayout(layout)
        self.setWindowTitle("添加支出记录")
        self.setModal(True)
    
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


class EditExpenseDialog(BaseEditDialog):
    """编辑支出对话框"""
    
    def __init__(self, db_manager, transaction_data, parent=None):
        super().__init__(db_manager, transaction_data, parent)
        self.transaction_type = "支出"
        self.setup_ui()
        self.load_categories("支出")
        self.load_transaction_data("支出")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息
        layout.addWidget(self.create_basic_info_group())
        
        # 类别选择
        layout.addWidget(self.create_category_group("支出类别选择"))
        
        # 其他信息
        layout.addWidget(self.create_other_info_group(include_settlement=True, include_refund=True))
        
        # 按钮
        layout.addLayout(self.create_button_layout())
        
        self.setLayout(layout)
        self.setWindowTitle("编辑支出记录")
        self.setModal(True)
    
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