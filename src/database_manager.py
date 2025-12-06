import sqlite3
import threading
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path="bookkeeping.db"):
        self.db_path = db_path
        self._local = threading.local()
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器，支持线程安全"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
        try:
            yield self._local.connection
        except Exception:
            self._local.connection.rollback()
            raise
    
    def close_connection(self):
        """关闭当前线程的数据库连接"""
        if hasattr(self._local, 'connection'):
            try:
                self._local.connection.close()
            except:
                pass  # 忽略关闭时的错误
            finally:
                delattr(self._local, 'connection')
    
    def cleanup_all_connections(self):
        """清理所有线程的数据库连接"""
        # 注意：threading.local无法直接清理所有线程的连接
        # 这个方法主要用于应用退出时的资源清理
        if hasattr(self._local, 'connection'):
            self.close_connection()
    
    def __del__(self):
        """析构函数，确保连接被清理"""
        try:
            self.cleanup_all_connections()
        except:
            pass  # 忽略析构时的错误
    
    def init_database(self):
        with self.get_connection() as conn:
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
            
            # 创建索引以提高查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_ledger ON transactions(ledger_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transfers_date ON transfers(transfer_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_accounts_name ON accounts(name)')
            
            # 插入默认类别数据
            self.insert_default_categories()
            conn.commit()
    
    def insert_default_categories(self):
        with self.get_connection() as conn:
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
            
            # 批量插入，提高性能
            all_data = []
            for parent, subs in expense_categories:
                for sub in subs:
                    all_data.append((parent, sub, "支出"))
            
            for parent, subs in income_categories:
                for sub in subs:
                    all_data.append((parent, sub, "收入"))
            
            cursor.executemany('''
                INSERT OR IGNORE INTO categories (parent_category, sub_category, type)
                VALUES (?, ?, ?)
            ''', all_data)
            
            conn.commit()
    
    def add_ledger(self, name, ledger_type, description):
        with self.get_connection() as conn:
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
            
            cursor.executemany('''
                INSERT INTO accounts (name, type, balance, bank, description)
                VALUES (?, ?, ?, ?, ?)
            ''', default_accounts)
            
            conn.commit()
    
    def get_ledgers(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ledgers ORDER BY created_time')
            ledgers = cursor.fetchall()
            return ledgers
    
    def delete_ledger(self, ledger_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE ledger_id = ?', (ledger_id,))
            cursor.execute('DELETE FROM ledgers WHERE id = ?', (ledger_id,))
            conn.commit()
    
    def get_categories(self, category_type=None):
        with self.get_connection() as conn:
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
            return categories
    
    def add_transaction(self, ledger_id, transaction_date, transaction_type, category, subcategory, 
                       amount, account, description, is_settled, refund_amount, refund_reason):
        with self.get_connection() as conn:
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
    
    def get_transactions(self, ledger_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM transactions WHERE ledger_id = ? 
                ORDER BY transaction_date DESC, created_time DESC
            ''', (ledger_id,))
            transactions = cursor.fetchall()
        return transactions
    
    def add_account(self, name, account_type, balance=0.0, bank=None, description=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO accounts (name, type, balance, bank, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, account_type, balance, bank, description))
            conn.commit()
    
    def add_account_without_ledger(self, name, account_type, balance=0.0, bank=None, description=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO accounts (name, type, balance, bank, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, account_type, balance, bank, description))
            conn.commit()
    
    def update_account(self, account_id, name, account_type, balance, bank, description):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE accounts SET name = ?, type = ?, balance = ?, bank = ?, description = ?
                WHERE id = ?
            ''', (name, account_type, balance, bank, description, account_id))
            conn.commit()
    
    def delete_account(self, account_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
            conn.commit()
    
    def update_transaction(self, transaction_id, transaction_date, transaction_type, category, 
                         subcategory, amount, account, description, is_settled, refund_amount, refund_reason):
        with self.get_connection() as conn:
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
    
    def delete_transaction(self, transaction_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            conn.commit()
    
    def get_accounts(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts ORDER BY name')
            accounts = cursor.fetchall()
        return accounts
    
    def update_account_balance(self, account_name, amount_change):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE accounts SET balance = balance + ? WHERE name = ?
            ''', (amount_change, account_name))
            conn.commit()
    
    def get_account_balance(self, account_name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT balance FROM accounts WHERE name = ?', (account_name,))
            result = cursor.fetchone()
        return result[0] if result else 0.0
    
    def add_transfer(self, transfer_date, from_account, to_account, amount, description):
        with self.get_connection() as conn:
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
    
    def get_transfers(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM transfers ORDER BY transfer_date DESC, created_time DESC
            ''')
            transfers = cursor.fetchall()
        return transfers
    
    def update_transfer(self, transfer_id, transfer_date, from_account, to_account, amount, description):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE transfers SET 
                    transfer_date = ?, from_account = ?, to_account = ?, 
                    amount = ?, description = ?
                WHERE id = ?
            ''', (transfer_date, from_account, to_account, amount, description, transfer_id))
            conn.commit()
    
    def delete_transfer(self, transfer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transfers WHERE id = ?', (transfer_id,))
            conn.commit()
    
    def get_transactions_by_date_range(self, start_date, end_date, ledger_id=None):
        """获取指定日期范围内的交易记录"""
        with self.get_connection() as conn:
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
        return transactions
    
    def get_statistics_summary(self, start_date, end_date, ledger_id=None):
        """获取收支汇总统计"""
        with self.get_connection() as conn:
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
        with self.get_connection() as conn:
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
        return results
    
    def get_account_statistics(self, start_date, end_date, ledger_id=None):
        """获取账户统计"""
        with self.get_connection() as conn:
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
        return results
    
    def get_settlement_statistics(self, start_date, end_date, ledger_id=None):
        """获取销账状态统计"""
        with self.get_connection() as conn:
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
    
    def get_day_transactions(self, date, ledger_id=None):
        """获取指定日期的所有交易记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if ledger_id:
                cursor.execute('''
                    SELECT created_time, transaction_type, category, subcategory, amount, account, description
                    FROM transactions 
                    WHERE transaction_date = ? AND ledger_id = ?
                    ORDER BY created_time
                ''', (date, ledger_id))
            else:
                cursor.execute('''
                    SELECT created_time, transaction_type, category, subcategory, amount, account, description
                    FROM transactions 
                    WHERE transaction_date = ?
                    ORDER BY created_time
                ''', (date,))
            
            transactions = cursor.fetchall()
        return transactions
    
    def get_week_trends(self, start_date, end_date, ledger_id=None):
        """获取一周内每日收支趋势"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if ledger_id:
                cursor.execute('''
                    SELECT transaction_date,
                           SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
                           SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expense,
                           COUNT(*) as count
                    FROM transactions 
                    WHERE transaction_date BETWEEN ? AND ? AND ledger_id = ?
                    GROUP BY transaction_date
                    ORDER BY transaction_date
                ''', (start_date, end_date, ledger_id))
            else:
                cursor.execute('''
                    SELECT transaction_date,
                           SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
                           SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expense,
                           COUNT(*) as count
                    FROM transactions 
                    WHERE transaction_date BETWEEN ? AND ?
                    GROUP BY transaction_date
                    ORDER BY transaction_date
                ''', (start_date, end_date))
            
            results = cursor.fetchall()
        return results
    
    def get_peak_consumption_hours(self, date, ledger_id=None):
        """获取指定日期的消费峰值时段"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if ledger_id:
                cursor.execute('''
                    SELECT 
                        CASE 
                            WHEN CAST(substr(created_time, 12, 2) AS INTEGER) BETWEEN 6 AND 11 THEN '06:00-12:00'
                            WHEN CAST(substr(created_time, 12, 2) AS INTEGER) BETWEEN 12 AND 17 THEN '12:00-18:00'
                            WHEN CAST(substr(created_time, 12, 2) AS INTEGER) BETWEEN 18 AND 23 THEN '18:00-24:00'
                            ELSE '00:00-06:00'
                        END as time_period,
                        SUM(ABS(amount)) as total_amount,
                        COUNT(*) as count
                    FROM transactions 
                    WHERE transaction_date = ? AND ledger_id = ? AND amount < 0
                    GROUP BY time_period
                    ORDER BY total_amount DESC
                    LIMIT 1
                ''', (date, ledger_id))
            else:
                cursor.execute('''
                    SELECT 
                        CASE 
                            WHEN CAST(substr(created_time, 12, 2) AS INTEGER) BETWEEN 6 AND 11 THEN '06:00-12:00'
                            WHEN CAST(substr(created_time, 12, 2) AS INTEGER) BETWEEN 12 AND 17 THEN '12:00-18:00'
                            WHEN CAST(substr(created_time, 12, 2) AS INTEGER) BETWEEN 18 AND 23 THEN '18:00-24:00'
                            ELSE '00:00-06:00'
                        END as time_period,
                        SUM(ABS(amount)) as total_amount,
                        COUNT(*) as count
                    FROM transactions 
                    WHERE transaction_date = ? AND amount < 0
                    GROUP BY time_period
                    ORDER BY total_amount DESC
                    LIMIT 1
                ''', (date,))
            
            result = cursor.fetchone()
        return result
    
    def get_refund_statistics(self, start_date, end_date, ledger_id=None):
        """获取退款统计"""
        with self.get_connection() as conn:
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