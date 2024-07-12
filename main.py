import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter import Toplevel, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os
from datetime import datetime

# Definição das classes Exercicio, SessaoTreino e Usuario
class Exercicio:
    def __init__(self, nome):
        self.nome = nome
        self.historico = []

    def adicionar_treino(self, series, repeticoes, peso):
        self.historico.append((series, repeticoes, peso))

    def total_kg(self):
        return sum(series * repeticoes * peso for series, repeticoes, peso in self.historico)


class SessaoTreino:
    def __init__(self, tipo, data):
        self.tipo = tipo
        self.data = data
        self.exercicios = []

    def adicionar_exercicio(self, exercicio):
        self.exercicios.append(exercicio)

    def total_kg_sessao(self):
        return sum(ex.total_kg() for ex in self.exercicios)


class Usuario:
    def __init__(self):
        self.sessoes = []

    def adicionar_sessao(self, tipo, data):
        sessao = SessaoTreino(tipo, data)
        self.sessoes.append(sessao)
        return sessao

    def adicionar_exercicio_na_sessao(self, sessao, exercicio):
        sessao.adicionar_exercicio(exercicio)

    def obter_sessoes(self):
        return self.sessoes

    def obter_sessoes_por_tipo(self, tipo):
        return [sessao for sessao in self.sessoes if sessao.tipo == tipo]


# Funções de persistência de dados
def salvar_dados(usuario):
    dados = {
        'sessoes': []
    }
    for sessao in usuario.sessoes:
        exercicios = []
        for exercicio in sessao.exercicios:
            historico = exercicio.historico
            exercicios.append({
                'nome': exercicio.nome,
                'historico': historico
            })
        dados['sessoes'].append({
            'tipo': sessao.tipo,
            'data': sessao.data,
            'exercicios': exercicios
        })

    with open('dados_treino.json', 'w') as f:
        json.dump(dados, f)


def carregar_dados(usuario):
    try:
        with open('dados_treino.json', 'r') as f:
            dados = json.load(f)
            for sessao_dados in dados['sessoes']:
                sessao = SessaoTreino(sessao_dados['tipo'], sessao_dados['data'])
                for exercicio_dados in sessao_dados['exercicios']:
                    exercicio = Exercicio(exercicio_dados['nome'])
                    exercicio.historico = exercicio_dados['historico']
                    sessao.adicionar_exercicio(exercicio)
                usuario.sessoes.append(sessao)
    except FileNotFoundError:
        pass






def apagar_todos_os_dados():
    usuario.sessoes = []
    if os.path.exists('dados_treino.json'):
        os.remove('dados_treino.json')
    atualizar_sessoes()
    desenhar_grafico_kg_por_sessao()


# Função para carregar a fonte Poppins
def carregar_fonte_poppins():
    if not os.path.exists('Poppins-Regular.ttf'):
        raise FileNotFoundError("Por favor, baixe a fonte Poppins e coloque no mesmo diretório do script.")

    root.tk.call('font', 'create', 'Poppins', '-family', 'Poppins', '-size', '12')
    return 'Poppins'


# Interface de visualização de dados
def desenhar_grafico_kg_por_sessao(tipo_treino=None):
    fig, ax = plt.subplots(figsize=(10, 5))

    if tipo_treino:
        sessoes = usuario.obter_sessoes_por_tipo(tipo_treino)
        titulo = f'Kg Levantados nas Sessões de {tipo_treino}'
    else:
        sessoes = usuario.sessoes
        titulo = 'Kg Levantados por Sessão de Treino'

    datas_sessoes = [datetime.strptime(sessao.data, "%d/%m/%Y") for sessao in sessoes]
    kgs_totais = [sessao.total_kg_sessao() for sessao in sessoes]

    ax.plot(datas_sessoes, kgs_totais, marker='o', linestyle='-', color='skyblue')
    ax.set_xlabel('Data da Sessão')
    ax.set_ylabel('Kg Levantados')
    ax.set_title(titulo)

    for widget in frame_grafico.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack()



def adicionar_sessao_interface():
    def salvar_sessao():
        tipo = tipo_treino_var.get()
        data = data_treino.get()
        if not tipo or not data:
            messagebox.showwarning("Dados Incompletos", "Por favor, selecione o tipo de treino e insira a data.")
            return
        usuario.adicionar_sessao(tipo, data)
        atualizar_sessoes()
        salvar_dados(usuario)
        desenhar_grafico_kg_por_sessao()
        janela_adicionar_sessao.destroy()

    janela_adicionar_sessao = Toplevel()
    janela_adicionar_sessao.title("Adicionar Sessão de Treino")

    tk.Label(janela_adicionar_sessao, text="Tipo de Treino:", font=('Poppins', 12)).grid(row=0, column=0)
    tipo_treino_var = tk.StringVar()
    tipos_treino = ["Peito", "Perna", "Costas", "Posterior", "Braços"]
    tipo_treino_menu = ttk.OptionMenu(janela_adicionar_sessao, tipo_treino_var, tipos_treino[0], *tipos_treino)
    tipo_treino_menu.grid(row=0, column=1)

    tk.Label(janela_adicionar_sessao, text="Data da Sessão (DD/MM/YYYY):", font=('Poppins', 12)).grid(row=1, column=0)
    data_treino = tk.Entry(janela_adicionar_sessao, font=('Poppins', 12))
    data_treino.grid(row=1, column=1)

    tk.Button(janela_adicionar_sessao, text="Salvar", command=salvar_sessao, font=('Poppins', 12)).grid(row=2, column=1)



def atualizar_sessoes():
    sessoes_menu['menu'].delete(0, 'end')
    for sessao in usuario.sessoes:
        sessoes_menu['menu'].add_command(label=f"{sessao.tipo} ({sessao.data})",
                                         command=lambda sessao=sessao: session_var.set(sessao))
    session_var.set('')



def inicializar_interface():
    carregar_dados(usuario)
    atualizar_sessoes()
    desenhar_grafico_kg_por_sessao()


def adicionar_exercicio_interface(sessao):
    if not sessao:
        return

    def salvar_exercicio():
        nome = nome_exercicio.get()
        if not nome:
            messagebox.showwarning("Dados Incompletos", "Por favor, insira o nome do exercício.")
            return
        exercicio = Exercicio(nome)

        series = []
        for frame in series_frames:
            series_entry = frame[0]
            repeticoes_entry = frame[1]
            peso_entry = frame[2]
            try:
                series_val = int(series_entry.get())
                repeticoes_val = int(repeticoes_entry.get())
                peso_val = float(peso_entry.get())
                series.append((series_val, repeticoes_val, peso_val))
            except ValueError:
                messagebox.showwarning("Dados Inválidos", "Por favor, insira valores válidos para séries, repetições e peso.")
                return

        for s in series:
            exercicio.adicionar_treino(*s)

        usuario.adicionar_exercicio_na_sessao(sessao, exercicio)
        salvar_dados(usuario)
        desenhar_grafico_kg_por_sessao()
        janela_adicionar.destroy()

    janela_adicionar = Toplevel()
    janela_adicionar.title("Adicionar Exercício")

    tk.Label(janela_adicionar, text="Nome do Exercício:", font=('Poppins', 12)).grid(row=0, column=0)
    nome_exercicio = tk.Entry(janela_adicionar, font=('Poppins', 12))
    nome_exercicio.grid(row=0, column=1)

    series_frames = []

    def adicionar_serie():
        row = len(series_frames) + 1
        tk.Label(janela_adicionar, text=f"Série {row}:", font=('Poppins', 12)).grid(row=row, column=0)
        series_entry = tk.Entry(janela_adicionar, font=('Poppins', 12))
        series_entry.grid(row=row, column=1)
        repeticoes_entry = tk.Entry(janela_adicionar, font=('Poppins', 12))
        repeticoes_entry.grid(row=row, column=2)
        peso_entry = tk.Entry(janela_adicionar, font=('Poppins', 12))
        peso_entry.grid(row=row, column=3)
        series_frames.append((series_entry, repeticoes_entry, peso_entry))

    adicionar_serie()  # Adiciona a primeira série por padrão

    tk.Button(janela_adicionar, text="Adicionar Série", command=adicionar_serie, font=('Poppins', 12)).grid(row=1, column=4)
    tk.Button(janela_adicionar, text="Salvar", command=salvar_exercicio, font=('Poppins', 12)).grid(row=2, column=4)



def mostrar_tabela():
    janela_tabela = Toplevel()
    janela_tabela.title("Tabela de Exercícios")

    colunas = ("Sessão", "Data", "Exercício", "Séries", "Repetições", "Peso")
    tabela = ttk.Treeview(janela_tabela, columns=colunas, show='headings')
    for col in colunas:
        tabela.heading(col, text=col)
    tabela.pack(fill=tk.BOTH, expand=True)

    for sessao in usuario.obter_sessoes():
        for exercicio in sessao.exercicios:
            for series, repeticoes, peso in exercicio.historico:
                tabela.insert("", "end", values=(sessao.tipo, sessao.data, exercicio.nome, series, repeticoes, peso))


# Interface principal
root = tk.Tk()
root.title("Controle de Treinos na Academia")
root.geometry("1200x800")

# Carregar a fonte Poppins
fonte_poppins = carregar_fonte_poppins()

# Inicializar o objeto Usuario antes de usá-lo
usuario = Usuario()

# Frame principal
frame_principal = tk.Frame(root, padx=10, pady=10)
frame_principal.pack(fill=tk.BOTH, expand=True)

# Frame para o gráfico
frame_grafico = tk.Frame(frame_principal)
frame_grafico.grid(row=0, column=0, rowspan=6, padx=10, pady=10)

# Botão para adicionar sessão de treino
botao_adicionar_sessao = tk.Button(frame_principal, text="Adicionar Sessão de Treino",
                                   command=adicionar_sessao_interface, font=('Poppins', 12))
botao_adicionar_sessao.grid(row=0, column=1, padx=10, pady=10)

# Botão para gerar tabela
botao_gerar_tabela = tk.Button(frame_principal, text="Gerar Tabela", command=mostrar_tabela, font=('Poppins', 12))
botao_gerar_tabela.grid(row=0, column=2, padx=10, pady=10)

# Dropdown para selecionar sessão de treino
session_var = tk.StringVar()
sessoes_menu = ttk.OptionMenu(frame_principal, session_var, '', *[])
sessoes_menu.grid(row=1, column=1, columnspan=2, padx=10, pady=10)

# Botão para gerar gráfico por sessão de treino
tipo_treino_var_grafico = tk.StringVar()
tipo_treino_menu_grafico = ttk.OptionMenu(frame_principal, tipo_treino_var_grafico, 'Todos', 'Peito', 'Perna', 'Costas',
                                          'Posterior', 'Braços')
tipo_treino_menu_grafico.grid(row=2, column=1, padx=10, pady=10)

botao_gerar_grafico = tk.Button(frame_principal, text="Gerar Gráfico", command=lambda: desenhar_grafico_kg_por_sessao(
    tipo_treino_var_grafico.get() if tipo_treino_var_grafico.get() != 'Todos' else None), font=('Poppins', 12))
botao_gerar_grafico.grid(row=2, column=2, padx=10, pady=10)

# Botão para adicionar exercício
botao_adicionar_exercicio = tk.Button(frame_principal, text="Adicionar Exercício",
                                      command=lambda: adicionar_exercicio_interface(session_var.get()),
                                      font=('Poppins', 12))
botao_adicionar_exercicio.grid(row=3, column=1, padx=10, pady=10)

# Botão para apagar todos os registros
botao_apagar_registros = tk.Button(frame_principal, text="Apagar Todos os Registros", command=apagar_todos_os_dados,
                                   font=('Poppins', 12))
botao_apagar_registros.grid(row=3, column=2, padx=10, pady=10)

# Inicializar a interface
inicializar_interface()

root.mainloop()
