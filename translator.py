import sqlite3 as sql
import re

from PyQt5.QtCore import QCoreApplication, QSettings


class DB:

    def __init__(self, current_dictionary, db_name="dictionary"):
        db_path = "resource\\db\\" + db_name + ".db"
        self.conn = sql.connect(db_path)
        self.DICT = current_dictionary
        self.db = self.conn.cursor()

    def create_table(self):
        self.db = self.conn.cursor()
        self.db.execute("CREATE TABLE IF NOT EXISTS" + self.DICT + " (word text NOT NULL, translation text NOT NULL)")

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
        self.db.execute("SELECT * FROM sqlite_master WHERE type = 'table'")
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


class Translator(DB):

    def translate(self, text, en=True):
        check = re.findall(r"\b(?:\w+-?)\b", text, flags=re.DOTALL)
        cnt = len(check)
        if cnt > 1:
            return self.translate_text(text, en)
        elif cnt == 1:
            return self.translate_word(text)

    def translate_word(self, word):
        return self.search_translation(word)

    def translate_text(self, text, en):
        match = re.findall(r"\b(?:\w+-?)\b", text, flags=re.DOTALL)
        for m in match:
            tr = self.search_translation(m)
            if tr:
                if en:
                    reg = r"\b(?:[A-Za-z']+-?\.?\s?)+\b"
                else:
                    reg = r"\b(?:[А-Яа-я']+-?\.?\s?)+\b"
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

