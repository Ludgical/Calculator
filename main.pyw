import math
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.writing_num1 = True
        self.last_operation_equals = False
        self.current_num_has_dot = False
        self.need_to_write_num = True
        self.label = QLabel()
        self.buttons = (
         (QPushButton("7"),QPushButton("8"),QPushButton("9"),QPushButton("/"),QPushButton("√")),
         (QPushButton("4"),QPushButton("5"),QPushButton("6"),QPushButton("*"),QPushButton("^")),
         (QPushButton("1"),QPushButton("2"),QPushButton("3"),QPushButton("-"),QPushButton("<")),
         (QPushButton("0"),QPushButton("."),QPushButton("="),QPushButton("+"),QPushButton("C"))
        )
        # Y, X   Equals button has its own style sheet (not in this list)
        self.non_num_button_locs=((0, 3),(0, 4),(1, 3),(1, 4),(2, 3),(2, 4),(3, 3),(3, 4))
        self.operators = ("+", "-", "*", "/", "^", "√")
        self.setWindowTitle("Calculator")
        self.init_layout()
        self.init_ui()

    def init_layout(self):
        layout = QVBoxLayout()

        grid = QGridLayout()

        # Initialize and connect buttons
        for y in range(4):
            for x in range(5):
                button: QPushButton = self.buttons[y][x]
                grid.addWidget(button, y, x)
                button.setCursor(QCursor(Qt.PointingHandCursor))
                button.clicked.connect(self.on_button_press)

        layout.addWidget(self.label)
        layout.addLayout(grid)

        self.setLayout(layout)

    def init_ui(self):
        self.label.setAlignment(Qt.AlignVCenter)
        self.label.setAlignment(Qt.AlignRight)

        self.style_sheet()

    def style_sheet(self):
        self.setStyleSheet("""
            Calculator{
                background-color: #ddd;
            }
            QPushButton{
                background-color: #4444ff;
                color: white;
                margin: 13px;
                cursor: hand;
                padding-top: 25px; padding-bottom: 25px;
                padding-right: 37px; padding-left: 37px;
                font-size: 40px;
                font-family: consolas;
                border-radius: 48px;
            }
            QLabel{
                font-size: 80px;
                font-family: consolas;
                color: #111;
            }
            QPushButton:pressed{
                margin: 16px;
                padding: 0px;
                border-radius: 45px;
                font-size: 38px;
            }
        """)

        # Non number buttons
        for x, y in self.non_num_button_locs:
            self.buttons[x][y].setStyleSheet("""
                background-color: #ccc;
                color: #333;
            """)

        # Equals button
        self.buttons[3][2].setStyleSheet("""
            background-color: #aaa;
            color: #222;
        """)

    @staticmethod
    def get_button_type(button_text: str) -> str: # "num", ".", "op", "=", "<", "C"
        if button_text.isdigit():
            return "num"
        elif button_text in ".=C<√":
            return button_text
        return "op"

    def on_button_press(self):
        if self.label.text() == "Error":
            self.on_press_c()
        button_text = self.sender().text()
        button_type = self.get_button_type(button_text)
        if button_type == "num":
            self.on_press_num(button_text)
        elif button_type == ".":
            self.on_press_dot()
        elif button_type == "op":
            self.on_press_op(button_text)
        elif button_type == "√":
            self.on_press_sqrt()
            return
        elif button_type == "=":
            self.on_press_eq()
            return
        elif button_type == "<":
            self.on_press_erase()
        elif button_type == "C":
            self.on_press_c()

    def on_press_num(self, button_text):
        if self.last_operation_equals:
            self.on_press_c()
        self.label.setText(self.label.text() + button_text)
        self.need_to_write_num = False
        self.last_operation_equals = False

    def on_press_dot(self):
        if self.last_operation_equals:
            self.on_press_c()
        if not self.current_num_has_dot:
            self.label.setText(self.label.text() + ".")
        self.current_num_has_dot = True
        self.last_operation_equals = False

    def on_press_op(self, button_text):
        label_text = self.label.text()
        # Return if not allowed to write operator {
        if self.need_to_write_num:
            cond1 = label_text == ""
            try:
                cond2 = label_text[-2].isdigit() or label_text[-2] == "."
            except IndexError:
                cond2 = False
            if not (button_text == "-" and (cond1 or cond2)):
                return
        # }

        # Don't run equals if a negative sign is being written {
        cond1 = label_text == "" and button_text == "-"
        try:
            cond2 = label_text[-1] in self.operators and button_text == "-"
        except IndexError:
            cond2 = False
        if not cond1 and not cond2:
            self.on_press_eq()
        # }

        self.label.setText(self.label.text() + button_text)
        self.need_to_write_num = True
        self.writing_num1 = False
        self.current_num_has_dot = False
        self.last_operation_equals = False

    def on_press_sqrt(self):
        if self.need_to_write_num:
            return
        self.on_press_eq()
        self.label.setText(self.label.text() + "√")
        self.on_press_eq()
        self.writing_num1 = False
        self.current_num_has_dot = False
        self.need_to_write_num = False

    def on_press_eq(self):
        label_text = self.label.text()
        operator = ""
        new_label_text = label_text
        # Find operator and index of it but ignore first letter if case it is "-"
        op_index = 1
        for char in new_label_text[1:]:
            if char in self.operators:
                operator = char
                break
            op_index += 1
        # Split label into num1 and num2
        nums = [new_label_text[:op_index], new_label_text[op_index + 1:]]
        if nums[0] == "Error":
            self.on_press_c()
            return
        if nums[1] == "":
            nums[1] = "0"
        try:
            self.label.setText(self.calc(float(nums[0]), float(nums[1]), operator))
        except ValueError:
            return
        self.last_operation_equals = True
        self.writing_num1 = True

    def on_press_c(self):
        self.label.setText("")
        self.writing_num1 = True
        self.last_operation_equals = False
        self.current_num_has_dot = False
        self.need_to_write_num = True

    def on_press_erase(self):
        removed_char = self.label.text()[-1]
        self.label.setText(self.label.text()[:-1])
        if removed_char == ".":
            self.current_num_has_dot = False
        if removed_char.isdigit() and self.label.text()[-1] in self.operators:
            self.need_to_write_num = True

    def calc(self, num1, num2, operator) -> str:
        try:
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
                    result = num1 **num2
                case "√":
                    result = math.sqrt(num1)
                case _:
                    result = num1
        except ZeroDivisionError:
            print("Dividing by 0")
            self.last_operation_equals = True
            self.need_to_write_num = True
            return "Error"
        except ValueError:
            print("Root of negative number")
            self.last_operation_equals = True
            self.need_to_write_num = True
            return "Error"


        if result.is_integer():
            return str(int(result))

        return str(round(result, 6))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())