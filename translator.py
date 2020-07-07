"""
Module containing necessary classes for working with sql database, settings and texts
"""
import sqlite3 as sql
import re

from PyQt5.QtCore import QCoreApplication, QSettings


class DB:

    def __init__(self):
        """
        Class for working with sqlite database
        """
        self.settings = Settings()
        db_name = self.settings.get_option("db_name")
        db_path = "resource\\db\\" + db_name + ".db"
        self.conn = sql.connect(db_path)
        self.db = self.conn.cursor()

    def create_table(self, table_name=None):
        """
        Creates a table in DB
        :param string table_name:
        :return null:
        """
        if table_name is None:
            table_name = self.settings.get_dictionary()
        self.db = self.conn.cursor()
        self.db.execute("CREATE TABLE IF NOT EXISTS " + table_name + " (word text NOT NULL, translation text NOT NULL);")

    def insert_translation(self, word, translation, table_name=None):
        """
        Adds a translation into db table
        :param string word:
        :param string translation:
        :param string table_name:
        :return:
        """
        cmd = "INSERT INTO {t} (word, translation) VALUES (?,?)"
        cmd = cmd.format(t= self.settings.get_dictionary() if table_name is None else table_name)
        self.db.execute(cmd, (word, translation))

    def search_translation(self, word):
        """
        Finds all occurrences of a given word
        :param string word:
        :return array:
        """
        cmd = "SELECT translation FROM {table} WHERE word LIKE ?;"
        cmd = cmd.format(table=self.settings.get_dictionary())
        self.db.execute(cmd, (word.lower(),))
        result = self.db.fetchall()
        if result:
            return result
        else:
            return False

    def get_tables(self):
        """
        Gets all dictionaries (tables in DB)
        :return array | bool False:
        """
        self.db.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        tables = self.db.fetchall()
        if tables:
            return tables
        else:
            return False

    def delete_table(self, table_name):
        """
        Deletes a dictionary (table in DB)
        :param  string table_name:
        :return null:
        """
        if table_name == "Не выбран":
            raise Exception("Вы не выбрали словарь!")
        if (table_name == 'ru_eng') or (table_name == 'en_rus'):
            raise Exception("Словари по умолчанию удалить нельзя!")
        cmd = "DROP TABLE IF EXISTS {table};"
        cmd = cmd.format(table=table_name)
        self.db.execute(cmd)

    def __del__(self):
        self.conn.close()


class Parser(DB):

    def parse_xdxf(self, path, lang, name, progress_bar=None):
        """
        Making a dictionary from XDXF dictionary type file
        :param string path: file path
        :param string lang: lang id
        :param string name: file name without extension
        :param object progress_bar: progress bar
        :return null:
        """
        table_name = lang + "_" + name
        if progress_bar:
            prog = 0
        with open(path, encoding="utf-8") as fin:
            text = fin.read()
        self.create_table(table_name)
        match = re.findall('<ar>.*?</ar>', text, flags=re.DOTALL)  # ленивый квантификатор ищем самое короткое совпадение
        step = 100 / len(match)

        for m in match:
            m = re.sub("<ar>|</ar>|<k>", "", m)
            if lang == "en":
                m = re.sub("<tr>", "[", m)
                m = re.sub("</tr>", "]", m)
            m = re.sub("&quot;", "\"", m)
            m = re.split(r"</k>\n", m)
            if m[0] and m[1]:
                self.insert_translation(m[0], m[1], table_name)
            if prog is not None:
                prog += step
                progress_bar.setValue(prog)
        if prog is not None:
            progress_bar.setValue(100)

        self.conn.commit()

    def parse_txt(self, path, lang, name, progress_bar=None):
        """
        Making a dictionary from txt file
        :param string path: file path
        :param string lang: lang id
        :param string name: file name without extension
        :param object progress_bar: progress bar
        :return null:
        """
        table_name = lang + "_" + name
        if progress_bar:
            prog = 0
        with open(path, encoding="utf-8") as fin:
            count = sum(1 for line in fin)
            step = 100 /count
            fin.seek(0)
            i = 0
            self.create_table(table_name)
            while i < count/2:
                lineA = fin.readline().rstrip()
                lineB = fin.readline().rstrip()
                lineB = re.sub(r"\t", "; ", lineB)
                self.insert_translation(lineA, lineB, table_name)
                if prog is not None:
                    prog += step
                    progress_bar.setValue(prog)
                i += 1
            self.conn.commit()
        if prog is not None:
            progress_bar.setValue(100)


class Translator(DB):
    """
    Class containing translation methods
    """
    def translate(self, text):
        """
        A method to choose which type of translation we need: full translation of a word or translation of a text
        :param string text: input text
        :return string: translation
        """
        text = text.strip()
        check = re.findall(r"\b(?:\w+-?)\b", text, flags=re.DOTALL)
        cnt = len(check)
        if cnt > 1:
            return self.translate_text(text)
        elif cnt == 1:
            return self.translate_word(text)

    def translate_word(self, word):
        """
        :param string word: a word to translate
        :return string | bool: translation or False
        """
        translations = self.search_translation(word)
        result = ""
        if translations is not False:
            for tr in translations:
                result = result + tr[0] + "\n"
            return result
        else:
            return False

    def translate_text(self, text):
        """
        Replace each word with it's short translation (first other language word in full translation)
        :param string text: text to translate
        :return string: text containing translations
        """
        lang = self.settings.get_lang()
        match = re.findall(r"\b(?:\w+-?)\b", text, flags=re.DOTALL)
        for m in match:
            translation = self.search_translation(m)
            if (translation):
                translation = str(translation[0][0])
            if translation:
                if lang == "ru":
                    reg = r"\b(?:[A-Za-z']+-?\.?\s?)+\b"
                elif lang == "en":
                    reg = r"\b[А-Яа-я']+-?\.?\s?\b"
                else:
                    raise Exception("Поддержка языка текущего словаря ещё не реализована.")

                translations = re.findall(reg, translation, flags=re.IGNORECASE)
                for tr in translations:
                    tr = tr.strip()
                    if tr:
                        if lang == "ru":
                            if len(tr) == 1 and (tr != "I" or (m != "Я" and m != "я")):
                                continue
                        elif lang == "en":
                            if (len(tr) == 1 and tr != "я") or tr == "прил." or tr == "прил" or tr == "сущ." \
                                    or tr == "сущ" or tr == "гл." or tr == "гл" or tr == "нареч." or tr == "нареч" or tr == "сравн." or tr == "сравн" or tr == "мест" or tr == "мест.":
                                continue
                        text = re.sub(r"\b" + m + r"\b", tr, text)
                        break
        return text


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
        Class that is a wrapper on QSettings
        Used for more simple settings manipulating
        Singleton
        """
        self.version = "1.0.0"
        self.organization = "AB"
        self.application = "STranslate"
        QCoreApplication.setApplicationVersion(self.version)
        QCoreApplication.setOrganizationName(self.organization)
        QCoreApplication.setApplicationName(self.application)
        self.settings = QSettings("config.ini", QSettings.IniFormat)
        if not QCoreApplication.organizationName() or not QCoreApplication.applicationName():
            self.set_default_options()

    def set_default_options(self):
        """
        Sets default settings
        """
        self.settings.setValue('db_name', 'dictionary')
        self.settings.setValue('dictionary/ru', 'ru_eng')
        self.settings.setValue('dictionary/en', 'en_rus')
        self.settings.setValue('language/from', 'ru')
        self.settings.setValue('language/to', 'en')
        self.settings.sync()

    def set_option(self, option, value):
        """
        Sets a particular setting
        :param string option: name of the option to set
        :param string value: value of the option
        """
        self.settings.setValue(option, value)
        self.settings.sync()

    def get_option(self, option):
        """
        Gets a particular setting
        :param string option: a setting we want to get
        :return string: value of setting
        """
        return self.settings.value(option)

    def get_dictionary(self):
        """
        Gets current dictionary
        :return string:
        """
        return self.get_option("dictionary/" + self.get_option("language/from"))

    def get_lang(self):
        """
        Gets current lang id (ru or en)
        :return string: lang id
        """
        return self.get_option("language/from")