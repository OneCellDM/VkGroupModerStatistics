from  datetime import *
import imp
import locale
import os
from os import listdir
from os.path import isfile, join


import time

HumanTimeFormat = "%H:%M:%S"
HumanDateFormat = "%d.%m.%Y"

def GetUnixDateTime() -> int :
    dt =  datetime.today()
    return time.mktime(dt.timetuple())

def GetHumanTimeFromUnixTime(time) -> str:
    date = datetime.fromtimestamp(time).strftime(HumanTimeFormat)
    return date

def GetTodayDate():
    return  datetime.today().date()

def GetTodayDateHuman():
    return  datetime.today().date().strftime(HumanDateFormat)

def GetHumanDate(date):
    return date.strftime(HumanDateFormat)

def GetDateFromHumanString(str):
    return time.strptime(str,HumanDateFormat)

def GetHumanTimeFromSeconds(secs,format)->str:
    return time.strftime(format, time.gmtime(secs))

def ArrayPartition(array,count):
        for i in range(0, len(array), count):
            yield array[i:i + count]

def GetFiles(path,startdate, enddate):
    resultsData=[]
    onlyfiles = [ ".".join (list(reversed(f.replace(".db","")
                                          .replace('-','.')
                                          .split('.')
                                          )
                                 )
                            )  for f in listdir(path) if isfile(join(path, f))]

    for item in onlyfiles:
        if item != 'TGUsers':
            date=GetDateFromHumanString(item)
            if date >=GetDateFromHumanString(startdate) and date <= GetDateFromHumanString(enddate):
                r = "-".join (list(reversed(item.split('.'))))
                r+='.db'
                resultsData.append([item,join(path, r)])
             
    return resultsData
     

    

locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))