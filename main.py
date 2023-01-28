import datetime

import vk_api.vk_api
import requests
import sqlite3
import time
from aiogram import  *
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType


vktoken="vk1.a.l3bhGsdd_8xcjiqbPga_fX5hwX2oFQ5u0n-r02fGVXYEAzrUTRCyKa6VpWbiQ5vxR18gQZFVD2o6AlTu4rF3IDQvICyOAMP0tqdki7ckutN41kc28ULrchrzA4R4Crkhs7IY-MCAc-29GhWDTlX-q9YY1dCQtbhs2OAJSpdsWFLDj68JTuiMgx046OiU4_8b";

vk_session = vk_api.VkApi(token = vktoken);
conn:sqlite3.Connection = None;
cursor:sqlite3.Cursor = None;

def DbInit():
    conn = sqlite3.connect(str(datetime.date.today())+'.db')

    cursor = conn.cursor()

    conn.execute("""CREATE TABLE IF NOT EXISTS Admins(
           id INT PRIMARY KEY,
           userName TEXT,
           answerCount INT,
           idlenessCount INT,
           firstMessageTime INT, lastMessageTime INT);""")

    conn.execute("""CREATE TABLE IF NOT EXISTS Chats(
           id INT PRIMARY KEY,
           answered BOOL,
           lastAnswerId INT);""")
    conn.commit()



def get_user_name(user_id):
    user = vk_session.get_api().users.get(user_id = user_id)[0];
    return user["first_name"]+" "+user["last_name"];

while(True):
    try:
        longpool = VkBotLongPoll(vk_session, "151115257");

        for event in longpool.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                DbInit()
                from_id = event.object.message["from_id"];
                cursor.execute("SELECT * FROM  Chats WHERE id = ?", (from_id,))
                user = cursor.fetchone()

                if user == None:
                    cursor.execute("INSERT INTO Chats (id, answered) VALUES (?,?)",(from_id,0,))

                else:
                    cursor.execute("Update Chats set answered = 0 where id = " + str(from_id))

                conn.commit()

            elif event.type == VkBotEventType.MESSAGE_REPLY:
                DbInit()
                from_id = event.object.from_id
                to_id = event.object.peer_id
                date = event.object.date

                cursor.execute("SELECT * FROM  Admins WHERE id = ?", (from_id,))

                user = cursor.fetchone()

                if user  == None:

                    name : str = get_user_name(from_id)

                    cursor.execute("INSERT INTO Admins (id, userName, answerCount, idlenessCount, firstMessageTime,lastMessageTime) VALUES (?, ?, ?, ?, ?, ?)",
                                   (from_id, name, 1, 0, date, date))

                    conn.commit()
                else:

                    cursor.execute("SELECT answerCount, idlenessCount, lastMessageTime FROM  Admins WHERE id = ?", (from_id,))

                    data = cursor.fetchone()

                    answercount = data[0]

                    idlenesscount = data[1]
                    timeValue = data[2]

                    cursor.execute("Select answered, lastAnswerId FROM Chats  where id = " + str(to_id))

                    data = cursor.fetchone()

                    if data != None and data[0] == 0:
                        answercount = answercount + 1

                    elif data != None and data[0] == 1 and data[1] != from_id:
                        answercount = answercount + 1

                    execStr = ""

                    if (date - timeValue) > (30 * 60):
                        idlenesscount = idlenesscount+1

                    cursor.execute("Update Chats set answered = 1, lastAnswerId = "+ str(from_id)+" where id = " + str(to_id))
                    conn.commit()

                    execStr = "Update Admins set answerCount = "+str(answercount)+", idlenessCount ="+ str(idlenesscount)+", lastMessageTime = \"" + str(date) + "\" where id = " + str(from_id) + ";"

                    cursor.execute(execStr);
                    conn.commit()

    except requests.exceptions.ReadTimeout as timeout:
        continue

    except Exception as ex:
        print(ex)









