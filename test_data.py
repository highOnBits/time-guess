#!/usr/bin/env python3
"""
Test script to verify data persistence
"""
import json
import os

# Same path logic as in app.py
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

print(f"Data file path: {DATA_FILE}")
print(f"Current working directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")

# Test data with historical games
test_data = {
    "guesses": [
        # July 31st game - Honor won
        {"date": "2025-07-31", "name": "Honor", "guess_time": "16:10"},
        {"date": "2025-07-31", "name": "Pilgrim", "guess_time": "16:20"},
        {"date": "2025-07-31", "name": "Dawn", "guess_time": "16:30"},
        # August 2nd game - Pilgrim won
        {"date": "2025-08-02", "name": "Pilgrim", "guess_time": "14:30"},
        {"date": "2025-08-02", "name": "Honor", "guess_time": "15:00"},
        {"date": "2025-08-02", "name": "Dawn", "guess_time": "13:00"}
    ],
    "actual_times": [
        {"date": "2025-07-31", "actual_time": "16:10"},
        {"date": "2025-08-02", "actual_time": "14:23"}
    ],
    "initial_scores": {"Honor": 0, "Dawn": 0, "Pilgrim": 0}
}

# Try to save
try:
    with open(DATA_FILE, 'w') as f:
        json.dump(test_data, f, indent=2)
    print(f"✅ Successfully wrote test data to {DATA_FILE}")
    
    # Verify file exists and has content
    if os.path.exists(DATA_FILE):
        file_size = os.path.getsize(DATA_FILE)
        print(f"✅ File exists with size: {file_size} bytes")
        
        # Try to read it back
        with open(DATA_FILE, 'r') as f:
            loaded_data = json.load(f)
        print(f"✅ Successfully read data back: {len(loaded_data['guesses'])} guesses")
    else:
        print("❌ File does not exist after write")
        
except Exception as e:
    print(f"❌ Error: {e}")
