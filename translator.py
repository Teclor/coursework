import sqlite3 as sql
import re


class DB:

    def __init__(self, current_dictionary, name="dictionary"):
        db_path = "resource\\db\\" + name + ".db"
        self.conn = sql.connect(db_path)
        self.DICT = current_dictionary

    def create_table(self):
        db = self.conn.cursor()
        db.execute("CREATE TABLE " + self.DICT + " (word text NOT NULL, translation text NOT NULL)")

    def insert_translation(self, word, translation):
        db = self.conn.cursor()
        cmd = "INSERT INTO {t} (word, translation) VALUES (?,?)"
        cmd = cmd.format(t=self.DICT)
        db.execute(cmd, (word, translation))

    def search_translation(self, word):
        db = self.conn.cursor()
        cmd = "SELECT translation FROM {table} WHERE word LIKE ?"
        cmd = cmd.format(table=self.DICT)
        db.execute(cmd, (word,))
        result = db.fetchall()
        if result:
            return str((result[0][0]))
        else:
            return False

    def __del__(self):
        self.conn.close()


class Parser(DB):

    def parse_xdxf(self):
        with open('resource/raw/' + self.DICT + '.xdxf', encoding="utf-8") as fin:
            text = fin.read()
        self.create_table()
        match = re.findall('<ar>.*?</ar>', text, re.DOTALL)  # ленивый квантификатор
        for m in match:
            m = re.sub("<ar>|</ar>|<k>", "", m)
            m = re.split(r"</k>\n", m)
            if m[0] and m[1]:
                self.insert_translation(m[0], m[1])
        self.conn.commit()


class Translator(DB):

    def translate(self, text, en=True):
        check = re.findall(r"\b(?:\w-?\.?)\b", text, re.DOTALL)
        cnt = len(check)
        if cnt > 1:
            return self.translate_text(text, en)
        elif cnt == 1:
            return self.translate_word(text)

    def translate_word(self, word):
        return self.search_translation(word)

    def translate_text(self, text, en):
        match = re.findall(r"\b(?:\w-?)\b", text, re.DOTALL)
        for m in match:
            tr = self.search_translation(m)
            if en:
                reg = r"\b(?:[A-Za-z']+-?\.?\s?)+\b"
            else:
                reg = r"\b(?:[А-Яа-я']+-?\.?\s?)+\b"
            tr = re.search(reg, tr)
            if tr[0]:
                re.sub(m, tr[0], text)
            return text
