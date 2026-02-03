from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

iris = datasets.load_iris()
X = iris.data
y = iris.target

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42)

# Create and train the Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=iris.target_names))

joblib.dump(model, 'model.pkl')
print("\nModel saved as 'model.pkl'")

loaded_model = joblib.load('model.pkl')
test_prediction = loaded_model.predict([[5.1, 3.5, 1.4, 0.2]])
print(f"\nTest prediction for [5.1, 3.5, 1.4, 0.2]: {iris.target_names[test_prediction[0]]}")



