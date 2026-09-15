"""
UltraScrape - Estilos y Tema Visual QSS (Modern Cyber-Dark)
"""

DARK_THEME_QSS = """
/* Reset y fondo general */
QWidget {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

/* Encabezados y Labels */
QLabel {
    color: #94A3B8;
    background-color: transparent;
}
QLabel#titleLabel {
    color: #38BDF8;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
QLabel#subtitleLabel {
    color: #64748B;
    font-size: 12px;
}
QLabel#sectionHeader {
    color: #E2E8F0;
    font-size: 14px;
    font-weight: 600;
    padding-top: 6px;
    padding-bottom: 2px;
}

/* Campos de entrada */
QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #0284C7;
}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #38BDF8;
    background-color: #1E293B;
}

/* ComboBox */
QComboBox {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 5px 12px;
    min-height: 24px;
}
QComboBox:hover {
    border: 1px solid #475569;
}
QComboBox QAbstractItemView {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    selection-background-color: #0284C7;
}

/* Botones Principales */
QPushButton {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
}
QPushButton:pressed {
    background-color: #0F172A;
}

/* Botón Iniciar (Verde Esmeralda) */
QPushButton#startBtn {
    background-color: #059669;
    color: #FFFFFF;
    border: 1px solid #10B981;
    font-size: 14px;
    font-weight: 700;
    padding: 9px 20px;
}
QPushButton#startBtn:hover {
    background-color: #10B981;
}
QPushButton#startBtn:disabled {
    background-color: #1E293B;
    color: #64748B;
    border-color: #334155;
}

/* Botón Pausar (Ámbar) */
QPushButton#pauseBtn {
    background-color: #D97706;
    color: #FFFFFF;
    border: 1px solid #F59E0B;
    font-weight: 600;
    padding: 8px 16px;
}
QPushButton#pauseBtn:hover {
    background-color: #F59E0B;
}

/* Botón Detener (Rojo Carmesí) */
QPushButton#stopBtn {
    background-color: #DC2626;
    color: #FFFFFF;
    border: 1px solid #EF4444;
    font-weight: 600;
    padding: 8px 16px;
}
QPushButton#stopBtn:hover {
    background-color: #EF4444;
}

/* Botón Secundario / Acento */
QPushButton#accentBtn {
    background-color: #0284C7;
    color: #FFFFFF;
    border: 1px solid #38BDF8;
}
QPushButton#accentBtn:hover {
    background-color: #0369A1;
}

/* CheckBox */
QCheckBox {
    color: #E2E8F0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #1E293B;
}
QCheckBox::indicator:checked {
    background-color: #0284C7;
    border-color: #38BDF8;
}

/* Tablas */
QTableWidget {
    background-color: #0F172A;
    gridline-color: #1E293B;
    border: 1px solid #1E293B;
    border-radius: 6px;
    color: #F8FAFC;
    selection-background-color: #0369A1;
}
QHeaderView::section {
    background-color: #1E293B;
    color: #94A3B8;
    padding: 6px 10px;
    border: none;
    border-right: 1px solid #334155;
    border-bottom: 2px solid #0284C7;
    font-weight: 600;
}

/* Pestañas (QTabWidget) */
QTabWidget::pane {
    border: 1px solid #1E293B;
    background-color: #0F172A;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #1E293B;
    color: #94A3B8;
    padding: 8px 18px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #0F172A;
    color: #38BDF8;
    font-weight: 600;
    border-top: 2px solid #38BDF8;
}

/* Barra de Progreso */
QProgressBar {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    text-align: center;
    color: #F8FAFC;
    font-weight: 600;
    height: 18px;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #10B981);
    border-radius: 5px;
}

/* ScrollBar */
QScrollBar:vertical {
    background: #0F172A;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
QScrollBar:horizontal {
    background: #0F172A;
    height: 10px;
}
QScrollBar::handle:horizontal {
    background: #334155;
    border-radius: 4px;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: 600;
    color: #94A3B8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    background-color: #0F172A;
    color: #38BDF8;
}
"""
