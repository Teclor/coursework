from PyQt5 import QtWidgets
from interface import Ui_MainWindow
import sys
import sqlite3 as sql
from sql_translate import search_translation

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.QuitBtn.clicked.connect(QtWidgets.QApplication.instance().quit)
        self.ui.translateBtn.clicked.connect(self.translate)
        
    def translate(self):
        in_text = self.ui.input.text()
        if in_text:
            out_text = search_translation(str(in_text))
            if out_text:
                self.ui.output.setText("Перевод слова: " + out_text)
            else:
                self.ui.output.setText("Вы ввели неверное значение.\nПожалуйста, проверьте введённые данные и попробуйте ещё раз.")


app = QtWidgets.QApplication([])
application = MyWindow()
application.show()

sys.exit(app.exec())
