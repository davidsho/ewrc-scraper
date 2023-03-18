from Helper import Helper
import pandas as pd

helper = Helper()
helper.login("S4C-rally","@!1Gup4irbNEkJMf")
events = pd.read_csv("events.csv")
print(events)
helper.generateResultCSV(events)