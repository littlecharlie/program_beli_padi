"""
Application Styles (QSS)
Stylesheet definitions for PyQt6 UI - Dark Mode Theme
"""

# Color Palette Constants
COLORS = {
    # Background Colors
    'bg_primary': '#1e1e1e',      # Deep Charcoal - Main background
    'bg_secondary': '#2d2d2d',    # Card/Panel background
    'bg_surface': '#3a3a3a',      # Elevated surfaces
    'bg_hover': '#404040',        # Hover state background
    'border': '#4a4a4a',          # Subtle borders
    'border_focus': '#4da6ff',    # Focus state border

    # Text Colors
    'text_primary': '#e0e0e0',    # High contrast white
    'text_secondary': '#b0b0b0',  # Muted text
    'text_disabled': '#666666',   # Disabled text

    # Accent Colors
    'primary': '#4da6ff',         # Primary blue
    'primary_hover': '#66b3ff',   # Primary hover
    'primary_pressed': '#3d8ae6', # Primary pressed
    'success': '#4caf50',         # Success green
    'warning': '#ff9800',         # Warning orange
    'error': '#f44336',           # Error red
    'info': '#29b6f6',            # Info cyan
    'purple': '#9c27b0',          # Purple accent

    # Status Colors (for stat cards)
    'status_blue': '#2196f3',
    'status_green': '#4caf50',
    'status_orange': '#ff9800',
    'status_cyan': '#00bcd4',
    'status_purple': '#9c27b0',
}

STYLESHEET = f"""
/* ============================================
   MAIN WINDOW & BASE STYLES
   ============================================ */
QMainWindow {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
}}

QWidget {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10pt;
}}

/* ============================================
   MENU BAR
   ============================================ */
QMenuBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 4px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['bg_hover']};
}}

QMenuBar::item:pressed {{
    background-color: {COLORS['primary']};
    color: white;
}}

QMenu {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 3px;
}}

QMenu::item:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}

/* ============================================
   BUTTONS
   ============================================ */
QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 10pt;
    min-height: 28px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_pressed']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_surface']};
    color: {COLORS['text_disabled']};
}}

/* Secondary Button Variant */
QPushButton[secondary="true"] {{
    background-color: {COLORS['bg_surface']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
}}

QPushButton[secondary="true"]:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['primary']};
}}

/* Danger Button Variant */
QPushButton[danger="true"] {{
    background-color: {COLORS['error']};
}}

QPushButton[danger="true"]:hover {{
    background-color: #e53935;
}}

/* Success Button Variant */
QPushButton[success="true"] {{
    background-color: {COLORS['success']};
}}

QPushButton[success="true"]:hover {{
    background-color: #66bb6a;
}}

/* ============================================
   INPUT FIELDS
   ============================================ */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    padding: 8px;
    border-radius: 4px;
    selection-background-color: {COLORS['primary']};
    selection-color: white;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {COLORS['border_focus']};
    background-color: {COLORS['bg_surface']};
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_disabled']};
    border-color: {COLORS['bg_surface']};
}}

/* ============================================
   COMBO BOX (DROPDOWN)
   ============================================ */
QComboBox {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    padding: 8px;
    border-radius: 4px;
    min-height: 28px;
}}

QComboBox:focus {{
    border: 2px solid {COLORS['border_focus']};
}}

QComboBox:disabled {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_disabled']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['primary']};
    selection-color: white;
    padding: 4px;
}}

/* ============================================
   LABELS
   ============================================ */
QLabel {{
    color: {COLORS['text_primary']};
    background-color: transparent;
}}

QLabel[secondary="true"] {{
    color: {COLORS['text_secondary']};
}}

QLabel[heading="true"] {{
    font-size: 14pt;
    font-weight: bold;
    color: {COLORS['text_primary']};
}}

/* ============================================
   TABLES
   ============================================ */
QTableWidget {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    gridline-color: {COLORS['border']};
    border-radius: 4px;
}}

QTableWidget::item {{
    padding: 8px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}

QTableWidget::item:hover {{
    background-color: {COLORS['bg_hover']};
}}

QTableWidget::item:alternate {{
    background-color: {COLORS['bg_primary']};
}}

/* Table Headers */
QHeaderView::section {{
    background-color: {COLORS['bg_surface']};
    color: {COLORS['text_primary']};
    padding: 8px;
    border: none;
    border-right: 1px solid {COLORS['border']};
    border-bottom: 1px solid {COLORS['border']};
    font-weight: 600;
}}

QHeaderView::section:hover {{
    background-color: {COLORS['bg_hover']};
}}

QHeaderView::section:first {{
    border-left: none;
}}

/* ============================================
   SCROLLBARS
   ============================================ */
QScrollBar:vertical {{
    background-color: {COLORS['bg_secondary']};
    width: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['bg_surface']};
    min-height: 30px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['bg_hover']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_secondary']};
    height: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['bg_surface']};
    min-width: 30px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['bg_hover']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ============================================
   TAB WIDGET
   ============================================ */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['bg_secondary']};
    border-radius: 4px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_surface']};
    color: {COLORS['text_secondary']};
    padding: 10px 20px;
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
    min-width: 80px;
}}

QTabBar::tab:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['primary']};
    border-bottom: 2px solid {COLORS['primary']};
    font-weight: 600;
}}

QTabBar::tab:!selected {{
    margin-top: 2px;
}}

/* ============================================
   GROUP BOX
   ============================================ */
QGroupBox {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    color: {COLORS['text_primary']};
    background-color: {COLORS['bg_secondary']};
}}

/* ============================================
   DIALOGS & MESSAGE BOXES
   ============================================ */
QDialog {{
    background-color: {COLORS['bg_primary']};
}}

QMessageBox {{
    background-color: {COLORS['bg_secondary']};
}}

QMessageBox QLabel {{
    color: {COLORS['text_primary']};
}}

QMessageBox QPushButton {{
    min-width: 80px;
}}

/* ============================================
   CHECKBOXES & RADIO BUTTONS
   ============================================ */
QCheckBox {{
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['border']};
    border-radius: 3px;
    background-color: {COLORS['bg_secondary']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['primary']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
    image: url(checkmark.png);
}}

QCheckBox::indicator:disabled {{
    background-color: {COLORS['bg_primary']};
    border-color: {COLORS['text_disabled']};
}}

QRadioButton {{
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['border']};
    border-radius: 9px;
    background-color: {COLORS['bg_secondary']};
}}

QRadioButton::indicator:hover {{
    border-color: {COLORS['primary']};
}}

QRadioButton::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

/* ============================================
   SPIN BOX
   ============================================ */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    padding: 6px;
    border-radius: 4px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {COLORS['border_focus']};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    background-color: {COLORS['bg_surface']};
    border-left: 1px solid {COLORS['border']};
    border-top-right-radius: 3px;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background-color: {COLORS['bg_surface']};
    border-left: 1px solid {COLORS['border']};
    border-bottom-right-radius: 3px;
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {COLORS['bg_hover']};
}}

/* ============================================
   DATE EDIT
   ============================================ */
QDateEdit, QDateTimeEdit {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    padding: 6px;
    border-radius: 4px;
}}

QDateEdit:focus, QDateTimeEdit:focus {{
    border: 2px solid {COLORS['border_focus']};
}}

QCalendarWidget {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
}}

QCalendarWidget QToolButton {{
    background-color: {COLORS['bg_surface']};
    color: {COLORS['text_primary']};
    border: none;
    border-radius: 3px;
    padding: 4px;
}}

QCalendarWidget QToolButton:hover {{
    background-color: {COLORS['primary']};
}}

QCalendarWidget QMenu {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
}}

QCalendarWidget QSpinBox {{
    background-color: {COLORS['bg_surface']};
    color: {COLORS['text_primary']};
}}

/* ============================================
   PROGRESS BAR
   ============================================ */
QProgressBar {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    text-align: center;
    color: {COLORS['text_primary']};
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 3px;
}}

/* ============================================
   TOOLTIP
   ============================================ */
QToolTip {{
    background-color: {COLORS['bg_surface']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 6px;
}}

/* ============================================
   STATUS BAR
   ============================================ */
QStatusBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border']};
}}

/* ============================================
   SPLITTER
   ============================================ */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {COLORS['primary']};
}}

/* ============================================
   TOOLBAR
   ============================================ */
QToolBar {{
    background-color: {COLORS['bg_secondary']};
    border: none;
    padding: 4px;
    spacing: 4px;
}}

QToolButton {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    border: none;
    border-radius: 4px;
    padding: 6px;
}}

QToolButton:hover {{
    background-color: {COLORS['bg_hover']};
}}

QToolButton:pressed {{
    background-color: {COLORS['primary']};
}}

/* ============================================
   LIST WIDGET
   ============================================ */
QListWidget {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
}}

QListWidget::item {{
    padding: 8px;
    border: none;
}}

QListWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}

QListWidget::item:hover {{
    background-color: {COLORS['bg_hover']};
}}

/* ============================================
   TREE WIDGET
   ============================================ */
QTreeWidget {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
}}

QTreeWidget::item {{
    padding: 6px;
}}

QTreeWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}

QTreeWidget::item:hover {{
    background-color: {COLORS['bg_hover']};
}}

QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {{
    image: url(branch-closed.png);
}}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {{
    image: url(branch-open.png);
}}
"""

def get_color(color_key: str) -> str:
    """Get color value by key"""
    return COLORS.get(color_key, '#ffffff')

def get_stat_card_style(color: str) -> str:
    """
    Get inline style for stat cards with specified accent color.
    This ensures stat card values have proper visibility in dark mode.

    Args:
        color: Hex color code for the accent (e.g., '#4da6ff')

    Returns:
        QSS style string for the stat card value label
    """
    return f"font-size: 20px; font-weight: bold; color: {color};"

def get_button_style(bg_color: str, hover_color: str = None, text_color: str = "white") -> str:
    """
    Get inline style for buttons with custom colors.
    Useful for quick action buttons that need specific brand colors.

    Args:
        bg_color: Background color hex code
        hover_color: Hover state color (optional, will darken bg_color if not provided)
        text_color: Text color (default: white)

    Returns:
        QSS style string for the button
    """
    if not hover_color:
        # Darken the background color slightly for hover
        hover_color = bg_color

    return f"""
        background-color: {bg_color};
        color: {text_color};
        padding: 10px;
        border: none;
        border-radius: 4px;
        font-weight: 600;
    """

# Color mappings for dashboard stat cards (optimized for dark mode)
STAT_COLORS = {
    'primary': '#4da6ff',      # Blue
    'success': '#4caf50',      # Green
    'warning': '#ff9800',      # Orange
    'info': '#29b6f6',         # Cyan
    'purple': '#ab47bc',       # Purple
    'error': '#f44336',        # Red
}
