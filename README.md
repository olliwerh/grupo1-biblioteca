# 📚 Biblioteca Escolar — Grupo 1

> **Projeto Final · Qualifica DF · Programador de Sistemas · 2026**

Sistema web para gerenciar o acervo e os empréstimos de uma biblioteca escolar.
Desenvolvido com **Python + Flask + SQLite + HTML/CSS**.

---

## 🎯 Objetivo

Criar uma aplicação web funcional que permita:
- Cadastrar e listar livros do acervo
- Registrar empréstimos de livros para alunos
- Registrar devoluções
- Visualizar o que está emprestado e o que está disponível

---

## 🗂️ Estrutura de pastas

```
grupo1-biblioteca/
│
├── app.py                  ← arquivo principal Flask
├── banco.py                ← funções do banco de dados
├── requirements.txt        ← dependências do projeto
│
├── templates/
│   ├── base.html           ← layout base (navbar, estilo)
│   ├── index.html          ← página inicial
│   ├── livros.html         ← lista de livros
│   ├── cadastrar_livro.html
│   ├── emprestimos.html    ← lista de empréstimos ativos
│   └── emprestar.html      ← formulário de empréstimo
│
└── static/
    └── style.css           ← estilos da aplicação
```

---

## 🗃️ Banco de Dados

Você vai usar **SQLite** — um banco de dados que fica salvo em um arquivo `.db` na própria pasta do projeto. Não precisa instalar nada extra.

### Tabelas

#### `livros`
| Coluna       | Tipo    | Descrição                        |
|--------------|---------|----------------------------------|
| `id`         | INTEGER | Chave primária (auto incremento) |
| `titulo`     | TEXT    | Título do livro                  |
| `autor`      | TEXT    | Nome do autor                    |
| `ano`        | INTEGER | Ano de publicação                |
| `disponivel` | INTEGER | 1 = disponível · 0 = emprestado  |

#### `emprestimos`
| Coluna          | Tipo    | Descrição                        |
|-----------------|---------|----------------------------------|
| `id`            | INTEGER | Chave primária (auto incremento) |
| `livro_id`      | INTEGER | Referência ao livro              |
| `nome_aluno`    | TEXT    | Nome do aluno                    |
| `data_emprest.` | TEXT    | Data do empréstimo               |
| `devolvido`     | INTEGER | 0 = em aberto · 1 = devolvido    |

### Código do banco (`banco.py`)

```python
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
```

---

## 🚀 Rotas da aplicação

### Passo 1 — Página inicial

**Rota:** `GET /`

Exibe a página inicial com um resumo do sistema (total de livros, total emprestado).

```python
@app.route("/")
def index():
    con = conectar()
    cur = con.cursor()
    total = cur.execute("SELECT COUNT(*) FROM livros").fetchone()[0]
    emprestados = cur.execute(
        "SELECT COUNT(*) FROM livros WHERE disponivel = 0"
    ).fetchone()[0]
    con.close()
    return render_template("index.html", total=total, emprestados=emprestados)
```

**Template `index.html`:**
```html
{% extends "base.html" %}
{% block conteudo %}
  <h1>📚 Biblioteca Escolar</h1>
  <div class="cards">
    <div class="card">
      <h2>{{ total }}</h2>
      <p>Livros no acervo</p>
    </div>
    <div class="card">
      <h2>{{ emprestados }}</h2>
      <p>Livros emprestados</p>
    </div>
    <div class="card">
      <h2>{{ total - emprestados }}</h2>
      <p>Disponíveis</p>
    </div>
  </div>
{% endblock %}
```

---

### Passo 2 — Listar livros

**Rota:** `GET /livros`

Exibe todos os livros do acervo com seu status (disponível ou emprestado).

```python
@app.route("/livros")
def listar_livros():
    con = conectar()
    cur = con.cursor()
    livros = cur.execute("SELECT * FROM livros ORDER BY titulo").fetchall()
    con.close()
    return render_template("livros.html", livros=livros)
```

**Template `livros.html`:**
```html
{% extends "base.html" %}
{% block conteudo %}
  <h1>📖 Acervo de Livros</h1>
  <a href="/cadastrar-livro" class="btn">+ Cadastrar livro</a>

  <table>
    <thead>
      <tr>
        <th>Título</th><th>Autor</th><th>Ano</th><th>Status</th>
      </tr>
    </thead>
    <tbody>
      {% for livro in livros %}
      <tr>
        <td>{{ livro[1] }}</td>
        <td>{{ livro[2] }}</td>
        <td>{{ livro[3] }}</td>
        <td>
          {% if livro[4] == 1 %}
            <span class="badge verde">Disponível</span>
          {% else %}
            <span class="badge vermelho">Emprestado</span>
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
{% endblock %}
```

---

### Passo 3 — Cadastrar livro

**Rotas:** `GET /cadastrar-livro` → exibe formulário | `POST /cadastrar-livro` → salva no banco

```python
@app.route("/cadastrar-livro", methods=["GET", "POST"])
def cadastrar_livro():
    if request.method == "POST":
        titulo = request.form["titulo"]
        autor  = request.form["autor"]
        ano    = request.form["ano"]

        con = conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO livros (titulo, autor, ano) VALUES (?, ?, ?)",
            (titulo, autor, ano)
        )
        con.commit()
        con.close()
        return redirect("/livros")

    return render_template("cadastrar_livro.html")
```

**Template `cadastrar_livro.html`:**
```html
{% extends "base.html" %}
{% block conteudo %}
  <h1>➕ Cadastrar Livro</h1>
  <form method="POST">
    <label>Título</label>
    <input type="text" name="titulo" required>

    <label>Autor</label>
    <input type="text" name="autor" required>

    <label>Ano de publicação</label>
    <input type="number" name="ano" required>

    <button type="submit">Cadastrar</button>
  </form>
{% endblock %}
```

---

### Passo 4 — Registrar empréstimo

**Rotas:** `GET /emprestar` → exibe formulário com livros disponíveis | `POST /emprestar` → salva empréstimo

```python
@app.route("/emprestar", methods=["GET", "POST"])
def emprestar():
    if request.method == "POST":
        livro_id   = request.form["livro_id"]
        nome_aluno = request.form["nome_aluno"]
        from datetime import date
        data_hoje = str(date.today())

        con = conectar()
        cur = con.cursor()

        # Registra o empréstimo
        cur.execute(
            "INSERT INTO emprestimos (livro_id, nome_aluno, data_empr) VALUES (?, ?, ?)",
            (livro_id, nome_aluno, data_hoje)
        )
        # Marca o livro como indisponível
        cur.execute(
            "UPDATE livros SET disponivel = 0 WHERE id = ?",
            (livro_id,)
        )
        con.commit()
        con.close()
        return redirect("/emprestimos")

    # GET: busca só os livros disponíveis
    con = conectar()
    cur = con.cursor()
    livros = cur.execute(
        "SELECT id, titulo FROM livros WHERE disponivel = 1"
    ).fetchall()
    con.close()
    return render_template("emprestar.html", livros=livros)
```

---

### Passo 5 — Listar empréstimos ativos

**Rota:** `GET /emprestimos`

Lista todos os empréstimos que ainda não foram devolvidos, com JOIN entre as tabelas.

```python
@app.route("/emprestimos")
def listar_emprestimos():
    con = conectar()
    cur = con.cursor()
    emprestimos = cur.execute("""
        SELECT e.id, l.titulo, e.nome_aluno, e.data_empr
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        WHERE e.devolvido = 0
        ORDER BY e.data_empr DESC
    """).fetchall()
    con.close()
    return render_template("emprestimos.html", emprestimos=emprestimos)
```

---

### Passo 6 — Registrar devolução

**Rota:** `POST /devolver/<int:emp_id>`

Marca o empréstimo como devolvido e libera o livro novamente.

```python
@app.route("/devolver/<int:emp_id>", methods=["POST"])
def devolver(emp_id):
    con = conectar()
    cur = con.cursor()

    # Busca qual livro está nesse empréstimo
    livro = cur.execute(
        "SELECT livro_id FROM emprestimos WHERE id = ?", (emp_id,)
    ).fetchone()

    # Marca empréstimo como devolvido
    cur.execute(
        "UPDATE emprestimos SET devolvido = 1 WHERE id = ?", (emp_id,)
    )
    # Libera o livro
    cur.execute(
        "UPDATE livros SET disponivel = 1 WHERE id = ?", (livro[0],)
    )
    con.commit()
    con.close()
    return redirect("/emprestimos")
```

No template `emprestimos.html`, adicione um botão de devolução para cada linha:
```html
<form action="/devolver/{{ emp[0] }}" method="POST" style="display:inline">
  <button type="submit" class="btn vermelho">Devolver</button>
</form>
```

---

## 📄 Arquivo principal (`app.py`)

```python
from flask import Flask, render_template, request, redirect
from banco import conectar, criar_tabelas

app = Flask(__name__)

# Cria as tabelas ao iniciar
criar_tabelas()

# Cole aqui todas as rotas dos passos acima

if __name__ == "__main__":
    app.run(debug=True)
```

---

## 📦 Dependências (`requirements.txt`)

```
flask
gunicorn
```

---

## 🎨 Estilo base (`static/style.css`)

```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; background: #f5f5f5; color: #333; }
nav { background: #1a4e7a; padding: 1rem 2rem; }
nav a { color: white; text-decoration: none; margin-right: 1.5rem; font-weight: bold; }
.container { max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
h1 { margin-bottom: 1.5rem; color: #1a4e7a; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
th { background: #1a4e7a; color: white; padding: 0.75rem 1rem; text-align: left; }
td { padding: 0.75rem 1rem; border-bottom: 1px solid #eee; }
.btn { display: inline-block; padding: 0.5rem 1rem; background: #1a4e7a; color: white;
       text-decoration: none; border-radius: 6px; border: none; cursor: pointer; margin-bottom: 1rem; }
.btn.vermelho { background: #c0392b; }
.badge { padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold; }
.badge.verde { background: #d4edda; color: #155724; }
.badge.vermelho { background: #f8d7da; color: #721c24; }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.card { background: white; padding: 2rem; border-radius: 8px; text-align: center;
        border-left: 4px solid #1a4e7a; }
.card h2 { font-size: 2.5rem; color: #1a4e7a; }
form label { display: block; margin: 1rem 0 0.25rem; font-weight: bold; }
form input, form select { width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; }
form button { margin-top: 1.5rem; }
```

---

## 🌐 Layout base (`templates/base.html`)

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <title>Biblioteca Escolar</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <nav>
    <a href="/">🏠 Início</a>
    <a href="/livros">📖 Livros</a>
    <a href="/emprestimos">📋 Empréstimos</a>
    <a href="/emprestar">➕ Emprestar</a>
  </nav>
  <div class="container">
    {% block conteudo %}{% endblock %}
  </div>
</body>
</html>
```

---

## ☁️ Deploy no Render

1. Suba o projeto no GitHub (faça fork deste repo e implemente nele)
2. Acesse [render.com](https://render.com) e crie uma conta gratuita
3. Clique em **New > Web Service** e conecte seu repositório
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Clique em **Deploy** — em alguns minutos a URL pública estará disponível!

---

## ✅ Checklist de entrega

- [ ] Cadastro de livros funcionando
- [ ] Listagem com status correto (disponível / emprestado)
- [ ] Empréstimo atualiza o status do livro no banco
- [ ] Devolução libera o livro novamente
- [ ] Lista de empréstimos ativos com JOIN funcionando
- [ ] Aplicação rodando no Render com URL pública
- [ ] README atualizado com a URL do deploy

---

*Qualifica DF · 2026 · Programador de Sistemas*
