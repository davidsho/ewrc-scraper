import requests
import pandas as pd
from bs4 import BeautifulSoup

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
        details = "".join(e for e in event.find("span").text.split('•')[1].replace("km","") if e.isalpha() or e == '-').split("-")
        return {"season":season,"round":round+1,"name":name,"url":url,"conditions":details}

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
            final_result["url"] = url
            final_result["conditions"] = conditions
            final_result["entry_number"] = result.find("td", class_="final-results-number").text.strip().replace("#","")
            final_result["driver"] = " ".join([e for e in entry[0].split(" ") if e not in ["","\n","\r\n"]])
            final_result["codriver"] = " ".join([e for e in entry[1].split(" ") if e not in ["","\n","\r\n"]])
            final_result["finish"] = result.find("td", class_="font-weight-bold text-left").text.replace(".","").strip()
            car = result.find("td", class_="final-results-car").children
            car = [c for c in car if c]
            final_result["car"] = car[0].strip()
            final_result["time"] = [r for r in result.find("td", class_="final-results-times").text.split(" ") if r not in ["","\n","\r\n"]][0].strip()
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
        r = self.s.get(self.baseURL + event['url'])
        soup = BeautifulSoup(r.content, 'html.parser')
        results = soup.find_all("tr")
        return [self.parseResult(result, event["season"], event["round"], event["name"], event["url"], event["conditions"]) for result in results]
    
    def parseEntry(self, leg, startNumber, entry):
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
        final_entry["leg"] = leg
        final_entry["start_number"] = startNumber
        final_entry["start_time"] = bolds[len(bolds) - 1].text.strip()
        final_entry["url"] = entry.find("a")['href']
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
        entryListURL = '/entries/' + event['url'].split('/')[2]
        leg = 1
        finalEntryList = []
        while True:
            r = self.s.get(self.baseURL + entryListURL + '/?leg=' + str(leg))
            soup = BeautifulSoup(r.content, 'html.parser')
            entryList = soup.find_all("tr")
            print(self.baseURL + entryListURL + '/?leg=' + str(leg))
            entryList = [self.parseEntry(leg, index + 1, entry) for index, entry in enumerate(entryList)]
            entryList = [e for e in entryList if e is not None]
            if not entryList:
                break
            finalEntryList.extend(entryList)
            leg += 1
        return finalEntryList

    def generateEventCSV(self):
        '''Generates CSV from parseEvent dictionaries

        Returns
        -------
        list
            List of parseEvent dictionaries
        '''
        events = []
        for i in range(2000,2025):
            season = self.getSeason(i)
            events.extend(season)
        df = pd.DataFrame(events)
        df.to_csv("./data/events.csv")
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
        df.to_csv("./data/results.csv")
        return results
    
    def generateEntryListCSV(self, events):
        '''Generates an entry list CSV for each event

        Parameters
        ----------
        events : pandas.core.frame.DataFrame
            Events CSV
        
        '''
        for index, event in events.iterrows():
            print(event)
            result = self.getEventEntryList(event)
            df = pd.DataFrame(result)
            df.to_csv("./data/entry-lists/"+str(event["season"])+"-"+str(event["round"])+"-entries.csv")