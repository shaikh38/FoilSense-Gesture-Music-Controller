
# FoilSense Gesture Music Controller

A real-time gesture-controlled music interface built using  ESP32 capacitive touch sensing, a **Python Tkinter GUI**, **serial communication**, and a **machine-learning gesture classifier**.  
The system allows you to control Spotify playback using physical gestures detected from an ESP32 foil-based touch sensor.

---

# ✨ Features

### 🟩 Hardware (ESP32 Touch Sensor)
- Capacitive touch sensing using ESP32 
- Robust gesture recognition (Single Tap, Double Tap, Long Press)
- Baseline calibration & dynamic thresholding
- Debouncing + timing algorithm for clean detection

### 🟦 Software (Python GUI + Spotify API)
- Modern Tkinter UI with:
  - Live **track name**
  - Live **artist name**
  - **Album art** loaded dynamically
  - Real-time **progress timer**
  - Playback controls (Prev / Play / Next)
- Auto-refresh every 2 seconds for smooth updates

### 🤖 Machine Learning (Random Forest Gesture Classifier)
- Python-based ML training pipeline  
- Serial data converted into feature vectors  
- Real-time gesture prediction  
- High accuracy (>90%) on tap classification  

### 🔌 Communication
- Seamless **Serial → Python** gesture streaming  
- Multi-threaded event handling  
- Spotify API integration using `spotipy`

---

# 🛠 Tech Stack

### **Hardware**
- ESP32 MCU  
- Capacitive foil touch sensor

### **Software**
- Python  
- Tkinter GUI  
- Spotify Web API (`spotipy`)  
- PySerial  
- PIL / Pillow  
- scikit-learn (Random Forest)

### **Languages**
- C++ (Arduino)  
- Python  

---

# 🧩 System Architecture
[ Foil Sensor ] → [ ESP32 Capacitive Touch ] → (Serial over USB)
        → [ Python Gesture Listener ] → [ ML Classifier ] → [ Spotify API ]
                                        ↓
                                      [ GUI Updates ]


