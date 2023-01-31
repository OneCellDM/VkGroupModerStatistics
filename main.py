import asyncio
import datetime
import os.path
import string
import sys
import time
from logging import handlers
from logging.handlers import TimedRotatingFileHandler

import  Utils
from aiogram import Bot, Dispatcher, types
import logging

from threading import*

import DB
import Vk

if os.path.exists("Logs") == False:
    os.makedirs("Logs")
handler = logging.handlers.TimedRotatingFileHandler(os.path.join("Logs","Bot"), when="midnight", interval=1)
handler.suffix = "%Y.%m.%d.log"
logging.basicConfig(
    encoding='UTF-8',
    level=logging.INFO,
    format = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    handlers=[
        handler,
        logging.StreamHandler(sys.stdout)
        ]
    )


db = DB.DB();


tgToken = ""
vkToken = ""
groupId = ""

def RadConfigs():
    global tgToken
    global vkToken
    global groupId
    f = open('TGToken.txt', 'r')
    try:
        tgToken = f.readline()
    finally:
        f.close()

    f = open('VkToken.txt', 'r')
    try:
        vkToken = f.readline()
    finally:
        f.close()
    f = open('GroupID.txt', 'r')
    try:
       groupId = f.readline()
    finally:
        f.close()

def CheckConfigs():
    if os.path.exists("TGToken.txt") == False:
        print("файл TGToken.txt не найден")
        tgToken = input("Введите токен >")
        f = open('TGToken.txt', 'w')
        try:
            f.write(tgToken)
        finally:
            f.close()

    if os.path.exists("VkToken.txt") == False:
        print("файл vkToken.txt не найден")
        vkToken = input("Введите токен >")
        f = open('vkToken.txt', 'w')
        try:
            f.write(vkToken)
        finally:
            f.close()

    if os.path.exists("GroupID.txt") == False:
        print("файл GroupID.txt не найден")
        groupId = input("Введите id группы >")
        f = open('GroupID.txt', 'w')
        try:
            f.write(groupId)
        finally:
            f.close()


CheckConfigs()
RadConfigs()

_vkbot = Vk.VkBot(db,vkToken,groupId)


bot = Bot(token = tgToken)

dp = Dispatcher(bot)

#Просмотр информации о модераторе по его id
@dp.message_handler(commands = ["check"])
async def check(message: types.Message):
    try:
        logging.info("Call Check Command")
        id = message.text.lower().replace("/check","").strip()
        if id.isdigit():
            adminInfo = db.SeacrhAdminFromId(int(id))
            logging.info("Check command response:\n" + str(adminInfo))
            if adminInfo != None:
                await  message.answer(str(AnswersToMessageConvert(adminInfo)))
            else:
                await  message.answer("Пользователь не найден")
        else:
            await message.answer("Введите числовой ID. \n Пример: /check 1999")

    except Exception as ex:
        logging.error("Telegram Bot Error:\n" + str(ex))

#Просмотр информации о всех модераторах
@dp.message_handler(commands = ["checkall"])
async def checkAll(message: types.Message):
    try:
        logging.info("Call CheckAll Command")
        answers = db.GetAllAnswersInfo()
        logging.info("CheckAll command response:\n" + str(answers))
        if (answers != None) and (len(answers) > 0):
            answersParts =  Utils.ArrayPartition(answers, 8)
            for answer in answersParts:
                text = ""
                for item in answer:
                    text += str(AnswersToMessageConvert(item)) + "\n\n"

                await message.answer(text)
        else:
            await  message.answer("Список модераторов пуст")
    except Exception as ex:
        logging.error("Telegram Bot Error:\n" + str(ex))

#Просмотр списка модераторов
@dp.message_handler(commands = ["list"])
async def list(message: types.Message):
    try:
        logging.info("Call List command")
        answers = db.GetAllAnswersInfo()
        logging.info("List command response:\n"+str(answers))
        if (answers != None) and (len(answers) > 0):
            answersParts = Utils.ArrayPartition(answers, 50)
            for answer in answersParts:
                text = ""
                for item in answer:
                    text += "{0} (id: {1})\n".format(item[1], item[0])

                await message.answer(text)
        else:
            await  message.answer("Список модераторов пуст")
    except Exception as ex:
        logging.error("Telegram Bot Error:\n"+str(ex))

#Помощ
@dp.message_handler(commands = ["help"])
async def help(message: types.Message):
    try:
        logging.info("Call Help command")
        await  message.answer("Список комманд:\n"
                              "/list - Список модераторов\n"
                              "/checkall - Информация о всех модераторах\n"
                              "/check id - Информация о конкретном модераторе")
    except Exception as ex:
        logging.error("Telegram Bot Error:\n" + str(ex))


def AnswersToMessageConvert(item):
    id=item[0]
    name= item[1]
    answers = item[2]
    idlness = item[3]
    firstAnswerTime = item[4]
    lastAnswerTime = item[5]

    idlnessTimeSecs = abs(int(Utils.GetUnixDateTime()) - int(lastAnswerTime))

    awarageTime = abs(int((( lastAnswerTime - firstAnswerTime) / answers)))
    timeFormat="%H Час. %M Мин. %S Сек."
    return "Модератор/Администратор: {1} (id {0})\n" \
           "Количество ответов: {2}\n"\
           "Количество задержек > 30 минут: {3}\n"\
           "Время первого ответа: {4}\n"\
            "Время последнего ответа: {5}\n"\
            "Время бездействия : {6} \n"\
            "Среднее время  ответов: {7} \n"\
            .format(id, name, answers, idlness,
                Utils.GetHumanTimeFromUnixTime(firstAnswerTime),
                Utils.GetHumanTimeFromUnixTime(lastAnswerTime),
                Utils.GetHumanTimeFromSeconds(idlnessTimeSecs,timeFormat),
                Utils.GetHumanTimeFromSeconds(awarageTime,timeFormat))
async def run():
    await dp.start_polling(bot)
    VkThread.join(2)
    exit(0)


VkThread = Thread(target=_vkbot.run)
VkThread.start()

asyncio.run(run())









