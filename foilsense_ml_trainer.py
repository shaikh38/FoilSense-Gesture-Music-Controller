# foilsense_ml_trainer.py
import serial
import numpy as np
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# Serial connection
ser = serial.Serial('COM3', 9600, timeout=0.1)
time.sleep(2)  

print("=== FoilSense ML Gesture Trainer ===")
print("This will train an AI to recognize YOUR gesture patterns")

# Data collection
gestures = ["SINGLE_TAP", "DOUBLE_TAP", "LONG_PRESS"]
X = []  # Features
y = []  # Labels

for gesture in gestures:
    print(f"\n--- Collect data for: {gesture} ---")
    input(f"Press Enter when ready to perform {gesture} 20 times...")

    samples_collected = 0
    while samples_collected < 20:
        if ser.in_waiting > 0:
            try:
                raw_line = ser.readline()
                # Decode line safely, ignoring decoding errors
                line = raw_line.decode('utf-8', errors='ignore').strip()
                if not line:
                    continue  # skip empty lines

                # Extract simple features - length and hashed content + timestamp mod 100
                timestamp = time.time()
                feature_vector = [
                    len(line),             # Length of gesture string
                    hash(line) % 1000,     # Hashed value mod 1000 as proxy numeric feature
                    timestamp % 100        # Cyclic time feature
                ]

                X.append(feature_vector)
                y.append(gesture)
                samples_collected += 1
                print(f"  Sample {samples_collected}/20: {line}")

                time.sleep(0.1)  # Small delay for next sample

            except UnicodeDecodeError:
                
                continue


print("\n=== Training AI Model ===") 
X = np.array(X)
y = np.array(y)

# Split into train/test sets for evaluation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest classifier 
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate accuracy
accuracy = model.score(X_test, y_test)
print(f"\nModel Accuracy: {accuracy * 100:.2f}%")

# Save trained model to file for later prediction usage
with open('foilsense_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("\nModel saved as 'foilsense_model.pkl'")
print("Run the predictor script to use your trained model!")

ser.close()

