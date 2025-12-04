import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from gui_main import MainWindow
from theme_manager import theme_manager

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("多账本记账系统")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("BookkeepingApp")
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 配置应用程序设置
    settings = QSettings()
    
    # 设置字体（如果需要）
    font = app.font()
    font.setFamily("Microsoft YaHei, SimHei, Arial")
    app.setFont(font)
    
    # 创建主窗口
    window = MainWindow()
    
    # 恢复窗口状态
    if settings.contains("geometry"):
        window.restoreGeometry(settings.value("geometry"))
    if settings.contains("windowState"):
        window.restoreState(settings.value("windowState"))
    
    window.show()
    
    # 运行应用程序
    exit_code = app.exec()
    
    # 保存窗口状态
    settings.setValue("geometry", window.saveGeometry())
    settings.setValue("windowState", window.saveState())
    
    # 清理资源
    try:
        # 清理数据库连接
        if hasattr(window, 'db_manager'):
            window.db_manager.cleanup_all_connections()
        
        # 清理matplotlib图形对象
        import matplotlib.pyplot as plt
        plt.close('all')
        
        # 清理主题管理器缓存
        if hasattr(theme_manager, '_cached_style'):
            delattr(theme_manager, '_cached_style')
            
    except Exception as e:
        # 忽略清理时的错误，确保程序能够正常退出
        print(f"清理资源时出现错误: {e}")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()