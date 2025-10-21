# Importa o módulo principal do tkinter para interfaces gráficas.
import tkinter as tk  

# Importa widgets temáticos e caixa de mensagens para alertas.
from tkinter import ttk, messagebox  

# Importa o módulo datetime para manipulação de datas.
import datetime  

# Importa função para conectar ao banco de dados.
from db import getconnection  

# Importa função para centralizar janelas na tela.
from utils import centralizarjanela  

def showgestaoestoque(app):
    
    for w in app.winfo_children():
        w.destroy()

    # Cria um frame superior para os botões. Padding para separar dos outros elementos.
    top = ttk.Frame(app, padding=8)
    top.pack(fill="x")

    # Botão para voltar à tela principal.
    ttk.Button(top, text="Voltar", command=app.showmain).pack(side="left")

    # Define colunas, cabeçalhos e larguras para a tabela (Treeview).
    cols = ("id", "nome", "quantidade", "estoque_minimo")
    headers = {"id": "ID", "nome": "Nome", "quantidade": "Quantidade", "estoque_minimo": "Estoque Mínimo"}
    colwidths = {"id": 60, "nome": 250, "quantidade": 120, "estoque_minimo": 150}

    # Cria o componente de tabela para listar os itens do estoque.
    tree = ttk.Treeview(app, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=headers[c])  # Define o título de cada coluna
        tree.column(c, width=colwidths[c], anchor="center")  # Define a largura de cada coluna

    tree.pack(expand=True, fill="both", padx=10, pady=8)  # Exibe a tabela na interface

    # Função para carregar os itens do estoque em ordem alfabética do nome.
    def loadcomidasordenadas():
        for it in tree.get_children():
            tree.delete(it)  # Limpa a tabela antes de recarregar

        with getconnection() as conn:
            cur = conn.execute("SELECT id, nome, quantidade, estoque_minimo FROM comidas")
            rows = [dict(r) for r in cur.fetchall()]  # Lista de dicionários para cada comida

        for r in sorted(rows, key=lambda r: r["nome"].lower()):  # Ordena pelo nome
            tag = "baixo" if r["quantidade"] <= r["estoque_minimo"] else ""
            # Marca alimentos com estoque igual ou abaixo do mínimo
            tree.insert("", "end", values=(r["id"], r["nome"], r["quantidade"], r["estoque_minimo"]), tags=(tag,))

        tree.tag_configure("baixo", background="red", foreground="white")  # Destaca itens em baixo estoque

    loadcomidasordenadas()  # Carrega alimentos na tabela ao abrir tela

    # Frame para botões que ficam abaixo da tabela.
    btns = ttk.Frame(app, padding=6)
    btns.pack(fill="x")

    # Botão para registrar movimentações de entrada/saída de estoque
    ttk.Button(btns, text="Registrar Movimentação", command=lambda: registrarmovimentacao(app, tree)).pack(side="left", padx=6)
    # Botão para visualizar histórico das movimentações do alimento escolhido
    ttk.Button(btns, text="Ver Histórico", command=lambda: verhistorico(tree)).pack(side="left", padx=6)

def registrarmovimentacao(app, tree):
    # Função para registrar uma entrada ou saída de alimento do estoque

    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Atenção", "Selecione uma comida para movimentar.")
        return

    cid = tree.item(sel[0])["values"][0]  # Id do alimento selecionado

    win = tk.Toplevel(app)
    win.title("Registrar Movimentação")
    centralizarjanela(win, 400, 300)

    # Widget para escolher tipo da movimentação (entrada ou saída)
    ttk.Label(win, text="Tipo").grid(column=0, row=0, sticky="e", padx=6, pady=4)
    tipocb = ttk.Combobox(win, values=["entrada", "saída"], state="readonly")
    tipocb.grid(column=1, row=0, padx=6, pady=4)
    tipocb.current(0)

    # Campo para digitar quantidade movimentada
    ttk.Label(win, text="Quantidade").grid(column=0, row=1, sticky="e", padx=6, pady=4)
    qtdent = ttk.Entry(win, width=20)
    qtdent.grid(column=1, row=1, padx=6, pady=4)

    # Campo para escolher/data, preenchido automaticamente com a data de hoje
    ttk.Label(win, text="Data (DD/MM/AAAA)").grid(column=0, row=2, sticky="e", padx=6, pady=4)
    dataent = ttk.Entry(win, width=20)
    dataent.grid(column=1, row=2, padx=6, pady=4)
    dataent.insert(0, datetime.date.today().strftime("%d/%m/%Y"))

    # Campo para observação extra da movimentação
    ttk.Label(win, text="Observação").grid(column=0, row=3, sticky="e", padx=6, pady=4)
    noteent = ttk.Entry(win, width=40)
    noteent.grid(column=1, row=3, padx=6, pady=4)

    def salvarmov():
        # Função para salvar movimentação no banco de dados

        tipo = tipocb.get()
        try:
            qtd = int(qtdent.get())
        except:
            messagebox.showwarning("Validação", "Quantidade inválida.")
            return

        datatxt = dataent.get().strip()
        try:
            dataiso = datetime.datetime.strptime(datatxt, "%d/%m/%Y").date().isoformat()
        except:
            messagebox.showwarning("Validação", "Data inválida. Use DD/MM/AAAA.")
            return

        with getconnection() as conn:
            comida = conn.execute("SELECT * FROM comidas WHERE id=?", (cid,)).fetchone()
            if not comida:
                messagebox.showerror("Erro", "Comida não encontrada.")
                return

            # Calcula novo valor de estoque para entrada ou saída
            newq = comida["quantidade"] + qtd if tipo == "entrada" else comida["quantidade"] - qtd

            if newq < 0:
                messagebox.showerror("Erro", "Quantidade insuficiente para esta saída.")
                return

            # Atualiza quantidade de comida na tabela
            conn.execute("UPDATE comidas SET quantidade=? WHERE id=?", (newq, cid))

            # Insere registro da movimentação para rastreabilidade
            conn.execute(
                "INSERT INTO movimentacoes (comida_id, usuario_id, tipo, quantidade, data, observacao) VALUES (?, ?, ?, ?, ?, ?)",
                (cid, app.currentuser["id"], tipo, qtd, dataiso, noteent.get().strip())
            )

            # Alerta se atingiu estoque abaixo do mínimo
            if newq <= comida["estoque_minimo"]:
                messagebox.showwarning("Estoque baixo", f"A comida '{comida['nome']}' está com quantidade {newq} (mínimo: {comida['estoque_minimo']}).")

        win.destroy()  # Fecha a janela de movimentação
        showgestaoestoque(app)  # Atualiza tela principal de estoque
        messagebox.showinfo("Sucesso", "Movimentação registrada.")  # Confirma ao usuário

    ttk.Button(win, text="Salvar", command=salvarmov).grid(column=0, row=4, columnspan=2, pady=10)

def verhistorico(tree):
    # Função para exibir histórico de todas movimentações de um alimento

    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Atenção", "Selecione uma comida para ver o histórico.")
        return

    cid = tree.item(sel[0])["values"][0]

    win = tk.Toplevel()
    win.title("Histórico de Movimentações")
    centralizarjanela(win, 700, 400)

    # Define colunas e cabeçalhos para exibir histórico.
    cols = ("id", "tipo", "quantidade", "data", "usuario", "observacao")
    tv = ttk.Treeview(win, columns=cols, show="headings")
    headers = {"id": "ID", "tipo": "Tipo", "quantidade": "Quantidade", "data": "Data", "usuario": "Usuário", "observacao": "Observação"}
    for c in cols:
        tv.heading(c, text=headers[c])
        tv.column(c, width=120, anchor="center")
    tv.pack(expand=True, fill="both", padx=10, pady=8)

    # Busca movimentações desse alimento, junta com usuários para exibir nome do responsável.
    with getconnection() as conn:
        cur = conn.execute("""
            SELECT m.id, m.tipo, m.quantidade, m.data, u.usuario AS usuario, m.observacao
            FROM movimentacoes m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.comida_id = ?
            ORDER BY m.data DESC
        """, (cid,))
        for r in cur.fetchall():
            try:
                # Formata data para padrão brasileiro
                databr = datetime.datetime.fromisoformat(r["data"]).strftime("%d/%m/%Y")
            except:
                databr = r["data"]
            tv.insert("", "end", values=(r["id"], r["tipo"], r["quantidade"], databr, r["usuario"], r["observacao"]))