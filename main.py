import asyncio
import datetime
import string
import time
import  Utils
from aiogram import Bot, Dispatcher, types
import logging

from threading import*

import DB
import  Vk

db = DB.DB();

_vkbot = Vk.VkBot(db)

logging.basicConfig(level = logging.INFO)
bot = Bot(token = "1654210574:AAFxGe6KprW9PC_gHVTFyjvIyC15VN1PC5M")

dp = Dispatcher(bot)

@dp.message_handler(commands = ["checkAll"])
async def checkAll(message: types.Message):
    try:
        print("checkAll command")
        answers = db.GetAllAnswersInfo()
        if (answers != None) and (len(answers) > 0):
            text = ""
            for answer in answers:
                text +=  str(AnswersToMessageConvert(answer))+"\n\n"

            await message.answer(text)
    except Exception as ex:
        print("Telegram Bot Error:")
        print(ex)

def AnswersToMessageConvert(answer):
    id=answer[0]
    name= answer[1]
    answers = answer[2]
    idlness = answer[3]
    firstAnswerTime = answer[4]
    lastAnswerTime = answer[5]
    idlnessTimeSecs = Utils.GetUnixDateTime() - lastAnswerTime

    return "Модератор/Администратор: {1} (id {0})\n" \
           "Количество ответов: {2}\n"\
           "Количество задержек > 30 минут: {3}\n"\
           "Время первого ответа: {4}\n"\
            "Время последнего ответа: {5}\n"\
            "Время бездействия :{6} мин\n"\
            .format(id, name, answers, idlness,
                Utils.GetHumanTimeFromUnixTime(firstAnswerTime), Utils.GetHumanTimeFromUnixTime(lastAnswerTime),
                    int(idlnessTimeSecs / 60))
async def run():
    await dp.start_polling(bot)


VkThread = Thread(target=_vkbot.run)
VkThread.start()

asyncio.run(run())









