from getpass import getuser
from os import path
import sqlite3

from aiogram.types import user
from asyncio.windows_events import NULL
class TGDB:
     def __init__(self):
        self.tableName="users"
        self.fileName="TGUsers"
        self.DBExst=".db"
        self.DBDirName= "DB"
        self.FilePath = path.join(self.DBDirName,self.fileName+self.DBExst)
        print(self.FilePath)
        self.DbInit()
        

     def DbInit(self):
        with sqlite3.connect(self.FilePath) as con:

           cur = con.execute("""CREATE TABLE IF NOT EXISTS """+self.tableName+""" (
                tgid UNSIGNED BIG INT PRIMARY KEY,
                notifyday SMALLINT,
                notifyweek SMALLINT,
                username varchar(256),
                mention varchar(256));""")
           con.commit()

            
     def AddUser(self,tgid,username,usermention):
         if self.GetUser(tgid) is None:
            if username == None:
                username="";
            username="'"+username+"'" 
            usermention="'"+usermention+"'"
            with sqlite3.connect(self.FilePath) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO  {0} (tgid, notifyday, notifyweek, username, mention) VALUES ({1}, {2},{3},{4},{5})"\
                            .format(self.tableName, 
                                    tgid,
                                    0,0,
                                    username,
                                    usermention)
                            )
                con.commit()
                
     def UpdateUser(self,tgid,username,usermention,notifyday,notifyweek):
          if self.GetUser(tgid) is None:
            if username == None:
                username=""; 
            
          username="'"+username+"'" 
          usermention="'"+usermention+"'"
          with sqlite3.connect(self.FilePath) as con:
                cur = con.cursor()
                cur.execute("UPDATE {0} set  notifyday={1},notifyweek={2},username={3},mention={4} where tgid={5}"\
                            .format(self.tableName,notifyday,notifyweek,username,usermention,tgid))
                con.commit()
         
     
     def GetUser(self,tgid):
          with sqlite3.connect(self.FilePath) as con:
            cur = con.cursor()
            cur.row_factory = sqlite3.Row
            cur.execute("SELECT * FROM {0} WHERE tgid = {1}".format(self.tableName,tgid));
            res = cur.fetchone()
            cur.close()
            return res
    
     
     def GetAllUsers(self):
         with sqlite3.connect(self.FilePath) as con:
            cur = con.cursor()
            cur.row_factory = sqlite3.Row
            cur.execute("SELECT * FROM {0}".format(self.tableName));
            res = cur.fetchall()
            cur.close()
            return res
         
     def ChangeNotifyDayStatus(self,tgid,username = None,usermention=None):
         user = self.GetOrAddUser(tgid,username,usermention)
         
         id = user["tgid"]
         
         status = self.InvertStatus(user["notifyday"])
         
         with sqlite3.connect(self.FilePath) as con:
            cur = con.cursor()
            cur.execute("Update {0} set notifyday = {1} where tgid = {2}".format(self.tableName,status,tgid));
            res = cur.fetchone()
            cur.close()
            return status
    
     def ChangeNotifyWeekStatus(self,tgid,userName = None,usermention=None):
         user = self.GetOrAddUser(tgid,userName,usermention);
         
         id = user["tgid"]
         status = self.InvertStatus(user["notifyweek"])
         
         with sqlite3.connect(self.FilePath) as con:
            cur = con.cursor()
            cur.execute("Update {0} set notifyweek = {1} where tgid = {2}".format(self.tableName,status,tgid));
            res = cur.fetchone()
            cur.close()
            return status 
         
     
             
     def InvertStatus(self,status): 
         if status == None:
             return 0
         
         if int(status) == 0:
             status = 1
         else: status = 0
         
         return status

     def GetOrAddUser(self,tgid,username,mention):
         user = self.GetUser(tgid)
         if user == None:
             self.AddUser(tgid,username,mention)
             user = self.GetUser(tgid)
         else:
             self.UpdateUser(tgid,username,mention,user["notifyday"],user["notifyweek"])
             user = self.GetUser(tgid)
         return user

   