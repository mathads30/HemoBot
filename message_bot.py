import pyodbc
from config import bot
import config
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
lista_ids = []
count = 0
def conectarSql():

    server = "localhost"
    driver = "MySQL ODBC 9.2 ANSI Driver"
    port = 3306
    database = "botdoacao"
    user = "root"
    senha = ''

    conexao = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};USER={user};PASSWORD={senha};" #cria conexao
    )
    cursor = conexao.cursor()
    return conexao, cursor

def analisar_descricao():
    if config.solicitacao['hospital'] == 'Hospital CRER':
        descricao = '''--*HOSPITAL CRER*

📍*Endereço*: Av. Ver. José Monteiro, 1655 - Setor Negrão de Lima, Goiânia - GO, 74653-230'''
        return descricao

    if config.solicitacao['hospital'] == 'Cais Campinas':
        descricao = '''--*CAIS CAMPINAS*
 
📍Endereço: R. P-26, 857 - St. dos Funcionários, Goiânia - GO'''
        return descricao

    if config.solicitacao['hospital'] == 'Hospital SAMARITANO':
        descricao = '''--*HOSPITAL SAMARITANO*

📍Endereço: Praça Walter Santos, 1 - Coimbra, Goiânia - GO, 74733-250'''
        return descricao

    if config.solicitacao['hospital'] == 'Hospital HGG':
        descricao = '''--*HOSPITAL HGG*

📍Endereço: Av. Anhanguera, 6479 - St. Oeste, Goiânia - GO, 74110-010'''
        return descricao

def verificar_doacao_disponivel(call):
    global lista_ids
    cursor, conexao = conectarSql()
    cursor_guia = cursor.execute(f"SELECT USER_ID FROM USUARIOS WHERE HOSPITAL = '{config.solicitacao['hospital']}' AND TIPO_SANGUINEO = '{config.solicitacao['tipo_sanguineo']}';")
    resultado = cursor_guia.fetchall()
    lista_ids = [item for tupla in resultado for item in tupla]
    mandar_mensagem(call)


def mandar_mensagem(call):
    global lista_ids, count
    for id in lista_ids:
        count+=1
        descricao_hospital = analisar_descricao()
        bot.send_message(id, f'''Doação disponivel perto de você!🥳
        
{descricao_hospital}

--Acontecerá na *DATA: {config.solicitacao['data']}*
Entre *11:00* e *18:00* horas da tarde.

                    *----REQUISITOS----*
                    
✔️ Ter entre 16 e 69 anos
✔️ Pesar mais de 50 kg
✔️ Estar em boas condições de saúde
✔️ Apresentar um documento oficial com foto
✔️ Não estar em jejum, mas evitar alimentos gordurosos nas horas que antecedem a doação
✔️ Não ter consumido bebidas alcoólicas nas últimas 12 horas
''', parse_mode='Markdown')





