# Copyright by Piotr Korczyk

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import json
import time


CALENDAR_ID = 'piotr.korczyk66@gmail.com'
EVENT_NAME = 'issue call'
# to do: add requirment pip install, configure moto account

def buildServiceConnection():
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service

def getLastEventDate(eventName):
    today = datetime.datetime.utcnow()
    pastThreeWeeks = today + datetime.timedelta(weeks=-3)
    pastThreeWeeks = pastThreeWeeks.isoformat() + 'Z'
    now = today.isoformat() + 'Z'
    eventsList = service.events().list(calendarId=CALENDAR_ID,
                                       singleEvents=True, orderBy='startTime',
                                       timeMin=pastThreeWeeks, timeMax=now, q=eventName).execute()
    filtredEvents = []

    f = open('test.json', 'w')
    f.write(json.dumps(eventsList['items']))

    for item in eventsList['items']:
        if item['summary'] == eventName:
            filtredEvents.append(item)
        else:
            continue
    try:
        lastEvent = filtredEvents[len(filtredEvents)-1]
    except IndexError:
        print('Cant find any '+eventName+' from last 3 weeks!')
        return 0
    print('Datetime of last '+EVENT_NAME+' (in local time): '+str(lastEvent['end']['dateTime']))
    return lastEvent['end']['dateTime'] # return date in LOCAL TIME, NO UTC !!! 
    


def findAndDeleteEvent(eventName, calendarService):
    eventNameToDelete = eventName
    service = calendarService
    today = datetime.datetime.utcnow()
    now = today.isoformat() + 'Z'
    endOfDay = datetime.datetime(
        today.year, today.month, today.day, 23,  59).isoformat() + 'Z'
    eventsList = service.events().list(calendarId=CALENDAR_ID,
                                       singleEvents=True, orderBy='startTime',
                                       timeMin=now, timeMax=endOfDay, q= eventNameToDelete).execute()
    eventsListItems = eventsList['items']
    itemToDeleteId = ''
    itemToDeleteDate = ''
    for item in eventsListItems:
        if item['summary'] == eventNameToDelete:
            itemToDeleteId = item['id']
            itemToDeleteDate = item['start']['dateTime']
            print('ID: '+itemToDeleteId)
            break
    if itemToDeleteId == '':
        print('Cant find event: '+eventNameToDelete +
              '! Time range(in UTC): from '+now+' to '+endOfDay+'')
    try:
        service.events().delete(calendarId=CALENDAR_ID,
                                             eventId=itemToDeleteId).execute()
        print('Event '+eventNameToDelete+' has been deleted, evetn time in local time: ' +itemToDeleteDate)
    except:
        print('Deleting went wrong!')


while True:
    t = datetime.datetime.utcnow()
    print('----- Issue script ----- utc time: '+str(t))
    service = buildServiceConnection()
    getLastEventDate(EVENT_NAME)
    findAndDeleteEvent(EVENT_NAME, service)
    print('----- end of script -----\n')
    
    time.sleep(600)