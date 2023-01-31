import datetime
import logging
import sys

from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType
import vk_api.vk_api
import  DB
import  requests

import Utils


class VkBot:
    def __init__(self, db:DB,token,groupid):
        self.Db = db
        self.token = token
        self.groupId = groupid
        self.vk_session = vk_api.VkApi(token=self.token);
    def get_user_name(self,user_id):
        user = self.vk_session.get_api().users.get(user_id=user_id)[0];
        return user["first_name"] + " " + user["last_name"];

    def run(self):
        logging.info("VK BOT RUN")
        while (True):
            try:
                logging.info("VK BOT Start Long Pool")
                longpool = VkBotLongPoll(self.vk_session, self.groupId);
                logging.info("VK BOT Started Long Pool")

                for event in longpool.listen():
                    self.Db.DbInit()

                    if event.type == VkBotEventType.MESSAGE_NEW:
                        from_id = event.object.message["from_id"];


                        user = self.Db.SeacrchChatFromId(from_id)

                        if user == None:
                            logging.info("New message fom: New User id :" + str(from_id))
                            self.Db.InsertChatsData(from_id, 0)

                        elif user[1] == 1:
                            logging.info("New message fom: User id :" + str(from_id))
                            self.Db.UpdateChats(from_id,0)

                    elif event.type == VkBotEventType.MESSAGE_REPLY:
                        from_id = event.object.from_id
                        logging.info("Message reply fom:" + str(from_id))


                        to_id = event.object.peer_id

                        date = Utils.GetUnixDateTime()
                        if from_id < 0:
                            continue

                        answercount = 0
                        idlenesscount = 0
                        name = ""
                        firstMessageTimeHumanText = ""
                        lastMessageTimeHumanText= Utils.GetHumanTimeFromUnixTime(date)
                        admin = self.Db.SeacrhAdminFromId(from_id)

                        if admin == None:
                            name = self.get_user_name(from_id)
                            firstMessageTimeHumanText = Utils.GetHumanTimeFromUnixTime(date)
                            self.Db.InsertAdminsData(from_id, name, 1, 0, date, date)

                        else:
                            name = admin[1]
                            answercount = admin[2]
                            idlenesscount = admin[3]

                            firstMessageTimeHumanText = Utils.GetHumanTimeFromUnixTime(admin[4])
                            timeValue = admin[5]
                            lastMessageTimeHumanText = Utils.GetHumanTimeFromUnixTime(timeValue)

                            chat = self.Db.SeacrchChatFromId(to_id)

                            IsLasAnswered="YES"
                            if chat != None and chat[1] == 0:
                                answercount = answercount + 1
                                IsLasAnswered = "NO"

                            elif chat != None and chat[1] == 1 and chat[2] != from_id:
                                answercount = answercount + 1
                                IsLasAnswered = "NO"


                            if (date - timeValue) > (30 * 60):
                                idlenesscount = idlenesscount + 1

                            self.Db.UpdateChats(to_id,1,from_id)
                            self.Db.UpdateAdminsData(from_id,answercount,idlenesscount,str(date))

                        logging.info("Message reply"
                                     "\n\tFom: {0} ({1})"
                                     "\n\tTo: {2}"
                                     "\n\tFirstMessageTime: {3}"
                                     "\n\tLastMessageTime: {4}"
                                     "\n\tAnswers:{5}"
                                     "\n\tLastAnsweredThisChat:{6}"
                                     "\n\tIdlness > 30 min:{7}"
                                     .format(str(from_id), name, str(to_id), firstMessageTimeHumanText, lastMessageTimeHumanText, str(answercount),IsLasAnswered, str(idlenesscount)))


            except requests.exceptions.ReadTimeout as timeout:
                continue

            except vk_api.ApiError as e:
                logging.error("VkApi Error: \n {0} \n Response data: {1}".format(str(e.raw),str(event)))

            except Exception as ex:
                logging.error("VkApi Error: \n {0} \n Response data: {1}".format(str(ex), str(event)))


