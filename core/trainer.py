import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import OneHotEncoder

entries_df = pd.read_csv('./data/entries.csv')
events_df = pd.read_csv('./data/events.csv')
legresults_df = pd.read_csv('./data/legresults.csv')
results_df = pd.read_csv('./data/results.csv')

merged_df = pd.merge(entries_df, legresults_df, on=['season','round','leg','entry_number'])
print(merged_df.dtypes)
print(results_df.dtypes)
merged_df = pd.merge(results_df.loc[:, results_df.columns != 'condition'], merged_df, on=['season','round','entry_number','driver','codriver','car'])
merged_df.to_csv('./data/merged_data.csv', index=False)

merged_df = merged_df[['conditions','driver','codriver','final_finish','car','final_time','leg','start_number','leg_finish','leg_time']]
print(merged_df)

categorical_columns = ['conditions', 'driver', 'codriver', 'car']
numerical_columns = ['final_finish', 'final_time', 'leg', 'start_number', 'leg_finish', 'leg_time']

merged_df_ohe = merged_df
for col in categorical_columns:
    col_ohe = pd.get_dummies(merged_df[col], prefix=col)
    merged_df_ohe = pd.concat((merged_df_ohe, col_ohe), axis=1).drop(col, axis=1)

merged_df_ohe.to_csv("./data/merged_data_ohe.csv")
print(merged_df_ohe)

# features = merged_df[['conditions','driver','codriver','final_finish','car','final_time','leg','start_number','leg_finish','leg_time']]
features = merged_df_ohe
labels = merged_df_ohe['leg_finish']

# Split the data into training and testing sets
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size=0.2)

# Train a random forest classifier
rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=0)
rf.fit(train_features, train_labels)

# Predict the outcome of an upcoming event
upcoming_event_df = pd.read_csv('./data/upcoming_event.csv')
upcoming_event_features = upcoming_event_df[['conditions', 'driver', 'codriver', 'car', 'start_number']]

upcoming_ohe = upcoming_event_features
for col in ['conditions','driver','codriver','car']:
    col_ohe = pd.get_dummies(upcoming_event_features[col], prefix=col)
    upcoming_ohe = pd.concat((upcoming_ohe, col_ohe), axis=1).drop(col, axis=1)

predicted_positions = rf.predict(upcoming_ohe)

# # Print the predicted positions
print(predicted_positions)