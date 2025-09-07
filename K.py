# প্রয়োজনীয় লাইব্রেরি ইমপোর্ট
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Dataset লোড
data = pd.read_csv('import kagglehub

# Download latest version
path = kagglehub.dataset_download("nancymee/house-prices-train-csv")

print("Path to dataset files:", path)')

# শুধু কিছু ফিচার নেওয়া
features = ['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF', 'FullBath', 'YearBuilt']
X = data[features]
y = data['SalePrice']

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ML Model
model = LinearRegression()
model.fit(X_train, y_train)

# Prediction
y_pred = model.predict(X_test)

# Performance measure
mse = mean_squared_error(y_test, y_pred)
rmse = mse ** 0.5
print(f"Root Mean Squared Error: {rmse}")

# নতুন prediction উদাহরণ
sample_house = pd.DataFrame({
    'OverallQual': [7],
    'GrLivArea': [2000],
    'GarageCars': [2],
    'TotalBsmtSF': [1000],
    'FullBath': [2],
    'YearBuilt': [2005]
})
predicted_price = model.predict(sample_house)
print(f"Predicted House Price: ${predicted_price[0]:,.2f}")
