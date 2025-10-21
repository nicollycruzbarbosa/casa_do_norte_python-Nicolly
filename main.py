import tkinter as tk  
from tkinter import ttk 

# Importa função para garantir que o banco de dados exista e esteja inicializado. 
from db import ensuredb  

from utils import centralizarjanela  

# Importa a função responsável por exibir a tela de login.
from login import showlogin  

from comidas import showcomidas  
from estoque import showgestaoestoque  

# Uma 'class' é como uma base fundamental para construir um objeto.
# Nossa classe 'App' é a base para construir a janela principal do nosso programa.
# Ela 'herda' de 'tk.Tk', o que significa que ela já nasce sabendo tudo que uma janela normal do Tkinter sabe fazer.

class App(tk.Tk):
    # O método construtor '__init__' é o que acontece assim que a janela é criada.

    def __init__(self):
        # Inicializa objeto Tk (janela principal).
        super().__init__()
        self.title("Controle de Estoque: Comidas Nordestinas")
        ensuredb()
        self.currentuser = None
        centralizarjanela(self, 400, 250)
        showlogin(self)

# Este método é responsável por mostrar o menu principal depois que o login dá certo.

    def showmain(self):        
        # Antes de desenhar a tela nova, precisamos limpar a antiga (a de login).
        for w in self.winfo_children():
            w.destroy()

        # Centraliza e expande janela para modo principal.
        centralizarjanela(self, 1000, 550)

        # Frame superior com dados do usuário e botões de navegação.
        top = ttk.Frame(self, padding=2)
        top.pack(fill="x")

        # Exibe quem está logado (usa 'nome_completo' do banco).
        ttk.Label(top, text=f" Usuário logado:{self.currentuser.get('nome_completo','')}").pack(side="left")

        # Botão para deslogar do sistema
        ttk.Button(top, text="Sair", command=lambda: showlogin(self)).pack(side="right")

        # Botão para acessar cadastro de comidas.
        ttk.Button(top, text="Cadastro de Comidas", command=lambda: showcomidas(self)).pack(side="right", padx=6)

        # Botão para acessar tela de gestão de estoque.
        ttk.Button(top, text="Gestão de Estoque", command=lambda: showgestaoestoque(self)).pack(side="right", padx=6)

        # Frame central para mensagem de boas-vindas e instruções.
        center = ttk.Frame(self, padding=40)
        center.pack(expand=True)
        msg = (
            f"Olá, {self.currentuser.get('nome_completo','')}!\n"
            "Bem-vindo ao sistema de controle de estoque de Comidas Nordestinas.\n\n"
            "Aqui você pode:\n"
            " ** Cadastrar novos pratos e comidas típicas\n"
            " ** Consultar e editar o estoque\n"
            " ** Registrar entradas e saídas"
            "\n\nEscolha um botão na barra de opções acima para começar."
        )
        tk.Label(center, text=msg, font=("TkDefaultFont", 18), justify="left").pack()

if __name__ == "__main__":
    # Inicia o programa chamando a classe principal.
    app = App()
    app.mainloop()  # Executa o loop principal da interface gráfica.