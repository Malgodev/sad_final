import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
df = pd.read_csv("data\Training.csv")

# Features: All symptom columns are 'yes'/'no' (or 0/1)
X = df.drop(["prognosis"], axis=1)
y = df["prognosis"]

# Encode target labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, input_shape=(X_train.shape[1],), activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(len(np.unique(y_encoded)), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=50, validation_data=(X_test, y_test))

# Save model and encoders
model.save("symptom_model.h5")
joblib.dump(label_encoder, "label_encoder.pkl")
joblib.dump(X.columns.tolist(), "symptom_columns.pkl")
print("Model and encoders saved.")