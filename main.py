import sys
import sqlite3
from datetime import datetime, date
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QLineEdit, QComboBox, 
                            QTableWidget, QTableWidgetItem, QTabWidget, QDialog,
                            QFormLayout, QTextEdit, QDateTimeEdit, QCheckBox,
                            QDoubleSpinBox, QMessageBox, QSplitter, QGroupBox,
                            QTreeWidget, QTreeWidgetItem, QHeaderView, QSpinBox)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont, QIcon

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
        if self.category_type == "income":
            self.setStyleSheet("""
                QPushButton {
                    border: 2px solid #4CAF50;
                    border-radius: 6px;
                    padding: 6px 10px;
                    background-color: white;
                    color: #333;
                    font-size: 11px;
                    font-weight: bold;
                    min-height: 25px;
                    max-height: 25px;
                    min-width: 60px;
                    max-width: 100px;
                }
                QPushButton:hover {
                    background-color: #E8F5E8;
                    border-color: #45a049;
                }
                QPushButton:selected {
                    background-color: #4CAF50;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    border: 2px solid #FF6B6B;
                    border-radius: 6px;
                    padding: 6px 10px;
                    background-color: white;
                    color: #333;
                    font-size: 11px;
                    font-weight: bold;
                    min-height: 25px;
                    max-height: 25px;
                    min-width: 60px;
                    max-width: 100px;
                }
                QPushButton:hover {
                    background-color: #FFE0E0;
                    border-color: #FF5252;
                }
                QPushButton:selected {
                    background-color: #FF6B6B;
                    color: white;
                }
            """)
    
    def set_selected(self, selected):
        self.is_selected = selected
        if selected:
            self.setProperty("selected", True)
            self.style().unpolish(self)
            self.style().polish(self)
        else:
            self.setProperty("selected", False)
            self.style().unpolish(self)
            self.style().polish(self)

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
        from PyQt6.QtWidgets import QScrollArea
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
                btn = CategoryButton(subcategory, "normal")
                btn.clicked.connect(lambda checked, sub=subcategory: self.on_subcategory_clicked(sub))
                row_layout.addWidget(btn)
            
            row_layout.addStretch()
            row_widget.setLayout(row_layout)
            self.subcategory_grid_layout.addWidget(row_widget)
        
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
        from PyQt6.QtWidgets import QScrollArea
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
                btn = CategoryButton(subcategory, "normal")
                btn.clicked.connect(lambda checked, sub=subcategory: self.on_subcategory_clicked(sub))
                row_layout.addWidget(btn)
            
            row_layout.addStretch()
            row_widget.setLayout(row_layout)
            self.subcategory_grid_layout.addWidget(row_widget)
        
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
        self.type_combo.addItems(["现金", "银行卡", "支付宝", "微信", "其他"])
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
        account_btn_layout.addWidget(add_account_btn)
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
                QMessageBox.information(self, "成功", "账户添加成功！")
    
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
                QMessageBox.information(self, "成功", "转账记录添加成功！")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.current_ledger_id = None
        self.ledgers = {}
        self.setup_ui()
        self.load_ledgers()
        
    def setup_ui(self):
        self.setWindowTitle("多账本记账系统")
        self.setGeometry(100, 100, 1200, 800)
        
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
        transaction_btn_layout.addStretch()
        transaction_layout.addLayout(transaction_btn_layout)
        
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
            self.load_transactions()
    
    def load_transactions(self):
        if not self.current_ledger_id:
            return
        
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
            self.transaction_table.setItem(row, 4, QTableWidgetItem(f"¥{amount:.2f}"))
            self.transaction_table.setItem(row, 5, QTableWidgetItem(account or ""))
            self.transaction_table.setItem(row, 6, QTableWidgetItem(description or ""))
            self.transaction_table.setItem(row, 7, QTableWidgetItem("是" if is_settled else "否"))
            self.transaction_table.setItem(row, 8, QTableWidgetItem(f"¥{refund_amount:.2f}" if refund_amount > 0 else ""))
            self.transaction_table.setItem(row, 9, QTableWidgetItem(refund_reason or ""))
            self.transaction_table.setItem(row, 10, QTableWidgetItem(created_time))
    
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

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()