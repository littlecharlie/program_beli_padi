"""
Context Menu Mixin
Provides reusable context menu functionality for table widgets
"""
from PyQt5.QtWidgets import QMenu, QTableWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QAction, QKeySequence


class TableContextMenuMixin:
    """
    Mixin class to add context menu functionality to table widgets

    Usage:
        class MyScreen(QWidget, TableContextMenuMixin):
            def __init__(self):
                super().__init__()
                self.setup_table_context_menu(self.my_table)
    """

    # Signals for context menu actions
    export_single_pdf = pyqtSignal(int)  # item_id
    export_batch_pdf = pyqtSignal(list)  # list of item_ids
    view_details = pyqtSignal(int)  # item_id
    edit_item = pyqtSignal(int)  # item_id
    delete_item = pyqtSignal(int)  # item_id
    print_receipt = pyqtSignal(int)  # item_id

    def setup_table_context_menu(self, table: QTableWidget, export_enabled: bool = True):
        """
        Setup context menu for table widget

        Args:
            table: QTableWidget instance
            export_enabled: Whether to show export options
        """
        self.table_widget = table
        self.export_enabled = export_enabled

        # Enable custom context menu
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._show_context_menu)

        # Enable multi-selection for batch operations
        table.setSelectionMode(QTableWidget.ExtendedSelection)
        table.setSelectionBehavior(QTableWidget.SelectRows)

    def _show_context_menu(self, position):
        """Show context menu at cursor position"""
        table = self.table_widget
        selected_rows = table.selectionModel().selectedRows()

        if not selected_rows:
            return

        menu = QMenu(table)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #4da6ff;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #4a4a4a;
                margin: 4px 0px;
            }
        """)

        # Get selected item IDs
        selected_ids = []
        for row in selected_rows:
            item = table.item(row.row(), 0)
            if item:
                item_id = item.data(Qt.ItemDataRole.UserRole)
                if item_id:
                    selected_ids.append(item_id)

        if not selected_ids:
            return

        single_selection = len(selected_ids) == 1
        item_id = selected_ids[0] if single_selection else None

        # View action
        if single_selection:
            view_action = QAction("View Details", table)
            view_action.triggered.connect(lambda: self.view_details.emit(item_id))
            menu.addAction(view_action)

        # Edit action
        if single_selection:
            edit_action = QAction("Edit", table)
            edit_action.setShortcut(QKeySequence("Ctrl+E"))
            edit_action.triggered.connect(lambda: self.edit_item.emit(item_id))
            menu.addAction(edit_action)

        menu.addSeparator()

        # PDF Export actions
        if self.export_enabled:
            if single_selection:
                export_pdf_action = QAction("Export as PDF", table)
                export_pdf_action.setShortcut(QKeySequence("Ctrl+P"))
                export_pdf_action.triggered.connect(lambda: self.export_single_pdf.emit(item_id))
                menu.addAction(export_pdf_action)
            else:
                export_batch_action = QAction(f"Export {len(selected_ids)} items as PDF", table)
                export_batch_action.triggered.connect(lambda: self.export_batch_pdf.emit(selected_ids))
                menu.addAction(export_batch_action)

        # Print receipt action
        if single_selection:
            print_action = QAction("Print Receipt", table)
            print_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
            print_action.triggered.connect(lambda: self.print_receipt.emit(item_id))
            menu.addAction(print_action)

        menu.addSeparator()

        # Delete action
        if single_selection:
            delete_action = QAction("Delete", table)
            delete_action.setShortcut(QKeySequence.Delete)
            delete_action.triggered.connect(lambda: self.delete_item.emit(item_id))
            menu.addAction(delete_action)
        else:
            delete_batch_action = QAction(f"Delete {len(selected_ids)} items", table)
            delete_batch_action.triggered.connect(lambda: self._handle_batch_delete(selected_ids))
            menu.addAction(delete_batch_action)

        # Show menu at cursor position
        menu.exec(table.viewport().mapToGlobal(position))

    def _handle_batch_delete(self, item_ids: list):
        """Handle batch delete (override in subclass)"""
        # This should be overridden in the actual screen class
        print(f"Batch delete requested for {len(item_ids)} items")


class ExportToolbarMixin:
    """
    Mixin class to add export toolbar to screens

    Provides a toolbar with export-related buttons
    """

    def create_export_toolbar(self):
        """Create toolbar with export buttons"""
        from PyQt5.QtWidgets import QToolBar, QToolButton
        from PyQt5.QtCore import QSize

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2d2d2d;
                border: none;
                padding: 4px;
                spacing: 4px;
            }
            QToolButton {
                background-color: transparent;
                color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 6px;
            }
            QToolButton:hover {
                background-color: #404040;
            }
            QToolButton:pressed {
                background-color: #4da6ff;
            }
        """)

        # Export Selected button
        export_selected_btn = QToolButton()
        export_selected_btn.setText("Export Selected")
        export_selected_btn.setToolTip("Export selected items to PDF (Ctrl+P)")
        toolbar.addWidget(export_selected_btn)

        # Export All button
        export_all_btn = QToolButton()
        export_all_btn.setText("Export All")
        export_all_btn.setToolTip("Export all items to PDF")
        toolbar.addWidget(export_all_btn)

        toolbar.addSeparator()

        # Export Filtered button
        export_filtered_btn = QToolButton()
        export_filtered_btn.setText("Export Filtered")
        export_filtered_btn.setToolTip("Export current filtered results to PDF")
        toolbar.addWidget(export_filtered_btn)

        return toolbar, export_selected_btn, export_all_btn, export_filtered_btn
