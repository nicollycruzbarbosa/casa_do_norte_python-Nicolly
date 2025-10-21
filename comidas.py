# Importa tkinter base para construção da interface
import tkinter as tk  

# Importa widgets temáticos e caixas de mensagem
from tkinter import ttk, messagebox  

# Importa função para conectar ao banco de dados
from db import getconnection  

# Importa função para centralizar janelas na tela# Importa tkinter base para construção da interface
import tkinter as tk  

# Importa widgets temáticos e caixas de mensagem
from tkinter import ttk, messagebox  

# Importa função para conectar ao banco de dados
from db import getconnection  

# Importa função para centralizar janelas na tela
from utils import centralizarjanela  

def showcomidas(app):
    
    for w in app.winfo_children():
        w.destroy()

    # Frame superior com botões para navegação e criação nova comida
    top = ttk.Frame(app, padding=8)
    top.pack(fill="x")
    ttk.Button(top, text="Voltar", command=app.showmain).pack(side="left")
    ttk.Button(top, text="Nova Comida", command=lambda: comidanova(app)).pack(side="right")

    # Frame para barra de busca
    searchframe = ttk.Frame(app, padding=6)
    searchframe.pack(fill="x")

    ttk.Label(searchframe, text="Buscar").pack(side="left")
    searchvar = tk.StringVar()
    searchentry = ttk.Entry(searchframe, textvariable=searchvar, width=40)
    searchentry.pack(side="left", padx=6)
    ttk.Button(searchframe, text="Buscar", command=lambda: loadcomidastree(searchvar.get().strip())).pack(side="left", padx=4)
    ttk.Button(searchframe, text="Limpar", command=lambda: searchvar.set("") or loadcomidastree("")).pack(side="left", padx=4)

    # Define colunas da tabela que sera exibida
    cols = ("id", "nome", "categoria", "origem", "porcao", "calorias", "quantidade", "estoque_minimo")

    # Cria widget de tabela (Treeview) com essas colunas
    tree = ttk.Treeview(app, columns=cols, show="headings")

    headers = {
        "id": "ID", "nome": "Nome", "categoria": "Categoria", "origem": "Origem",
        "porcao": "Porção", "calorias": "Calorias", "quantidade": "Quantidade", "estoque_minimo": "Estoque Mínimo"
    }

    colwidths = {"id": 30, "nome": 160, "categoria": 80, "origem": 100, "porcao": 60, "calorias": 80, "quantidade": 80, "estoque_minimo": 100}

    for c in cols:
        # Define cabeçalhos e alinhamento da tabela
        tree.heading(c, text=headers[c], anchor="w" if c == "nome" else "center")
        tree.column(c, width=colwidths[c], anchor="w" if c == "nome" else "center")

    # Empacota/mostra a tabela preenchendo o espaço disponível
    tree.pack(expand=True, fill="both", padx=10, pady=8)

    def loadcomidastree(searchterm=""):
        # Função que carrega listagem de comidas, filtrando pela busca se houver texto
        # Limpa os elementos já exibidos
        for it in tree.get_children():
            tree.delete(it)

        with getconnection() as conn:
            if searchterm:
                # Usa comodin % para busca aproximada no nome ou descrição da comida
                q = f"%{searchterm}%"
                cur = conn.execute("SELECT * FROM comidas WHERE nome LIKE ? OR descricao LIKE ?", (q, q))
            else:
                # Se não buscar, seleciona todo o conteúdo
                cur = conn.execute("SELECT * FROM comidas")

            rows = cur.fetchall()
            # Ordena as comidas por nome ignorando maiúsculas/minúsculas
            for r in sorted(rows, key=lambda r: r["nome"].lower()):
                # Destaca em vermelho as comidas com quantidade igual ou menor ao estoque mínimo
                tag = "baixo" if r["quantidade"] <= r["estoque_minimo"] else ""
                tree.insert(
                    "", "end",
                    values=(r["id"], r["nome"], r["categoria"], r["origem"], r["porcao"], r["calorias"], r["quantidade"], r["estoque_minimo"]),
                    tags=(tag,)
                )

            tree.tag_configure("baixo", background="red", foreground="white")

    loadcomidastree()  # Carrega a lista inicial sem filtro

    # Frame para botões de edição e exclusão
    btns = ttk.Frame(app, padding=6)
    btns.pack(fill="x")
    ttk.Button(btns, text="Editar", command=lambda: comidaeditar(app, tree)).pack(side="left", padx=6)
    ttk.Button(btns, text="Excluir", command=lambda: comidaexcluir(app, tree)).pack(side="left", padx=6)

def comidanova(app):
    # Exibe o formulário para cadastro de nova comida
    comidaform(app)

def comidaeditar(app, tree):
    # Edição da comida selecionada
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Atenção", "Selecione uma comida para editar.")
        return
    cid = tree.item(sel[0])["values"][0]
    with getconnection() as conn:
        row = conn.execute("SELECT * FROM comidas WHERE id=?", (cid,)).fetchone()
        if row:
            comidaform(app, existing=row)

def comidaexcluir(app, tree):
    # Excluir uma comida após confirmação, somente se não houver movimentações relacionadas
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Atenção", "Selecione uma comida para excluir.")
        return
    cid = tree.item(sel[0])["values"][0]
    with getconnection() as conn:
        cur = conn.execute("SELECT COUNT(*) AS total FROM movimentacoes WHERE comida_id=?", (cid,))
        total = cur.fetchone()["total"]
        if total > 0:
            messagebox.showwarning("Aviso", "Não é possível excluir! Existem movimentações registradas para esta comida.")
            return
    if messagebox.askyesno("Confirmar", "Deseja realmente excluir a comida selecionada?"):
        with getconnection() as conn:
            conn.execute("DELETE FROM comidas WHERE id=?", (cid,))
        showcomidas(app)

def comidaform(app, existing=None):
    # Janela para cadastro ou edição de comida, preenchida se existing for passada
    win = tk.Toplevel(app)
    win.title("Comida Nordestina")
    centralizarjanela(win, 500, 550)

    # Campos a serem preenchidos
    labels = [
        "nome", "descricao", "categoria", "origem", "ingredientes", "porcao",
        "calorias", "quantidade", "estoque_minimo"
    ]

    # Map de nomes exibidos para os campos
    labelspt = {
        "nome": "Nome", "descricao": "Descrição", "categoria": "Categoria", "origem": "Origem", "ingredientes": "Ingredientes",
        "porcao": "Porção", "calorias": "Calorias", "quantidade": "Quantidade", "estoque_minimo": "Estoque Mínimo"
    }

    fields = {}
    for i, key in enumerate(labels):
        ttk.Label(win, text=labelspt[key]).grid(column=0, row=i, sticky="e", padx=6, pady=4)
        ent = ttk.Entry(win, width=40)
        ent.grid(column=1, row=i, padx=6, pady=4, sticky="we")
        fields[key] = ent

        # Se for edição, insere os dados já existentes nos campos
        if existing:
            ent.insert(0, str(existing[key]) if existing[key] is not None else "")

    def save():
        # Função para salvar os dados no banco, após validação
        data = {k: fields[k].get().strip() for k in labels}

        if not data["nome"]:
            messagebox.showwarning("Validação", "Nome obrigatório.")
            return

        try:
            calorias = float(data["calorias"]) if data["calorias"] else 0.0
            quantidade = int(data["quantidade"]) if data["quantidade"] else 0
            estoque_minimo = int(data["estoque_minimo"]) if data["estoque_minimo"] else 0
        except:
            messagebox.showwarning("Validação", "Calorias, Quantidade ou Estoque mínimo inválidos.")
            return

        with getconnection() as conn:
            if existing:
                # Atualiza registro existente
                conn.execute("""
                    UPDATE comidas SET nome=?, descricao=?, categoria=?, origem=?, ingredientes=?, porcao=?, calorias=?, quantidade=?, estoque_minimo=? WHERE id=?
                """, (data["nome"], data["descricao"], data["categoria"], data["origem"], data["ingredientes"], data["porcao"], calorias, quantidade, estoque_minimo, existing["id"]))
            else:
                # Insere novo registro no banco
                conn.execute("""
                    INSERT INTO comidas (nome, descricao, categoria, origem, ingredientes, porcao, calorias, quantidade, estoque_minimo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data["nome"], data["descricao"], data["categoria"], data["origem"], data["ingredientes"], data["porcao"], calorias, quantidade, estoque_minimo))

        win.destroy()  # Fecha janela do formulário
        showcomidas(app)  # Atualiza a listagem da tela principal
        messagebox.showinfo("Sucesso", "Comida salva com sucesso.")

    ttk.Button(win, text="Salvar", command=save).grid(column=0, row=len(labels), columnspan=2, pady=10)
from utils import centralizarjanela  

def showcomidas(app):
    
    for w in app.winfo_children():
        w.destroy()

    # Frame superior com botões para navegação e criação nova comida
    top = ttk.Frame(app, padding=8)
    top.pack(fill="x")
    ttk.Button(top, text="Voltar", command=app.showmain).pack(side="left")
    ttk.Button(top, text="Nova Comida", command=lambda: comidanova(app)).pack(side="right")

    # Frame para barra de busca
    searchframe = ttk.Frame(app, padding=6)
    searchframe.pack(fill="x")

    ttk.Label(searchframe, text="Buscar").pack(side="left")
    searchvar = tk.StringVar()
    searchentry = ttk.Entry(searchframe, textvariable=searchvar, width=40)
    searchentry.pack(side="left", padx=6)
    ttk.Button(searchframe, text="Buscar", command=lambda: loadcomidastree(searchvar.get().strip())).pack(side="left", padx=4)
    ttk.Button(searchframe, text="Limpar", command=lambda: searchvar.set("") or loadcomidastree("")).pack(side="left", padx=4)

    # Define colunas da tabela que sera exibida
    cols = ("id", "nome", "categoria", "origem", "porcao", "calorias", "quantidade", "estoque_minimo")

    # Cria widget de tabela (Treeview) com essas colunas
    tree = ttk.Treeview(app, columns=cols, show="headings")

    headers = {
        "id": "ID", "nome": "Nome", "categoria": "Categoria", "origem": "Origem",
        "porcao": "Porção", "calorias": "Calorias", "quantidade": "Quantidade", "estoque_minimo": "Estoque Mínimo"
    }

    colwidths = {"id": 30, "nome": 160, "categoria": 80, "origem": 100, "porcao": 60, "calorias": 80, "quantidade": 80, "estoque_minimo": 100}

    for c in cols:
        # Define cabeçalhos e alinhamento da tabela
        tree.heading(c, text=headers[c], anchor="w" if c == "nome" else "center")
        tree.column(c, width=colwidths[c], anchor="w" if c == "nome" else "center")

    # Empacota/mostra a tabela preenchendo o espaço disponível
    tree.pack(expand=True, fill="both", padx=10, pady=8)

    def loadcomidastree(searchterm=""):
        # Função que carrega listagem de comidas, filtrando pela busca se houver texto
        # Limpa os elementos já exibidos
        for it in tree.get_children():
            tree.delete(it)

        with getconnection() as conn:
            if searchterm:
                # Usa comodin % para busca aproximada no nome ou descrição da comida
                q = f"%{searchterm}%"
                cur = conn.execute("SELECT * FROM comidas WHERE nome LIKE ? OR descricao LIKE ?", (q, q))
            else:
                # Se não buscar, seleciona todo o conteúdo
                cur = conn.execute("SELECT * FROM comidas")

            rows = cur.fetchall()
            # Ordena as comidas por nome ignorando maiúsculas/minúsculas
            for r in sorted(rows, key=lambda r: r["nome"].lower()):
                # Destaca em vermelho as comidas com quantidade igual ou menor ao estoque mínimo
                tag = "baixo" if r["quantidade"] <= r["estoque_minimo"] else ""
                tree.insert(
                    "", "end",
                    values=(r["id"], r["nome"], r["categoria"], r["origem"], r["porcao"], r["calorias"], r["quantidade"], r["estoque_minimo"]),
                    tags=(tag,)
                )

            tree.tag_configure("baixo", background="red", foreground="white")

    loadcomidastree()  # Carrega a lista inicial sem filtro

    # Frame para botões de edição e exclusão
    btns = ttk.Frame(app, padding=6)
    btns.pack(fill="x")
    ttk.Button(btns, text="Editar", command=lambda: comidaeditar(app, tree)).pack(side="left", padx=6)
    ttk.Button(btns, text="Excluir", command=lambda: comidaexcluir(app, tree)).pack(side="left", padx=6)

def comidanova(app):
    # Exibe o formulário para cadastro de nova comida
    comidaform(app)

def comidaeditar(app, tree):
    # Edição da comida selecionada
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Atenção", "Selecione uma comida para editar.")
        return
    cid = tree.item(sel[0])["values"][0]
    with getconnection() as conn:
        row = conn.execute("SELECT * FROM comidas WHERE id=?", (cid,)).fetchone()
        if row:
            comidaform(app, existing=row)

def comidaexcluir(app, tree):
    # Excluir uma comida após confirmação, somente se não houver movimentações relacionadas
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Atenção", "Selecione uma comida para excluir.")
        return
    cid = tree.item(sel[0])["values"][0]
    with getconnection() as conn:
        cur = conn.execute("SELECT COUNT(*) AS total FROM movimentacoes WHERE comida_id=?", (cid,))
        total = cur.fetchone()["total"]
        if total > 0:
            messagebox.showwarning("Aviso", "Não é possível excluir! Existem movimentações registradas para esta comida.")
            return
    if messagebox.askyesno("Confirmar", "Deseja realmente excluir a comida selecionada?"):
        with getconnection() as conn:
            conn.execute("DELETE FROM comidas WHERE id=?", (cid,))
        showcomidas(app)

def comidaform(app, existing=None):
    # Janela para cadastro ou edição de comida, preenchida se existing for passada
    win = tk.Toplevel(app)
    win.title("Comida Nordestina")
    centralizarjanela(win, 500, 550)

    # Campos a serem preenchidos
    labels = [
        "nome", "descricao", "categoria", "origem", "ingredientes", "porcao",
        "calorias", "quantidade", "estoque_minimo"
    ]

    # Map de nomes exibidos para os campos
    labelspt = {
        "nome": "Nome", "descricao": "Descrição", "categoria": "Categoria", "origem": "Origem", "ingredientes": "Ingredientes",
        "porcao": "Porção", "calorias": "Calorias", "quantidade": "Quantidade", "estoque_minimo": "Estoque Mínimo"
    }

    fields = {}
    for i, key in enumerate(labels):
        ttk.Label(win, text=labelspt[key]).grid(column=0, row=i, sticky="e", padx=6, pady=4)
        ent = ttk.Entry(win, width=40)
        ent.grid(column=1, row=i, padx=6, pady=4, sticky="we")
        fields[key] = ent

        # Se for edição, insere os dados já existentes nos campos
        if existing:
            ent.insert(0, str(existing[key]) if existing[key] is not None else "")

    def save():
        # Função para salvar os dados no banco, após validação
        data = {k: fields[k].get().strip() for k in labels}

        if not data["nome"]:
            messagebox.showwarning("Validação", "Nome obrigatório.")
            return

        try:
            calorias = float(data["calorias"]) if data["calorias"] else 0.0
            quantidade = int(data["quantidade"]) if data["quantidade"] else 0
            estoque_minimo = int(data["estoque_minimo"]) if data["estoque_minimo"] else 0
        except:
            messagebox.showwarning("Validação", "Calorias, Quantidade ou Estoque mínimo inválidos.")
            return

        with getconnection() as conn:
            if existing:
                # Atualiza registro existente
                conn.execute("""
                    UPDATE comidas SET nome=?, descricao=?, categoria=?, origem=?, ingredientes=?, porcao=?, calorias=?, quantidade=?, estoque_minimo=? WHERE id=?
                """, (data["nome"], data["descricao"], data["categoria"], data["origem"], data["ingredientes"], data["porcao"], calorias, quantidade, estoque_minimo, existing["id"]))
            else:
                # Insere novo registro no banco
                conn.execute("""
                    INSERT INTO comidas (nome, descricao, categoria, origem, ingredientes, porcao, calorias, quantidade, estoque_minimo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data["nome"], data["descricao"], data["categoria"], data["origem"], data["ingredientes"], data["porcao"], calorias, quantidade, estoque_minimo))

        win.destroy()  # Fecha janela do formulário
        showcomidas(app)  # Atualiza a listagem da tela principal
        messagebox.showinfo("Sucesso", "Comida salva com sucesso.")

    ttk.Button(win, text="Salvar", command=save).grid(column=0, row=len(labels), columnspan=2, pady=10)
