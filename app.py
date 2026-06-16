# O menor app Flask possível — 5 linhas!
from flask import Flask

app = Flask(__name__)          # cria a aplicação

@app.route("/")                # define a URL que aciona essa função
def pagina_inicial():
    return "<h1>Olá Mundo!</h1>"   # o que o browser recebe

if __name__ == "__main__":
    app.run(debug=True)        # inicia o servidor em localhost:5000
