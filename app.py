# O menor app Flask possível — 5 linhas!
from flask import Flask, redirect, render_template, request

from banco import conectar, criar_tabelas

app = Flask(__name__)          # cria a aplicação
# Cria as tabelas ao iniciar
criar_tabelas()
      # inicia o servidor em localhost:5000

#pagina inicial
@app.route("/")
def index():
    conn = conectar()
    cursor = conn.cursor()
    total = cursor.execute("SELECT COUNT(*) FROM livros").fetchone()[0]
    emprestados = cursor.execute(
        "SELECT COUNT(*) FROM livros WHERE disponivel = 0"
    ).fetchone()[0]
    conn.close()
    return render_template("index.html", total=total, emprestados=emprestados)

#cadastrar livros
@app.route("/cadastrar-livro", methods=["GET", "POST"])
def cadastrar_livro():
    if request.method == "POST":
        titulo = request.form["titulo"]
        autor  = request.form["autor"]
        ano    = request.form["ano"]

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO livros (titulo, autor, ano) VALUES (?, ?, ?)",
            (titulo, autor, ano)
        )
        conn.commit()
        conn.close()
        return redirect("/livros")

    return render_template("cadastrar_livro.html")

# listar livros
@app.route("/livros")
def listar_livros():
    conn = conectar()
    cursor = conn.cursor()
    livros = cursor.execute("SELECT * FROM livros ORDER BY titulo").fetchall()
    conn.close()
    return render_template("livros.html", livros=livros)

#emprestar livros
@app.route("/emprestar", methods=["GET", "POST"])
def emprestar():
    if request.method == "POST":
        livro_id   = request.form["livro_id"]
        nome_aluno = request.form["nome_aluno"]
        from datetime import date
        data_hoje = str(date.today())

        conn = conectar()
        cursor = conn.cursor()

        # Registra o empréstimo
        cursor.execute(
            "INSERT INTO emprestimos (livro_id, nome_aluno, data_empr) VALUES (?, ?, ?)",
            (livro_id, nome_aluno, data_hoje)
        )
        # Marca o livro como indisponível
        cursor.execute(
            "UPDATE livros SET disponivel = 0 WHERE id = ?",
            (livro_id,)
        )
        conn.commit()
        conn.close()
        return redirect("/emprestimos")

    # GET: busca só os livros disponíveis
    conn = conectar()
    cursor = conn.cursor()
    livros = cursor.execute(
        "SELECT id, titulo FROM livros WHERE disponivel = 1"
    ).fetchall()
    conn.close()
    return render_template("emprestar.html", livros=livros)

# listar empréstimos
@app.route("/emprestimos")
def listar_emprestimos():
    conn = conectar()
    cursor = conn.cursor()
    emprestimos = cursor.execute("""
        SELECT e.id, l.titulo, e.nome_aluno, e.data_empr
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        WHERE e.devolvido = 0
        ORDER BY e.data_empr DESC
    """).fetchall()
    conn.close()
    return render_template("emprestimos.html", emprestimos=emprestimos)

# devolver livros
@app.route("/devolver/<int:emp_id>", methods=["POST"])
def devolver(emp_id):
    conn = conectar()
    cursor = conn.cursor()

    # Busca qual livro está nesse empréstimo
    livro = cursor.execute(
        "SELECT livro_id FROM emprestimos WHERE id = ?", (emp_id,)
    ).fetchone()

    # Marca empréstimo como devolvido
    cursor.execute(
        "UPDATE emprestimos SET devolvido = 1 WHERE id = ?", (emp_id,)
    )
    # Libera o livro
    cursor.execute(
        "UPDATE livros SET disponivel = 1 WHERE id = ?", (livro[0],)
    )
    conn.commit()
    conn.close()
    return redirect("/emprestimos")



# Cole aqui todas as rotas dos passos acima

if __name__ == "__main__":
    app.run(debug=True)

