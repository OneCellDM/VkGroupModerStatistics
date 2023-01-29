from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType
import vk_api.vk_api
import  DB
import  requests

import Utils


class VkBot:
    def __init__(self, db:DB):
        self.Db = db
        self.token = "vk1.a.l3bhGsdd_8xcjiqbPga_fX5hwX2oFQ5u0n-r02fGVXYEAzrUTRCyKa6VpWbiQ5vxR18gQZFVD2o6AlTu4rF3IDQvICyOAMP0tqdki7ckutN41kc28ULrchrzA4R4Crkhs7IY-MCAc-29GhWDTlX-q9YY1dCQtbhs2OAJSpdsWFLDj68JTuiMgx046OiU4_8b";
        self.vk_session = vk_api.VkApi(token=self.token);
    def get_user_name(self,user_id):
        user = self.vk_session.get_api().users.get(user_id=user_id)[0];
        return user["first_name"] + " " + user["last_name"];

    def run(self):
        print("VK BOT STARTED")
        while (True):
            try:
                longpool = VkBotLongPoll(self.vk_session, "151115257");
                print("VK BOT POOLING ")

                for event in longpool.listen():
                    self.Db.DbInit()
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        from_id = event.object.message["from_id"];

                        user = self.Db.SeacrchChatFromId(from_id)

                        if user == None:
                            self.Db.InsertChatsData(from_id, 0)

                        elif user[1] == 1:
                            self.Db.UpdateChatsIA(from_id,0)

                    elif event.type == VkBotEventType.MESSAGE_REPLY:
                        from_id = event.object.from_id
                        to_id = event.object.peer_id
                        date = Utils.GetUnixDateTime()

                        admin = self.Db.SeacrhAdminFromId(from_id)

                        if admin == None:

                            name: str = self.get_user_name(from_id)
                            self.Db.InsertAdminsData(from_id, name, 1, 0, date, date)

                        else:

                            answercount = admin[2]
                            idlenesscount = admin[3]
                            timeValue = admin[5]

                            chat = self.Db.SeacrchChatFromId(to_id)


                            if chat != None and chat[1] == 0:
                                answercount = answercount + 1

                            elif chat != None and chat[1] == 1 and chat[2] != from_id:
                                answercount = answercount + 1


                            if (date - timeValue) > (30 * 60):
                                idlenesscount = idlenesscount + 1

                            self.Db.UpdateChatsIAL(to_id,1,from_id)
                            self.Db.UpdateAdminsData(from_id,answercount,idlenesscount,str(date))


            except requests.exceptions.ReadTimeout as timeout:
                continue
            except Exception as ex:
                print("VkApi Error:")
                print(ex)

