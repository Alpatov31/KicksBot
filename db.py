import sqlite3

if __name__ == '__main__':
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    sql = '''
    CREATE TABLE Users (
    id integer PRIMARY KEY,
    state text,
    color integer,
    size text,
    gender text);
    '''
    cursor.execute(sql)
    conn.commit()
