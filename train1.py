import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Load your original dataset
df = pd.read_csv("cleaned_player_stats_in_venues_filled.csv")

# Drop missing performance or average values
df = df.dropna(subset=['Performance_bat', 'batting_average'])

# Save player and venue info for later
player_names = df['Player_bat']
venue_names = df['Venue']

# One-hot encode categorical columns
df_encoded = pd.get_dummies(df, columns=['Country_bat', 'Venue'], drop_first=True)

# Encode target (Performance_bat)
label_encoder = LabelEncoder()
df_encoded['Performance_bat_encoded'] = label_encoder.fit_transform(df_encoded['Performance_bat'])

# Drop irrelevant/bowling columns and Player name (not used in model)
X = df_encoded.drop(columns=[
    'p_id', 'Player_bat', 'Performance_bat',
    'matches_played_bowl', 'total_runs_conceded',
    'balls_bowled', 'economy', 'total_wickets',
    'Bowling_Strike_Rate', 'Performance_bowl'
])
y = df_encoded['Performance_bat_encoded']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Predict for entire dataset
y_pred = model.predict(X)
predicted_labels = label_encoder.inverse_transform(y_pred)

# Combine with player and venue names
results = pd.DataFrame({
    "Player": player_names,
    "Venue": venue_names,
    "Predicted Performance": predicted_labels
})

# Save to CSV
results.to_csv("player_venue_predicted_performance.csv", index=False)
print("Saved to player_venue_predicted_performance.csv")

from sklearn.metrics import accuracy_score

y_test_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_test_pred)
print("Test Accuracy:", accuracy)

from sklearn.metrics import classification_report

print(classification_report(y_test, y_test_pred, target_names=label_encoder.classes_))

import matplotlib.pyplot as plt

# Get feature importances
importances = model.feature_importances_
feature_names = X.columns

# Create a bar chart
plt.figure(figsize=(10, 6))
plt.barh(feature_names, importances)
plt.xlabel("Importance")
plt.title("Feature Importances")
plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt

# Get feature importances
importances = model.feature_importances_
feature_names = X.columns

# Sort by importance
indices = importances.argsort()[::-1]
sorted_features = feature_names[indices]
sorted_importances = importances[indices]

# Plot
plt.figure(figsize=(10, 6))
plt.barh(sorted_features, sorted_importances)
plt.xlabel("Feature Importance")
plt.title("Which Features Affect Player Batting Performance Prediction?")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()


import matplotlib.pyplot as plt

# Get feature importances from the trained model
importances = model.feature_importances_
feature_names = X.columns

# Sort features by importance
indices = importances.argsort()[::-1]
sorted_features = feature_names[indices]
sorted_importances = importances[indices]

# Plot
plt.figure(figsize=(10, 6))
plt.barh(sorted_features, sorted_importances)
plt.xlabel("Feature Importance")
plt.title("Which Features Affect Player Batting Performance Prediction?")
plt.gca().invert_yaxis()  # So most important is at the top
plt.tight_layout()
plt.show()
