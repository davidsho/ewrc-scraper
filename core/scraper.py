from Helper import Helper
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

helper = Helper()
helper.login(USERNAME,PASSWORD)
# helper.generateEventCSV()
events = pd.read_csv("./data/events.csv")
helper.generateResultCSV(events)
# helper.generateEntryListCSV(events)
# helper.generateLegResultCSV(events)