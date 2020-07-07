import traceback

from PyQt5 import QtWidgets
from PyQt5.QtCore import QFileInfo, QSize, QCoreApplication
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QDialog, QComboBox, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QMessageBox

from interface import Ui_MainWindow
import sys
import translator


class DictDialog(QDialog):
    def __init__(self, parent=None):
        """
        Modal window with settings
        :param object parent:
        """
        super(DictDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle('Выбор словаря')
        self.db = translator.DB()
        self.settings = translator.Settings()
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
        self.set_dictionaries_lists()

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
        self.save.clicked.connect(self.save_preferences)
        self.load_btn.clicked.connect(self.show_open_file_dialog)
        self.delete_btn.clicked.connect(self.delete_dictionary)
        self.decline.clicked.connect(self.close)

    def set_dictionaries_lists(self):
        """
        Gets and sets to comboboxes lists of dictionaries
        :return:
        """
        db_tables = self.db.get_tables()
        self.ru_en_dict_combo.clear()
        self.en_ru_dict_combo.clear()
        self.delete_combo.clear()
        self.delete_combo.addItem("Не выбран")
        if db_tables is not False:
            for table in db_tables:
                table = str(table[0])
                lang = table.split("_")[0]
                if lang == "ru":
                    self.ru_en_dict_combo.addItem(table)
                elif lang == "en":
                    self.en_ru_dict_combo.addItem(table)
                self.delete_combo.addItem(table)
        if db_tables is not False:
            self.en_ru_dict_combo.setCurrentText(self.settings.get_option("dictionary/en"))
            self.ru_en_dict_combo.setCurrentText(self.settings.get_option("dictionary/ru"))

    def show_open_file_dialog(self):
        """
        Opens and parses file
        :return null:
        """
        file = QFileDialog.getOpenFileName(self, 'Откройте файл со словарем', '/', "Файлы XML-словаря (*.xdxf);;Текстовые файлы (*.txt)")[0]
        if file:
            file_name = QFileInfo(file).baseName()
            file_ext = QFileInfo(file).suffix()
            parser = translator.Parser()
            lang = "ru" if self.load_combo.currentIndex() == 0 else "en"
            if file_ext == "xdxf" or file_ext == "XDXF":
                parser.parse_xdxf(file, lang , file_name, self.progress)
            elif file_ext == "TXT" or file_ext == "txt":
                parser.parse_txt(file, lang, file_name, self.progress)
            QMessageBox.question(self, 'Успех', "Словарь добавлен!", QMessageBox.Ok)
            self.progress.setValue(0)
            self.set_dictionaries_lists()

    def delete_dictionary(self):
        """
        A wrapper for DB.delete_table()
        :return:
        """
        table = self.delete_combo.currentText()
        self.db.delete_table(table)
        if table == self.settings.get_dictionary():
            self.settings.set_default_options()
        QMessageBox.question(self, 'Информация', "Словарь удалён!", QMessageBox.Ok)
        self.set_dictionaries_lists()

    def save_preferences(self):
        """
        Saves chosen settings
        :return:
        """
        self.settings.set_option("dictionary/ru", self.ru_en_dict_combo.currentText())
        self.settings.set_option("dictionary/en", self.en_ru_dict_combo.currentText())
        self.close()


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
        self.ui.about.triggered.connect(self.show_about_app)
        self.ui.creator.triggered.connect(self.show_about_developer)
        self.settings = translator.Settings()
        self.ui.langFrom.setCurrentIndex(0 if self.settings.get_option("language/from") == "en" else 1)

    def translate(self):
        """
        Starts translation
        :return null:
        """
        tr = translator.Translator()
        in_text = self.ui.input.toPlainText()
        if in_text:
            out_text = tr.translate(str(in_text))
            if out_text:
                self.ui.output.setPlainText(str(out_text))
            else:
                self.ui.output.setPlainText("Перевод не найден.\nПожалуйста, проверьте введённые данные и попробуйте ещё раз.")

    def change_lang(self, index):
        """
        Changes langFrom and langTo values
        :param int index: new index
        :return:
        """
        sender = self.sender()
        from_combo = self.ui.langFrom
        to_combo = self.ui.langTo
        if sender == from_combo and to_combo != index:
            to_combo.setCurrentIndex(index)
        if sender == to_combo and from_combo != index:
            from_combo.setCurrentIndex(index)
        if from_combo.currentIndex() == 0:
            self.settings.set_option("language/from", "en")
            self.settings.set_option("language/to", "ru")
        else:
            self.settings.set_option("language/from", "ru")
            self.settings.set_option("language/to", "en")

    def show_dictionaries_menu(self):
        """
        Opens settings menu
        :return:
        """
        dialog = DictDialog(self)
        dialog.show()

    def show_about_app(self):
        text = ("Версия: " + QCoreApplication.applicationVersion() +
           "\nНазвание: " + QCoreApplication.applicationName() +
            "\nПомощь: \nПеревод: приложение может перевести как отдельные слова, так и комбинации различных слов (в основном в изначальной форме, т.е. инфинитивы, имен. падеж и т.д."
            "\nДобавление словаря: чтобы загрузить словарь нужно сначала выбрать его тип, затем нажать \"добавить словарь\". Поддерживаются только xdxf словари и только приведённые к нужному виду txt."
            "\nTXT словарь должен содержать на первой своей строке слово на языке с которого идет перевод, на второй сам перевод и сохранять данную последовательность до конца файла."
            "\nПеред добавлением нового словаря с существующим названием настоятельно рекомендуется удалить старый."
            "\nУдаление словаря: чтобы удалить словарь, достаточно выбрать его из списка и нажать кнопку удалить."
            "\nВыбор словарей: для того чтобы сохранить выбор словарей достаточно выбрать их из списка и нажать кнопку \"Сохранить\"" )
        QMessageBox.question(self, 'О приложении', text, QMessageBox.Ok)

    def show_about_developer(self):
        QMessageBox.question(self, 'О разработчике', 'Приложение разработал: \nСтудент института ИМИТ ВолГУ Бондаренко А.А.', QMessageBox.Ok)

    def app_excepthook(self, type, value, tback):
        """
        Allows to show exceptions in app
        :param type:
        :param value:
        :param tback:
        :return:
        """
        QtWidgets.QMessageBox.critical(
            self, "Ошибка", str(value),
            QtWidgets.QMessageBox.Ok
        )
        sys.__excepthook__(type, value, tback)
        with open("error.log", "a") as lf:
            lf.write(str(type) + str(value) + str(traceback.format_tb(tback)) + "\n")


app = QtWidgets.QApplication([])
application = TrMainWindow()
sys.excepthook = application.app_excepthook
application.show()
sys.exit(app.exec())

