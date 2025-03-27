import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot
import config
import message_bot


lista_hosp = {'1': 'Hospital CRER',  '2': 'Cais Campinas',  '3': 'Hospital SAMARITANO', '4': 'Hospital HGG'} #lista dos pontos de coleta
lista_sangue = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']  #lista dos tipos sanguineos
hospital = ''
tipo_sanguineo = ''
data = ''
def ola_adm(mensagem):
    menu = InlineKeyboardMarkup()
    botao_adm = InlineKeyboardButton('Criar solicitação', callback_data='iniciar_solicitacao')
    menu.add(botao_adm)
    bot.send_message(mensagem.chat.id,f'Ola {config.nome_usuario}.Você está no modo Administrador, clique no botão para criar uma solicitação:', reply_markup=menu)

#Hospital (ponto de coleta)
@bot.callback_query_handler(func=lambda call:call.data in ['iniciar_solicitacao'])
def salvar(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, '''Escolha um ponto de coleta pelo número:
1 - Hospital CRER
2 - Cais Campinas
3 - Hospital SAMARITANO
4 - Hospital HGG''')
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, verificar_hosp)

def verificar_hosp(mensagem):
    global hospital
    resp_hosp = mensagem.text
    if resp_hosp in lista_hosp.keys():
        hospital = lista_hosp[resp_hosp] #pega o valor do dicionario igual a 'resp_hosp'
        config.solicitacao['hospital'] = hospital
        bot.send_message(mensagem.chat.id, '''Qual o tipo sanguíneo?
- A+
- A-
- B+
- B-
- AB+
- AB-
- O+
- O-''')
        bot.register_next_step_handler(mensagem, tipo_sangue)

    elif resp_hosp not in ['1', '2', '3', '4']: #se não estiver na lista de hospitais
        bot.send_message(mensagem.chat.id, '❌ Resposta inválida')
        bot.register_next_step_handler(mensagem, verificar_hosp)

#Tipo sanguineo

def tipo_sangue(mensagem):
    global tipo_sanguineo
    text_tipo = mensagem.text
    if text_tipo in lista_sangue:
        tipo_sanguineo = text_tipo
        config.solicitacao['tipo_sanguineo'] = tipo_sanguineo
        bot.send_message(mensagem.chat.id, 'Em qual data vai ocorrer as doações? (formato: xx/xx/xxxx)')
        bot.register_next_step_handler(mensagem, data_solicitacao)
    else:
        bot.send_message(mensagem.chat.id, '❌ Não existe este tipo sanguíneo')
        bot.register_next_step_handler(mensagem, tipo_sangue)

#Data da solicitação
def data_solicitacao(mensagem):
    global data
    data = mensagem.text
    config.solicitacao['data'] = data
    menu_final(mensagem)

def menu_final(mensagem):
    menu = InlineKeyboardMarkup()
    botao_confirmar_adm = InlineKeyboardButton('☑️ Confirmar', callback_data='confirmar_adm')
    botao_recomeca_adm = InlineKeyboardButton('✏️ Recomecar', callback_data='recomecar_adm')
    menu.add(botao_confirmar_adm, botao_recomeca_adm)
    bot.send_message(mensagem.chat.id, 'Você deseja Confirmar ou Recomeçar a solicitação?', reply_markup=menu)
    print(config.solicitacao)

@bot.callback_query_handler(func=lambda call: call.data in ['confirmar_adm', 'recomecar_adm'])
def analisar_menu_final(call):
    if call.data=='confirmar_adm':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        message_bot.verificar_doacao_disponivel(call)
        bot.send_message(call.message.chat.id, f'''✅ Solicitação concluida com sucesso! 
        
Aviso enviado para {message_bot.count} usuarios.

Aperte aqui para voltar ao inicio: /start''')
        config.solicitacao.clear()
        print(config.solicitacao)
        message_bot.count=0
    elif call.data=='recomecar_adm':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, '❌ Solicitção cancelada. Aperte aqui para recomeçar: /start')
        config.solicitacao.clear()
        print(config.solicitacao)


