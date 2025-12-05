"""
图表工具模块 - 提供通用的图表创建功能
"""
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from theme_manager import theme_manager

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


class ChartUtils:
    """图表工具类"""
    
    @staticmethod
    def create_pie_chart(figure, data, labels, title, colors=None):
        """创建圆环图"""
        try:
            # 清理之前的图形对象以释放内存
            figure.clear()
            ax = figure.add_subplot(111)
            
            # 获取主题颜色
            theme_colors = theme_manager.get_color('chart_colors')
            theme_bg = theme_manager.get_color('background')
            theme_text = theme_manager.get_color('primary_text')
            theme_border = theme_manager.get_color('border')
            
            if not data or sum(data) == 0:
                ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=12, color=theme_text)
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
            wedges, texts, autotexts = ax.pie(
                data, labels=labels, colors=colors, autopct='%1.1f%%', 
                startangle=90, textprops={'fontsize': 9, 'color': theme_text},
                wedgeprops=dict(width=0.6, edgecolor=theme_bg, linewidth=2)
            )
            
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
            
        except Exception as e:
            # 如果绘图出错，创建一个简单的错误显示
            figure.clear()
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, f'图表加载错误\n{str(e)}', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='red')
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.axis('off')
    
    @staticmethod
    def create_chart_widget(title, figsize=(4, 3)):
        """创建图表控件"""
        figure = Figure(figsize=figsize, dpi=100)
        canvas = FigureCanvas(figure)
        
        # 应用主题
        ChartUtils.apply_theme_to_figure(figure)
        
        return figure, canvas
    
    @staticmethod
    def apply_theme_to_figure(figure):
        """应用主题到图表"""
        colors = theme_manager.get_current_theme()["colors"]
        figure.patch.set_facecolor(colors['background'])
        
        # 设置matplotlib参数
        plt.rcParams['figure.facecolor'] = colors['background']
        plt.rcParams['axes.facecolor'] = colors['background']
        plt.rcParams['axes.edgecolor'] = colors['border']
        plt.rcParams['axes.labelcolor'] = colors['primary_text']
        plt.rcParams['xtick.color'] = colors['primary_text']
        plt.rcParams['ytick.color'] = colors['primary_text']
        plt.rcParams['text.color'] = colors['primary_text']
        plt.rcParams['legend.facecolor'] = colors['card_background']
        plt.rcParams['legend.edgecolor'] = colors['border']
        plt.rcParams['legend.labelcolor'] = colors['primary_text']
    
    @staticmethod
    def limit_data_display(labels, data, max_items=8):
        """限制数据显示数量，其余合并为'其他'"""
        if len(labels) <= max_items:
            return labels, data
        
        # 按值排序
        combined = list(zip(labels, data))
        combined.sort(key=lambda x: x[1], reverse=True)
        
        # 取前max_items-1项
        limited_labels = [item[0] for item in combined[:max_items-1]]
        limited_data = [item[1] for item in combined[:max_items-1]]
        
        # 其余合并为"其他"
        other_amount = sum(item[1] for item in combined[max_items-1:])
        limited_labels.append("其他")
        limited_data.append(other_amount)
        
        return limited_labels, limited_data
    
    @staticmethod
    def safe_draw_canvas(canvas):
        """安全地绘制画布"""
        try:
            canvas.draw()
        except Exception as e:
            # 清理画布并显示错误
            canvas.figure.clear()
            ax = canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'绘制错误\n{str(e)}', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='red')
            ax.axis('off')
            canvas.draw()