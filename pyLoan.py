import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox, QVBoxLayout
)
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator
from PyQt5.QtCore import Qt

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
        self.setFixedSize(400, 450)
        self.init_ui()

    def init_ui(self):
        font_label = QFont("Segoe UI", 10)
        font_input = QFont("Segoe UI", 10)

        # Group: Loan Parameters
        grp_loan = QGroupBox("Loan Parameters")
        layout_loan = QGridLayout()
        self.edit_down = QLineEdit(); self.edit_down.setValidator(QDoubleValidator(0,1e9,2))
        self.edit_loan = QLineEdit(); self.edit_loan.setValidator(QDoubleValidator(0,1e9,2))
        self.edit_rate = QLineEdit(); self.edit_rate.setValidator(QDoubleValidator(0,100,4))
        self.edit_tenure = QLineEdit(); self.edit_tenure.setValidator(QDoubleValidator(0,100,2))
        for lbl, w, row in [
            ("Downpayment (₹):", self.edit_down, 0),
            ("Total Loan (₹):", self.edit_loan, 1),
            ("Interest Rate (% p.a.):", self.edit_rate, 2),
            ("Tenure (years):", self.edit_tenure, 3),
        ]:
            l = QLabel(lbl); l.setFont(font_label)
            w.setFont(font_input)
            layout_loan.addWidget(l, row, 0)
            layout_loan.addWidget(w, row, 1)
        grp_loan.setLayout(layout_loan)

        # Group: Prepayment
        grp_lump = QGroupBox("Lump-sum Prepayment (optional)")
        layout_lump = QGridLayout()
        self.edit_lump = QLineEdit(); self.edit_lump.setValidator(QDoubleValidator(0,1e9,2))
        self.edit_year = QLineEdit(); self.edit_year.setValidator(QIntValidator(0,100))
        for lbl, w, row in [
            ("Lump sum (₹):", self.edit_lump, 0),
            ("At year (n):", self.edit_year, 1),
        ]:
            l = QLabel(lbl); l.setFont(font_label)
            w.setFont(font_input)
            layout_lump.addWidget(l, row, 0)
            layout_lump.addWidget(w, row, 1)
        grp_lump.setLayout(layout_lump)

        # Calculate button
        btn_calc = QPushButton("Calculate EMI")
        btn_calc.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_calc.setStyleSheet("padding:8px; background:#007ACC; color:white; border-radius:4px;")
        btn_calc.clicked.connect(self.on_calculate)

        # Results
        self.lbl_result = QLabel("")
        self.lbl_result.setFont(QFont("Segoe UI", 10))
        self.lbl_result.setAlignment(Qt.AlignTop)

        # Main layout
        vbox = QVBoxLayout()
        vbox.addWidget(grp_loan)
        vbox.addWidget(grp_lump)
        vbox.addWidget(btn_calc, alignment=Qt.AlignCenter)
        vbox.addWidget(self.lbl_result)
        self.setLayout(vbox)

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

        text = []
        text.append(f"<b>Principal after downpayment:</b> ₹{principal:,.2f}")
        text.append(f"<b>Monthly EMI:</b> ₹{emi:,.2f}")
        text.append(f"<b>Total Payment:</b> ₹{total_pay:,.2f}")
        text.append(f"<b>Total Interest:</b> ₹{total_int:,.2f}")

        # If lump sum applies
        if lump > 0 and 1 <= year_n < tenure:
            new_emi = calculate_new_emi_after_lump(principal, rate, tenure, lump, year_n)
            if new_emi > 0:
                rem_months = int(tenure*12 - year_n*12)
                text.append(f"<br><b>After ₹{lump:,.2f} at year {year_n}:</b>")
                text.append(f"Remaining months: {rem_months}")
                text.append(f"Revised EMI: ₹{new_emi:,.2f}")
            else:
                text.append("<br><b>Your lump-sum fully paid off the remaining loan!</b>")

        self.lbl_result.setText("<br>".join(text))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = EMICalculator()
    win.show()
    sys.exit(app.exec_())
