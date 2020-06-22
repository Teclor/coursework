from PyQt5 import QtWidgets
from interface import Ui_MainWindow
import sys
import translator

DICTIONARY = "rus_dict"


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.translateBtn.clicked.connect(self.translate)
        self.ui.output.setReadOnly(True)
        self.ui.input.setPlaceholderText("Введите слова для перевода")
        self.ui.output.setPlaceholderText("Перевод")
        self.ui.langFrom.currentIndexChanged.connect(self.change_lang)
        self.ui.langTo.currentIndexChanged.connect(self.change_lang)
        

    def translate(self):
        en = True if (self.ui.langTo.currentIndex() == 1) else False
        tr = translator.Translator(DICTIONARY)
        in_text = self.ui.input.toPlainText()
        if in_text:
            out_text = tr.translate(str(in_text), en)
            if out_text:
                self.ui.output.setPlainText(str(out_text))
            else:
                self.ui.output.setPlainText("Перевод не найден.\nПожалуйста, проверьте введённые данные и попробуйте ещё раз.")

    def change_lang(self, index):
        sender = self.sender()
        from_combo = self.ui.langFrom
        to_combo = self.ui.langTo
        if sender == from_combo and to_combo != index:
            to_combo.setCurrentIndex(index)
        if sender == to_combo and from_combo != index:
            from_combo.setCurrentIndex(index)


app = QtWidgets.QApplication([])
application = MyWindow()
application.show()

sys.exit(app.exec())
