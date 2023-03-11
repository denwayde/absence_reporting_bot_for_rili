#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import aiogram
import datetime
import re
import openpyxl
#import aioschedule
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.utils.exceptions import BotBlocked

from database import DatabaseHandler
#from users_notifier import UsersNotifier
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
bot_dispatcher = Dispatcher(bot, storage=MemoryStorage())
db_handler = DatabaseHandler("mydatabase.db")

scheduler = AsyncIOScheduler(timezone = "Asia/Yekaterinburg")

persons = {
    # telegram_id: {
    #   user_name: '',
    #   corp: first or second,
    #   class_name: ''
    # }
}

choosen_class = ''
@bot_dispatcher.message_handler(commands=["start"])
async def start_message(message: types.Message):

    if bool(db_handler.get_data("SELECT * FROM teachers WHERE telega_id =?", (message.chat.id, ))) or bool(db_handler.get_data("SELECT * FROM admins WHERE telega_id =?", (message.chat.id, ))):
        await bot.send_message(message.from_user.id, f'Вы уже инициализированный пользователь бота. Скорее всего это сообщение пришло к Вам в результате того, что Вы почистили историю сообщении с ботом. Для востановления работы напишите сюда @Dinis_Rafikovich или удалите свои данные нажав /delete_user и авторизуйтесь заново нажав /start. ')
    else:
        reply = message.from_user.first_name
        await bot.send_message(message.from_user.id, f'Здравствуйте {reply}. Это телеграм бот предназначенный для сбора информации о посещаемости от классных руководителей и формирования быстрых отчетов о посещаемости для администрации.\nДля продолжения работы с ботом введите пароль, который Вам прислал @Dinis_Rafikovich')


@bot_dispatcher.message_handler(commands=['change_settings'])
async def change_settings(message: types.Message):
    d = datetime.datetime.now().strftime("%Y-%m-%d")
    if bool(db_handler.get_data("SELECT*FROM teachers WHERE telega_id = ?", (message.chat.id,))):
        db_handler.sql_operation_processing("DELETE FROM teachers WHERE telega_id=?", (message.chat.id,))
        if bool(db_handler.get_data("SELECT*FROM kuramshin_otchet WHERE telega_id = ? AND date = ?", (message.chat.id, d, ))):
                db_handler.sql_operation_processing("DELETE FROM kuramshin_otchet WHERE telega_id = ? AND date = ?", (message.chat.id, d, ))
    buttons = [
        types.InlineKeyboardButton(text="Классный руководитель", callback_data="cl_ruk"),
        types.InlineKeyboardButton(text="Администрация", callback_data="zam_dir")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await bot.send_message(message.chat.id,
                           f'Здравствуйте {message.from_user.username}. Это телеграм бот предназначенный для сбора информации о посещаемости от классных руководителей. Давайте выполним первоначальные настройки. Укажиет свою должность:',
                           reply_markup=keyboard)


@bot_dispatcher.message_handler(commands=["delete_user"])
async def remove_user(message):
    if db_handler.is_user_in_table(message.chat.id, "teachers"):
        db_handler.sql_operation_processing(f"DELETE FROM teachers WHERE telega_id={message.chat.id}", ())
        await bot.send_message(message.chat.id,
                               'Ваши данные удалены. Если захотите вернуться, нажмите на /start. Всего Вам хорошего')
    elif db_handler.is_user_in_table(message.chat.id, "admins"):
        db_handler.sql_operation_processing(f"DELETE FROM admins WHERE telega_id={message.chat.id}", ())
        await bot.send_message(message.chat.id,
                               'Ваши данные удалены. Если захотите вернуться, нажмите на /start. Всего Вам хорошего')
    else:
        await bot.send_message(message.chat.id,
                               'Вы не инициализированный пользователь. Если вы сотрудник учреждения и желаете настроить бота нажмите на /start. Всего Вам хорошего')


@bot_dispatcher.callback_query_handler(lambda call: call.data == "cl_ruk")
async def cl_role_handler(call):
    btns = [
        aiogram.types.InlineKeyboardButton(text='Первый корпус', callback_data='first_corp_'),
        aiogram.types.InlineKeyboardButton(text='Второй корпус', callback_data='second_corp_')
    ]
    keyb = aiogram.types.InlineKeyboardMarkup(row_width=3)
    keyb.add(*btns)
    await bot.send_message(call.message.chat.id, 'В каком корпусе вы работаете?', reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: call.data == "first_corp_")
async def cl_ruk_first_corp(call):
    persons[call.message.chat.id] = {}
    persons[call.message.chat.id]["user_name"] = call.message.chat.username
    persons[call.message.chat.id]["user_id"] = call.message.chat.id
    persons[call.message.chat.id]["corp"] = "first_corp"
    btns = [
        aiogram.types.InlineKeyboardButton(text='5а', callback_data='5а'),
        aiogram.types.InlineKeyboardButton(text='5б', callback_data='5б'),
        aiogram.types.InlineKeyboardButton(text='6а', callback_data='6а'),
        aiogram.types.InlineKeyboardButton(text='6б', callback_data='6б'),
        aiogram.types.InlineKeyboardButton(text='7а', callback_data='7а'),
        aiogram.types.InlineKeyboardButton(text='7б', callback_data='7б'),
        aiogram.types.InlineKeyboardButton(text='8а', callback_data='8а'),
        aiogram.types.InlineKeyboardButton(text='8б', callback_data='8б'),
        aiogram.types.InlineKeyboardButton(text='9а', callback_data='9а'),
        aiogram.types.InlineKeyboardButton(text='9б', callback_data='9б'),
        aiogram.types.InlineKeyboardButton(text='10а', callback_data='10а'),
        aiogram.types.InlineKeyboardButton(text='10б', callback_data='10б'),
        aiogram.types.InlineKeyboardButton(text='10в', callback_data='10в'),
        aiogram.types.InlineKeyboardButton(text='11а', callback_data='11а'),
        aiogram.types.InlineKeyboardButton(text='11б', callback_data='11б')
    ]
    keyb = aiogram.types.InlineKeyboardMarkup(row_width=3)
    keyb.add(*btns)
    await bot.send_message(call.message.chat.id, 'Классным руководителем какого класса Вы являетесь?',
                           reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: call.data == "second_corp_")
async def cl_ruk_second_corp(call):
    persons[call.message.chat.id] = {}
    persons[call.message.chat.id]["user_name"] = call.message.chat.username
    persons[call.message.chat.id]["user_id"] = call.message.chat.id
    persons[call.message.chat.id]["corp"] = "second_corp"
    btns = [
        aiogram.types.InlineKeyboardButton(text='5в', callback_data='5в'),
        aiogram.types.InlineKeyboardButton(text='6в', callback_data='6в'),
        aiogram.types.InlineKeyboardButton(text='7в', callback_data='7в'),
        aiogram.types.InlineKeyboardButton(text='8в', callback_data='8в'),
        aiogram.types.InlineKeyboardButton(text='9в', callback_data='9в'),
        aiogram.types.InlineKeyboardButton(text='10г', callback_data='10г'),
        aiogram.types.InlineKeyboardButton(text='10д', callback_data='10д'),
        aiogram.types.InlineKeyboardButton(text='11г', callback_data='11г'),
        aiogram.types.InlineKeyboardButton(text='11д', callback_data='11д')
    ]
    keyb = aiogram.types.InlineKeyboardMarkup(row_width=3)
    keyb.add(*btns)
    await bot.send_message(call.message.chat.id, 'Классным руководителем какого класса Вы являетесь?',
                           reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: call.data == "zam_dir")
async def zam_role_handler(call):
    if db_handler.is_user_in_table(call.message.chat.id, 'teachers'):
        db_handler.sql_operation_processing(f"DELETE FROM teachers WHERE `telega_id` = {call.message.chat.id}", ())
    if db_handler.is_user_in_table(call.message.chat.id, 'admins'):
        db_handler.sql_operation_processing(f"DELETE FROM admins WHERE `telega_id` = {call.message.chat.id}", ())
    db_handler.sql_operation_processing("INSERT INTO admins(telega_id, admin_name) VALUES(?, ?);",
                                        (call.message.chat.id, call.message.chat.username,))
    answer = 'Ныне Вам доступны отчеты посещаемости классных руководителей, которые Вы сможете просмотреть в одном из нижеследующих вариантов. Если желаете изменить какие-либо свои данные, нажмите на /change_settings. Если желаете удалить свои данные из настроек бота, нажмите /delete_user. Если у Вас возникли какие-либо вопросы по работе бота, обратитесь сюда: @Dinis_Rafikovich'
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn2 = types.KeyboardButton('Exel')
    itembtn3 = types.KeyboardButton('Telegram сообщение')
    markup.add(itembtn2, itembtn3)
    await bot.send_message(call.message.chat.id, answer, reply_markup=markup)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: re.fullmatch(r'[0-9]{1,3}[а-я]', call.data))  #
async def class_handler(call):
    persons[call.message.chat.id]['class_name'] = call.data

    btns = [
        aiogram.types.InlineKeyboardButton(text='Выбрать еще один класс', callback_data='add_class_'),
        aiogram.types.InlineKeyboardButton(text='Сохранить настройки', callback_data='save_settings_'),
    ]
    keyb = aiogram.types.InlineKeyboardMarkup(row_width=2)
    keyb.add(*btns)
    print(persons)
    T = (call.message.chat.id, persons[call.message.chat.id]["user_name"],
         persons[call.message.chat.id]["class_name"], persons[call.message.chat.id]["corp"])

    if db_handler.is_user_in_table(call.message.chat.id, 'admins'):
        db_handler.sql_operation_processing(f"DELETE FROM admins WHERE telega_id = ?", (call.message.chat.id, ))

    if bool(db_handler.get_data("SELECT*FROM teachers WHERE class_name = ?",
                                (persons[call.message.chat.id]['class_name'],))):
        db_handler.sql_operation_processing("DELETE FROM teachers WHERE class_name = ?",
                                            (persons[call.message.chat.id]['class_name'],))
    db_handler.sql_operation_processing(
        "INSERT INTO teachers(telega_id, teacher_name, class_name, corp) VALUES(?, ?, ?, ?);", T)

    await bot.send_message(call.message.chat.id,
                           "Если Вы классный руководитель еще одного класса нажмите на кнопку \"Выбрать еще один класс\". В ином случае нажмите на кнопку \"Сохранить настройки\"",
                           reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: call.data == 'add_class_')  # добавляем еще один класс учителю
async def add_class_(call):
    btns = [
        aiogram.types.InlineKeyboardButton(text='Первый корпус', callback_data='first_corp_'),
        aiogram.types.InlineKeyboardButton(text='Второй корпус', callback_data='second_corp_')
    ]
    keyb = aiogram.types.InlineKeyboardMarkup(row_width=2)
    keyb.add(*btns)
    await bot.send_message(call.message.chat.id, 'Выберите корпус', reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: call.data == 'save_settings_')  # сохраняем настройки для учителя
async def save_settings_(call):
    print(persons)
    T = (call.message.chat.id, persons[call.message.chat.id]["user_name"],
         persons[call.message.chat.id]["class_name"], persons[call.message.chat.id]["corp"])
    if db_handler.is_user_in_table(call.message.chat.id, 'admins'):
        db_handler.is_user_in_table(f"DELETE FROM admins WHERE telega_id = {call.message.chat.id}")
    if bool(db_handler.get_data("SELECT*FROM teachers WHERE class_name = ?",
                                (persons[call.message.chat.id]['class_name'],))):
        db_handler.sql_operation_processing("DELETE FROM teachers WHERE class_name = ?",
                                            (persons[call.message.chat.id]['class_name'],))
    db_handler.sql_operation_processing(
        "INSERT INTO teachers(telega_id, teacher_name, class_name, corp) VALUES(?, ?, ?, ?);", tuple(T))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn1 = [
        types.KeyboardButton('Отчет'),
    ]
    markup.add(*itembtn1)
    await bot.send_message(call.message.chat.id,
                           "Настройка завершена. Бот будет ежедневно отправлять Вам напоминание об отчете классного руководителя в 9:12, если вы этого не сделали до этого времени. До 10.00 Вам нужно отправлять отчет: для этого нажмите кнопку ниже. Если желаете изменить какие-либо свои данные, нажмите на /change_settings. Если желаете удалить свои данные из настроек бота, нажмите /delete_user. Если у Вас возникли какие-либо вопросы по работе бота, обратитесь сюда: @Dinis_Rafikovich",
                           reply_markup=markup)
    await bot.delete_message(call.message.chat.id, call.message["message_id"])
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.message_handler(content_types='text')
async def report_handler(message):

    day = datetime.datetime.now().strftime("%Y-%m-%d")

    if message.text == 'rili248789':#ТУТ ВВОДИТЬСЯ ПАРОЛЬ
        reply = message.from_user.first_name
        persons[message.from_user.id] = {}
        persons[message.from_user.id]["user_name"] = reply
        persons[message.from_user.id]["user_id"] = message.from_user.id

        buttons = [
            types.InlineKeyboardButton(text="Классный руководитель", callback_data="cl_ruk"),
            types.InlineKeyboardButton(text="Администрация", callback_data="zam_dir")
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)

        await bot.send_message(message.from_user.id,
                               'Давайте выполним первоначальные настройки. Укажиет свою должность:',
                               reply_markup=keyboard)

        # await bot.send_sticker(message.chat.id,
        #                        'CAACAgIAAxkBAAEFtdljDOQAAYeSWlqRWHqoAAFs-70pFNAyAALiFgACsjrJSe3our3zzSx7KQQ')


    if db_handler.is_user_in_table(message.chat.id, 'teachers'):  # ТУТ НАЧАЛО ДЕЙСТВИЙ ОТЧЕТА

        if message.text == 'Отчет':

            # if bool(fetch_data("SELECT*FROM kuramshin_otchet WHERE telega_id = ? AND date = ?", (message.chat.id, d,))):
            #     sql_operation("DELETE FROM kuramshin_otchet WHERE telega_id = ? AND date = ?", (message.chat.id, d,))

            cl_arr = db_handler.get_data("SELECT class_name FROM teachers WHERE telega_id = ?", (message.chat.id,))
            if len(cl_arr) > 1:  # предлагаем пользователю выбор из нескольких классов!!!!!ЕСЛИ У КЛАССНОГО РУКОВОДИТЕЛЯ НЕСКОЛЬКО КЛАССОВ ПРЕДЛОЖИТЬ ЕМУ ВЫБОР ЭТИХ КЛАССОВ!!!!!
                cl_list = []
                for a in cl_arr:
                    cl_list.append(aiogram.types.InlineKeyboardButton(text=a[0], callback_data=f"{a[0]}_++"))

                print(cl_list, cl_arr)

                cancel = aiogram.types.InlineKeyboardButton(text="❌Отмена",
                                                            callback_data=f"otmena_{message.message_id}")

                keyb = aiogram.types.InlineKeyboardMarkup(row_width=2)

                keyb.add(*cl_list, cancel)
                await bot.send_message(message.chat.id, 'Выберите класс', reply_markup=keyb)
                await bot.delete_message(message.chat.id, message.message_id)

            else:
                cl_list = []
                choosen_class = db_handler.get_class_name(message.chat.id)[0]

                db_handler.sql_operation_processing("INSERT INTO class_for_otchet(telega_id, class_name) VALUES(?, ?)", (message.chat.id, choosen_class,))
                
                for x in db_handler.get_data("SELECT child_id, child_name FROM childrens WHERE class_name = ? ORDER BY child_name", (choosen_class, )):

                    cl_list.append(aiogram.types.InlineKeyboardButton(text=x[1], callback_data=f"{x[0]}_{x[1]}"))

                cancel = aiogram.types.InlineKeyboardButton(text="❌Отмена",
                                                            callback_data=f"otmena_{message.message_id}")
                no_absence = aiogram.types.InlineKeyboardButton(text="🎉ВСЕ", callback_data="no_absence_")

                keyb = aiogram.types.InlineKeyboardMarkup(row_width=3)
                keyb.add(*cl_list, cancel)
                keyb.row(no_absence, )
                msg_id = await bot.send_message(message.chat.id, f'Выберите пожалуйста отсутствующего',
                                                reply_markup=keyb)
                await bot.delete_message(message.chat.id, message.message_id)

        elif message.text == 'Просмотр отчета':
            result = db_handler.get_data(
                "SELECT*FROM kuramshin_otchet INNER JOIN childrens USING(child_id) INNER JOIN reasons USING(reason_id) WHERE date = ? AND telega_id = ?",
                (day, message.chat.id,))
            result_with_empty = db_handler.get_data("SELECT*FROM kuramshin_otchet WHERE telega_id = ? AND date = ?",
                                                    (message.chat.id, day,))
            soobshenie = ''
            if bool(result) or bool(result_with_empty):
                for b in result_with_empty:
                    if b[1] == None and b[2] == None:
                        soobshenie = soobshenie + f"{b[4]} Отсутствующих нет\n\n"
                for x in result:
                    soobshenie = soobshenie + f'{x[6]} {x[7]} {x[8]}\n'
                await bot.send_message(message.chat.id, soobshenie)
                await bot.delete_message(message.chat.id, message.message_id)

            else:
                await bot.send_message(message.chat.id, 'Сегодня Вы не отправляли отчет посещаемости')
                await bot.delete_message(message.chat.id, message.message_id)


        elif message.text == 'Удалить отчет':
            result = db_handler.get_data(
                "SELECT*FROM kuramshin_otchet INNER JOIN childrens USING(child_id) INNER JOIN reasons USING(reason_id) WHERE date = ? AND telega_id = ?",
                (day, message.chat.id,))
            result_with_empty = db_handler.get_data("SELECT*FROM kuramshin_otchet WHERE telega_id = ? AND date = ?",
                                                    (message.chat.id, day,))
            if bool(result) or bool(result_with_empty):
                db_handler.sql_operation_processing("DELETE FROM kuramshin_otchet WHERE telega_id = ? AND date = ?",
                                                    (message.chat.id, day,))
                await bot.send_message(message.chat.id, "Отчет удален. Не забудьте отправить отчет.")
                await bot.delete_message(message.chat.id, message.message_id)
            else:
                await bot.send_message(message.chat.id, "Сегодня Вы не отправляли отчет посещаемости")
                await bot.delete_message(message.chat.id, message.message_id)

    elif db_handler.is_user_in_table(message.chat.id, 'admins'):
        if bool(db_handler.get_data('SELECT*FROM kuramshin_otchet WHERE date = ?',
                                            (day,))):  # ТУТ КРАТКО НУЖНО ОТДАТЬ ОТЧЕТ В ВИДЕ СООБЩЕНИЯ
            if message.text == 'Telegram сообщение':
                msg = for_admins()
                await bot.send_message(message.chat.id, msg)
                await bot.delete_message(message.chat.id, message.message_id)

            elif message.text == 'Exel':  # ЗДЕСЬ НУЖНО ОТДАТЬ ОТЧЕТ ПО КУРАМШИНСКОМУ ТИПУ
                wb = openpyxl.Workbook()
                list = wb.active
                reasons_el = []
                for x in db_handler.get_absence_reasons_list():
                    reasons_el.append(x[1])
                # Создание строки с заголовками
                list.append(('Дата', f'{day}'))
                list.append(('Класс', 'Всего учеников', 'Отсутствуют', *reasons_el, '% отсутствующих'))
                # класс|всего|отсутствуют|орви|неинф.болезни|заявл.родит.|прием.у.врача|контакт.с.ковид|%отстутв
                total_child_len = len(db_handler.get_data("SELECT child_name FROM childrens"))
                total_missing_len = 0
                orvi = 0
                other_ill = 0
                parent_taked = 0
                on_doctor = 0
                kovid = 0
                for z in message_creator():  # ТУТ ВОЗМОЖНА ОШИБКА!!!!
                    total_missing_len = total_missing_len + z[2]
                    orvi = orvi + z[3]
                    other_ill = other_ill + z[4]
                    parent_taked = parent_taked + z[5]
                    on_doctor = on_doctor + z[6]
                    kovid = kovid + z[7]
                    list.append(z)
                tot_persent = round((total_missing_len / total_child_len) * 100)
                list.append(("Всего", total_child_len, total_missing_len, orvi, other_ill, parent_taked, on_doctor,
                             kovid, tot_persent))
                otchet_name = f'otchet_{day}.xlsx'
                wb.save(f'exels/{otchet_name}')
                file = open(f'exels/{otchet_name}', 'rb')
                await bot.send_document(message.chat.id, file)
                file.close()
        else:
            await bot.send_message(message.chat.id, "Отчетов еще нету.")
            await bot.delete_message(message.chat.id, message.message_id)
    



@bot_dispatcher.callback_query_handler(lambda call: re.fullmatch(r'otmena\_[0-9]+', call.data))  # ОТМЕНА СООБЩЕНИЯ
async def otmena(call):
    msg_id_del = call.data.split('_')[1]
    await bot.delete_message(call.message.chat.id, int(msg_id_del) + 1)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: re.fullmatch(r'[0-9]{1,3}[а-я]\_\+\+', call.data))  # ЗДЕСЬ выбираем ученика если у классного руководителя несколько классов
async def child_choose_(call):
    
    cl_list = []
    choosen_class = call.data.split('_')[0]

    db_handler.sql_operation_processing("INSERT INTO class_for_otchet(telega_id, class_name) VALUES(?, ?)", (call.message.chat.id, choosen_class,))

    for x in db_handler.get_data("SELECT child_id, child_name FROM childrens WHERE class_name=? ORDER BY child_name", (choosen_class, )):
        cl_list.append(aiogram.types.InlineKeyboardButton(text=x[1], callback_data=f"{x[0]}_{x[1]}"))

    otmena = aiogram.types.InlineKeyboardButton(text="❌Отмена", callback_data=f"otmena_{call.message.message_id}")
    kklassam = aiogram.types.InlineKeyboardButton(text="🧾К классам", callback_data="back_to_class_choose_")
    no_absence = aiogram.types.InlineKeyboardButton(text="🎉ВСЕ", callback_data="no_absence_")

    keyb = aiogram.types.InlineKeyboardMarkup(row_width=3)
    keyb.add(*cl_list, )
    keyb.row(kklassam, otmena)
    keyb.row(no_absence)
    await bot.send_message(call.message.chat.id, 'Выберите пожалуйста отсутствующего', reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: call.data == "back_to_class_choose_")  # ЗДЕСЬ ВЫБИРАЕМ КЛАСС если у учителя несколько классов
async def back_to_class_choose_(call):
    cl_arr = db_handler.get_data("SELECT class_name FROM teachers WHERE telega_id = ?", (call.message.chat.id,))
    cl_list = []
    for a in cl_arr:
        cl_list.append(aiogram.types.InlineKeyboardButton(text=a[0], callback_data=f"{a[0]}_++"))
    otmena = aiogram.types.InlineKeyboardButton(text="❌Отмена", callback_data=f"otmena_{call.message.message_id}")
    keyb = aiogram.types.InlineKeyboardMarkup(row_width=2)
    keyb.add(*cl_list, otmena)
    await bot.send_message(call.message.chat.id, 'Выберите класс', reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: re.fullmatch(r'[0-9]+\_([а-яА-Я\s\-]+)', call.data))  # ЗДЕСЬ ВЫБИРАЕМ ПРИЧИНУ И ЗАПОМИНАЕМ ID УЧЕНИКА!!!    ЭТО МОЖЕТ НЕ РАБОТАТЬ!!!
async def reason_for_absense(call):
    #kuramshin_otchet['child_id'] = call.data.split('_')[0]
    child_name = call.data.split('_')[1]

    db_handler.sql_operation_processing("INSERT INTO child_for_otchet(child_id, telega_id) VALUES(?,?)",(call.data.split('_')[0], call.message.chat.id, ))
    
    reasons = []
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    for x in db_handler.get_absence_reasons_list():
        reasons.append(aiogram.types.InlineKeyboardButton(text=x[1], callback_data=f"{x[0]}_{x[1]}_"))
    keyb = aiogram.types.InlineKeyboardMarkup(row_width=2)

    kspisku = aiogram.types.InlineKeyboardButton(text="📜К списку класса", callback_data="back_to_class_list_")
    otmena = aiogram.types.InlineKeyboardButton(text="❌Отмена", callback_data=f"otmena_{call.message.message_id}")

    keyb.add(*reasons)
    keyb.row(kspisku, otmena)
    await bot.send_message(call.message.chat.id, f"Вы выбрали ✅ <b>{child_name}</b>", parse_mode='HTML',
                           reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: re.fullmatch(r'[0-9]\_([а-яА-Я\.\s]+)\_', call.data))  # ЗДЕСЬ ПОЯВЛЯЕТСЯ МЕНЮ ДЛЯ ВОЗВРАТА НАЗАД ИЛИ ОТПРАВКИ ОТЧЕТА
async def save_or_add(call):
    
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    # !!!ЗДЕСЬ НУЖНО ВЫПОЛНЯТЬ СОХРАНЕНИЕ ОТЧЕТА В БД!!!!
    #kuramshin_otchet['reason_id'] = call.data.split('_')[0]
    arr = [
        aiogram.types.InlineKeyboardButton(text='К списку класса', callback_data="back_to_class_list_"),
        aiogram.types.InlineKeyboardButton(text='Сохранить и отправить отчет', callback_data="save_and_send_")
    ]

    child_id = db_handler.get_data("SELECT child_id FROM child_for_otchet WHERE telega_id = ? ORDER BY id DESC", (call.message.chat.id, ))[0][0]
    choosen_class = db_handler.get_data("SELECT class_name FROM childrens WHERE child_id = ?", (child_id, ))[0][0]
    # if bool(db_handler.get_data("SELECT*FROM kuramshin_otchet WHERE date = ? AND child_id = ?",
    #                             (day, kuramshin_otchet['child_id'],))):
    #     db_handler.sql_operation_processing('DELETE FROM kuramshin_otchet WHERE child_id = ? AND date = ?',
    #                                         (kuramshin_otchet['child_id'], day,))
    pr_otchet = db_handler.get_data("SELECT*FROM kuramshin_otchet WHERE telega_id = ? AND date = ?", (call.message.chat.id, day, ))
    for x in pr_otchet:
        if x[1] == None or x[2] == child_id:
            db_handler.sql_operation_processing('DELETE FROM kuramshin_otchet WHERE otchet_id = ?', (x[0], ))#15.11

    #choosen_class = db_handler.get_class_name(call.message.chat.id)
    db_handler.sql_operation_processing(
        'INSERT INTO kuramshin_otchet (reason_id, child_id, telega_id, class_name, date) VALUES (?, ?, ?, ?, ?)',
        (call.data.split('_')[0], child_id, call.message.chat.id, choosen_class, day,))

    #choosen_class = db_handler.get_data("SELECT class_name FROM teachers WHERE telega_id = ?", (call.message.chat.id, ))[0][0]#16.11

    #print(choosen_class)

    keyb = aiogram.types.InlineKeyboardMarkup(row_width=1)
    keyb.add(*arr)
    await bot.send_message(call.message.chat.id,
                           'Если у класса есть еще отсутствующие, нажмите на кнопку \"К списку класса\". Если отсутствующих нет, нажмите на \"Сохранить и отправить отчет\"',
                           reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: call.data == 'back_to_class_list_')  # ЗДЕСЬ ВЫПОЛНЯЕМ ВОЗВРАТ К СПИСКУ УЧЕНИКОВ
async def back_to_list(call):
    
    d = datetime.datetime.now().strftime("%Y-%m-%d")
    cl_list = []

    choosen_class = db_handler.get_data("SELECT class_name FROM childrens INNER JOIN child_for_otchet USING(child_id) WHERE child_for_otchet.telega_id = ? ORDER BY child_for_otchet.id DESC", (call.message.chat.id, ))[0][0]
    
    for x in db_handler.get_data("SELECT child_id, child_name FROM childrens WHERE class_name=? ORDER BY child_name", (choosen_class, )):
        cl_list.append(aiogram.types.InlineKeyboardButton(text=x[1],
                                                          callback_data=f"{x[0]}_{x[1]}"))  # кАЛБЭК ДЛЯ ВЫЗОВА УКАЗАНИЯ ПРИЧИНЫ ОТСУТСТВИЯ
    otmena = aiogram.types.InlineKeyboardButton(text="❌Отмена", callback_data=f"otmena_{call.message.message_id}")
    cl_arr = db_handler.get_data("SELECT class_name FROM teachers WHERE telega_id = ?", (call.message.chat.id,))
    keyb = aiogram.types.InlineKeyboardMarkup(row_width=3)
    keyb.add(*cl_list)
    if len(cl_arr) > 1:
        kklassam = aiogram.types.InlineKeyboardButton(text="🧾К классам", callback_data="back_to_class_choose_")
        keyb.row(kklassam, otmena)
    else:
        keyb.row(otmena, )
    await bot.send_message(call.message.chat.id, 'Выберите пожалуйста отсутствующего', reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: call.data == 'save_and_send_')  # ЗДЕСЬ ВЫПОЛНЯЕМ СОХРАНЕНИЕ ОТЧЕТА
async def save_and_send(call):
    global choosen_class
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    cl_arr = db_handler.get_data("SELECT class_name FROM teachers WHERE telega_id = ?", (call.message.chat.id,))
    
    if len(cl_arr) > 1:  # предлагаем пользователю выбор из нескольких классов
        keyb = aiogram.types.InlineKeyboardMarkup(row_width=2)
        btn_list = [
            aiogram.types.InlineKeyboardButton(text='К выбору класса', callback_data="choose_class_again_"),
            aiogram.types.InlineKeyboardButton(text='Завершить отчет', callback_data="end_otchet_")
        ]
        keyb.add(*btn_list)

        await bot.send_message(call.message.chat.id,
                               'Если у Вашего другого класса есть отсутствующие, то нажмите на кнопку \"К выбору класса\" В ином случае нажмите на кнопку \"Завершить отчет\".',
                               reply_markup=keyb)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.answer_callback_query(callback_query_id=call.id)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        itembtn = [
            types.KeyboardButton('Отчет'),
            types.KeyboardButton('Удалить отчет'),
            types.KeyboardButton('Просмотр отчета')
        ]
        markup.add(*itembtn)
        await bot.send_message(call.message.chat.id, 'Спасибо. Ваш отчет отправлен', reply_markup=markup)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: call.data == 'choose_class_again_')  # ЗДЕСЬ снова выбирается класс
async def choose_class_again(call):
    cl_arr = db_handler.get_data("SELECT class_name FROM teachers WHERE telega_id = ?", (call.message.chat.id,))
    cl_list = []
    for a in cl_arr:
        cl_list.append(aiogram.types.InlineKeyboardButton(text=a[0], callback_data=f"{a[0]}_++"))
    keyb = aiogram.types.InlineKeyboardMarkup(row_width=2)
    otmena = aiogram.types.InlineKeyboardButton(text="❌Отмена", callback_data=f"otmena_{call.message.message_id}")
    keyb.add(*cl_list, otmena)
    await bot.send_message(call.message.chat.id, 'Выберите класс', reply_markup=keyb)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)


# no_absence = telebot.types.InlineKeyboardButton(text="🎉ВСЕ", callback_data="no_absence_")
@bot_dispatcher.callback_query_handler(lambda call: call.data == 'no_absence_')
async def no_absence_(call):
    
    choosen_class = db_handler.get_data("SELECT class_name FROM class_for_otchet WHERE telega_id = ? ORDER BY id DESC", (call.message.chat.id, ))[0][0]
    
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    if bool(db_handler.get_data("SELECT*FROM kuramshin_otchet WHERE telega_id = ? AND date = ? AND class_name = ?",
                                (call.message.chat.id, day, choosen_class,))):
        db_handler.sql_operation_processing(
            'DELETE FROM kuramshin_otchet WHERE telega_id = ? AND date = ? AND class_name = ?',
            (call.message.chat.id, day, choosen_class,))
    db_handler.sql_operation_processing(
        'INSERT INTO kuramshin_otchet (reason_id, child_id, telega_id, class_name, date) VALUES (?, ?, ?, ?, ?)',
        (None, None, call.message.chat.id, choosen_class, day,))
    if len(db_handler.get_data("SELECT*FROM teachers WHERE telega_id = ?", (call.message.chat.id,))) > 1:
        await save_and_send(call)
    else:
        await bot.send_message(call.message.chat.id, 'Спасибо Ваш отчет отправлен')
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.answer_callback_query(callback_query_id=call.id)


@bot_dispatcher.callback_query_handler(lambda call: call.data == 'end_otchet_')  # ЗДЕСЬ снова выбирается класс
async def end_otchet_(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn = [
        types.KeyboardButton('Отчет'),
        types.KeyboardButton('Удалить отчет'),
        types.KeyboardButton('Просмотр отчета'),
    ]
    markup.add(*itembtn)
    await bot.send_message(call.message.chat.id, 'Спасибо. Ваш отчет отправлен', reply_markup=markup)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.answer_callback_query(callback_query_id=call.id)



def message_creator():
    day = datetime.datetime.now().strftime("%Y-%m-%d")

    reasons_el = []
    for x in db_handler.get_absence_reasons_list():
        reasons_el.append(x[1])
    cl_name = db_handler.get_data(
        'SELECT DISTINCT class_name FROM kuramshin_otchet  WHERE date = ? ORDER BY class_name DESC',
        (day,))
    output = []
    for x in cl_name:
        cl_name_1 = x[0]
        cl_total = len(db_handler.get_data('SELECT child_name FROM childrens WHERE class_name = ?', (x[0],)))
        missing_len = len(db_handler.get_data(
            "SELECT*FROM childrens INNER JOIN kuramshin_otchet ON kuramshin_otchet.child_id = childrens.child_id WHERE childrens.class_name = ? AND kuramshin_otchet.date = ?",
            (x[0], day,)))
        missing_per = round((missing_len / cl_total) * 100)
        reasons_len = []
        for y in range(1, len(reasons_el) + 1):
            reason_elem = len(db_handler.get_data(
                "SELECT * FROM kuramshin_otchet INNER JOIN childrens ON kuramshin_otchet.child_id = childrens.child_id INNER JOIN reasons ON kuramshin_otchet.reason_id = reasons.reason_id WHERE childrens.class_name = ? AND kuramshin_otchet.date = ? AND kuramshin_otchet.reason_id = ?",
                (x[0], day, str(y))))
            reasons_len.append(reason_elem)
        output.append((cl_name_1, cl_total, missing_len, *reasons_len, missing_per))
    return output


#async def start_morning_notifications(bot_dispatcher: Dispatcher):
#    users_notifier = UsersNotifier(bot)
#    asyncio.create_task(users_notifier.start_notifies())
def for_admins():#ТУТ СООБЩЕНИЕ ДЛЯ АДМИНОВ
    soobshenie = ''
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    total_child_len = len(db_handler.get_data("SELECT child_name FROM childrens"))
    total_missing_len = 0
    orvi = 0
    other_ill = 0
    parent_taked = 0
    on_doctor = 0
    kovid = 0
    for z in message_creator():
        total_missing_len = total_missing_len + z[2]
        orvi = orvi + z[3]
        other_ill = other_ill + z[4]
        parent_taked = parent_taked + z[5]
        on_doctor = on_doctor + z[6]
        kovid = kovid + z[7]
        soobshenie = soobshenie + f"{z[0]} | {z[1]} | Отсутствуют: {z[2]} | ОРВИ. Грипп: {z[3]} | Неинф. болезни: {z[4]} | По заявлению родителей: {z[5]} | На приеме у врача: {z[6]} | Контакт с КОВИД: {z[7]} \n\n"

    klasses_in_teachers = db_handler.get_data("SELECT class_name FROM teachers")
    otchet_absence = ''
    for b in klasses_in_teachers:
        if not bool(db_handler.get_data("SELECT class_name FROM kuramshin_otchet WHERE class_name = ? AND date = ?", (b[0], day,))):
            otchet_absence = otchet_absence + f"{b[0]}: отчета еще нету\n"

    soob = f"Общее количество: {total_child_len} | Отсутствующие вобщем: {total_missing_len} | ОРВИ.Грипп: {orvi} | Неинф. болезни: {other_ill}| По заявлению: {parent_taked} | У врача: {on_doctor} | КОВИД: {kovid}"
    final_soobshenie = soobshenie + "\n" + soob + "\n\n" + otchet_absence
    return final_soobshenie

async def schedule_for_admins():
    msg = for_admins()
    ids = db_handler.get_data("SELECT telega_id FROM admins")
    for x in ids:
        try:
            await bot.send_message(x[0], msg)
        except BotBlocked:
            await asyncio.sleep(1)

async def noon_print():
    d = datetime.datetime.now().strftime("%Y-%m-%d")
    ids = db_handler.get_data("SELECT telega_id FROM teachers")
    kur_ids = db_handler.get_data("SELECT DISTINCT telega_id FROM kuramshin_otchet WHERE date = ?", (d,))
    for x in ids:
        for v in kur_ids:
            if x == v:
                ids.remove(v)
    for z in ids:
        try:
            await bot.send_message(z[0], "Доброго времени суток, отправьте пожалуйста отчет посещаемости")
        except BotBlocked:
            await asyncio.sleep(1)

'''async def scheduler():
    aioschedule.every().day.at("08:17").do(noon_print)
    aioschedule.every().day.at("09:13").do(noon_print)
    
    aioschedule.every().day.at("09:20").do(schedule_for_admins)
    aioschedule.every().day.at("17:47").do(noon_print)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_strtp(_):
    asyncio.create_task(scheduler())
'''
def schedule_jobs():
    scheduler.add_job(noon_print, 'cron', day_of_week='mon-sat', hour=8, minute=15)
    scheduler.add_job(noon_print, 'cron', day_of_week='mon-sat', hour=9, minute=15)
    scheduler.add_job(schedule_for_admins, 'cron', day_of_week='mon-sat', hour=9, minute=20)
    scheduler.add_job(schedule_for_admins, 'cron', day_of_week='mon-sat', hour=10, minute=40)

async def on_strtp(bot_dispatcher):
    schedule_jobs()
#, end_date='2021-05-30'


if __name__ == '__main__':

    scheduler.start()

    executor.start_polling(
        dispatcher=bot_dispatcher,
        skip_updates=True,
        on_startup=on_strtp
    )
