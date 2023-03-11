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

def noon_print():
    d = datetime.datetime.now().strftime("%Y-%m-%d")
    ids = db_handler.get_data("SELECT telega_id FROM teachers")
    kur_ids = db_handler.get_data("SELECT DISTINCT telega_id FROM kuramshin_otchet WHERE date = ?", (d,))
    
    print()
    print()
    print(ids)
    print()
    print()
    print(kur_ids)
    print()
    print()

    print(kur_ids[0]==ids[-2])
    for x in ids:
        for v in kur_ids:
            if x == v:
                ids.remove(v)
    
    print(ids)


noon_print()
'''
    for x in ids:
        for v in kur_ids:
            if x == v:
                ids.remove(v)
        
    
    for z in ids:
        try:
            await bot.send_message(z[0], "Доброго времени суток, отправьте пожалуйста отчет посещаемости")
        except BotBlocked:
            await asyncio.sleep(1)
'''