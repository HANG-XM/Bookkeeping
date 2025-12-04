import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from gui_main import MainWindow

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
    
    # 清理数据库连接
    if hasattr(window, 'db_manager'):
        window.db_manager.close_connection()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()