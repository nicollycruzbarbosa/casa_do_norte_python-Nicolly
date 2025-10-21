# Necessário importar as bibliotecas necessárias para interagir com o banco de dados e o sistema de arquivos

# 1º passo: Importar o módulo 'sqlite3', que é a biblioteca padrão do Python para trabalhar com bancos de dados SQLite
import sqlite3

# 2º passo: Importar o módulo 'os', que permite interagir com o sitema operacional, como verificar se um arquivo existe  
import os       

# 3º passo: Definir o nome do arquivo que será usado para banco de dados
DBFILENAME = "comidasdb.sqlite"  # Nome do arquivo do banco de dados

# --- Função para Obter Conexão ----
# Toda vez que o programa precisa ler ou escrever dados, ele chamará esta função

def getconnection():
    """Abre uma conexão com o banco de dados SQLite"""

    # Estabelece comunicação com o arquivo do danco de dados
    conn = sqlite3.connect(DBFILENAME)
    conn.row_factory = sqlite3.Row
    # Executa um comando PRAGMA no SQLite para garantir que as regras de chave estrangeira sejam sempre aplicadas.
    # Isso é crucial para manter a integridade dos dados (ex: não permitir uma movimentação para uma comida que não existe).
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# --- Função para Garantir a Existência do Banco ---
# Esta função é chamada uma única vez, no início da aplicação.
# Ela verifica se o banco de dados já foi criado. Se não, ela o cria.
def ensuredb():
    # Verifica se o arquivo do banco de dados já existe
    if not os.path.exists(DBFILENAME):
        scriptpath = os.path.join(os.path.dirname(__file__), "db_init.sql")
        if os.path.exists(scriptpath):
            with getconnection() as conn:
                with open(scriptpath, "r", encoding="utf-8") as f:conn.executescript(f.read())

        else:
            # Gera erro caso o arquivo db_init.sql não esteja disponível
            raise FileNotFoundError("db_init.sql não encontrado. Coloque db_init.sql na mesma pasta.")