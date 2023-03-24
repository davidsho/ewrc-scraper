from trueskill import Rating, rate_1vs1
import pandas as pd

# Load the dataset
data = pd.read_csv("./data/results.csv")

# Group the data by driver and calculate their mean rating
driver_ratings = {}
for driver in data["driver"].unique():
    driver_data = data[data["driver"] == driver]
    print(driver, driver_data)
    print(driver_data["final_finish"])
    print(driver_data["final_finish"].mean(), driver_data["final_finish"].std())
    if driver_data["final_finish"].std() > 0:
        driver_ratings[driver] = Rating(mu=driver_data["final_finish"].mean(), sigma=driver_data["final_finish"].std())
    else:
        driver_ratings[driver] = Rating(mu=driver_data["final_finish"].mean())

# Use the TrueSkill algorithm to rank the drivers
ranked_drivers = sorted(driver_ratings.items(), key=lambda x: x[1], reverse=True)
for driver, rating in ranked_drivers:
    print(f"{driver}: {rating}")