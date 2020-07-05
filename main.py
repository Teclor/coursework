from PyQt5 import QtWidgets
from PyQt5.QtCore import QFileInfo, QThread, QSize
from PyQt5.QtWidgets import QFileDialog, QDialog, QComboBox, QGridLayout

from interface import Ui_MainWindow
import sys
import translator


class DictDialog(QDialog):
    def __init__(self, parent=None):                      # + parent
        super(DictDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle('Выбор словаря')
        layout = QGridLayout()
        ru_en_dict_combo = QComboBox(self)
        en_ru_dict_combo = QComboBox(self)
        db = translator.DB()
        db_tables = db.get_tables()
        for table in db_tables:
            table = str(table)
            lang = table.split("_")[0]
            if lang == "rus":
                ru_en_dict_combo.addItem(table)
            elif lang == "en":
                en_ru_dict_combo.addItem(table)
        self.save = QtWidgets.QPushButton("Сохранить")
        self.decline = QtWidgets.QPushButton("Отмена")
        ru_label = QtWidgets.QLabel(self)
        ru_label.setText("Выберите словарь для русско-английского перевода:")
        ru_label.setWordWrap(True)
        en_label = QtWidgets.QLabel(self)
        en_label.setText("Выберите словарь для англо-русского перевода:")
        en_label.setWordWrap(True)
        elements = [ru_label, ru_en_dict_combo,
                    en_label, en_ru_dict_combo,
                    self.save, self.decline]
        positions = [(i, j) for i in range(3) for j in range(2)]
        for position, element in zip(positions, elements):
            layout.addWidget(element, *position)
        self.setLayout(layout)
        self.resize(QSize(300, 150))


class TrMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(TrMainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.translateBtn.clicked.connect(self.translate)
        self.ui.output.setReadOnly(True)
        self.ui.input.setPlaceholderText("Введите слова для перевода")
        self.ui.output.setPlaceholderText("Перевод")
        self.ui.langFrom.currentIndexChanged.connect(self.change_lang)
        self.ui.langTo.currentIndexChanged.connect(self.change_lang)
        self.ui.dictionaries.triggered.connect(self.show_dictionaries_menu)
        self.ui.load.triggered.connect(self.show_open_file_dialog)

    def translate(self):
        settings = translator.Settings()
        tr = translator.Translator(settings.get_option("dictionary"))
        in_text = self.ui.input.toPlainText()
        if in_text:
            out_text = tr.translate(str(in_text))
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
        file = QFileDialog.getOpenFileName(self, 'Откройте файл со словарем', '/', "Файлы XML-словаря (*.xdxf);;Текстовые файлы (*.txt)")[0]
        if file:
            file_name = QFileInfo(file).baseName()
            file_ext = QFileInfo(file).suffix()
            if file_ext == "xdxf":
                parser = translator.Parser()
            f = open(file, 'r')
            with f:
                data = f.read()
                #textEdit.setText(DICTIONARY)

    def show_dictionaries_menu(self):
        dialog = DictDialog(self)
        dialog.show()


    def app_excepthook(self, type, value, tback):
        QtWidgets.QMessageBox.critical(
            self, "Ошибка", str(value),
            QtWidgets.QMessageBox.Ok
        )

        sys.__excepthook__(type, value, tback)


app = QtWidgets.QApplication([])
application = TrMainWindow()
sys.excepthook = application.app_excepthook
application.show()
sys.exit(app.exec())

