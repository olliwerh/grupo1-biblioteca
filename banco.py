import sqlite3

def conectar():
    return sqlite3.connect("biblioteca.db")

def criar_tabelas():
    con = conectar()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS livros (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo      TEXT    NOT NULL,
            autor       TEXT    NOT NULL,
            ano         INTEGER NOT NULL,
            disponivel  INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS emprestimos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            livro_id     INTEGER NOT NULL,
            nome_aluno   TEXT    NOT NULL,
            data_empr    TEXT    NOT NULL,
            devolvido    INTEGER DEFAULT 0,
            FOREIGN KEY (livro_id) REFERENCES livros(id)
        )
    """)

    con.commit()
    con.close()