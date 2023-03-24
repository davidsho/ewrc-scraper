import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import datetime

import sys
sys.setrecursionlimit(10000)

class Helper:
    '''
    Class containing helper functions to scrape the ewrc website

    ...

    Attributes
    ----------
    s : requests.Session
        Requests session containing cookies
    baseURL : str
        Root ewrc result URL

    '''

    def __init__(self):
        self.s = requests.Session()
        self.baseURL = "https://www.ewrc-results.com"

    def login(self, username, password):
        '''Logs in to ewrc site and stores cookies in session variable

        Parameters
        ----------
        username : str
        password : str
        '''
        d = {"username":username,"password":password}
        self.s.get(self.baseURL + "/inc/login.php", data=d)

    def parseEvent(self, season, round, event):
        '''Parses event HTML to find name, url and conditions

        Parameters
        ----------
        season : int
            Season year
        round : int
            Round number in season
        event : bs4.element.Tag
            Event html tag to parse

        Returns
        -------
        dict
            Dictionary containing event information
        '''
        title = event.find("a")
        name = title.text
        url = title['href']
        details = "".join(e for e in event.find("span").text.split('•')[1].replace("km","") if e.isalpha() or e == '-').replace('-cancelled','')
        return {"season":season,"round":round+1,"event_name":name,"event_url":url,"conditions":details}

    def getSeason(self, season):
        '''Gets all events in a season

        Parameters
        ----------
        season : int
            Season year

        Returns
        -------
        list
            List of parseEvent dictionaries
        '''
        print(self.baseURL + "/season/" + str(season) + "/1-wrc/")
        r = self.s.get(self.baseURL + "/season/" + str(season) + "/1-wrc/")
        soup = BeautifulSoup(r.content, 'html.parser')
        events = soup.find_all("div", class_="season-event")
        events = [self.parseEvent(season, i, event) for i, event in enumerate(events)]
        return events

    def parseResult(self, result, season, round, event_name, url, conditions):
        '''Parses result HTML to find essential details

        Parameters
        ----------
        result : bs4.element.Tag
            Result html to parse
        season : int
            Season year
        round : int
            Round in the season
        event_name : str
            The event name
        url : str
            ewrc event URL
        conditions : list
            List of condition strings for event

        Returns
        -------
        dict
            Dictionary containing essential result info
        None
            If error occurs
        '''
        try:
            entry = result.find("td", class_="final-entry").find("a").children
            entry = [e for e in entry if e.name != "span" and e != '\n']
            final_result = {}
            final_result["season"] = season
            final_result["round"] = round
            final_result["event_name"] = event_name
            final_result["event_url"] = url
            final_result["conditions"] = conditions
            # final_result["entry_number"] = result.find("td", class_="final-results-number").text.strip().replace("#","")
            final_result["entry_number"] = list(result.find("td", class_="final-results-number").children)[0].strip().replace("#","")
            # final_result["entry_number"] = result.find("td", class_=)
            final_result["driver"] = " ".join([e for e in entry[0].split(" ") if e not in ["","\n","\r\n"]])
            final_result["codriver"] = " ".join([e for e in entry[1].split(" ") if e not in ["","\n","\r\n"]])
            final_result["final_finish"] = result.find("td", class_="font-weight-bold text-left").text.replace(".","").strip()
            car = result.find("td", class_="final-results-car").children
            car = [c for c in car if c]
            final_result["car"] = car[0].strip()
            # final_result["time"] = [r for r in result.find("td", class_="final-results-times").text.split(" ") if r not in ["","\n","\r\n"]][0].strip()
            t = time.strptime(list(result.find("td", class_="final-results-times").children)[0].strip(), '%H:%M:%S.%f')
            final_result["final_time"] = datetime.timedelta(hours=t.tm_hour, minutes=t.tm_min, seconds=t.tm_sec).total_seconds()
            return final_result
        except:
            pass

    def getEvent(self, event):
        '''Gets result page for specific event

        Parameters
        ----------
        event : dict
            Event dictionary returned in parseEvent function

        Returns
        -------
        list
            List of parseResult dictionaries
        '''
        r = self.s.get(self.baseURL + event['event_url'])
        soup = BeautifulSoup(r.content, 'html.parser')
        results = soup.find_all("tr")
        return [self.parseResult(result, event["season"], event["round"], event["event_name"], event["event_url"], event["conditions"]) for result in results]
    
    def parseEntry(self, season, round, leg, startNumber, entry):
        '''Parses each entry in an entry list to dict

        Parameters
        ----------
        leg : int
            Leg number of the event
        startNumber : int
            Start number in the leg for the entry
        entry : bs4.element.Tag
            Entry HTML

        Returns
        -------
        dict
            Entry dictionary with essential info
        '''
        entry_name = entry.find("a").children
        entry_name = [e for e in entry_name if e.name != "span" and e != '\n']
        bolds = entry.find_all("td", class_="font-weight-bold")
        final_entry = {}
        final_entry["season"] = season
        final_entry["round"] = round
        final_entry["leg"] = leg
        final_entry["start_number"] = startNumber
        final_entry["start_time"] = bolds[len(bolds) - 1].text.strip()
        final_entry["entry_url"] = entry.find("a")['href']
        final_entry["entry_number"] = entry.find("td", class_="final-results-number").text.strip().replace("#","")
        final_entry["driver"] = " ".join([e for e in entry_name[0].split(" ") if e not in ["","\n","\r\n"]])
        final_entry["codriver"] = " ".join([e for e in entry_name[1].split(" ") if e not in ["","\n","\r\n"]])
        final_entry["car"] = bolds[len(bolds) - 2].text.strip()
        return final_entry
    
    def getEventEntryList(self, event):
        '''Gets entry lists for all legs of an event

        Parameters
        ----------
        event : dict
            Event dictionary returned in parseEvent function

        Returns
        -------
        list
            List of entry orders for each leg of the event
        '''
        entryListURL = '/entries/' + event['event_url'].split('/')[2]
        leg = 1
        finalEntryList = []
        while True:
            r = self.s.get(self.baseURL + entryListURL + '/?leg=' + str(leg))
            soup = BeautifulSoup(r.content, 'html.parser')
            entryList = soup.find_all("tr")
            print(self.baseURL + entryListURL + '/?leg=' + str(leg))
            # print(entryList)
            entryList = [self.parseEntry(event["season"], event["round"], leg, index + 1, entry) for index, entry in enumerate(entryList)]
            entryList = [e for e in entryList if e is not None]
            if not entryList:
                break
            # print(entryList)
            finalEntryList.extend(entryList)
            leg += 1
        return finalEntryList
    
    def parseLegResult(self, season, round, leg, position, result):
        '''Parse a leg result into a dictionary

        Issues with this function as it appears the leg results pages are mal-formated

        Parameters
        ----------
        leg : int
            Leg number
        position : int
            The position in leg finishing order
        result : bs4.element.Tag
            The result html

        Returns
        -------
        dict
            Dictionary containing essential result details
        '''
        final_entry = {}
        # bolds = result.find_all("td", class_="font-weight-bold")
        # print(bolds)
        final_entry["season"] = season
        final_entry["round"] = round
        final_entry["leg"] = leg
        final_entry["leg_finish"] = position
        # print(result.find(class_="legs-number").text)
        # print(leg, position, result.prettify())
        final_entry["entry_number"] = result.find(class_="legs-number").text.strip().replace("#","").split(" ")[0]
        # final_entry["time"] = [r for r in result.find("td", class_="font-weight-bold text-right").text.split(" ") if r not in ["","\n","\r\n"]][0].strip()
        # final_entry["leg_time"] = list(result.find("td", class_="font-weight-bold text-right").children)[0].strip()
        try:
            t = time.strptime(list(result.find("td", class_="font-weight-bold text-right").children)[0].strip(), '%H:%M:%S.%f')
            final_entry["leg_time"] = datetime.timedelta(hours=t.tm_hour, minutes=t.tm_min, seconds=t.tm_sec).total_seconds()
        except:
            t = time.strptime(list(result.find("td", class_="font-weight-bold text-right").children)[0].strip(), '%M:%S.%f')
            final_entry["leg_time"] = datetime.timedelta(minutes=t.tm_min, seconds=t.tm_sec).total_seconds()
        return final_entry
    
    def getLegResults(self, event):
        '''Gets all leg results for an event

        Parameters
        ----------
        event : dict
            Event dictionary

        Returns
        -------
        list
            List of final results for each leg of event
        '''
        legURL = '/leg/' + event['event_url'].split('/')[2]
        leg = 1
        finalResultList = []
        while True:
            print(event, leg, self.baseURL + legURL + '/?leg=' + str(leg))
            r = self.s.get(self.baseURL + legURL + '/?leg=' + str(leg))
            soup = BeautifulSoup(r.content, 'html.parser')
            resultList = soup.find("table", class_="results").find_all("tr")
            resultList = [self.parseLegResult(event["season"], event["round"], leg, i+1, result) for i, result in enumerate(resultList)]
            resultList = [r for r in resultList if r is not None]
            if not resultList:
                break
            finalResultList.extend(resultList)
            leg += 1
        return finalResultList

    def generateEventCSV(self):
        '''Generates CSV from parseEvent dictionaries

        Returns
        -------
        list
            List of parseEvent dictionaries
        '''
        events = []
        for i in range(2018,2025):
            season = self.getSeason(i)
            events.extend(season)
        df = pd.DataFrame(events)
        df.to_csv("./data/events.csv", index=False)
        return events

    def generateResultCSV(self, events):
        '''Generates CSV from parseResult dictionaries

        Parameters
        ----------
        events : pandas.core.frame.DataFrame
            Events CSV

        Returns
        -------
        list
            List of parseResult dictionaries
        '''
        results = []
        for index, event in events.iterrows():
            print(event)
            result = self.getEvent(event)
            results.extend(result)
        results = [i for i in results if i is not None]
        print(results)
        df = pd.DataFrame(results)
        df.to_csv("./data/results.csv", index=False)
        return results
    
    def generateEntryListCSV(self, events):
        '''Generates an entry list CSV for each event

        Parameters
        ----------
        events : pandas.core.frame.DataFrame
            Events CSV
        
        '''
        results = []
        for index, event in events.iterrows():
            print(event)
            result = self.getEventEntryList(event)
            results.extend(result)
        results = [i for i in results if i is not None]
        df = pd.DataFrame(results)
        # df.to_csv("./data/entry-lists/"+str(event["season"])+"-"+str(event["round"])+"-entries.csv")
        df.to_csv("./data/entries.csv", index=False)

    def generateLegResultCSV(self, events):
        '''Generates a leg finishing order CSV for each event

        ISSUES WITH THIS

        Parameters
        ----------
        events : pandas.core.frame.DataFrame
            Events CSV
        '''
        results = []
        for _, event in events.iterrows():
            print(event)
            result = self.getLegResults(event)
            results.extend(result)
        df = pd.DataFrame(results)
        # df.to_csv("./data/leg-results/"+str(event["season"])+"-"+str(event["round"])+"-results.csv")
        df.to_csv("./data/legresults.csv", index=False)