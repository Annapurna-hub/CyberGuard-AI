import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

def train_model():
    print("Training started...")

    # Load dataset
    data = pd.read_csv("data.csv")

    # Drop unnecessary columns
    data = data.drop(['timestamp', 'src_ip', 'dst_ip'], axis=1)

    # Convert categorical columns to numeric
    data = pd.get_dummies(data)

    # Split features and target
    X = data.drop('label', axis=1)
    y = data['label']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Models
    lr = LogisticRegression(max_iter=1000)
    dt = DecisionTreeClassifier()
    rf = RandomForestClassifier()

    # Train
    lr.fit(X_train, y_train)
    dt.fit(X_train, y_train)
    rf.fit(X_train, y_train)

    # Predict
    lr_pred = lr.predict(X_test)
    dt_pred = dt.predict(X_test)
    rf_pred = rf.predict(X_test)

    # Accuracy
    print("Logistic Regression:", accuracy_score(y_test, lr_pred))
    print("Decision Tree:", accuracy_score(y_test, dt_pred))
    print("Random Forest:", accuracy_score(y_test, rf_pred))

    # Save best model (we use Random Forest)
    rf.fit(X, y)
    pickle.dump(rf, open("model.pkl", "wb"))

if __name__ == "__main__":
    train_model()