import sqlite3
import  queue
import datetime
import traceback
import Utils
from  os import *
class DB:

    def GetFileName(self):
        if path.exists(self.DBDirName) == False:
            makedirs(self.DBDirName)

        return path.join(self.DBDirName, str(Utils.GetTodayDate())+self.DBExst )
    def __init__(self):
        self.DBExst=".db"
        self.DBDirName= "DB"
        self.DbInit()

    def DbInit(self):
        with sqlite3.connect(self.GetFileName()) as con:

            con.execute("""CREATE TABLE IF NOT EXISTS Admins(
                id UNSIGNED BIG INT PRIMARY KEY,
                userName TEXT,
                answerCount INT,
                idlenessCount INT,
                firstMessageTime UNSIGNED BIG INT, 
                lastMessageTime UNSIGNED BIG INT);""")

            con.execute("""CREATE TABLE IF NOT EXISTS Chats(
                id UNSIGNED BIG INT PRIMARY KEY,
                answered BOOL,
                lastAnswerId UNSIGNED BIG INT);""")
            con.commit()



    def InsertAdminsData(self, from_id,name, answerCount, idlenessCount, firstMessageTime, lastMessageTime)-> bool :
        with sqlite3.connect(self.GetFileName()) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Admins (id, userName, answerCount, idlenessCount, firstMessageTime,lastMessageTime) VALUES (?, ?, ?, ?, ?, ?)",
                (from_id, name, answerCount, idlenessCount, firstMessageTime,lastMessageTime))
            con.commit()


    def InsertChatsData(self, id, answered):
        with sqlite3.connect(self.GetFileName()) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Chats (id, answered) VALUES (?,?)", (id, answered,));
            con.commit()


    def UpdateChats(self, id, answered, lastAnsweredId = None):
        with sqlite3.connect(self.GetFileName()) as con:
            cur = con.cursor()

            if lastAnsweredId is not None:
                cur.execute("Update Chats set answered = {0}, lastAnswerId = {1} where id ={2};".format(answered, lastAnsweredId, id))

            else:
                cur.execute("Update Chats set answered = {0} where id ={1};".format(answered,id) );
            con.commit()
    def UpdateAdminsData(self,id,answeredCount,idlnessCount,lastMessageTime):
        with sqlite3.connect(self.GetFileName()) as con:
            cur = con.cursor()
            cur.execute("Update Admins set answerCount = {0}, idlenessCount = {1}, lastMessageTime = \"{2}\" where id = {3};"
                        .format(answeredCount,idlnessCount,lastMessageTime,id))
            con.commit()
    def SeacrchChatFromId(self,id):
        with sqlite3.connect(self.GetFileName()) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM  Chats WHERE id = ?", (id,));
            res = cur.fetchone()
            cur.close()
            return res
    def SeacrhAdminFromId(self,id):
        with sqlite3.connect(self.GetFileName()) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM  Admins WHERE id = ?", (id,));
            res = cur.fetchone()
            cur.close()
            return res
    def GetAllAnswersInfo(self):
        with sqlite3.connect(self.GetFileName()) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM  Admins");
            res = cur.fetchall()
            cur.close()
            return res


