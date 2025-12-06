"""
导出导入功能模块
支持Excel和CSV格式的数据导出导入
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import subprocess
import tempfile
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                            QPushButton, QComboBox, QCheckBox, QRadioButton, 
                            QButtonGroup, QGroupBox, QProgressBar, QTextEdit,
                            QFileDialog, QMessageBox, QFormLayout, QLineEdit,
                            QSpinBox, QTabWidget, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from database_manager import DatabaseManager
from ui_base_components import BaseDialog, StyleHelper, MessageHelper, ConfigManager


class ExportWorker(QThread):
    """导出工作线程"""
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(str, bool)  # 文件路径, 是否成功
    error_occurred = pyqtSignal(str)
    
    def __init__(self, db_manager, export_config):
        super().__init__()
        self.db_manager = db_manager
        self.export_config = export_config
    
    def run(self):
        try:
            file_path = self.export_data()
            self.finished.emit(file_path, True)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def export_data(self):
        """执行导出操作"""
        # 获取导出配置
        export_type = self.export_config['export_type']  # 'all', 'filtered', 'specific'
        export_format = self.export_config['export_format']  # 'excel', 'csv'
        export_scope = self.export_config['export_scope']  # ['transactions', 'budgets', 'accounts']
        ledger_name = self.export_config.get('ledger_name', '默认账本')
        file_path = self.export_config['file_path']
        
        # 创建导出数据容器
        export_data = {}
        
        # 根据导出类型获取数据
        if export_type == 'all':
            # 导出所有账本数据
            data_generators = {
                'transactions': lambda: self.get_all_transactions(),
                'budgets': lambda: self.get_all_budgets(),
                'accounts': lambda: self.get_all_accounts()
            }
        elif export_type == 'filtered':
            # 导出筛选结果
            data_generators = {
                'transactions': lambda: self.get_filtered_transactions(self.export_config),
                'budgets': lambda: self.get_filtered_budgets(self.export_config),
                'accounts': lambda: self.get_filtered_accounts(self.export_config)
            }
        else:  # specific
            # 导出指定数据类型
            data_generators = {}
            if 'transactions' in export_scope:
                if 'start_date' in self.export_config:
                    data_generators['transactions'] = lambda: self.get_date_range_transactions(
                        self.export_config['start_date'], 
                        self.export_config['end_date']
                    )
                else:
                    data_generators['transactions'] = lambda: self.get_all_transactions()
            
            if 'budgets' in export_scope:
                data_generators['budgets'] = lambda: self.get_all_budgets()
            
            if 'accounts' in export_scope:
                data_generators['accounts'] = lambda: self.get_all_accounts()
        
        # 获取数据并转换为DataFrame
        total_steps = len(data_generators)
        current_step = 0
        
        for data_type, generator in data_generators.items():
            self.progress_updated.emit(int((current_step / total_steps) * 100))
            data = generator()
            if data:
                df = pd.DataFrame(data)
                # 清理和格式化数据
                df = self.clean_dataframe(df, data_type)
                export_data[data_type] = df
            current_step += 1
        
        self.progress_updated.emit(100)
        
        # 保存文件
        if export_format == 'excel':
            self.save_excel_file(export_data, file_path, ledger_name)
        else:
            self.save_csv_file(export_data, file_path, ledger_name)
        
        return file_path
    
    def get_all_transactions(self):
        """获取所有交易记录"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.id, l.name as ledger_name, t.transaction_date, 
                       t.transaction_type, t.category, t.subcategory, 
                       t.amount, t.account, t.description, 
                       t.is_settled, t.refund_amount, t.refund_reason, t.created_time
                FROM transactions t
                JOIN ledgers l ON t.ledger_id = l.id
                ORDER BY t.transaction_date DESC, t.created_time DESC
            ''')
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_all_budgets(self):
        """获取所有预算配置"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT b.id, l.name as ledger_name, b.category, b.budget_type,
                       b.amount, b.warning_threshold, b.start_date, b.end_date,
                       b.is_active, b.created_time, b.updated_time
                FROM budgets b
                JOIN ledgers l ON b.ledger_id = l.id
                ORDER BY l.name, b.category
            ''')
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_all_accounts(self):
        """获取所有账户信息"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, type, balance, bank, description
                FROM accounts
                ORDER BY name
            ''')
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_filtered_transactions(self, config):
        """获取筛选的交易记录"""
        start_date = config.get('start_date')
        end_date = config.get('end_date')
        ledger_id = config.get('ledger_id')
        
        return self.db_manager.get_transactions_by_date_range(start_date, end_date, ledger_id)
    
    def get_filtered_budgets(self, config):
        """获取筛选的预算配置"""
        ledger_id = config.get('ledger_id')
        if ledger_id:
            budgets = self.db_manager.get_budgets(ledger_id)
            # 转换为字典格式
            result = []
            for budget in budgets:
                ledger_name = self.get_ledger_name(ledger_id)
                budget_dict = budget.copy()
                budget_dict['ledger_name'] = ledger_name
                result.append(budget_dict)
            return result
        return self.get_all_budgets()
    
    def get_filtered_accounts(self, config):
        """获取筛选的账户信息"""
        # 对于账户，通常不需要按日期筛选，返回所有账户
        return self.get_all_accounts()
    
    def get_date_range_transactions(self, start_date, end_date):
        """获取指定日期范围的交易记录"""
        return self.db_manager.get_transactions_by_date_range(start_date, end_date)
    
    def get_ledger_name(self, ledger_id):
        """获取账本名称"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor('SELECT name FROM ledgers WHERE id = ?', (ledger_id,))
            result = cursor.fetchone()
            return result[0] if result else '未知账本'
    
    def clean_dataframe(self, df, data_type):
        """清理和格式化DataFrame"""
        if data_type == 'transactions':
            # 交易记录特殊处理
            if 'is_settled' in df.columns:
                df['is_settled'] = df['is_settled'].apply(lambda x: '是' if x else '否')
            if 'amount' in df.columns:
                df['amount'] = df['amount'].apply(lambda x: float(f"{x:.2f}"))
            if 'refund_amount' in df.columns:
                df['refund_amount'] = df['refund_amount'].apply(lambda x: float(f"{x:.2f}" if x else 0))
        
        elif data_type == 'budgets':
            # 预算配置特殊处理
            if 'is_active' in df.columns:
                df['is_active'] = df['is_active'].apply(lambda x: '是' if x else '否')
            if 'amount' in df.columns:
                df['amount'] = df['amount'].apply(lambda x: float(f"{x:.2f}"))
            if 'warning_threshold' in df.columns:
                df['warning_threshold'] = df['warning_threshold'].apply(lambda x: f"{x:.1f}%")
        
        elif data_type == 'accounts':
            # 账户信息特殊处理
            if 'balance' in df.columns:
                df['balance'] = df['balance'].apply(lambda x: float(f"{x:.2f}"))
        
        return df
    
    def save_excel_file(self, export_data, file_path, ledger_name):
        """保存Excel文件"""
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for sheet_name, df in export_data.items():
                # 中文工作表名称
                sheet_names = {
                    'transactions': '记账记录',
                    'budgets': '预算配置',
                    'accounts': '账户信息'
                }
                display_name = sheet_names.get(sheet_name, sheet_name)
                df.to_excel(writer, sheet_name=display_name, index=False)
                
                # 设置列宽
                worksheet = writer.sheets[display_name]
                for idx, col in enumerate(df.columns):
                    max_len = max(
                        df[col].astype(str).map(len).max(),
                        len(str(col))
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_len + 2, 50)
    
    def save_csv_file(self, export_data, file_path, ledger_name):
        """保存CSV文件（多文件）"""
        base_name = os.path.splitext(file_path)[0]
        
        for data_type, df in export_data.items():
            sheet_names = {
                'transactions': '记账记录',
                'budgets': '预算配置', 
                'accounts': '账户信息'
            }
            display_name = sheet_names.get(data_type, data_type)
            csv_file = f"{base_name}_{display_name}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')


class ImportWorker(QThread):
    """导入工作线程"""
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(dict)  # 导入结果统计
    error_occurred = pyqtSignal(str)
    validation_finished = pyqtSignal(dict)  # 校验结果
    
    def __init__(self, db_manager, import_config):
        super().__init__()
        self.db_manager = db_manager
        self.import_config = import_config
    
    def run(self):
        try:
            # 校验文件
            validation_result = self.validate_file()
            self.validation_finished.emit(validation_result)
            
            if not validation_result['is_valid']:
                return
            
            # 执行导入
            import_result = self.import_data()
            self.finished.emit(import_result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def validate_file(self):
        """校验导入文件"""
        file_path = self.import_config['file_path']
        import_type = self.import_config['import_type']
        
        if not os.path.exists(file_path):
            return {'is_valid': False, 'errors': ['文件不存在']}
        
        try:
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                # Excel文件
                validation_result = self.validate_excel_file(file_path, import_type)
            elif file_path.endswith('.csv'):
                # CSV文件
                validation_result = self.validate_csv_file(file_path, import_type)
            else:
                return {'is_valid': False, 'errors': ['不支持的文件格式，仅支持Excel和CSV文件']}
            
            return validation_result
            
        except Exception as e:
            return {'is_valid': False, 'errors': [f'文件读取失败: {str(e)}']}
    
    def validate_excel_file(self, file_path, import_type):
        """校验Excel文件"""
        sheet_names = {
            'transactions': '记账记录',
            'budgets': '预算配置',
            'accounts': '账户信息'
        }
        
        expected_sheet = sheet_names.get(import_type, import_type)
        
        try:
            # 尝试读取指定工作表
            df = pd.read_excel(file_path, sheet_name=expected_sheet)
            return self.validate_dataframe(df, import_type)
        except:
            # 如果中文名工作表不存在，尝试英文名
            try:
                df = pd.read_excel(file_path, sheet_name=import_type)
                return self.validate_dataframe(df, import_type)
            except Exception as e:
                return {'is_valid': False, 'errors': [f'无法读取工作表: {str(e)}']}
    
    def validate_csv_file(self, file_path, import_type):
        """校验CSV文件"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            return self.validate_dataframe(df, import_type)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='gbk')
                return self.validate_dataframe(df, import_type)
            except Exception as e:
                return {'is_valid': False, 'errors': [f'CSV文件编码错误: {str(e)}']}
        except Exception as e:
            return {'is_valid': False, 'errors': [f'CSV文件格式错误: {str(e)}']}
    
    def validate_dataframe(self, df, import_type):
        """校验DataFrame"""
        errors = []
        warnings = []
        
        # 检查是否有数据
        if df.empty:
            return {'is_valid': False, 'errors': ['文件中没有数据']}
        
        # 根据类型校验字段
        if import_type == 'transactions':
            required_fields = ['transaction_date', 'transaction_type', 'category', 'amount']
            optional_fields = ['subcategory', 'account', 'description', 'is_settled', 'refund_amount', 'refund_reason']
            
        elif import_type == 'budgets':
            required_fields = ['category', 'budget_type', 'amount']
            optional_fields = ['warning_threshold', 'start_date', 'end_date', 'is_active']
            
        elif import_type == 'accounts':
            required_fields = ['name', 'type']
            optional_fields = ['balance', 'bank', 'description']
        
        else:
            return {'is_valid': False, 'errors': ['不支持的导入类型']}
        
        # 检查必填字段
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            errors.append(f'缺少必填字段: {", ".join(missing_fields)}')
        
        # 检查数据完整性
        row_errors = []
        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel行号从2开始
            
            # 检查必填字段是否为空
            for field in required_fields:
                if pd.isna(row.get(field, '')) or str(row.get(field, '')).strip() == '':
                    row_errors.append(f'第{row_num}行: {field}字段为空')
            
            # 检查数据格式
            if import_type == 'transactions':
                # 日期格式检查
                date_val = row.get('transaction_date')
                if pd.notna(date_val):
                    try:
                        pd.to_datetime(date_val)
                    except:
                        row_errors.append(f'第{row_num}行: 日期格式错误')
                
                # 交易类型检查
                transaction_type = str(row.get('transaction_type', '')).strip()
                if transaction_type not in ['收入', '支出']:
                    row_errors.append(f'第{row_num}行: 交易类型必须是"收入"或"支出"')
                
                # 金额检查
                amount = row.get('amount')
                if pd.notna(amount):
                    try:
                        float_amount = float(amount)
                        if float_amount <= 0:
                            row_errors.append(f'第{row_num}行: 金额必须大于0')
                    except:
                        row_errors.append(f'第{row_num}行: 金额格式错误')
            
            elif import_type == 'budgets':
                # 预算类型检查
                budget_type = str(row.get('budget_type', '')).strip()
                if budget_type not in ['monthly', 'yearly', '月度', '年度']:
                    row_errors.append(f'第{row_num}行: 预算类型必须是"monthly"或"yearly"')
                
                # 金额检查
                amount = row.get('amount')
                if pd.notna(amount):
                    try:
                        float_amount = float(amount)
                        if float_amount <= 0:
                            row_errors.append(f'第{row_num}行: 预算金额必须大于0')
                    except:
                        row_errors.append(f'第{row_num}行: 预算金额格式错误')
            
            elif import_type == 'accounts':
                # 账户类型检查
                account_type = str(row.get('type', '')).strip()
                if account_type not in ['现金', '电子支付', '银行卡', '信用卡', '其他']:
                    row_errors.append(f'第{row_num}行: 账户类型必须是有效的类型')
                
                # 余额检查
                balance = row.get('balance')
                if pd.notna(balance):
                    try:
                        float(balance)
                    except:
                        row_errors.append(f'第{row_num}行: 余额格式错误')
        
        # 限制错误显示数量
        if len(row_errors) > 20:
            row_errors = row_errors[:20] + [f'... 还有{len(row_errors)-20}个错误未显示']
        
        errors.extend(row_errors)
        
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'total_rows': len(df),
            'valid_rows': len(df) - len(row_errors)
        }
    
    def import_data(self):
        """执行数据导入"""
        file_path = self.import_config['file_path']
        import_type = self.import_config['import_type']
        import_mode = self.import_config.get('import_mode', 'append')  # 'append' or 'overwrite'
        
        # 读取数据
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            sheet_names = {'transactions': '记账记录', 'budgets': '预算配置', 'accounts': '账户信息'}
            expected_sheet = sheet_names.get(import_type, import_type)
            try:
                df = pd.read_excel(file_path, sheet_name=expected_sheet)
            except:
                df = pd.read_excel(file_path, sheet_name=import_type)
        else:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # 清理和转换数据
        df = self.clean_import_data(df, import_type)
        
        # 执行导入
        total_rows = len(df)
        success_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                if import_type == 'transactions':
                    self.import_transaction(row, import_mode)
                elif import_type == 'budgets':
                    self.import_budget(row, import_mode)
                elif import_type == 'accounts':
                    self.import_account(row, import_mode)
                
                success_count += 1
                self.progress_updated.emit(int((success_count / total_rows) * 100))
                
            except Exception as e:
                error_count += 1
                # 记录错误但继续处理其他记录
        
        return {
            'total_rows': total_rows,
            'success_count': success_count,
            'error_count': error_count,
            'import_mode': import_mode
        }
    
    def clean_import_data(self, df, import_type):
        """清理导入数据"""
        if import_type == 'transactions':
            # 转换日期格式
            df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m-%d')
            
            # 转换金额
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            if 'refund_amount' in df.columns:
                df['refund_amount'] = pd.to_numeric(df['refund_amount'], errors='coerce').fillna(0)
            
            # 转换布尔值
            if 'is_settled' in df.columns:
                df['is_settled'] = df['is_settled'].apply(lambda x: 1 if str(x).strip() in ['是', 'True', '1', 'true'] else 0)
            
        elif import_type == 'budgets':
            # 转换金额
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            if 'warning_threshold' in df.columns:
                df['warning_threshold'] = pd.to_numeric(df['warning_threshold'], errors='coerce').fillna(80.0)
            
            # 转换预算类型
            df['budget_type'] = df['budget_type'].replace({
                '月度': 'monthly',
                '年度': 'yearly',
                'monthly': 'monthly',
                'yearly': 'yearly'
            })
            
            # 转换布尔值
            if 'is_active' in df.columns:
                df['is_active'] = df['is_active'].apply(lambda x: 1 if str(x).strip() in ['是', 'True', '1', 'true'] else 0)
        
        elif import_type == 'accounts':
            # 转换余额
            df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0.0)
        
        # 填充空值
        df = df.fillna('')
        
        return df
    
    def import_transaction(self, row, import_mode):
        """导入单条交易记录"""
        # 获取或创建账本ID
        ledger_name = row.get('ledger_name', '默认账本')
        ledger_id = self.get_or_create_ledger(ledger_name)
        
        # 插入交易记录
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions 
                (ledger_id, transaction_date, transaction_type, category, subcategory, 
                 amount, account, description, is_settled, refund_amount, refund_reason, created_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ledger_id,
                row['transaction_date'],
                row['transaction_type'],
                row['category'],
                row.get('subcategory', ''),
                row['amount'],
                row.get('account', ''),
                row.get('description', ''),
                row.get('is_settled', 0),
                row.get('refund_amount', 0),
                row.get('refund_reason', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
    
    def import_budget(self, row, import_mode):
        """导入单条预算配置"""
        # 获取或创建账本ID
        ledger_name = row.get('ledger_name', '默认账本')
        ledger_id = self.get_or_create_ledger(ledger_name)
        
        # 插入预算配置
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO budgets 
                (ledger_id, category, budget_type, amount, warning_threshold, 
                 start_date, end_date, is_active, created_time, updated_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ledger_id,
                row['category'],
                row['budget_type'],
                row['amount'],
                row.get('warning_threshold', 80.0),
                row.get('start_date', datetime.now().strftime('%Y-%m-01')),
                row.get('end_date', ''),
                row.get('is_active', 1),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
    
    def import_account(self, row, import_mode):
        """导入单个账户信息"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor('''
                INSERT OR REPLACE INTO accounts 
                (name, type, balance, bank, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['name'],
                row['type'],
                row.get('balance', 0.0),
                row.get('bank', ''),
                row.get('description', '')
            ))
    
    def get_or_create_ledger(self, ledger_name):
        """获取或创建账本ID"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor('SELECT id FROM ledgers WHERE name = ?', (ledger_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # 创建新账本
                cursor = conn.cursor('''
                    INSERT INTO ledgers (name, created_time, ledger_type, description)
                    VALUES (?, ?, ?, ?)
                ''', (ledger_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '个人', ''))
                return cursor.lastrowid


class ExportDialog(BaseDialog):
    """导出对话框"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.worker = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("数据导出")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        StyleHelper.apply_label_style(title_label)
        layout.addWidget(title_label)
        
        # 导出范围
        scope_group = QGroupBox("导出范围")
        StyleHelper.apply_groupbox_style(scope_group)
        scope_layout = QVBoxLayout()
        
        self.scope_group = QButtonGroup()
        self.all_radio = QRadioButton("全账本数据导出")
        self.all_radio.setChecked(True)
        self.filtered_radio = QRadioButton("筛选结果导出")
        self.specific_radio = QRadioButton("指定数据类型导出")
        
        self.scope_group.addButton(self.all_radio, 0)
        self.scope_group.addButton(self.filtered_radio, 1)
        self.scope_group.addButton(self.specific_radio, 2)
        
        scope_layout.addWidget(self.all_radio)
        scope_layout.addWidget(self.filtered_radio)
        scope_layout.addWidget(self.specific_radio)
        
        scope_group.setLayout(scope_layout)
        layout.addWidget(scope_group)
        
        # 数据类型选择（仅在指定类型时显示）
        self.data_type_group = QGroupBox("数据类型")
        StyleHelper.apply_groupbox_style(self.data_type_group)
        data_type_layout = QVBoxLayout()
        
        self.transactions_check = QCheckBox("记账记录")
        self.transactions_check.setChecked(True)
        self.budgets_check = QCheckBox("预算配置")
        self.accounts_check = QCheckBox("账户信息")
        
        data_type_layout.addWidget(self.transactions_check)
        data_type_layout.addWidget(self.budgets_check)
        data_type_layout.addWidget(self.accounts_check)
        
        self.data_type_group.setLayout(data_type_layout)
        self.data_type_group.hide()  # 初始隐藏
        
        layout.addWidget(self.data_type_group)
        
        # 导出格式
        format_group = QGroupBox("导出格式")
        StyleHelper.apply_groupbox_style(format_group)
        format_layout = QHBoxLayout()
        
        self.format_group = QButtonGroup()
        self.excel_radio = QRadioButton("Excel (.xlsx)")
        self.excel_radio.setChecked(True)
        self.csv_radio = QRadioButton("CSV")
        
        self.format_group.addButton(self.excel_radio, 0)
        self.format_group.addButton(self.csv_radio, 1)
        
        format_layout.addWidget(self.excel_radio)
        format_layout.addWidget(self.csv_radio)
        format_layout.addStretch()
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # 文件命名预览
        preview_group = QGroupBox("文件命名预览")
        StyleHelper.apply_groupbox_style(preview_group)
        preview_layout = QVBoxLayout()
        
        self.filename_preview = QLabel()
        self.filename_preview.setStyleSheet(f"""
            QLabel {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
            }}
        """)
        
        preview_layout.addWidget(QLabel("文件名:"))
        preview_layout.addWidget(self.filename_preview)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 操作区域
        operation_layout = QVBoxLayout()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        operation_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        operation_layout.addWidget(self.status_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("开始导出")
        self.export_btn.clicked.connect(self.start_export)
        StyleHelper.apply_button_style(self.export_btn)
        button_layout.addWidget(self.export_btn)
        
        self.open_folder_btn = QPushButton("打开文件夹")
        self.open_folder_btn.clicked.connect(self.open_export_folder)
        self.open_folder_btn.hide()
        StyleHelper.apply_button_style(self.open_folder_btn)
        button_layout.addWidget(self.open_folder_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("关闭")
        cancel_btn.clicked.connect(self.reject)
        StyleHelper.apply_button_style(cancel_btn)
        button_layout.addWidget(cancel_btn)
        
        operation_layout.addLayout(button_layout)
        layout.addLayout(operation_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.scope_group.idClicked.connect(self.on_scope_changed)
        self.format_group.idClicked.connect(self.update_filename_preview)
        
        # 更新文件名预览
        self.update_filename_preview()
        
        # 定时更新预览
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_filename_preview)
        self.preview_timer.start(1000)  # 每秒更新一次
    
    def on_scope_changed(self, button_id):
        """导出范围改变时的处理"""
        if button_id == 2:  # 指定数据类型
            self.data_type_group.show()
        else:
            self.data_type_group.hide()
        
        self.update_filename_preview()
    
    def update_filename_preview(self):
        """更新文件名预览"""
        current_time = datetime.now().strftime('%Y%m%d')
        
        # 获取导出类型描述
        if self.all_radio.isChecked():
            export_type = "全账本数据"
        elif self.filtered_radio.isChecked():
            export_type = "筛选结果"
        else:
            selected_types = []
            if self.transactions_check.isChecked():
                selected_types.append("记账记录")
            if self.budgets_check.isChecked():
                selected_types.append("预算配置")
            if self.accounts_check.isChecked():
                selected_types.append("账户信息")
            export_type = "+".join(selected_types) if selected_types else "未选择"
        
        # 获取格式扩展名
        if self.excel_radio.isChecked():
            extension = ".xlsx"
        else:
            extension = ".csv"
        
        filename = f"日常消费-{export_type}-{current_time}{extension}"
        self.filename_preview.setText(filename)
    
    def start_export(self):
        """开始导出"""
        # 验证选择
        if self.specific_radio.isChecked():
            if not any([self.transactions_check.isChecked(), 
                       self.budgets_check.isChecked(), 
                       self.accounts_check.isChecked()]):
                MessageHelper.show_warning(self, "提示", "请至少选择一种数据类型！")
                return
        
        # 选择保存路径
        export_format = 'excel' if self.excel_radio.isChecked() else 'csv'
        file_extension = '.xlsx' if export_format == 'excel' else '.csv'
        
        filename = self.filename_preview.text()
        
        if export_format == 'csv' and self.specific_radio.isChecked():
            # CSV多文件模式，选择文件夹
            folder_path = QFileDialog.getExistingDirectory(self, "选择保存文件夹")
            if not folder_path:
                return
            file_path = os.path.join(folder_path, filename)
        else:
            # Excel单文件或CSV单文件
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存文件", filename, 
                f"{export_format.upper()}文件 (*{file_extension})"
            )
            if not file_path:
                return
        
        # 确定导出配置
        if self.all_radio.isChecked():
            export_type = 'all'
        elif self.filtered_radio.isChecked():
            export_type = 'filtered'
        else:
            export_type = 'specific'
            export_scope = []
            if self.transactions_check.isChecked():
                export_scope.append('transactions')
            if self.budgets_check.isChecked():
                export_scope.append('budgets')
            if self.accounts_check.isChecked():
                export_scope.append('accounts')
        
        export_config = {
            'export_type': export_type,
            'export_format': export_format,
            'export_scope': export_scope if export_type == 'specific' else [],
            'file_path': file_path,
            'ledger_name': '日常消费'
        }
        
        # 如果是筛选结果，需要获取筛选条件
        if export_type == 'filtered':
            # 这里可以从父窗口获取当前的筛选条件
            # 暂时使用默认值
            export_config.update({
                'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d'),
                'ledger_id': None
            })
        
        # 开始导出
        self.export_btn.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.status_label.setText("正在导出数据...")
        
        self.worker = ExportWorker(self.db_manager, export_config)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.error_occurred.connect(self.on_export_error)
        self.worker.start()
    
    def on_export_finished(self, file_path, success):
        """导出完成"""
        self.progress_bar.hide()
        self.export_btn.setEnabled(True)
        
        if success:
            self.status_label.setText(f"导出成功！文件已保存至: {file_path}")
            self.open_folder_btn.show()
            self.exported_file_path = file_path
            
            MessageHelper.show_info(
                self, "导出成功", 
                f"数据导出成功！\n文件路径: {file_path}"
            )
        else:
            self.status_label.setText("导出失败")
            MessageHelper.show_error(self, "导出失败", "导出过程中发生未知错误")
    
    def on_export_error(self, error_message):
        """导出错误"""
        self.progress_bar.hide()
        self.export_btn.setEnabled(True)
        self.status_label.setText("导出失败")
        
        MessageHelper.show_error(self, "导出失败", f"导出过程中发生错误:\n{error_message}")
    
    def open_export_folder(self):
        """打开导出文件所在文件夹"""
        if hasattr(self, 'exported_file_path'):
            folder_path = os.path.dirname(self.exported_file_path)
            try:
                if sys.platform == "win32":
                    os.startfile(folder_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", folder_path])
                else:
                    subprocess.run(["xdg-open", folder_path])
            except Exception as e:
                MessageHelper.show_warning(self, "提示", f"无法打开文件夹: {str(e)}")


class ImportDialog(BaseDialog):
    """导入对话框"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.worker = None
        self.import_result = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("数据导入")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        StyleHelper.apply_label_style(title_label)
        layout.addWidget(title_label)
        
        # 导入类型选择
        type_group = QGroupBox("导入数据类型")
        StyleHelper.apply_groupbox_style(type_group)
        type_layout = QVBoxLayout()
        
        self.import_type_group = QButtonGroup()
        self.import_transactions_radio = QRadioButton("记账记录")
        self.import_transactions_radio.setChecked(True)
        self.import_budgets_radio = QRadioButton("预算配置")
        self.import_accounts_radio = QRadioButton("账户信息")
        
        self.import_type_group.addButton(self.import_transactions_radio, 0)
        self.import_type_group.addButton(self.import_budgets_radio, 1)
        self.import_type_group.addButton(self.import_accounts_radio, 2)
        
        type_layout.addWidget(self.import_transactions_radio)
        type_layout.addWidget(self.import_budgets_radio)
        type_layout.addWidget(self.import_accounts_radio)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # 文件选择
        file_group = QGroupBox("文件选择")
        StyleHelper.apply_groupbox_style(file_group)
        file_layout = QVBoxLayout()
        
        # 文件路径显示
        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(QLabel("文件路径:"))
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        file_path_layout.addWidget(self.file_path_edit)
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_file)
        StyleHelper.apply_button_style(self.browse_btn)
        file_path_layout.addWidget(self.browse_btn)
        
        file_layout.addLayout(file_path_layout)
        
        # 模板下载
        template_layout = QHBoxLayout()
        self.download_template_btn = QPushButton("下载标准导入模板")
        self.download_template_btn.clicked.connect(self.download_template)
        StyleHelper.apply_button_style(self.download_template_btn)
        template_layout.addWidget(self.download_template_btn)
        template_layout.addStretch()
        
        file_layout.addLayout(template_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 导入模式
        mode_group = QGroupBox("导入模式")
        StyleHelper.apply_groupbox_style(mode_group)
        mode_layout = QVBoxLayout()
        
        self.import_mode_group = QButtonGroup()
        self.append_radio = QRadioButton("追加导入（推荐）")
        self.append_radio.setChecked(True)
        self.overwrite_radio = QRadioButton("覆盖导入")
        
        self.import_mode_group.addButton(self.append_radio, 0)
        self.import_mode_group.addButton(self.overwrite_radio, 1)
        
        mode_layout.addWidget(self.append_radio)
        mode_layout.addWidget(self.overwrite_radio)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # 校验结果显示
        self.validation_group = QGroupBox("文件校验结果")
        StyleHelper.apply_groupbox_style(self.validation_group)
        validation_layout = QVBoxLayout()
        
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(150)
        validation_layout.addWidget(self.validation_text)
        
        self.validation_group.setLayout(validation_layout)
        self.validation_group.hide()
        layout.addWidget(self.validation_group)
        
        # 导入进度
        progress_group = QGroupBox("导入进度")
        StyleHelper.apply_groupbox_style(progress_group)
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 导入结果
        self.result_group = QGroupBox("导入结果")
        StyleHelper.apply_groupbox_style(self.result_group)
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        
        self.result_group.setLayout(result_layout)
        self.result_group.hide()
        layout.addWidget(self.result_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("开始导入")
        self.import_btn.clicked.connect(self.start_import)
        self.import_btn.setEnabled(False)
        StyleHelper.apply_button_style(self.import_btn)
        button_layout.addWidget(self.import_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("关闭")
        cancel_btn.clicked.connect(self.reject)
        StyleHelper.apply_button_style(cancel_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择导入文件", "",
            "Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv);;所有文件 (*)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            self.import_btn.setEnabled(True)
    
    def download_template(self):
        """下载标准导入模板"""
        import_type = self.get_import_type()
        
        # 选择保存路径
        file_extension = '.xlsx'
        file_types = f"Excel文件 (*{file_extension})"
        
        template_names = {
            'transactions': '记账记录导入模板.xlsx',
            'budgets': '预算配置导入模板.xlsx',
            'accounts': '账户信息导入模板.xlsx'
        }
        
        filename = template_names.get(import_type, '导入模板.xlsx')
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存模板文件", filename, file_types
        )
        
        if file_path:
            try:
                self.create_template_file(file_path, import_type)
                MessageHelper.show_info(
                    self, "模板下载成功", 
                    f"标准导入模板已保存至:\n{file_path}"
                )
            except Exception as e:
                MessageHelper.show_error(
                    self, "模板下载失败", 
                    f"模板文件创建失败:\n{str(e)}"
                )
    
    def create_template_file(self, file_path, import_type):
        """创建模板文件"""
        if import_type == 'transactions':
            # 记账记录模板
            template_data = pd.DataFrame({
                'ledger_name': ['示例账本'],
                'transaction_date': ['2025-01-01'],
                'transaction_type': ['支出'],
                'category': ['餐饮'],
                'subcategory': ['外卖'],
                'amount': [25.00],
                'account': ['微信'],
                'description': ['午餐'],
                'is_settled': [1],
                'refund_amount': [0.00],
                'refund_reason': ['']
            })
            
        elif import_type == 'budgets':
            # 预算配置模板
            template_data = pd.DataFrame({
                'ledger_name': ['示例账本'],
                'category': ['餐饮'],
                'budget_type': ['monthly'],
                'amount': [1000.00],
                'warning_threshold': [80.0],
                'start_date': ['2025-01-01'],
                'end_date': [''],
                'is_active': [1]
            })
            
        elif import_type == 'accounts':
            # 账户信息模板
            template_data = pd.DataFrame({
                'name': ['现金', '微信', '支付宝'],
                'type': ['现金', '电子支付', '电子支付'],
                'balance': [100.00, 500.00, 200.00],
                'bank': ['个人', '腾讯', '阿里巴巴'],
                'description': ['现金余额', '微信支付余额', '支付宝余额']
            })
        
        # 保存模板文件
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            template_data.to_excel(writer, sheet_name='模板数据', index=False)
            
            # 添加说明工作表
            instructions = self.get_template_instructions(import_type)
            instructions_df = pd.DataFrame({'说明': instructions})
            instructions_df.to_excel(writer, sheet_name='使用说明', index=False)
    
    def get_template_instructions(self, import_type):
        """获取模板使用说明"""
        if import_type == 'transactions':
            return [
                '记账记录导入使用说明',
                '',
                '必填字段:',
                '- ledger_name: 账本名称',
                '- transaction_date: 交易日期 (YYYY-MM-DD格式)',
                '- transaction_type: 交易类型 (收入/支出)',
                '- category: 大类',
                '- amount: 金额 (必须大于0)',
                '',
                '可选字段:',
                '- subcategory: 小类',
                '- account: 账户',
                '- description: 描述',
                '- is_settled: 是否销账 (1/0 或 是/否)',
                '- refund_amount: 退款金额',
                '- refund_reason: 退款原因',
                '',
                '注意事项:',
                '1. 日期格式必须为YYYY-MM-DD',
                '2. 交易类型只能是"收入"或"支出"',
                '3. 金额必须为正数',
                '4. 请确保数据完整性'
            ]
        
        elif import_type == 'budgets':
            return [
                '预算配置导入使用说明',
                '',
                '必填字段:',
                '- ledger_name: 账本名称',
                '- category: 预算类别',
                '- budget_type: 预算类型 (monthly/yearly)',
                '- amount: 预算金额',
                '',
                '可选字段:',
                '- warning_threshold: 预警阈值百分比',
                '- start_date: 生效开始日期',
                '- end_date: 生效结束日期',
                '- is_active: 是否启用 (1/0 或 是/否)',
                '',
                '注意事项:',
                '1. budget_type可以是monthly/yearly或对应的中文',
                '2. 预算金额必须大于0',
                '3. 预警阈值范围为0-100'
            ]
        
        elif import_type == 'accounts':
            return [
                '账户信息导入使用说明',
                '',
                '必填字段:',
                '- name: 账户名称',
                '- type: 账户类型',
                '',
                '可选字段:',
                '- balance: 余额',
                '- bank: 银行/机构',
                '- description: 描述',
                '',
                '注意事项:',
                '1. 账户类型: 现金/电子支付/银行卡/信用卡/其他',
                '2. 账户名称不能重复',
                '3. 余额为数字格式'
            ]
    
    def get_import_type(self):
        """获取导入类型"""
        button_id = self.import_type_group.checkedId()
        type_map = {0: 'transactions', 1: 'budgets', 2: 'accounts'}
        return type_map.get(button_id, 'transactions')
    
    def start_import(self):
        """开始导入"""
        file_path = self.file_path_edit.text()
        if not file_path:
            MessageHelper.show_warning(self, "提示", "请选择要导入的文件！")
            return
        
        import_type = self.get_import_type()
        import_mode = 'append' if self.append_radio.isChecked() else 'overwrite'
        
        import_config = {
            'file_path': file_path,
            'import_type': import_type,
            'import_mode': import_mode
        }
        
        # 禁用导入按钮
        self.import_btn.setEnabled(False)
        self.validation_group.hide()
        self.result_group.hide()
        
        # 开始校验和导入
        self.worker = ImportWorker(self.db_manager, import_config)
        self.worker.validation_finished.connect(self.on_validation_finished)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_import_finished)
        self.worker.error_occurred.connect(self.on_import_error)
        self.worker.start()
    
    def on_validation_finished(self, validation_result):
        """文件校验完成"""
        self.validation_group.show()
        
        if validation_result['is_valid']:
            # 校验通过
            validation_text = f"✅ 文件校验通过！\n"
            validation_text += f"总行数: {validation_result['total_rows']}\n"
            validation_text += f"有效行数: {validation_result['valid_rows']}\n"
            
            if validation_result['warnings']:
                validation_text += "\n⚠️ 警告:\n"
                for warning in validation_result['warnings']:
                    validation_text += f"- {warning}\n"
            
            self.validation_text.setText(validation_text)
            self.validation_text.setStyleSheet("QTextEdit { color: green; }")
            
            # 显示进度条
            self.progress_bar.show()
            self.progress_bar.setValue(0)
            self.status_label.setText("正在导入数据...")
            
        else:
            # 校验失败
            validation_text = f"❌ 文件校验失败！\n"
            validation_text += f"总行数: {validation_result['total_rows']}\n"
            validation_text += f"有效行数: {validation_result['valid_rows']}\n\n"
            
            if validation_result['errors']:
                validation_text += "错误详情:\n"
                for error in validation_result['errors']:
                    validation_text += f"- {error}\n"
            
            self.validation_text.setText(validation_text)
            self.validation_text.setStyleSheet("QTextEdit { color: red; }")
            
            # 重新启用导入按钮
            self.import_btn.setEnabled(True)
    
    def on_import_finished(self, import_result):
        """导入完成"""
        self.progress_bar.hide()
        self.result_group.show()
        self.status_label.setText("导入完成")
        
        # 显示导入结果
        result_text = f"🎉 导入完成！\n\n"
        result_text += f"总处理行数: {import_result['total_rows']}\n"
        result_text += f"成功导入: {import_result['success_count']}\n"
        result_text += f"失败行数: {import_result['error_count']}\n"
        result_text += f"导入模式: {'追加' if import_result['import_mode'] == 'append' else '覆盖'}\n"
        
        if import_result['error_count'] > 0:
            result_text += "\n⚠️ 部分数据导入失败，请检查数据格式是否正确"
        
        self.result_text.setText(result_text)
        self.import_result = import_result
        
        # 显示成功消息
        if import_result['success_count'] > 0:
            MessageHelper.show_info(
                self, "导入成功", 
                f"成功导入 {import_result['success_count']} 条记录！"
            )
        else:
            MessageHelper.show_warning(
                self, "导入完成", 
                "没有数据被导入，请检查文件格式和内容"
            )
        
        # 重新启用导入按钮
        self.import_btn.setEnabled(True)
    
    def on_import_error(self, error_message):
        """导入错误"""
        self.progress_bar.hide()
        self.status_label.setText("导入失败")
        self.import_btn.setEnabled(True)
        
        MessageHelper.show_error(self, "导入失败", f"导入过程中发生错误:\n{error_message}")


class DataManagementDialog(BaseDialog):
    """数据管理主对话框"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("数据管理")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        StyleHelper.apply_label_style(title_label)
        layout.addWidget(title_label)
        
        # 功能按钮区域
        buttons_layout = QVBoxLayout()
        
        # 导出按钮
        export_group = QGroupBox("数据导出")
        StyleHelper.apply_groupbox_style(export_group)
        export_layout = QVBoxLayout()
        
        export_btn = QPushButton("📤 导出数据")
        export_btn.clicked.connect(self.open_export_dialog)
        export_btn.setMinimumHeight(50)
        StyleHelper.apply_button_style(export_btn)
        export_layout.addWidget(export_btn)
        
        export_info = QLabel("支持导出全账本数据、筛选结果或指定类型的数据，支持Excel和CSV格式")
        export_info.setWordWrap(True)
        export_info.setStyleSheet("color: #666; font-size: 12px; margin: 5px;")
        export_layout.addWidget(export_info)
        
        export_group.setLayout(export_layout)
        buttons_layout.addWidget(export_group)
        
        # 导入按钮
        import_group = QGroupBox("数据导入")
        StyleHelper.apply_groupbox_style(import_group)
        import_layout = QVBoxLayout()
        
        import_btn = QPushButton("📥 导入数据")
        import_btn.clicked.connect(self.open_import_dialog)
        import_btn.setMinimumHeight(50)
        StyleHelper.apply_button_style(import_btn)
        import_layout.addWidget(import_btn)
        
        import_info = QLabel("支持导入记账记录、预算配置和账户信息，提供标准模板下载")
        import_info.setWordWrap(True)
        import_info.setStyleSheet("color: #666; font-size: 12px; margin: 5px;")
        import_layout.addWidget(import_info)
        
        import_group.setLayout(import_layout)
        buttons_layout.addWidget(import_group)
        
        layout.addLayout(buttons_layout)
        
        # 关闭按钮
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        StyleHelper.apply_button_style(close_btn)
        close_layout.addWidget(close_btn)
        
        layout.addLayout(close_layout)
        self.setLayout(layout)
    
    def open_export_dialog(self):
        """打开导出对话框"""
        dialog = ExportDialog(self.db_manager, self)
        dialog.exec()
    
    def open_import_dialog(self):
        """打开导入对话框"""
        dialog = ImportDialog(self.db_manager, self)
        dialog.exec()