from Helper import Helper
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

helper = Helper()
helper.login(USERNAME,PASSWORD)
events = pd.read_csv("./data/events.csv")
print(events)
helper.generateLegResultCSV(events)