# Importa o módulo principal do tkinter para construção de interfaces gráficas
import tkinter as tk  

# Importa widgets temáticos ("ttk") e caixas de mensagem para exibir alertas e notificações
from tkinter import ttk, messagebox  

# Importa a função responsável pela conexão com o banco de dados
from db import getconnection  

# Importa a função utilitária para centralizar a janela na tela
from utils import centralizarjanela  

# --- Definição da Função Principal ---
# Esta função é responsável por desenhar e controlar toda a tela de login.
# Ela recebe 'app' como argumento, que é a janela principal da nossa aplicação.

def showlogin(app):
        
    # Limpa a tela para exibir apenas o login
    for w in app.winfo_children():
        w.destroy()
    
    # Centraliza a janela principal na tela, largura=400px e altura=250px
    centralizarjanela(app, 400, 250)
    
    # Cria um frame (área interna) com preenchimento, que organiza os widgets de login
    frm = ttk.Frame(app, padding=20)
    frm.pack(expand=True)
    
    # Cria um título "Login" centralizado, usando fonte maior
    ttk.Label(frm, text="Login", font=("TkDefaultFont", 16)).grid(column=0,row=0, columnspan=2, pady=10)
    
    # Cria o texto "Usuário" à direita na grid (linha 1, coluna 0)
    ttk.Label(frm, text="Usuário").grid(column=0, row=1, sticky="e")
    
    # Cria um campo de entrada de texto para digitar o nome de usuário
    userent = ttk.Entry(frm, width=25)
    userent.grid(column=1, row=1)
    
    # Cria e posiciona o rótulo "Senha" à direita na grid (linha 2, coluna 0)
    ttk.Label(frm, text="Senha").grid(column=0, row=2, sticky="e")
    
    # Cria campo de entrada para senha, ocultando os caracteres digitados
    pwdent = ttk.Entry(frm, show="*", width=25)
    pwdent.grid(column=1, row=2)
    
    # Função interna para realizar login ao clicar no botão "Entrar"
    def attempt_login():
        username = userent.get().strip() # Obtém o nome de usuário removendo espaços extras
        password = pwdent.get().strip() # Obtém a senha e remove espaços extras

        # Verifica se ambos os campos foram preenchidos
        if not username or not password:
            # Alerta se faltou algum campo
            messagebox.showwarning("Falha", "Preencha usuário e senha.")
            return

        # Executa a consulta no banco de dados para verificar usuário e senha
        with getconnection() as conn:
            cur = conn.execute(
                "SELECT * FROM usuarios WHERE usuario=? AND senha=?",
                (username, password)
            )
            row = cur.fetchone() # Obtém o primeiro resultado (se existir)
            
        # Se encontrou usuário válido, armazena dados em app e direciona para tela principal
        if row:
            app.currentuser = dict(row)
            app.showmain()
        else:
            messagebox.showerror("Falha", "Usuário ou senha inválidos.")
    
    # Cria o botão "Entrar" que chama attempt_login quando pressionado
    ttk.Button(frm, text="Entrar", command=attempt_login).grid(column=0, row=3, columnspan=2, pady=10)