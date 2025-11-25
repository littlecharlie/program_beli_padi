"""
Application Styles (QSS)
Stylesheet definitions for PyQt6 UI
"""

STYLESHEET = """
QMainWindow {
    background-color: #f0f0f0;
}

QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #ddd;
}

QMenuBar::item:selected {
    background-color: #e0e0e0;
}

QPushButton {
    background-color: #007ACC;
    color: white;
    border: none;
    padding: 5px 15px;
    border-radius: 3px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #005a9e;
}

QPushButton:pressed {
    background-color: #004578;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}

QLineEdit, QTextEdit, QComboBox {
    border: 1px solid #ddd;
    padding: 5px;
    border-radius: 3px;
    background-color: white;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 2px solid #007ACC;
}

QLabel {
    color: #333333;
}

QTableWidget {
    border: 1px solid #ddd;
    gridline-color: #ddd;
}

QTableWidget::item {
    padding: 5px;
}

QHeaderView::section {
    background-color: #f0f0f0;
    padding: 5px;
    border: none;
    border-right: 1px solid #ddd;
    border-bottom: 1px solid #ddd;
}

QTabWidget::pane {
    border: 1px solid #ddd;
}

QTabBar::tab {
    background-color: #f0f0f0;
    padding: 8px 20px;
    border: 1px solid #ddd;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: 2px solid #007ACC;
}

QGroupBox {
    border: 1px solid #ddd;
    border-radius: 3px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}

QDialog {
    background-color: #f0f0f0;
}

QMessageBox {
    background-color: #f0f0f0;
}
"""
