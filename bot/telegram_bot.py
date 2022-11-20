import telebot
import random
from telebot import types # для указание типов
from collections import defaultdict
import requests
from telegram_bot_admin_check import *



# Создаем бота
bot = telebot.TeleBot('')

messages = ['', '']  # для отлова ролей
admin_state = [0, '']  # для админа
trend = ['', '']


# Команда start
@bot.message_handler(commands=["start"])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Генеральный директор")
    btn2 = types.KeyboardButton("Бухгалтер")


    # проверяем на админа
    admin_state[0] = admin_check(message.from_user.id)
    if(admin_state[0]):
        btn4 = types.KeyboardButton("Показать тренды/инсайты")
        markup.add(btn1, btn2, btn4)
    else:
        markup.add(btn1, btn2)


    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я тестовый бот для вывода новостей!".format(
                         message.from_user), reply_markup=markup)



# Получение сообщений от юзера
@bot.message_handler(content_types=['text'])
def func(message):


    # =============================
    # тренды/инсайды
    # =============================
    # админ функционал по трендам
    if(message.text == "Создать тренд/инсайт" and admin_state[0]):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add()
        bot.send_message(message.chat.id, text="Введите тренд", reply_markup=markup)
        admin_state[1] = "Создать тренд"
    # ввод тренда
    elif(admin_state[0] and admin_state[1] == "Создать тренд"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add()
        trend[0] = message.text
        admin_state[1] = 'Введите инсайт'
        bot.send_message(message.chat.id, text="Введите инсайт", reply_markup=markup)
    # ввод инсайда
    elif(admin_state[0] and admin_state[1] == "Введите инсайт"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add()
        trend[1] = message.text
        admin_state[1] = ''
        res = requests.post("http://127.0.0.1:3000/api/post_trend", json={"trend":trend[0], "inside":trend[1]})
        bot.send_message(message.chat.id, text="Добавлено\nТренд: " + trend[0] + "\nИнсайт: " + trend[1], reply_markup=markup)
        trend[0] = ""
        trend[1] = ""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Генеральный директор")
        btn2 = types.KeyboardButton("Бухгалтер")
        # проверяем на админа
        if(admin_state[0]):
            btn4 = types.KeyboardButton("Показать тренды/инсайты")
            markup.add(btn1, btn2, btn4)
            bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)
            markup.add(btn1, btn2)



    # =============================
    # аналитика
    # =============================
    elif(admin_state[0] and message.text == "Показать тренды/инсайты"):
        res = requests.get("http://127.0.0.1:3000/api/get_analis")
        res = res.json()
        for i in range(10):
            message_news = "Тренд №" + str(i+1)
            message_news += "\nОбщие число новостей: " + str(res[i][11])
            message_news += "\nКлюченвые слова: " \
                    "{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}".format(
                str(res[i][1]), str(res[i][2]), str(res[i][3]), str(res[i][4]), str(res[i][5]),
                str(res[i][6]), str(res[i][7]), str(res[i][8]), str(res[i][9]), str(res[i][10])
            )
            message_news += "\nТренд: " + str(res[i][12])
            message_news += "\nИнсайт: " + str(res[i][13])
            bot.send_message(message.chat.id, message_news)






    # выбор роли
    elif(message.text == "Генеральный директор" or message.text == "Бухгалтер"):
        if(message.text == "Генеральный директор"):
            messages[0] = "1"
            messages[1] = "Генеральный директор"
        elif(message.text == "Бухгалтер"):
            messages[0] = "0"
            messages[1] = "Бухгалтер"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Новости")
        btn2 = types.KeyboardButton("Новости по датам")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, back)
        bot.send_message(message.chat.id, text="Выберите действие", reply_markup=markup)




    # показ новостей
    elif (message.text == "Новости"):
        if(messages[0] == "0" or messages[0] == "1"):
            res = requests.get("http://127.0.0.1:3000/api/main/" + messages[0] +"/0")
            res = res.json()
            for body_news in res:
                message_news = "НОВОСТИ ДЛЯ " + messages[1].upper() + "\n\n"
                if(body_news[2] is None):
                    source_name = ""
                else:
                    source_name = body_news[2]
                message_news += "📰 Новость: " + body_news[0] + "\n\n Источник: " + source_name + "\n Дата: " +\
                                body_news[3] + "\n Тема: " + body_news[5] + "\n\nОписание: " + body_news[4] +\
                                "\n\n Полную информацию можно посмотреть здесь: " + body_news[1] + "\n\n\n\n\n"
                bot.send_message(message.chat.id, message_news)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton("Генеральный директор")
            button2 = types.KeyboardButton("Бухгалтер")
            markup.add(button1, button2)
            bot.send_message(message.chat.id, text="Вам нужно выбрать роль", reply_markup=markup)



    # Показ новостей по датам ( не работает)
    elif message.text == "Новости по датам":
        if(messages[0] == "score_role_2" or messages[0] == "score_role_1"):
            bot.send_message(message.chat.id, text="тут будет запрос к апи по датам" + messages[0])
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton("Генеральный директор")
            button2 = types.KeyboardButton("Бухгалтер")
            markup.add(button1, button2)
            bot.send_message(message.chat.id, text="Вам нужно выбрать роль", reply_markup=markup)




    # показ трендов
    elif message.text == "Тренды/Инсайты":
        res = requests.get("http://127.0.0.1:3000/api/get_trend")
        res = res.json()
        messag = "Тренд: " + res[0][0] + "\nИнсайт: " + res[0][1]

        bot.send_message(message.chat.id, text=messag)





    # Вернуться в главное меню
    elif(message.text == "Вернуться в главное меню"):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Генеральный директор")
        btn2 = types.KeyboardButton("Бухгалтер")



        # проверяем на админа
        if(admin_state[0]):
            btn4 = types.KeyboardButton("Показать тренды/инсайты")
            markup.add(btn1, btn2, btn4)
            bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)
        else:
            markup.add(btn1, btn2)
            bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)






    # неизвестная команда
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммирован..")


# Запускаем бота
bot.polling(none_stop=True, interval=0)