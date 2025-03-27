import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import adm
from config import bot
import config
import pyodbc

users = dict()

user_id= ''  #7287623121
valor_nome = ''
valor_idade = int
valor_sexo = ''
valor_cpf = ''
valor_sangue = ''

def conectarSql():

    server = "localhost"
    driver = "MySQL ODBC 9.2 ANSI Driver"
    port = 3306
    database = "botdoacao"
    user = "root"
    senha = ''

    conexao = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};USER={user};PASSWORD={senha};" #cria conexão
    )
    cursor = conexao.cursor()  # cria cursor
    return conexao, cursor




#Verifica a situação do usuário (adm, cadastrado, novo usuário)
def verificar_id(mensagem):
    global user_id
    msg_inicial = mensagem.text
    user_id = str(mensagem.from_user.id)
    config.nome_usuario = mensagem.chat.first_name #armazena o nome do usuário em 'config'
    cursor, conexao = conectarSql()
    cursor_guia = cursor.execute('SELECT USER_ID FROM USUARIOS')
    resultado = cursor_guia .fetchall()  #captura todas as linhas encontradas
    tabela_usuarios =[item for tupla in resultado for item in tupla]  # tira as tuplas do resultado e deixa somente em lista

    cursor_guia = cursor.execute('SELECT ID_ADM FROM ADMS')
    resultado = cursor_guia. fetchall()
    tabela_adms = [item for tupla in resultado for item in tupla]
    conexao.close()

    if msg_inicial=='/start' and user_id in tabela_adms:  #se o usuário for um adm, direciona para 'adm'
        adm.ola_adm(mensagem)

    elif msg_inicial=='/start' and user_id not in tabela_usuarios and user_id not in tabela_adms:  # se não estiver no banco e não for adm, cadastra o usuário
        return True

    elif user_id in tabela_usuarios and user_id not in tabela_adms: #usuário já cadastrado
        cadastrado_2(mensagem)


##==CADASTRO

#Boas Vindas
@bot.message_handler(func=verificar_id)
def boas_vindas(mensagem):
    users['id'] = user_id
    menu = InlineKeyboardMarkup() #cria o menu de botões
    botao_cadastro = InlineKeyboardButton('Cadastrar', callback_data='cadastro')
    menu.add(botao_cadastro)
    bot.send_message(mensagem.chat.id, f'Bem vindo *{config.nome_usuario}*! Vamos começar seu cadastro, clique no botão:', parse_mode='Markdown', reply_markup=menu)


#Nome
@bot.callback_query_handler(func=lambda call: call.data in ['cadastro']) #lê o valor do botão e só aceita 'cadastro'
def nome(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None) #apaga o último após ser pressionado
    bot.send_message(call.message.chat.id, 'Qual o seu nome completo?')
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, exibir_botao_nome)   #espera a proxima mensagem e após ela chama a função 'exibir_botao_nome'

def exibir_botao_nome(mensagem):
    global valor_nome
    valor_nome = mensagem.text
    if valor_nome.isnumeric()==True: #verifica se 'nome' tem números
        bot.send_message(mensagem.chat.id, '❌ Escolha um nome que contenha letras:')
        bot.register_next_step_handler(mensagem, exibir_botao_nome)

    else:
        menu = InlineKeyboardMarkup()
        botao_confirmar = InlineKeyboardButton('☑️ Confirmar', callback_data='1')
        botao_editar = InlineKeyboardButton('✏️ Editar', callback_data='2')
        menu.add(botao_confirmar, botao_editar)
        bot.send_message(mensagem.chat.id, f'Você confima o nome: "{mensagem.text}"?', reply_markup=menu)

@bot.callback_query_handler(func=lambda call: call.data in ['1','2'])
def analisar_nome(call):
    global valor_nome
    if call.data=='1': #call.data é o valor do botão
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        users['nome'] = valor_nome
        bot.send_message(call.message.chat.id, '✅ Nome confirmado')
        bot.send_message(call.message.chat.id, 'Qual o seu CPF?') #se confirmado, começa o proximo passo
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, exibir_botao_cpf)  #recebe a mensagem e manda para a função do 'cpf'
        print(users)

    if call.data=='2': #editar nome
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, 'Edite seu nome:')
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, editar_nome)


def editar_nome(mensagem):
    nome_editado = mensagem.text
    if nome_editado.isnumeric()==True:
        bot.send_message(mensagem.chat.id, '❌ Escolha um nome que contenha letras')
        bot.register_next_step_handler(mensagem, editar_nome)
    else:
        users['nome'] = nome_editado
        bot.send_message(mensagem.chat.id, f'✅ Nome editado para: "{nome_editado}"')
        bot.send_message(mensagem.chat.id, 'Qual o seu CPF?')
        bot.register_next_step_handler_by_chat_id(mensagem.chat.id, exibir_botao_cpf)
        print(users)

#Cpf

def exibir_botao_cpf(mensagem):
    global valor_cpf
    valor_cpf = mensagem.text
    if not valor_cpf.isnumeric(): #verifica se cpf não é um texto
        bot.send_message(mensagem.chat.id, '❌ Um CPF contém apenas números. Tente novamente:')
        bot.register_next_step_handler(mensagem, exibir_botao_cpf)

    elif not len(str(valor_cpf)) == 11: #verifica se tem 11 digitos
        bot.send_message(mensagem.chat.id, '❌ Um CPF contém 11 dígitos. Tente novamente:')
        bot.register_next_step_handler(mensagem, exibir_botao_cpf)

    else:
        menu =InlineKeyboardMarkup()
        botao7 = InlineKeyboardButton('☑️ Confirmar', callback_data='7')
        botao8 = InlineKeyboardButton('✏️ Editar', callback_data='8')
        menu.add(botao7, botao8)
        bot.send_message(mensagem.chat.id, f'Você confirma o CPF: "{valor_cpf}"?', reply_markup=menu)



@bot.callback_query_handler(func=lambda call: call.data in ['7', '8'])
def analisar_cpf(call):
    global valor_cpf
    if call.data=='7': #confirma
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        users['cpf'] = valor_cpf
        bot.send_message(call.message.chat.id, '✅ CPF confirmado')
        print(users)
        bot.send_message(call.message.chat.id, 'Qual a sua idade?')
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, exibir_botao_idade)

    elif call.data=='8': #edita
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, 'Edite seu CPF:')
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, editar_cpf)

def editar_cpf(mensagem):
    cpf_editado = mensagem.text
    if not cpf_editado.isnumeric():
        bot.send_message(mensagem.chat.id, '❌ Um CPF contém apenas números. Tente novamente:')
        bot.register_next_step_handler(mensagem, editar_cpf)

    elif not len(str(cpf_editado)) == 11:
        bot.send_message(mensagem.chat.id, '❌ Um CPF contém 11 digitos. Tente novamente:')
        bot.register_next_step_handler(mensagem, editar_cpf)

    else:
        users['cpf'] = cpf_editado
        bot.send_message(mensagem.chat.id, f'✅ CPF editado para: "{cpf_editado}"')
        print(users)
        bot.send_message(mensagem.chat.id, 'Qual a sua idade?')
        bot.register_next_step_handler(mensagem, exibir_botao_idade)


#Idade

def exibir_botao_idade(mensagem):
    global valor_idade
    valor_idade = mensagem.text
    if not valor_idade.isnumeric():  #verifica se idade é um número
        bot.send_message(mensagem.chat.id, '❌ Idade inválida, use apenas números:')
        bot.register_next_step_handler(mensagem, exibir_botao_idade)

    else:
        valor_idade = int(mensagem.text)
        menu = InlineKeyboardMarkup()
        botao3 = InlineKeyboardButton('☑️ Confirmar', callback_data='3')
        botao4  = InlineKeyboardButton('✏️ Editar', callback_data='4')
        menu.add(botao3, botao4)
        bot.send_message(mensagem.chat.id, f'Você confima a idade de: "{valor_idade} anos"?', reply_markup=menu)


@bot.callback_query_handler(func=lambda call: call.data in ['3', '4'])
def analisar_idade(call):
    global valor_idade
    if call.data=='3' and valor_idade<16:   #menor de 16 leva para o inicio
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, '❌ Menores de 16 não podem doar. Aperte aqui para voltar: /start ')
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, menor_16)

    if call.data=='3' and valor_idade>16:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        users['idade'] = valor_idade
        bot.send_message(call.message.chat.id, '✅ Idade confimada')
        print(users)
        sexo(call)

    if call.data=='4': #editar
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, 'Edite sua idade:')
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, editar_idade)

def menor_16(mensagem): #garante que o usuário vai voltar para o inicio
    if mensagem.text!='/start':
        bot.send_message(mensagem.chat.id, '❌ Menores de 16 não podem doar. Aperte aqui para voltar: /start ')
        bot.register_next_step_handler_by_chat_id(mensagem.chat.id, menor_16)
    elif mensagem.text=='/start':
        boas_vindas(mensagem)

def editar_idade(mensagem):
    idade_editada = int(mensagem.text)
    if idade_editada < 16:
        bot.send_message(mensagem.chat.id, '❌ Menores de 16 não podem doar. Aperte aqui para voltar: /start ')
        bot.register_next_step_handler_by_chat_id(mensagem.chat.id, menor_16)

    else:
        users['idade'] = idade_editada
        bot.send_message(mensagem.chat.id, f'✅ Idade editada para: "{idade_editada} anos"')
        sexo2(mensagem)
    print(users)


#Gênero
def sexo(call):  #cria os botoes de sexo com parametro call (vindo de 'analisar_idade')
    menu = InlineKeyboardMarkup()
    botao_masculino = InlineKeyboardButton('Masculino', callback_data='Masculino')
    botao_feminino = InlineKeyboardButton('Feminino', callback_data='Feminino')
    menu.add(botao_masculino, botao_feminino)
    bot.send_message(call.message.chat.id, 'Qual o seu gênero?', reply_markup=menu)

def sexo2(mensagem): #cria os botoes de sexo com parametro mensagem (vindo de 'editar_mensagem')

    menu = InlineKeyboardMarkup()
    botao_masculino = InlineKeyboardButton('Masculino', callback_data='Masculino')
    botao_feminino = InlineKeyboardButton('Feminino', callback_data='Feminino')
    menu.add(botao_masculino, botao_feminino)
    bot.send_message(mensagem.chat.id, 'Qual o seu gênero?', reply_markup=menu)

@bot.callback_query_handler(func=lambda call: call.data in ['Masculino', 'Feminino']) #recebe valores de 'sexo' ou 'sexo2'
def exibir_botao_sexo(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    global valor_sexo
    valor_sexo = call.data
    menu = InlineKeyboardMarkup()
    botao5 = InlineKeyboardButton('☑️ Confirmar', callback_data='5')
    botao6 = InlineKeyboardButton('✏️ Editar', callback_data='6')
    menu.add(botao5, botao6)
    bot.send_message(call.message.chat.id, f'Você confirma o gênero: "{valor_sexo}"?', reply_markup=menu)

@bot.callback_query_handler(func=lambda call: call.data in ['5', '6'])
def confirmar_sexo(call):
    global valor_sexo
    if call.data=='5':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        users['sexo'] = valor_sexo
        bot.send_message(call.message.chat.id, f'✅ Gênero "{valor_sexo}" confirmado')
        print(users)
        tipo_sangue(call)

    if call.data=='6':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        menu = InlineKeyboardMarkup()
        botao_masculino = InlineKeyboardButton('Masculino', callback_data='masculino2')
        botao_feminino = InlineKeyboardButton('Feminino', callback_data='feminino2')
        menu.add(botao_masculino, botao_feminino)
        bot.send_message(call.message.chat.id, 'Edite o seu gênero:', reply_markup=menu)

@bot.callback_query_handler(func=lambda call: call.data in ['masculino2', 'feminino2']) #recebe os valores dos botões de edição
def editar_genero(call):
    if call.data=='masculino2':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        genero_editado = 'Masculino'

    elif call.data=='feminino2':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        genero_editado = 'Feminino'

    users['sexo'] = genero_editado
    bot.send_message(call.message.chat.id, f'✅ Gênero editado para: "{genero_editado}"')
    print(users)
    tipo_sangue(call)



#Tipo Sanguineo
def tipo_sangue(call):
    global valor_cidade
    menu = InlineKeyboardMarkup()
    botao_a_positivo = InlineKeyboardButton('A+', callback_data='A+')
    botao_a_negativo = InlineKeyboardButton('A-', callback_data='A-')
    botao_b_positivo = InlineKeyboardButton('B+', callback_data='B+')
    botao_b_negativo = InlineKeyboardButton('B-', callback_data='B-')
    botao_ab_positivo = InlineKeyboardButton('AB+', callback_data='AB+')
    botao_ab_negativo = InlineKeyboardButton('AB-', callback_data='AB-')
    botao_o_positivo = InlineKeyboardButton('O+', callback_data='O+')
    botao_o_negativo = InlineKeyboardButton('O-', callback_data='O-')

    menu.add(botao_a_positivo, botao_a_negativo,  botao_b_positivo, botao_b_negativo,  botao_ab_positivo,  botao_ab_negativo,  botao_o_positivo,  botao_o_negativo )

    bot.send_message(call.message.chat.id, 'Qual o seu tipo sanguíneo?', reply_markup=menu)  # ja comeca a idade pelo fato de ter o parametro 'call'


@bot.callback_query_handler(func=lambda call: call.data in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
def exibir_botao_sangue(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    global valor_sangue
    valor_sangue = call.data
    menu = InlineKeyboardMarkup()
    botao_confirma_sangue = InlineKeyboardButton('☑️ Confirmar', callback_data='confirma_sangue')
    botao_edita_sangue = InlineKeyboardButton('✏️ Editar', callback_data='edita_sangue')
    menu.add(botao_confirma_sangue, botao_edita_sangue)
    bot.send_message(call.message.chat.id, f'Você confirma o tipo sanguíneo: "{valor_sangue}"?', reply_markup=menu)

@bot.callback_query_handler(func=lambda call: call.data in ['confirma_sangue', 'edita_sangue'])
def confirma_sangue(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    global valor_sangue
    if call.data=='confirma_sangue':
        users['sangue'] = valor_sangue
        bot.send_message(call.message.chat.id, '✅ Tipo sanguíneo confirmado')
        print(users)
        hospital(call)

    else:  #editar
        menu = InlineKeyboardMarkup()
        botao_a_positivo = InlineKeyboardButton('A+', callback_data='A+_edit')
        botao_a_negativo = InlineKeyboardButton('A-', callback_data='A-_edit')
        botao_b_positivo = InlineKeyboardButton('B+', callback_data='B+_edit')
        botao_b_negativo = InlineKeyboardButton('B-', callback_data='B-_edit')
        botao_ab_positivo = InlineKeyboardButton('AB+', callback_data='AB+_edit')
        botao_ab_negativo = InlineKeyboardButton('AB-', callback_data='AB-_edit')
        botao_o_positivo = InlineKeyboardButton('O+', callback_data='O+_edit')
        botao_o_negativo = InlineKeyboardButton('O-', callback_data='O-_edit')

        menu.add(botao_a_positivo, botao_a_negativo, botao_b_positivo, botao_b_negativo, botao_ab_positivo,botao_ab_negativo, botao_o_positivo, botao_o_negativo)
        bot.send_message(call.message.chat.id, 'Edite o seu tipo sanguíneo:', reply_markup=menu)

@bot.callback_query_handler(func=lambda call: call.data in ['A+_edit', 'A-_edit', 'B+_edit', 'B-_edit', 'AB+_edit','AB-_edit', 'O+_edit','O-_edit'])
def editar_sangue(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    sangue_edit = call.data
    sangue_editado = sangue_edit.split('_')[0]
    print(sangue_editado)
    users['sangue'] = sangue_editado
    bot.send_message(call.message.chat.id, f'✅ Tipo sanguíneo editado para: "{sangue_editado}"')
    print(users)
    hospital(call)


#Ponto de coleta (hospital)
def hospital(call):
    menu = InlineKeyboardMarkup()
    botao_crer = InlineKeyboardButton(  'Hospital Crer - Setor Negrão de Lima', callback_data='Hospital CRER')
    botao_cais = InlineKeyboardButton('Cais Campinas - St. dos Funcionários', callback_data='Cais Campinas')
    botao_sama = InlineKeyboardButton('Hospital Samaritano - St. Coimbra', callback_data='Hospital SAMARITANO')
    botao_hgg = InlineKeyboardButton('Hospital Hgg - St. Oeste', callback_data='Hospital HGG')
    menu.add(botao_crer)
    menu.add(botao_cais)
    menu.add(botao_sama)
    menu.add(botao_hgg)
    bot.send_message(call.message.chat.id, f'Qual ponto de coleta está mais proximo de você?', reply_markup=menu)

@bot.callback_query_handler(func=lambda call: call.data in ['Hospital CRER', 'Cais Campinas', 'Hospital SAMARITANO', 'Hospital HGG'])
def exibir_botao_hospital(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    global valor_hospital
    valor_hospital = call.data
    menu = InlineKeyboardMarkup()
    botao_confirma_hospital = InlineKeyboardButton('☑️ Confirmar', callback_data='confirma_hospital')
    botao_edita_hospital = InlineKeyboardButton('✏️ Editar', callback_data='edita_hospital')
    menu.add(botao_confirma_hospital, botao_edita_hospital)
    if call.data=='Hospital CRER':
        bot.send_message(call.message.chat.id, f'''Você confirma o ponto de coleta: HOSPITAL CRER
        
📍Endereço: Av. Ver. José Monteiro, 1655 - Setor Negrão de Lima, Goiânia - GO, 74653-230''', reply_markup=menu)

    elif call.data=='Cais Campinas':
        bot.send_message(call.message.chat.id, f'''Você confirma o ponto de coleta: CAIS CAMPINAS
        
📍Endereço: R. P-26, 857 - St. dos Funcionários, Goiânia - GO''', reply_markup=menu)

    elif call.data == 'Hospital SAMARITANO':
        bot.send_message(call.message.chat.id, f'''Você confirma o ponto de coleta: HOSPITAL SAMARITANO
        
📍Endereço: Praça Walter Santos, 1 - Coimbra, Goiânia - GO, 74733-250''', reply_markup=menu)

    elif call.data == 'Hospital HGG':
        bot.send_message(call.message.chat.id, f'''Você confirma o ponto de coleta: HOSPITAL HGG
        
📍Endereço: Av. Anhanguera, 6479 - St. Oeste, Goiânia - GO, 74110-010''', reply_markup=menu)

@bot.callback_query_handler(func=lambda call: call.data in ['confirma_hospital', 'edita_hospital'])
def analise_sangue(call):
    if call.data=='confirma_hospital':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, f'✅ Ponto de coleta confirmado para: "{valor_hospital}"')
        users['hospital'] = valor_hospital
        botao_confirmar_cadastro(call)
    if call.data=='edita_hospital':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        menu = InlineKeyboardMarkup()
        botao_crer = InlineKeyboardButton('Hospital Crer - Setor Negrão de Lima', callback_data='Hospital CRER_edit ')
        botao_cais = InlineKeyboardButton('Cais Campinas - St. dos Funcionários', callback_data='Cais Campinas_edit')
        botao_sama = InlineKeyboardButton('Hospital Samaritano - St. Coimbra', callback_data='Hospital SAMARITANO_edit')
        botao_hgg = InlineKeyboardButton('Hospital Hgg - St. Oeste', callback_data='Hospital HGG_edit')
        menu.add(botao_crer)
        menu.add(botao_cais)
        menu.add(botao_sama)
        menu.add(botao_hgg)
        bot.send_message(call.message.chat.id, 'Edite seu ponto de coleta, confire o mais proximo de você:', reply_markup=menu)
@bot.callback_query_handler(func=lambda call: call.data in ['Hospital CRER_edit', 'Cais Campinas_edit', 'Hospital SAMARITANO_edit', 'Hospital HGG_edit'])
def editar_hospital(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    hospital_editado = call.data
    hospital_editado = hospital_editado.split('_')[0]
    print(hospital_editado)
    users['hospital'] = hospital_editado
    bot.send_message(call.message.chat.id, f'✅ Ponto de coleta editado para: "{hospital_editado}"' )
    botao_confirmar_cadastro(call)

#Confirmar cadastro

def botao_confirmar_cadastro(call):
    menu = InlineKeyboardMarkup()
    botao_confirmar = InlineKeyboardButton('☑️ Confirmar', callback_data='confirmar')
    botao_recomecar = InlineKeyboardButton('🔄 Recomeçar', callback_data='recomecar')
    menu.add(botao_confirmar, botao_recomecar)
    bot.send_message(call.message.chat.id,'Clique no botão para confirmar seu cadastro:', reply_markup=menu)

@bot.callback_query_handler(func=lambda call: call.data in ['confirmar', 'recomecar'])
def botao_confirmar_recomecar(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    if call.data=='confirmar':
        bot.send_message(call.message.chat.id, '✅ Cadastro concluido com sucesso!!')
        bot.send_message(call.message.chat.id, 'Avisaremos quando tiver doações disponiveis. ')
        print(users)
        salvar_no_banco(call)

    if call.data=='recomecar':
        bot.send_message(call.message.chat.id, 'Clique aqui para recomeçar: /start')
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, recomecar)

def recomecar(mensagem):
    resposta = mensagem.text
    if not resposta=='/start':
        bot.send_message(mensagem.chat.id, 'Clique aqui para recomeçar: /start')
        bot.register_next_step_handler(mensagem, recomecar)
    else:
        users.clear() #limpa o dicionario e volta ao começo
        boas_vindas(mensagem)

def salvar_no_banco(call):
    global users
    valores = (users['id'], users['nome'], users['idade'], users['cpf'], users['sexo'], users['sangue'], users['hospital'])
    cursor, conexao = conectarSql()
    cursor.execute(f"INSERT INTO USUARIOS (user_id, nome, idade, cpf, genero, tipo_sanguineo, hospital) VALUES (?, ?, ?, ?, ?, ?, ? )", valores)
    conexao.commit()
    conexao.close()


#Usuario cadastrado
def cadastrado_2(mensagem):
    bot.send_message(mensagem.chat.id, 'Avisaremos quando tiver doações disponiveis')


bot.polling() #mantém o bot rodando
