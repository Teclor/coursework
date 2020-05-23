import sqlite3 as sql




def create_db():
    conn = sql.connect("resource\\eng_words.db")
    db = conn.cursor()
    db.execute("CREATE TABLE words (word text, translation text)")
    f = open('resource\\ENRUS.txt', 'r')
    count = sum(1 for line in f)
    f.seek(0)
    i = int(0)
    while i < count//2:
        lineA = f.readline().rstrip()
        lineB = f.readline().rstrip()
        db.execute("INSERT INTO words (word, translation) VALUES (?,?)", (lineA, lineB))
        i += 1
    f.close()
    conn.commit()
    conn.close()


def search_translation(word):
    conn = sql.connect("resource\\eng_words.db")
    db = conn.cursor()
    db.execute("SELECT translation FROM words WHERE word LIKE ?", (word,))
    result = db.fetchall()
    conn.close()
    if result:
        return str((result[0][0]))
    else:
        return False

