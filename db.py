import os
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="translator",
        user="root",
        password="root")
    return conn

def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE translated_recordings (id serial PRIMARY KEY,'
                'title varchar (150) NOT NULL,'
                'language varchar (50) NOT NULL,'
                'date_added timestamp DEFAULT CURRENT_TIMESTAMP);'
                )
    conn.commit()
    cur.close()
    conn.close()

def get_last_recording_by_language(date_added = None, lang="ro"):
    conn = get_db_connection()
    cur = conn.cursor()
    if date_added is None:
        print(date_added)
        cur.execute('SELECT title, date_added FROM translated_recordings where language=\'{}\' order by date_added desc;'.format(lang))
    else:
        print(date_added)
        cur.execute('SELECT title, date_added FROM translated_recordings where language=\'{}\' and date_added>\'{}\' order by date_added asc;'.format(lang, date_added))

    title = cur.fetchall()

    cur.close()
    conn.close()
    if not title:
        return None, None

    print(title)
    print(title[0][0], title[0][1])
    return title[0][0], title[0][1]

def insert_recording(title, lang="ro"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO translated_recordings (title, language) VALUES (%s, %s)', (title, lang))
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_table()
