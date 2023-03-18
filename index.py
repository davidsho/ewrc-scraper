import requests
import pandas as pd
from bs4 import BeautifulSoup

s = requests.Session()

baseURL = "https://www.ewrc-results.com"

def login(username, password):
    d = {"username":username,"password":password}
    r = s.get(baseURL + "/inc/login.php", data=d)

def topStats():
    r = s.get(baseURL + "/champs/")
    print(r.text)

def parseEvent(season, round, event):
    title = event.find("a")
    name = title.text
    url = title['href']
    details = "".join(e for e in event.find("span").text.split('•')[1].replace("km","") if e.isalpha() or e == '-').split("-")
    return {"season":season,"round":round+1,"name":name,"url":url,"conditions":details}

def getSeason(season):
    print(baseURL + "/season/" + str(season) + "/1-wrc/")
    r = s.get(baseURL + "/season/" + str(season) + "/1-wrc/", headers={"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                                                           "Accept-Encoding":"gzip, deflate, br",
                                                           "Host":"www.ewrc-results.com",
                                                           "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
                                                           "Accept-Language":"en-GB,en;q=0.9",
                                                           "Referer":"https://www.ewrc-results.com/season/2020/",
                                                           "Connection":"keep-alive"})
    soup = BeautifulSoup(r.content, 'html.parser')
    events = soup.find_all("div", class_="season-event")
    events = [parseEvent(season, i, event) for i, event in enumerate(events)]
    return events

def parseResult(result, season, round, event_name, url, conditions):
    # print(result, season, round, event_name, url, conditions)
    try:
        entry = result.find("td", class_="final-entry").find("a").children
        entry = [e for e in entry if e.name != "span" and e != '\n']
        final_result = {}
        final_result["season"] = season
        final_result["round"] = round
        final_result["event_name"] = event_name
        final_result["url"] = url
        final_result["conditions"] = conditions
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

def getEvent(event):
    r = s.get(baseURL + event['url'])
    soup = BeautifulSoup(r.content, 'html.parser')
    results = soup.find_all("tr")
    return [parseResult(result, event["season"], event["round"], event["name"], event["url"], event["conditions"]) for result in results]

def generateEventCSV():
    events = []
    for i in range(2000,2025):
        season = getSeason(i)
        events.extend(season)

    df = pd.DataFrame(events)
    df.to_csv("events.csv")
    return events

def generateResultCSV(events):
    results = []
    for index, event in events.iterrows():
        print(event)
        result = getEvent(event)
        results.extend(result)
    results = [i for i in results if i is not None]
    print(results)
    df = pd.DataFrame(results)
    df.to_csv("results.csv")
    return results

login("S4C-rally","@!1Gup4irbNEkJMf")
events = pd.read_csv("events.csv")
print(events)
generateResultCSV(events)