from trueskill import Rating, rate_1vs1
import pandas as pd
from scipy.stats import spearmanr
import math

# Load the dataset
data = pd.read_csv("./data/results.csv")

# Group the data by driver and calculate their mean rating
# driver_ratings = {}
# for driver in data["driver"].unique():
#     driver_data = data[data["driver"] == driver]
#     print(driver, driver_data)
#     print(driver_data["final_finish"])
#     print(driver_data["final_finish"].mean(), driver_data["final_finish"].std())
#     if driver_data["final_finish"].std() > 0:
#         driver_ratings[driver] = Rating(mu=driver_data["final_finish"].mean(), sigma=driver_data["final_finish"].std())
#     else:
#         driver_ratings[driver] = Rating(mu=driver_data["final_finish"].mean())

# # Use the TrueSkill algorithm to rank the drivers
# ranked_drivers = sorted(driver_ratings.items(), key=lambda x: x[1], reverse=True)
# for driver, rating in ranked_drivers:
#     print(f"{driver}: {rating}")

conditions_rankings = {}
for condition in data["conditions"].unique():
    condition_data = data[data["conditions"] == condition]
    conditions_rankings[condition] = {"driver": {}, "codriver": {}, "car": {}, "tyre": {}}
    car_ratings = {}
    for car in condition_data["car"].unique():
        car_data = condition_data[condition_data["car"] == car]
        if car_data["final_finish"].std() > 0:
            car_ratings[car] = Rating(mu=car_data["final_finish"].mean(), sigma=car_data["final_finish"].std())
        else:
            car_ratings[car] = Rating(mu=car_data["final_finish"].mean())
    # print(car_ratings)

    tyre_ratings = {}
    for tyre in condition_data["tyre"].unique():
        tyre_data = condition_data[condition_data["tyre"] == tyre]
        if tyre_data["final_finish"].std() > 0:
            tyre_ratings[tyre] = Rating(mu=tyre_data["final_finish"].mean(), sigma=tyre_data["final_finish"].std())
        else:
            tyre_ratings[tyre] = Rating(mu=tyre_data["final_finish"].mean())

    codriver_ratings = {}
    for codriver in condition_data["codriver"].unique():
        codriver_data = condition_data[condition_data["codriver"] == codriver]
        if codriver_data["final_finish"].std() > 0:
            codriver_ratings[codriver] = Rating(mu=codriver_data["final_finish"].mean(), sigma=codriver_data["final_finish"].std())
        else:
            codriver_ratings[codriver] = Rating(mu=codriver_data["final_finish"].mean())

    driver_ratings = {}
    for driver in condition_data["driver"]:
        driver_data = condition_data[condition_data["driver"] == driver]
        if driver_data["final_finish"].std() > 0:
            driver_ratings[driver] = Rating(mu=driver_data["final_finish"].mean(), sigma=driver_data["final_finish"].std())
        else:
            driver_ratings[driver] = Rating(mu=driver_data["final_finish"].mean())

    conditions_rankings[condition]["driver"] = driver_ratings
    conditions_rankings[condition]["codriver"] = codriver_ratings
    conditions_rankings[condition]["car"] = car_ratings
    conditions_rankings[condition]["tyre"] = tyre_ratings

# for condition, rankings in conditions_rankings.items():
#     print(f"--------- CONDITION: {condition.upper()} ---------")
#     ranked_drivers = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
#     for driver, rating in ranked_drivers:
#         print(f"{driver}: {rating}")

print(conditions_rankings)

driver_entries = data[data["event_name"] == "91. Rallye Automobile Monte-Carlo 2023"]
print(driver_entries)

true_order = [driver["driver"] for _, driver in driver_entries.iterrows()]
print(true_order)

condition = driver_entries["conditions"].iloc[0]
expected_finish_order = {}
for _, driver in driver_entries.iterrows():
    # print(condition, driver)
    driver_rating = conditions_rankings[condition]["driver"].get(driver["driver"], Rating())
    codriver_rating = conditions_rankings[condition]["codriver"].get(driver["codriver"], Rating())
    car_rating = conditions_rankings[condition]["car"].get(driver["car"], Rating())
    # rating = conditions_rankings[condition].get(driver, Rating())
    if driver["tyre"]:
        tyre_rating = conditions_rankings[condition]["tyre"].get(driver["tyre"], Rating())
        weighting_factors = [3, 1, 2, 1]  # weights for driver, codriver, car, tyre
        ratings = [driver_rating, codriver_rating, car_rating, tyre_rating]
        weighted_ratings = [w * r.mu for w, r in zip(weighting_factors, ratings)]
        mu = sum(weighted_ratings) / sum(weighting_factors)
        sigma = math.sqrt(sum(r.sigma ** 2 * w ** 2 for r, w in zip(ratings, weighting_factors)) / sum(weighting_factors) ** 2)
        rating = Rating(mu=mu, sigma=sigma)
        # rating = Rating(mu=(driver_rating.mu + codriver_rating.mu + car_rating.mu + tyre_rating.mu)/4, sigma=(driver_rating.sigma + codriver_rating.sigma + car_rating.sigma + tyre_rating.sigma))
    else:
        weighting_factors = [3, 1, 2]  # weights for driver, codriver, car, tyre
        ratings = [driver_rating, codriver_rating, car_rating]
        weighted_ratings = [w * r for w, r in zip(weighting_factors, ratings)]
        mu = sum(weighted_ratings) / sum(weighting_factors)
        sigma = math.sqrt(sum(r.sigma ** 2 * w ** 2 for r, w in zip(ratings, weighting_factors)) / sum(weighting_factors) ** 2)
        rating = Rating(mu=mu, sigma=sigma)
        # rating = Rating(mu=(driver_rating.mu + codriver_rating.mu + car_rating.mu)/3, sigma=(driver_rating.sigma + codriver_rating.sigma + car_rating.sigma))
    # rating = Rating(mu=(driver_rating.mu + codriver_rating.mu + car_rating.mu)/3, sigma=(driver_rating.sigma + codriver_rating.sigma + car_rating.sigma))
    # rating = Rating(mu=driver_rating.mu, sigma=driver_rating.sigma)
    # rating = Rating(mu=car_rating.mu, sigma=car_rating.sigma)
    # rating = Rating(mu=codriver_rating.mu, sigma=codriver_rating.sigma)
    # rating = Rating(mu=(driver_rating.mu + car_rating.mu), sigma=(driver_rating.sigma + car_rating.sigma))
    # rating = Rating(mu=(driver_rating.mu + codriver_rating.mu), sigma=(driver_rating.sigma + codriver_rating.sigma))
    # rating = Rating(mu=(car_rating.mu + codriver_rating.mu), sigma=(car_rating.sigma + codriver_rating.sigma))
    # print(driver["driver"], rating)
    driver_str = "{0} - {1} - {2} - {3}".format(driver["driver"], driver["codriver"], driver["car"], driver["tyre"])
    expected_finish_order[driver_str] = rating.mu

sorted_driver_entries = sorted(expected_finish_order.items(), key=lambda x: x[1])

# Print the predicted finish order
print("Predicted finish order:")
for i, driver_entry in enumerate(sorted_driver_entries):
    print(f"{i+1}. {driver_entry[0]} - prediction: {driver_entry[1]}")

predicted_order = [driver_entry[0] for driver_entry in sorted_driver_entries]

spearman_correlation, p_value = spearmanr(true_order, predicted_order)

print(f"Spearman's rank correlation coefficient: {spearman_correlation:.2f}")