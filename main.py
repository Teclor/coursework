from PyQt5 import QtWidgets
from PyQt5.QtCore import QFileInfo, QThread
from PyQt5.QtWidgets import QFileDialog, QDialog, QComboBox

from interface import Ui_MainWindow
import sys
import translator


class TryThread(QThread):

  def new_run(self):
    print("Abstract class")

  def run(self):
    try:
      self.new_run()
    except:
      print ("Ups")

class PreDialog(QDialog):
    def __init__(self, parent=None):                      # + parent
        super(PreDialog, self).__init__(parent)
        combo = QComboBox(self)
        combo.addItem("Apple")
        combo.addItem("Pineapple")
        self.setWindowTitle('Host Parameters')
        self.setModal(True)
        self.line_host = QtWidgets.QLineEdit()
        self.line_user = QtWidgets.QLineEdit()
        self.line_pass = QtWidgets.QLineEdit()
        self.line_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.save = QtWidgets.QPushButton("Сохранить")
        self.spinBox_port = QtWidgets.QSpinBox()
        self.spinBox_port.setProperty("value", 22)
        self.hbox = QtWidgets.QHBoxLayout()
        self.ssh_radio = QtWidgets.QRadioButton("SSH")
        self.telnet_radio = QtWidgets.QRadioButton("Telnet")

        self.hbox.addWidget(self.ssh_radio)
        self.hbox.addWidget(self.telnet_radio)

        self.form = QtWidgets.QFormLayout()
        self.form.setSpacing(20)

        self.form.addRow("&Язык:", combo)
        self.form.addRow("&Host:",self.line_host)
        self.form.addRow("&User:",self.line_user)
        self.form.addRow("&Password:",self.line_pass)
        self.form.addRow("&Port:",self.spinBox_port)
        self.form.addRow("Session:",self.hbox)
        self.form.addRow(self.save)

        self.setLayout(self.form)


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
        self.ui.dictionaries.triggered.connect(self.show_dictionaries_menu)

    def translate(self):
        settings = translator.Settings()
        en = True if (self.ui.langTo.currentIndex() == 1) else False
        tr = translator.Translator(translator.Settings.get_option())
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

    def show_open_file_dialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Откройте файл со словарем', '/', "Файлы XML-словаря (*.xdxf);;Текстовые файлы (*.txt)")[0]
        if fname:
            filename = QFileInfo(fname).baseName()
            f = open(fname, 'r')
            with f:
                data = f.read()
                #textEdit.setText(DICTIONARY)

    def show_error(self, err):
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage("Ошибка: " + str(err))

    def show_dictionaries_menu(self):
        dialog = PreDialog(self.ui.centralWidget)
        dialog.show()

app = QtWidgets.QApplication([])
application = MyWindow()
application.show()
sys.exit(app.exec())

