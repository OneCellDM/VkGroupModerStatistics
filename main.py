import asyncio
from concurrent.futures import ProcessPoolExecutor, thread
from contextlib import nullcontext
from ctypes import util
import datetime
from email import utils
from imaplib import Commands
import os.path
from pickle import NONE
from re import L
import string
import sys
from tarfile import NUL
import time
from logging import handlers
from logging.handlers import TimedRotatingFileHandler
from xmlrpc.client import DateTime

from aiogram.utils.helper import ItemsList
from asyncio.windows_events import NULL
from TGDB import TGDB

import  Utils
from aiogram import Bot, Dispatcher, types
import logging

from threading import*

import DB
import Vk

if os.path.exists("Logs") == False:
    os.makedirs("Logs")
#handler = logging.handlers.TimedRotatingFileHandler(os.path.join("Logs","Bot"), when="midnight", interval=1)
#handler.suffix = "%Y.%m.%d.log"
#logging.basicConfig(
  #  encoding='UTF-8',
 #   level=logging.INFO,
   # format = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    #datefmt='%H:%M:%S',
    #handlers=[
        #handler,
        #logging.StreamHandler(sys.stdout)
       # ]
   # )


db = DB.DB();
tgdb = TGDB();


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

def GetStatisticsForWeek():
    currentDate = Utils.GetTodayDate()
    prevDate = currentDate-datetime.timedelta(7)
       
    fdate = Utils.GetHumanDate(currentDate)
    bdate = Utils.GetHumanDate(prevDate)
        
    files = Utils.GetFiles('db',bdate,fdate)
        
    AllData = {}
    answersCount=0
    for filearray in files:
           date = filearray[0]
           file = filearray[1]
          
           answersData = db.GetAllAnswersInfo(file)
           aCount = db.GetAllAnswersCount(file)[0]
           if aCount == None or aCount==0:
               continue
           
           answersCount = answersCount + aCount
           
           for answer in answersData:
               if answer["id"] in AllData:
                   AllData[answer["id"]] = AnswersSumCalculate(answer,AllData[answer["id"]])
                   
               else:
                   AllData[answer["id"]] = answer
        
    messagesCount = 0;     
    text="Статистика за неделю ({0} - {1}): \n общее количество ответов: {2}\n\n".format(bdate,fdate,answersCount) 
        
    for key in AllData:
         messagesCount = messagesCount+1
         text += AnswersToMessageSumConvert(AllData[key],answersCount)+"\n"
            
    if messagesCount==0:
        text = "Статистика за неделю ({0} - {1})  пуста. \n".format(bdate,fdate)
    
    return text;
    



@dp.message_handler(commands = ["notifyday"])
async def changeNotify(message: types.Message):
    try: 
       res = tgdb.ChangeNotifyDayStatus(message.from_id,message.chat.first_name+" "+message.chat.last_name,message.from_user.mention)
       if res == 0:
           await message.answer("Рассылка статистики в конце дня выключена")
       else:  await message.answer("Рассылка статистики в конце дня включена")
    except Exception as ex:
        logging.error("Telegram Bot Error:\n" + str(ex))
        
@dp.message_handler(commands = ["notifyweek"])
async def changeNotify(message: types.Message):
    try:
       res = tgdb.ChangeNotifyWeekStatus(message.from_id,message.chat.first_name+" "+message.chat.last_name,message.from_user.mention)
       if res == 0:
           await message.answer("Рассылка каждую неделю (понедельник) выключена")
       else:  await message.answer("Рассылка каждую неделю (понедельник) включена")
    except Exception as ex:
        logging.error("Telegram Bot Error:\n" + str(ex))
    
#Просмотр информации о модераторе по его id
@dp.message_handler(commands = ["check"])
async def check(message: types.Message):
    try:
        tgdb.GetOrAddUser(message.from_id,message.chat.first_name+" "+message.chat.last_name, message.from_user.mention);
        logging.info("Call Check Command")
        data = message.text.lower()
        data =  " ".join(data.split())
        data = data.replace("/check","").strip().split(' ')
        
        #Если данных больше 1
        if (len(data) > 2 ):
            id = data[0]
            bdate = data[1]
            fdate = data[2]
            
            countData=0;
            filesData = Utils.GetFiles('db',bdate,fdate);
            
            
            for i in filesData:
              date=i[0]
              file=i[1]
             
              adminInfo =  db.SeacrhAdminFromId(int(id),file)
              answersCount = db.GetAllAnswersCount(file)
              logging.info("Check command response:\n" + str(adminInfo))
              if(adminInfo != None):
                 countData+=1
                 await message.answer(date+"\n"+ str(AnswersToMessageConvert(adminInfo,answersCount)))
                  
            if countData == 0 :
                await  message.answer("Пользователь не найден")
         
              
            
        #Если данных = 1 
        else:
            id = data[0]
            if id.isdigit():
                adminInfo = db.SeacrhAdminFromId(int(id))
                answersCount = db.GetAllAnswersCount()
                logging.info("Check command response:\n" + str(adminInfo))
                if adminInfo != None:
                    await  message.answer(str(AnswersToMessageConvert(adminInfo,answersCount)))
                else:
                    await  message.answer("Пользователь не найден")
            else:
                await message.answer("Введите числовой ID. \n Пример: /check 1999")

    except Exception as ex:
        logging.error("Telegram Bot Error:\n" + str(ex))

#Просмотр информации о всех модераторах за сегодня
@dp.message_handler(commands = ["checkall"])
async def checkAll(message: types.Message):
    try:
        tgdb.GetOrAddUser(message.from_id,message.chat.first_name+" "+message.chat.last_name, message.from_user.mention);
        logging.info("Call CheckAll Command")
    
        data = message.text.lower()
        data =  " ".join(data.split())
        data = data.replace("/checkall","").strip().split(' ')
        if (len(data) > 1 ):
            bdate = data[0]
            fdate = data[1]
            
            countData = 0;
            filesData = Utils.GetFiles('db',bdate,fdate);
            
            for i in filesData:
                date=i[0]
                file=i[1]
                answers = db.GetAllAnswersInfo(file)
                if (answers != None) and (len(answers) > 0):
                    answersParts =  Utils.ArrayPartition(answers, 8)
                    answersCount = db.GetAllAnswersCount(file)
                    text = date+"\n"
                    for answer in answersParts:
                        countData+=1
                        for item in answer:
                            text += str(AnswersToMessageConvert(item,answersCount)) + "\n\n"
                           
                        await message.answer(text)
                        text=""
                    
            if countData == 0:
                await  message.answer("Список модераторов пуст")
        
        else:        

            answers = db.GetAllAnswersInfo()
            logging.info("CheckAll command response:\n" + str(answers))
            if (answers != None) and (len(answers) > 0):
                answersParts =  Utils.ArrayPartition(answers, 8)
                answersCount = db.GetAllAnswersCount()
                for answer in answersParts:
                    text = ""
                    for item in answer:
                        text += str(AnswersToMessageConvert(item,answersCount)) + "\n\n"

                    await message.answer(text)
            else:
                await  message.answer("Список модераторов пуст")
    except Exception as ex:
        logging.error("Telegram Bot Error:\n" + str(ex))

#Просмотр списка модераторов
@dp.message_handler(commands = ["list"])
async def list(message: types.Message):
    try:
        tgdb.GetOrAddUser(message.from_id,message.chat.first_name+" "+message.chat.last_name, message.from_user.mention);
        logging.info("Call List command")
        answers = db.GetAllAnswersInfo()
        logging.info("List command response:\n"+str(answers))
        if (answers != None) and (len(answers) > 0):
            answersParts = Utils.ArrayPartition(answers, 50)
            for answer in answersParts:
                text = ""
                for item in answer:
                    text += "{0} (id: {1})\n".format(item["username"], item["id"])

                await message.answer(text)
                text=""
        else:
            await  message.answer("Список модераторов пуст")
    except Exception as ex:
        logging.error("Telegram Bot Error:\n"+str(ex))

@dp.message_handler(commands=["notifylist"])
async def notifyList(message: types.message):
    tgdb.GetOrAddUser(message.from_id,message.chat.first_name+" "+message.chat.last_name, message.from_user.mention);
    datatext="Нет информаци"
    
    users = tgdb.GetAllUsers();
    if len(users)>0:
        datatext=""
        
    for user in users:
        usenotifyday=""
        
        usenotifyweek=""
        
        if user["notifyday"] == 1:
             usenotifyday ="Отправка статистики в конце дня: Включено"
        else:
            usenotifyday ="Отравка статистики в конце дня: Выключено"
            
        if user["notifyweek"] == 1:
            usenotifyweek = "Отправка статистики каждую неделю: Включено"
        else:
             usenotifyweek = "Отправка статистики каждую неделю: Выключено"
        
        datatext = datatext + "{0} ({1} | {2}) \n {3} \n {4}\n\n".format(user["username"],user["tgid"],user["mention"], usenotifyday,usenotifyweek)
   
        if len(datatext) == 0:
            datatext="Нет информации"
            
    await message.answer(datatext)
        
    
    

            
@dp.message_handler(commands = ["week"])
async def week(message: types.message):
    try:
        tgdb.GetOrAddUser(message.from_id,message.chat.first_name+" "+message.chat.last_name, message.from_user.mention);
        logging.info("Call week command")
        countData = 0
        text=""
        text = GetStatisticsForWeek();
           
        await message.answer(text)
        
         
        
        
    except Exception as ex:
        logging.error("Telegram Bot Error:\n" + str(ex))


def AnswersSumCalculate(answer1,answer2):
   
   return{
       "id":answer1["id"],
       "userName":answer1["userName"],
       "answerCount" : answer1["answerCount"]+answer2["answerCount"],
       "idlenessCount" : answer1["idlenessCount"]+answer2["idlenessCount"],
       }
    
#Помощ
@dp.message_handler(commands = ["help"])
async def help(message: types.Message):
    try:
        tgdb.GetOrAddUser(message.from_id,message.chat.first_name+" "+message.chat.last_name, message.from_user.mention);
        logging.info("Call Help command")
        await  message.answer("Список комманд:\n"
                              "/list - Список модераторов\n"
                              "/checkall - Информация о всех модераторах\n"
                              "/checkall <Начальная дата> <Конечная дата> - Информация о всех модераторах за период\n"
                              "/week  - Получить сводную статистику за неделю\n" 
                              "/check <id> - Информация о конкретном модераторе\n"
                              "/check <id> <Начальная дата> <Конечная дата>  - Информация о конкретном модераторе за период\n"
                              "/notifyday - Включить/Выключить отправку статистики в конце дня\n" 
                              "/notifyweek - Включить/выключить отправку сводной статистике за неделю (Каждый понедельник)\n"
                              "/notifyList - Показать список пользователей включивших оповещение"
                             )
    except Exception as ex:
        logging.error("Telegram Bot Error:\n" + str(ex))


def AnswersToMessageSumConvert(item,answersCount):
    id=item["id"]
    name= item["userName"]
    answers = item["answerCount"]
    idlness = item["idlenessCount"]

    allAnswersCount = 1
  
    if(type(answersCount) is list and len(answersCount)>0):
        allAnswersCount=answersCount[0]
        
    if (type(answersCount) is int):
        allAnswersCount = answersCount

    return "Модератор/Администратор: {1} (id {0})\n" \
           "Количество ответов: {2} ({3}%)\n"\
           "Количество задержек > 30 минут: {4}\n"\
           .format(id, name, answers,   round(( float(answers)/float(allAnswersCount) )*100,2) ,idlness)
            

def AnswersToMessageConvert(item,answersCount):
    id=item["id"]
    name= item["userName"]
    answers = item["answerCount"]
    idlness = item["idlenessCount"]
    firstAnswerTime = item["firstMessageTime"]
    lastAnswerTime = item["lastMessageTime"]
    allAnswersCount = 1
  
    if(type(answersCount) is list and len(answersCount)>0):
        allAnswersCount=answersCount[0]
        
    if (type(answersCount) is int):
        allAnswersCount = answersCount
    
    idlnessTimeSecs = abs(int(Utils.GetUnixDateTime()) - int(lastAnswerTime))

    awarageTime = abs(int(((lastAnswerTime - firstAnswerTime) / answers)))
    timeFormat="%H Час. %M Мин. %S Сек."
    return "Модератор/Администратор: {1} (id {0})\n" \
           "Количество ответов: {2} ({3}%)\n"\
           "Количество задержек > 30 минут: {4}\n"\
           "Время первого ответа: {5}\n"\
            "Время последнего ответа: {6}\n"\
            "Время бездействия: {7} \n"\
            "Среднее время  ответов: {8} \n"\
            .format(id, name, answers,  round(( float(answers)/float(allAnswersCount) )*100,2) , idlness,
                Utils.GetHumanTimeFromUnixTime(firstAnswerTime),
                Utils.GetHumanTimeFromUnixTime(lastAnswerTime),
                Utils.GetHumanTimeFromSeconds(idlnessTimeSecs,timeFormat),
                Utils.GetHumanTimeFromSeconds(awarageTime,timeFormat))

async def SendingStatistics(time):
    filesData = Utils.GetFiles('db',time,time);
    if len(filesData)>0:
        filesData=filesData[0]
    answers = db.GetAllAnswersInfo(filesData[1])
    users = tgdb.GetAllUsers();
    for user in users:
       try:
           if  user == None: continue
           
           if int(user["notifyday"]) == 1:
                try:
                    if (answers != None) and (len(answers) > 0):
                        answersParts =  Utils.ArrayPartition(answers, 8)
                        answersCount = db.GetAllAnswersCount(filesData[1])
                        text = "Ежедневный отчёт "+time
                        await bot.send_message(user["tgid"],text)
                        for answer in answersParts:
                            text=""
                            for item in answer:
                                text += str(AnswersToMessageConvert(item,answersCount)) + "\n\n"
                    
                            await bot.send_message(user["tgid"],text)
                except BaseException as ex:
                    logging.error("Telegram Bot Error:\n" + str(ex))
                    
           if int(user["notifyweek"]) == 1 and Utils.GetTodayDate().weekday() == 0:
                text = GetStatisticsForWeek()
                await bot.send_message(user["tgid"],text)
                
       except BaseException as ex:
           logging.error("Telegram Bot Error:\n" + str(ex))
           

async def CallEveryTime():
    oldTime = Utils.GetTodayDate();
    while(True):
        if Utils.GetTodayDate() > oldTime:
            
            await SendingStatistics(Utils.GetHumanDate(oldTime));
            oldTime = Utils.GetTodayDate()
           
        await asyncio.sleep(60)
 
VkThread = Thread(target=_vkbot.run)
#VkThread.start()

async def run():
    await asyncio.gather(
      
       dp.start_polling(bot),
       CallEveryTime(),
    )
    VkThread.join(2)
    exit(0)

if __name__ == '__main__':
    asyncio.run(run())
    
   
    







