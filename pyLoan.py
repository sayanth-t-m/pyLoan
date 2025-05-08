import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox, QVBoxLayout, QTabWidget,
    QScrollArea, QFrame
)
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator, QPalette, QColor
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

def calculate_emi(principal, annual_rate, tenure_years):
    monthly_rate = annual_rate / 100 / 12
    total_months = int(tenure_years * 12)
    return principal * monthly_rate * (1 + monthly_rate) ** total_months / ((1 + monthly_rate) ** total_months - 1)

def calculate_outstanding_principal(principal, annual_rate, tenure_years, paid_months):
    monthly_rate = annual_rate / 100 / 12
    total_months = int(tenure_years * 12)
    factor = (1 + monthly_rate) ** total_months
    paid_factor = (1 + monthly_rate) ** paid_months
    return principal * (factor - paid_factor) / (factor - 1)

def calculate_new_emi_after_lump(principal, annual_rate, tenure_years, lump_sum, nth_year):
    paid_months = int(nth_year * 12)
    outstanding = calculate_outstanding_principal(principal, annual_rate, tenure_years, paid_months)
    new_principal = max(0.0, outstanding - lump_sum)
    remaining_months = int(tenure_years * 12) - paid_months
    if remaining_months <= 0 or new_principal == 0:
        return 0.0
    return calculate_emi(new_principal, annual_rate, remaining_months / 12)

class EMICalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EMI Calculator")
        self.setMinimumSize(900, 700)  # Slightly larger for better spacing
        self.setup_dark_theme()
        self.init_ui()

    def setup_dark_theme(self):
        # Set dark theme palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
        self.setPalette(dark_palette)

    def init_ui(self):
        # Style constants
        MAIN_FONT = QFont("Segoe UI", 10)
        HEADER_FONT = QFont("Segoe UI", 12, QFont.Bold)
        
        # Base styles
        self.setStyleSheet("""
            QWidget {
                background-color: #353535;
                color: #FFFFFF;
            }
            QGroupBox {
                border: 2px solid #5A5A5A;
                border-radius: 8px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #5A5A5A;
                border-radius: 4px;
                background-color: #2A2A2A;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #007ACC;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                padding: 10px 20px;
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0098FF;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QTabWidget::pane {
                border: 1px solid #5A5A5A;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #2A2A2A;
                color: #FFFFFF;
                padding: 8px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #007ACC;
            }
            QTabBar::tab:hover:!selected {
                background-color: #404040;
            }
        """)

        # Create main layout with tabs
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        tab_widget = QTabWidget()

        # Input Tab
        input_widget = QWidget()
        input_layout = QVBoxLayout()
        input_layout.setSpacing(15)

        # Title label
        title_label = QLabel("Loan EMI Calculator")
        title_label.setFont(HEADER_FONT)
        title_label.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(title_label)

        # Group: Loan Parameters
        grp_loan = QGroupBox("Loan Parameters")
        grp_loan.setFont(HEADER_FONT)
        layout_loan = QGridLayout()
        layout_loan.setSpacing(10)
        
        self.edit_down = QLineEdit()
        self.edit_loan = QLineEdit()
        self.edit_rate = QLineEdit()
        self.edit_tenure = QLineEdit()
        
        # Set up validators and placeholders
        self.edit_down.setValidator(QDoubleValidator(0,1e9,2))
        self.edit_loan.setValidator(QDoubleValidator(0,1e9,2))
        self.edit_rate.setValidator(QDoubleValidator(0,100,4))
        self.edit_tenure.setValidator(QDoubleValidator(0,100,2))
        
        self.edit_down.setPlaceholderText("Enter downpayment amount")
        self.edit_loan.setPlaceholderText("Enter total loan amount")
        self.edit_rate.setPlaceholderText("Enter interest rate")
        self.edit_tenure.setPlaceholderText("Enter loan duration")

        for lbl, w, row in [
            ("Downpayment (₹):", self.edit_down, 0),
            ("Total Loan (₹):", self.edit_loan, 1),
            ("Interest Rate (% p.a.):", self.edit_rate, 2),
            ("Tenure (years):", self.edit_tenure, 3),
        ]:
            l = QLabel(lbl)
            l.setFont(MAIN_FONT)
            w.setFont(MAIN_FONT)
            layout_loan.addWidget(l, row, 0)
            layout_loan.addWidget(w, row, 1)
        grp_loan.setLayout(layout_loan)

        # Group: Prepayment
        grp_lump = QGroupBox("Lump-sum Prepayment (optional)")
        grp_lump.setFont(HEADER_FONT)
        layout_lump = QGridLayout()
        layout_lump.setSpacing(10)
        
        self.edit_lump = QLineEdit()
        self.edit_year = QLineEdit()
        
        self.edit_lump.setValidator(QDoubleValidator(0,1e9,2))
        self.edit_year.setValidator(QIntValidator(0,100))
        
        self.edit_lump.setPlaceholderText("Enter lump sum amount")
        self.edit_year.setPlaceholderText("Enter year of payment")

        for lbl, w, row in [
            ("Lump sum (₹):", self.edit_lump, 0),
            ("At year (n):", self.edit_year, 1),
        ]:
            l = QLabel(lbl)
            l.setFont(MAIN_FONT)
            w.setFont(MAIN_FONT)
            layout_lump.addWidget(l, row, 0)
            layout_lump.addWidget(w, row, 1)
        grp_lump.setLayout(layout_lump)

        # Calculate button with new styling
        btn_calc = QPushButton("Calculate EMI")
        btn_calc.setFont(HEADER_FONT)
        btn_calc.setCursor(Qt.PointingHandCursor)
        btn_calc.clicked.connect(self.on_calculate)

        # Results area with border
        results_frame = QFrame()
        results_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        results_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #5A5A5A;
                border-radius: 8px;
                padding: 10px;
                background-color: #2A2A2A;
            }
        """)
        results_layout = QVBoxLayout(results_frame)
        self.lbl_result = QLabel("")
        self.lbl_result.setFont(MAIN_FONT)
        self.lbl_result.setAlignment(Qt.AlignTop)
        self.lbl_result.setWordWrap(True)
        results_layout.addWidget(self.lbl_result)

        # Add widgets to input layout
        input_layout.addWidget(grp_loan)
        input_layout.addWidget(grp_lump)
        input_layout.addWidget(btn_calc, alignment=Qt.AlignCenter)
        input_layout.addWidget(results_frame)
        input_widget.setLayout(input_layout)

        # Graphs Tab with dark theme
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout()
        
        # Configure matplotlib dark theme
        plt.style.use('dark_background')
        self.figure = plt.figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #2A2A2A;")
        graphs_layout.addWidget(self.canvas)
        graphs_widget.setLayout(graphs_layout)

        # Add tabs
        tab_widget.addTab(input_widget, "Calculator")
        tab_widget.addTab(graphs_widget, "Graphs")
        
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)

    def plot_graphs(self, principal, rate, tenure, emi, total_pay, total_int, lump=0, year_n=0):
        self.figure.clear()
        
        # Set figure background color
        self.figure.patch.set_facecolor('#2A2A2A')
        
        # Create subplot layout
        gs = self.figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Custom colors for graphs
        colors = ['#007ACC', '#00CC89', '#CC4400', '#CC008B']
        
        # 1. Payment Breakdown Pie Chart
        ax1 = self.figure.add_subplot(gs[0, 0])
        ax1.set_facecolor('#2A2A2A')
        labels = ['Principal', 'Interest']
        sizes = [principal, total_int]
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         startangle=90, colors=colors)
        ax1.set_title('Payment Breakdown', color='white', pad=20)

        # 2. Monthly Payment Schedule
        ax2 = self.figure.add_subplot(gs[0, 1])
        ax2.set_facecolor('#2A2A2A')
        months = np.arange(1, tenure * 12 + 1)
        outstanding = []
        monthly_rate = rate / 100 / 12
        
        for month in months:
            out = calculate_outstanding_principal(principal, rate, tenure, month)
            outstanding.append(out)
        
        ax2.plot(months, outstanding, color=colors[0], linewidth=2)
        ax2.set_title('Outstanding Principal Over Time', color='white', pad=20)
        ax2.set_xlabel('Months', color='white')
        ax2.set_ylabel('Outstanding Amount (₹)', color='white')
        ax2.grid(True, linestyle='--', alpha=0.3)
        ax2.tick_params(colors='white')
        for spine in ax2.spines.values():
            spine.set_color('white')

        # 3. EMI Components Over Time
        ax3 = self.figure.add_subplot(gs[1, :])
        ax3.set_facecolor('#2A2A2A')
        principal_component = []
        interest_component = []
        
        for month in months:
            outstanding_amount = calculate_outstanding_principal(principal, rate, tenure, month-1)
            interest = outstanding_amount * monthly_rate
            principal_part = emi - interest
            principal_component.append(principal_part)
            interest_component.append(interest)

        ax3.stackplot(months, [principal_component, interest_component], 
                     labels=['Principal', 'Interest'], colors=colors[:2])
        ax3.set_title('EMI Components Over Time', color='white', pad=20)
        ax3.set_xlabel('Months', color='white')
        ax3.set_ylabel('Amount (₹)', color='white')
        ax3.legend(facecolor='#2A2A2A', edgecolor='white', labelcolor='white')
        ax3.grid(True, linestyle='--', alpha=0.3)
        ax3.tick_params(colors='white')
        for spine in ax3.spines.values():
            spine.set_color('white')

        # Adjust layout and display
        self.figure.tight_layout()
        self.canvas.draw()

    def on_calculate(self):
        try:
            down = float(self.edit_down.text())
            loan = float(self.edit_loan.text())
            rate = float(self.edit_rate.text())
            tenure = float(self.edit_tenure.text())
            lump = float(self.edit_lump.text() or 0)
            year_n = int(self.edit_year.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values.")
            return

        principal = loan - down
        if principal <= 0:
            QMessageBox.information(self, "Done", "No loan after downpayment.")
            return

        emi = calculate_emi(principal, rate, tenure)
        total_pay = emi * tenure * 12
        total_int = total_pay - principal

        # Update text results
        text = []
        text.append(f"<b>Principal after downpayment:</b> ₹{principal:,.2f}")
        text.append(f"<b>Monthly EMI:</b> ₹{emi:,.2f}")
        text.append(f"<b>Total Payment:</b> ₹{total_pay:,.2f}")
        text.append(f"<b>Total Interest:</b> ₹{total_int:,.2f}")
        text.append(f"<b>Interest to Principal Ratio:</b> {(total_int/principal):,.2%}")

        # If lump sum applies
        if lump > 0 and 1 <= year_n < tenure:
            new_emi = calculate_new_emi_after_lump(principal, rate, tenure, lump, year_n)
            if new_emi > 0:
                rem_months = int(tenure*12 - year_n*12)
                text.append(f"<br><b>After ₹{lump:,.2f} at year {year_n}:</b>")
                text.append(f"Remaining months: {rem_months}")
                text.append(f"Revised EMI: ₹{new_emi:,.2f}")
                old_total = total_pay
                new_total = (emi * year_n * 12) + (new_emi * rem_months) + lump
                savings = old_total - new_total
                text.append(f"Total savings: ₹{savings:,.2f}")
            else:
                text.append("<br><b>Your lump-sum fully paid off the remaining loan!</b>")

        self.lbl_result.setText("<br>".join(text))
        
        # Update graphs
        self.plot_graphs(principal, rate, tenure, emi, total_pay, total_int, lump, year_n)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = EMICalculator()
    win.show()
    sys.exit(app.exec_())
