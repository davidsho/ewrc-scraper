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

conditions_rankings = {}
for condition in data["conditions"].unique():
    condition_data = data[data["conditions"] == condition]
    driver_ratings = {}
    for driver in condition_data["driver"]:
        driver_data = condition_data[condition_data["driver"] == driver]
        if driver_data["final_finish"].std() > 0:
            driver_ratings[driver] = Rating(mu=driver_data["final_finish"].mean(), sigma=driver_data["final_finish"].std())
        else:
            driver_ratings[driver] = Rating(mu=driver_data["final_finish"].mean())
    conditions_rankings[condition] = driver_ratings

for condition, rankings in conditions_rankings.items():
    print(f"--------- CONDITION: {condition.upper()} ---------")
    ranked_drivers = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
    for driver, rating in ranked_drivers:
        print(f"{driver}: {rating}")

driver_entries = data[data["event_name"] == "91. Rallye Automobile Monte-Carlo 2023"]
condition = driver_entries["conditions"].iloc[0]
expected_finish_order = {}
for driver in driver_entries["driver"]:
    print(condition, driver)
    rating = conditions_rankings[condition].get(driver, Rating())
    expected_finish_order[driver] = rating.mu

sorted_driver_entries = sorted(expected_finish_order.items(), key=lambda x: x[1])

# Print the predicted finish order
print("Predicted finish order:")
for i, driver_entry in enumerate(sorted_driver_entries):
    print(f"{i+1}. {driver_entry[0]} - prediction: {driver_entry[1]}")