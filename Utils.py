from  datetime import *
import time
def GetUnixDateTime() -> int :
    dt =  datetime.today()
    return time.mktime(dt.timetuple())
def GetHumanTimeFromUnixTime(time) -> str:
    date = datetime.fromtimestamp(time).strftime('%H:%M:%S')
    return date

def GetTodayDate():
    return  datetime.today().date()