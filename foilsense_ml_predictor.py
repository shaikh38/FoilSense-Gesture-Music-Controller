import serial
import pickle
import numpy as np
import time

# Load trained model
with open('foilsense_model.pkl', 'rb') as f:
    model = pickle.load(f)

print("Loaded trained model!")

# Serial connection 
ser = serial.Serial('COM3', 9600, timeout=0.1)
time.sleep(2)

print("=== FoilSense AI Predictor ===")
print("Perform gestures and watch AI predict them!\n")

try:
    while True:
        if ser.in_waiting > 0:
            raw_line = ser.readline()
            line = raw_line.decode('utf-8', errors='ignore').strip()
            if not line:
                continue

            timestamp = time.time()
            features = np.array([[
                len(line),
                hash(line) % 1000,
                timestamp % 100
            ]])

            prediction = model.predict(features)[0]
            confidence = max(model.predict_proba(features)[0]) * 100

            print(f"Detected: {line:15s} | AI Predicts: {prediction:15s} | Confidence: {confidence:.1f}%")

except KeyboardInterrupt:
    ser.close()
    print("\nExiting predictor...")
