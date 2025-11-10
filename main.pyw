import math
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.current_num_has_dot = False
        self.need_to_write_num = True
        self.need_to_write_op = False
        self.memory = 0
        self.label = QLabel()
        self.label.setObjectName('label')
        self.error_label = QLabel()
        self.error_label.setObjectName('error_label')
        self.buttons = (
         (QPushButton("7"),QPushButton("8"),QPushButton("9"),QPushButton("/"),QPushButton("√"),QPushButton("M+")),
         (QPushButton("4"),QPushButton("5"),QPushButton("6"),QPushButton("*"),QPushButton("^"),QPushButton("M-")),
         (QPushButton("1"),QPushButton("2"),QPushButton("3"),QPushButton("-"),QPushButton("←"),QPushButton("MR")),
         (QPushButton("0"),QPushButton("."),QPushButton("="),QPushButton("+"),QPushButton("C"),QPushButton("MC"))
        )
        # X, Y   Equals button has its own style sheet (not in this list)
        self.non_num_button_locs=[(x, y) for x in range(3, 5) for y in range(0, 4)]
        self.mem_button_locs = [(5, y) for y in range(0, 4)]

        self.operators = ("+", "-", "*", "/", "^", "√")
        self.setWindowTitle("Calculator")
        self.init_layout()
        self.init_ui()

    def init_layout(self):
        layout = QVBoxLayout()

        grid = QGridLayout()

        # Initialize and connect buttons
        for x in range(6):
            for y in range(4):
                button: QPushButton = self.buttons[y][x]
                grid.addWidget(button, y, x)
                button.setCursor(QCursor(Qt.PointingHandCursor))
                button.clicked.connect(self.on_button_press)

        layout.addWidget(self.label)
        layout.addWidget(self.error_label)
        layout.addLayout(grid)

        self.setLayout(layout)

    def init_ui(self):
        self.label.setAlignment(Qt.AlignRight)
        self.error_label.setAlignment(Qt.AlignRight)

        self.style_sheet()

    def style_sheet(self):
        with open("style.css") as file:
            css = file.read()
        self.setStyleSheet(css)

        # Non number buttons
        for x, y in self.non_num_button_locs:
            self.buttons[y][x].setStyleSheet("""
                background-color: #ccc;
                color: #333;
            """)

        for x, y in self.mem_button_locs:
            self.buttons[y][x].setStyleSheet("""
                background-color: #ccc;
                color: #333;
                padding-top: 25px; padding-bottom: 25px;
                padding-right: 26px; padding-left: 26px;
            """)

        # Equals button
        self.buttons[3][2].setStyleSheet("""
            background-color: #aaa;
            color: #222;
        """)

    @staticmethod
    def get_button_type(button_text: str) -> str:
        if button_text.isdigit():
            return "num"
        elif button_text in (".", "=", "←", "C", "√", "M+", "M-", "MR", "MC"):
            return button_text
        return "op"

    def on_button_press(self):
        if self.label.text() == "Error":
            self.on_press_c()

        button_text = self.sender().text()
        button_type = self.get_button_type(button_text)

        match button_type:
            case "num":
                self.on_press_num(button_text)
            case ".":
                self.on_press_dot()
            case "op":
                self.on_press_op(button_text)
            case "√":
                self.on_press_sqrt()
            case "=":
                self.on_press_eq()
            case "M+":
                self.on_press_m_plus()
            case "M-":
                self.on_press_m_minus()
            case "MR":
                self.on_press_m_r()
            case "MC":
                self.on_press_m_c()
            case "←":
                self.on_press_erase()
            case "C":
                self.on_press_c()

    def on_press_num(self, button_text):
        if self.need_to_write_op:
            self.on_press_c()
        self.label.setText(self.label.text() + button_text)
        self.need_to_write_num = False
        self.need_to_write_op = False

    def on_press_dot(self):
        if self.need_to_write_op:
            self.on_press_c()
        if not self.current_num_has_dot:
            self.label.setText(self.label.text() + ".")
        self.current_num_has_dot = True
        self.need_to_write_op = False

    def on_press_op(self, button_text):
        text = self.label.text()
        # Return if not allowed to write operator
        if self.need_to_write_num:
            cond1 = text == ""
            try:
                cond2 = text[-2].isdigit() or text[-2] == "."
            except IndexError:
                cond2 = False
            if button_text != "-" or (not cond1 and not cond2):
                return

        # Don't run equals if a negative sign is being written {
        cond1 = text == "" and button_text == "-"
        try:
            cond2 = text[-1] in self.operators and button_text == "-"
        except IndexError:
            cond2 = False
        if not cond1 and not cond2:
            self.on_press_eq()
        if self.label.text() == "Error":
            return
        self.label.setText(self.label.text() + button_text)
        self.need_to_write_num = True
        self.current_num_has_dot = False
        self.need_to_write_op = False

    def on_press_sqrt(self):
        if self.need_to_write_num:
            return
        self.on_press_eq()
        if self.label.text() == "Error":
            return
        self.label.setText(self.label.text() + "√")
        self.on_press_eq()
        self.current_num_has_dot = False
        self.need_to_write_num = False

    def on_press_eq(self):
        text = self.label.text()
        if text == "Error":
            self.on_press_c()
            return

        op_index = self.get_op_index()
        operator = text[op_index] if op_index < len(text) else ""

        # Split label into num1 and num2
        num1, num2 = text[:op_index], text[op_index + 1:]

        self.label.setText(self.calc(num1, num2, operator))

        self.need_to_write_op = True

    def on_press_m_plus(self):
        self.on_press_eq()
        text = self.label.text()
        if text == "":
            return
        self.memory += float(text)

    def on_press_m_minus(self):
        text = self.label.text()
        if text == "":
            return
        self.memory -= float(text)

    def on_press_m_r(self):
        text = self.label.text()

        if len(text) > 0 and text[-1] not in self.operators:
            self.on_press_c()

        if self.memory.is_integer():
            memory = str(int(self.memory))
        else:
            memory = str(self.memory)

        for num in memory:
            if num.isdigit():
                self.on_press_num(num)
            elif num == ".":
                self.on_press_dot()
            elif num == "-":
                if text.endswith("--"):
                    self.label.setText(text[:-2])
                self.on_press_op("-")
            else:
                self.error_label.setText("Memory Error")
                self.on_press_c()

        self.need_to_write_op = True

    def on_press_m_c(self):
        self.memory = 0.0

    def on_press_c(self):
        self.label.setText("")
        self.error_label.setText("")
        self.current_num_has_dot = False
        self.need_to_write_num = True
        self.need_to_write_op = False

    def on_press_erase(self):
        text = self.label.text()
        length = len(text)
        if length == 0:
            return

        if self.need_to_write_op:
            # Wrote memory, erase removes whole last number
            op_index = self.get_op_index()
            if op_index == len(text):
                self.on_press_c()
            else:
                self.label.setText(text[:op_index + 1])
            self.need_to_write_num = True
            self.need_to_write_op = False
            self.current_num_has_dot = False
            return

        removed_char = text[-1]
        self.label.setText(text[:-1])
        if removed_char == ".":
            self.current_num_has_dot = False
        if length == 1 or (removed_char.isdigit() and self.label.text()[-1] in self.operators):
            self.need_to_write_num = True

    def get_op_index(self) -> int:
        # Find operator and index of it but ignore first letter in case it is "-"
        op_index = 1
        for char in self.label.text()[1:]:
            if char in self.operators:
                return op_index
            op_index += 1
        return len(self.label.text())

    def calc(self, num1, num2, operator) -> str:
        if num2 == "" and operator != "√":
            return num1
        num1 = float(num1)
        if num2 != "":
            num2 = float(num2)

        try:
            result = None
            match operator:
                case "+":
                    result = num1 + num2
                case "-":
                    result = num1 - num2
                case "*":
                    result = num1 * num2
                case "/":
                    result = num1 / num2
                case "^":
                    result = num1 ** num2
                case "√":
                    result = math.sqrt(num1)
                case _:
                    result = num1

        except ZeroDivisionError:
            self.error_label.setText("Dividing by 0")
            self.need_to_write_num = True
            return "Error"
        except ValueError:
            self.error_label.setText("Root of negative number")
            self.need_to_write_num = True
            return "Error"
        except Exception as e:
            print(e)
            return "Error"

        if result.is_integer():
            return str(int(result))

        return str(round(result, 6))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())
