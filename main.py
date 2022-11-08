# TelegramBot
import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup
import sqlite3
from datetime import datetime
import time
import logging
import re

logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot('Your token here', parse_mode='html')
print('Bot connected')

database = sqlite3.connect('telebot_test.db', check_same_thread=False)
cursor = database.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users_of_bot(\n"
               "                       id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,\n"
               "                       date TIMESTAMP,\n"
               "                       name_u TEXT,\n"
               "                       lastname_u TEXT,\n"
               "                       email_u TEXT,\n"
               "                       chat_id TEXT)")

database.commit()
print('Database connected')


#Display columns in table
print('\nColumns in users_of_bot table: ')
datab = cursor.execute('''SELECT * FROM users_of_bot''')
for column in datab.description:
    print(column[0])

#Display data in columns
print('\nData in Columns of table users_of_bot: ')
datac = cursor.execute('''SELECT * FROM users_of_bot''')
for row in datac:
    print(row)

data = cursor.fetchall()
database.commit()
print(cursor.fetchall())
day = str(datetime.today())[:16]
print(day)

user_dict={}

class User:
    def __init__(self, name):
        self.name = name
        self.lastname = None
        self.email = None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 f' Hi there, {message.from_user.first_name} {message.from_user.last_name}'
                 f' You can do:\n'
                 f' * Say Hello\n'
                 f' * Ask for yours ID by taping "id"\n '
                 f' * Ask for a cute photo by taping "photo"\n'
                 f' * You can send me a photo as well!\n'
                 f' * Ask for "/help" if you want to see all functions\n'
                 f' * Start an inscription by taping "/rdv me" \n'
                 f' \nWhats your name? ')
    bot.register_next_step_handler(message, process_name_step)
    print('Message of welcome printed')

def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, "That's your last name?")
        bot.register_next_step_handler(msg, process_lastname_step)
    except Exception as e:
        bot.reply_to(message, 'Oooops')
    print('Name has given successfully', name, user_dict)

def process_lastname_step(message):
    try:
        chat_id = message.chat.id
        lastname = message.text
        user = user_dict[chat_id]
        user.lastname = lastname
        msg = bot.reply_to(message, "Tell me your email, please?")
        bot.register_next_step_handler(msg, process_email_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')
    print('Lastname has given successfully', lastname, user_dict)


def process_email_step(message):
    try:
        chat_id = message.chat.id
        email = message.text
        print(email)
        user = user_dict[chat_id]
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if re.search(regex, email):
            print("Valid Email")
            user.email = email
           # return True
        else:
            print("Invalid input")
            #return False
        print(user_dict)
        bot.reply_to(message, f'{chat_id} Nice to meet you, {user.name} {user.lastname}!'
                              f' And your email is: {user.email}')
    except Exception as e:
        print(e)
        bot.reply_to(message, 'oooops')
print(user_dict)
bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

@bot.message_handler(commands=['help'])
def send_help(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    bot.reply_to(message,
                 f' So my friend, {user.name} {user.lastname}'
                 f' You can do:\n'
                 f' * Say Hello\n'
                 f' * Ask for yours ID by taping "id"\n '
                 f' * Ask for a cute photo by taping "photo"\n'
                 f' * You can send me a photo as well!\n'
                 f' * Ask for "/help" if you want to see all functions\n'
                 f' * Start an inscription by taping "/rdv me" \n')

    print('Message of help sent')


@bot.message_handler(commands=['rdvme'])  # receiving text or command from user
def rdv_me(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    email = message.text
    mess = f'Thank you, {user.name} ' \
           f'{user.lastname} , for your inscription!\n'\
           f' I am working on it...'

    bot.send_message(message.chat.id, mess)
    time.sleep(5)
    # check and add in fields
    cursor.execute(f"SELECT chat_id FROM users_of_bot WHERE chat_id = {chat_id}")
    cursor.execute(f"SELECT * FROM users_of_bot ")
    data = cursor.fetchall()
    print(f"Current data is: {data}, chats id: {chat_id}")
    print('User selected')
    count_user = 250

    if data == []:
        count_user += 1
        user_id = count_user
        print(f"current user_id is: {user_id}")
        chat_id = [message.chat.id]
        the_day = str(datetime.today())[:16]
        try:
            name_u = user.name
            lastname_u = user.lastname
            email = user.email
        except:
            name_u = [message.from_user.first_name]
            lastname_u = [message.from_user.last_name]
            if lastname_u is None:
                lastname_u = 'John Doe'
            else:
                lastname_u = ['JohnDoe']
        print(the_day)
        print(name_u, lastname_u, chat_id, email, count_user)

        cursor.execute('INSERT INTO users_of_bot( date, name_u, lastname_u, email_u, chat_id) '
                       'VALUES (?, ?, ?, ?, ?)', (the_day, name_u[0], lastname_u[0], email[0], chat_id[0]))
        database.commit()
        print('User created')
        bot.send_message(message.chat.id, 'Great, you have been registered ! You can now see all option by typing /menu')
    else:
        chat_id = [message.chat.id]
        user_id = count_user
        print(f"current user_id is: {user_id}")
        bot.send_message(message.chat.id, f'I have yours IDs already!\nIt is: {chat_id} '
                                          f'You can now see all option by typing /menu ')
    print('User registered')
    print(data)
    database.close()

@bot.message_handler(commands=['website'])  # buttons creations
def website_button(message):
    print('CouCou')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Google it!", url='https://www.google.com/'))
    bot.send_message(message.chat.id, "If I don't know, you can find it here o____O", reply_markup=markup)
    print('Giving external link')

@bot.message_handler(commands=['menu'])  # buttons in a place of chat
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    registr = types.KeyboardButton('/rdvme')
    starts = types.KeyboardButton("/start")
    helpy = types.KeyboardButton('/help')
    weby = types.KeyboardButton('/website')
    markup.add(registr, starts, helpy, weby)
    bot.send_message(message.chat.id, 'There you go all my options ^^', reply_markup=markup)
    print('Trying to button ')

@bot.message_handler(content_types=['text'])
def get_user_text(message):  # giving answer to specified message
    if message.text == 'Hello':
        bot.send_message(message.chat.id, f'So Hello you too, my friend, {message.from_user.first_name} !')
        print('Greeting user')
    elif message.text == "id":  # to ask for ID number
        bot.send_message(message.chat.id, f'Your ID, my friend, is: {message.from_user.id} ')
        print('Sending users ID')
    elif message.text == 'photo':
        photo = open('photo1651333196.jpeg', 'rb') #photo must to be in same folder as this script
        bot.send_photo(message.chat.id, photo, 'Look what I got!')
        print('Sending photo to user')
    else:
        bot.send_message(message.chat.id, "I didn't get it -____-")
        print("Don't understand the question")


# to see chats ID commands use
# def get_user_text(message):
#   bot.send_message(message.chat.id, message)
#   after can add specified function like message.text to use .text command (example lines 14-16)

@bot.message_handler(content_types=['photo'])  # not receiving photos ???? only the same as received from bot
def get_user_photo(message: object) -> object:
    bot.send_message(message.chat.id, 'Wow, very cool photo, my friend!')
    print('Receiving photo from user')








bot.polling(none_stop=True)  # everytime running mode
