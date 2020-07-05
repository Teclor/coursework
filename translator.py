import sqlite3 as sql
import re

from PyQt5.QtCore import QCoreApplication, QSettings


class DB:
    def __new__(cls):
        """
        Checks the existence of class instance
        :return: instance of DB
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(DB, cls).__new__(cls)
        return cls.instance

    def __init__(self, db_name="dictionary"):
        db_path = "resource\\db\\" + db_name + ".db"
        self.conn = sql.connect(db_path)
        settings = Settings()
        self.DICT = settings.get_option("dictionary")
        self.db = self.conn.cursor()

    def create_table(self):
        self.db = self.conn.cursor()
        self.db.execute("CREATE TABLE IF NOT EXISTS" + self.DICT + " (ID INT NOT NULL AUTO_INCREMENT, word text NOT NULL, translation text NOT NULL)")

    def insert_translation(self, word, translation):
        cmd = "INSERT INTO {t} (word, translation) VALUES (?,?)"
        cmd = cmd.format(t=self.DICT)
        self.db.execute(cmd, (word, translation))

    def search_translation(self, word):
        cmd = "SELECT translation FROM {table} WHERE word LIKE ?"
        cmd = cmd.format(table=self.DICT)
        self.db.execute(cmd, (word.lower(),))
        result = self.db.fetchall()
        if result:
            return str((result[0][0]))
        else:
            return False

    def get_tables(self):
        self.db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        return self.db.fetchall()[0]

    def delete_table(self, table_name):
        if table_name is not 'rus_eng' or 'eng_rus':
            cmd = "DROP TABLE IF EXISTS {table}"
            cmd = cmd.format(table=table_name)
            self.db.execute(cmd)

    def __del__(self):
        self.conn.close()


class Parser(DB):

    def parse_xdxf(self):
        with open('resource/raw/' + self.DICT + '.xdxf', encoding="utf-8") as fin:
            text = fin.read()
        self.create_table()
        match = re.findall('<ar>.*?</ar>', text, flags=re.DOTALL)  # ленивый квантификатор
        for m in match:
            m = re.sub("<ar>|</ar>|<k>", "", m)
            m = re.split(r"</k>\n", m)
            if m[0] and m[1]:
                self.insert_translation(m[0], m[1])
        self.conn.commit()

    def parse_txt(self):
        with open('resource/raw/' + self.DICT + '.txt', encoding="utf-8") as fin:
            text = fin.read()
        self.create_table()
        match = re.findall('<ar>.*?</ar>', text, flags=re.DOTALL)  # ленивый квантификатор
        for m in match:
            m = re.sub("<ar>|</ar>|<k>", "", m)
            m = re.split(r"</k>\n", m)
            if m[0] and m[1]:
                self.insert_translation(m[0], m[1])
        self.conn.commit()


"""
Class containing translation methods
"""


class Translator(DB):

    def get_lang(self):
        return self.DICT.split("_")[0]

    def translate(self, text):
        """
        A method to choose which type of translation we need: full translation of a word or translation of a text
        :param text: string input text
        :return: string translation
        """
        check = re.findall(r"\b(?:\w+-?)\b", text, flags=re.DOTALL)
        cnt = len(check)
        if cnt > 1:
            return self.translate_text(text)
        elif cnt == 1:
            return self.search_translation(text)

    def translate_text(self, text):
        """
        Replace each word with it's short translation (first other language word in full translation)
        :param text: string text to translate
        :return: string text containing translations
        """
        en = self.get_lang()
        match = re.findall(r"\b(?:\w+-?)\b", text, flags=re.DOTALL)
        for m in match:
            tr = self.search_translation(m)
            if tr:
                if en == "en":
                    reg = r"\b(?:[A-Za-z']+-?\.?\s?)+\b"
                elif en == "ru":
                    reg = r"\b(?:[А-Яа-я']+-?\.?\s?)+\b"
                else:
                    raise Exception("Поддержка языка текущего словаря ещё не реализована.")

                tr = re.search(reg, tr, flags=re.IGNORECASE)
                if tr[0]:
                    text = re.sub(m, tr[0].strip(), text)
        return text


"""
Class that is a wrapper on QSettings
Used for more simple settings manipulating
Singleton
"""


class Settings:

    def __new__(cls):
        """
        Checks the existence of class instance
        :return: instance of Settings
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """
        Some default app parameters
        """
        self.version = "1.0.0"
        self.organization = "AB"
        self.application = "STranslate"
        if not QCoreApplication.organizationName() or not QCoreApplication.applicationName():
            self.set_default_options()
        self.settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName())

    def set_default_options(self):
        """
        Sets default settings
        """
        QCoreApplication.setApplicationVersion(self.version)
        QCoreApplication.setOrganizationName(self.organization)
        QCoreApplication.setApplicationName(self.application)
        settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName())
        settings.setValue('dictionary', 'rus_eng')
        settings.setValue('language/from', 'ru')
        settings.setValue('language/to', 'en')

    def set_option(self, option, value, default=False):
        """
        :param option: string name of the option to set
        :param value: string value of the option
        :param default: bool true if you want to discard all options
        """
        if not default:
            self.settings.setValue(option, value)
        else:
            self.set_default_options()

    def get_option(self, option):
        return self.settings.value(option)

