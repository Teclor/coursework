from PyQt5 import QtWidgets
from PyQt5.QtCore import QFileInfo, QSize
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QDialog, QComboBox, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QProgressBar

from interface import Ui_MainWindow
import sys
import translator


class DictDialog(QDialog):
    def __init__(self, parent=None):
        super(DictDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle('Выбор словаря')

        self.main_layout = QVBoxLayout()
        self.choose_layout = QGridLayout()
        self.load_layout = QHBoxLayout()
        self.delete_layout = QHBoxLayout()
        self.ru_en_dict_combo = QComboBox(self)
        self.en_ru_dict_combo = QComboBox(self)
        self.load_combo = QComboBox(self)
        self.delete_combo = QComboBox(self)
        self.ru_label = QLabel(self)
        self.en_label = QLabel(self)
        self.load_label = QLabel(self)
        self.delete_label = QLabel(self)
        self.load_btn = QtWidgets.QPushButton("Добавить словарь")
        self.progress = QProgressBar(self)
        self.save = QPushButton("Сохранить")
        self.decline = QPushButton("Отмена")
        self.delete_btn = QPushButton("Удалить")
        self.delete_combo.addItem("Не выбран")
        self.load_combo.addItems(["Русско-английский", "Англо-русский"])
        self.load_layout.addWidget(self.load_btn)
        self.load_layout.addWidget(self.progress)
        self.load_layout.addWidget(self.load_combo)
        self.delete_layout.addWidget(self.delete_combo)
        self.delete_label.setText("Выберите словарь для удаления")
        self.load_label.setText("Выберите словарь для загрузки.")
        self.load_label.setAlignment(Qt.AlignCenter)
        self.delete_label.setAlignment(Qt.AlignCenter)
        self.delete_label.setWordWrap(True)
        self.delete_layout.addWidget(self.delete_btn)
        db = translator.DB()
        db_tables = db.get_tables()

        for table in db_tables:
            table = str(table)
            lang = table.split("_")[0]
            if lang == "rus":
                self.ru_en_dict_combo.addItem(table)
            elif lang == "en":
                self.en_ru_dict_combo.addItem(table)
            self.delete_combo.addItem(table)

        self.ru_label.setText("Выберите словарь для русско-английского перевода:")
        self.ru_label.setWordWrap(True)
        self.en_label.setText("Выберите словарь для англо-русского перевода:")
        self.en_label.setWordWrap(True)
        elements = [self.ru_label, self.ru_en_dict_combo,
                    self.en_label, self.en_ru_dict_combo,
                    self.save, self.decline]
        positions = [(i, j) for i in range(3) for j in range(2)]
        for position, element in zip(positions, elements):
            self.choose_layout.addWidget(element, *position)

        self.main_layout.addLayout(self.choose_layout)
        self.main_layout.addWidget(self.load_label)
        self.main_layout.addLayout(self.load_layout)
        self.main_layout.addWidget(self.delete_label)
        self.main_layout.addLayout(self.delete_layout)
        self.setLayout(self.main_layout)
        self.resize(QSize(300, 150))

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.load_btn.clicked.connect(self.show_open_file_dialog)
        self.decline.clicked.connect(self.close)

    def show_open_file_dialog(self):
        file = QFileDialog.getOpenFileName(self, 'Откройте файл со словарем', '/', "Файлы XML-словаря (*.xdxf);;Текстовые файлы (*.txt)")[0]
        if file:
            file_name = QFileInfo(file).baseName()
            file_ext = QFileInfo(file).suffix()
            parser = translator.Parser()
            print(file_ext)
            if file_ext == "xdxf" or "XDXF":
                parser.parse_xdxf(file, self.progress)
            elif file_ext == "TXT" or "txt":
                parser.parse_txt(file, self.progress)


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
        self.ui.help_quit.triggered.connect(self.close)

    def translate(self):
        tr = translator.Translator()
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
        settings = translator.Settings()
        if from_combo.currentIndex() == 0:
            settings.set_option("language/from", "en")
            settings.set_option("language/to", "ru")
        else:
            settings.set_option("language/from", "ru")
            settings.set_option("language/to", "en")

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

