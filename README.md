# 🐭 Rat Office Time Guess

A Streamlit web application for guessing when the office rat will go home each day.

## Features

- **Daily Guessing Game**: Three friends (Gaurav, Upanshu, Yatin) guess when the rat will leave
- **Time Tracking**: Record actual leave time after all guesses are submitted
- **Live Leaderboard**: Track who makes the most accurate guesses over time
- **Data Persistence**: All data stored in local `data.json` file
- **Daily Reset**: Option to reset today's guesses and replay

## Installation

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## How It Works

1. **First Visit**: Shows headline "When will the rat go home today?"
2. **Guessing Phase**: Each friend enters their guess in HH:MM format
3. **Actual Time**: After all 3 guesses, input field appears for actual leave time
4. **Results**: Shows today's rankings and overall leaderboard
5. **Reset**: Button to clear today's data and start over

## Data Storage

- All data stored in `data.json` (auto-created)
- Tracks guesses and actual times by date
- Maintains historical leaderboard across all days
