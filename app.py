import streamlit as st
import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional

# Configuration
DATA_FILE = "data.json"
FRIENDS = ["Gaurav", "Upanshu", "Yatin"]

def load_data() -> Dict:
    """Load data from JSON file, create empty structure if file doesn't exist"""
    if not os.path.exists(DATA_FILE):
        return {"guesses": [], "actual_times": []}
    
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"guesses": [], "actual_times": []}

def save_data(data: Dict) -> None:
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_today_string() -> str:
    """Get today's date as string in YYYY-MM-DD format"""
    return date.today().strftime("%Y-%m-%d")

def get_today_guesses(data: Dict) -> List[Dict]:
    """Get all guesses for today's date"""
    today = get_today_string()
    return [guess for guess in data["guesses"] if guess["date"] == today]

def get_today_actual_time(data: Dict) -> Optional[Dict]:
    """Get actual time entry for today's date"""
    today = get_today_string()
    actual_times = [entry for entry in data["actual_times"] if entry["date"] == today]
    return actual_times[0] if actual_times else None

def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM time string to minutes since midnight"""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    except:
        return 0

def calculate_leaderboard(data: Dict) -> Dict[str, int]:
    """Calculate leaderboard showing wins for each friend across all days"""
    wins = {friend: 0 for friend in FRIENDS}
    
    # Group data by date
    dates_with_complete_data = set()
    
    # Find dates that have both all guesses and actual time
    for actual_entry in data["actual_times"]:
        date_str = actual_entry["date"]
        date_guesses = [g for g in data["guesses"] if g["date"] == date_str]
        
        # Check if all friends have guessed for this date
        guessed_friends = {g["name"] for g in date_guesses}
        if len(guessed_friends) == 3 and all(friend in guessed_friends for friend in FRIENDS):
            dates_with_complete_data.add(date_str)
    
    # Calculate winners for each complete date
    for date_str in dates_with_complete_data:
        actual_entry = next(entry for entry in data["actual_times"] if entry["date"] == date_str)
        actual_minutes = time_to_minutes(actual_entry["actual_time"])
        
        date_guesses = [g for g in data["guesses"] if g["date"] == date_str]
        
        # Calculate differences for each friend
        differences = {}
        for guess in date_guesses:
            guess_minutes = time_to_minutes(guess["guess_time"])
            diff = abs(actual_minutes - guess_minutes)
            differences[guess["name"]] = diff
        
        # Find the winner (closest guess)
        if differences:
            winner = min(differences.keys(), key=lambda x: differences[x])
            wins[winner] += 1
    
    return wins

def reset_today_data() -> None:
    """Remove today's entries from data.json"""
    data = load_data()
    today = get_today_string()
    
    # Remove today's guesses
    data["guesses"] = [guess for guess in data["guesses"] if guess["date"] != today]
    
    # Remove today's actual time
    data["actual_times"] = [entry for entry in data["actual_times"] if entry["date"] != today]
    
    save_data(data)

def main():
    st.set_page_config(page_title="Rat Office Time Guess", page_icon="🐭")
    
    # Load data
    data = load_data()
    today_guesses = get_today_guesses(data)
    today_actual = get_today_actual_time(data)
    
    # Main headline - show only on first visit of the day
    if len(today_guesses) == 0 and today_actual is None:
        st.title("🐭 When will the rat go home today?")
    else:
        st.title("🐭 Rat Office Time Guess")
    
    # Show current date
    st.write(f"**Date:** {get_today_string()}")
    
    # Section 1: Friend Guesses
    st.header("📝 Submit Your Guess")
    
    # Show who has already guessed
    guessed_friends = {guess["name"] for guess in today_guesses}
    
    if len(today_guesses) < 3:
        # Show input fields for friends who haven't guessed yet
        with st.form("guess_form"):
            st.write("Enter your guess for when the rat will leave (HH:MM format):")
            
            guesses_input = {}
            for friend in FRIENDS:
                if friend not in guessed_friends:
                    guesses_input[friend] = st.text_input(
                        f"{friend}:",
                        placeholder="HH:MM (e.g., 17:30)",
                        key=f"guess_{friend}"
                    )
            
            submitted = st.form_submit_button("Submit Guess")
            
            if submitted:
                # Validate and save guesses
                today = get_today_string()
                valid_guesses = []
                
                for friend, guess_time in guesses_input.items():
                    if guess_time and friend not in guessed_friends:
                        # Validate time format
                        try:
                            datetime.strptime(guess_time, "%H:%M")
                            valid_guesses.append({
                                "date": today,
                                "name": friend,
                                "guess_time": guess_time
                            })
                        except ValueError:
                            st.error(f"Invalid time format for {friend}. Please use HH:MM format.")
                            return
                
                if valid_guesses:
                    # Add to data
                    data["guesses"].extend(valid_guesses)
                    save_data(data)
                    st.success(f"Guess(es) submitted successfully!")
                    st.rerun()
    
    # Show current guesses
    if today_guesses:
        st.subheader("Today's Guesses:")
        for guess in sorted(today_guesses, key=lambda x: x["name"]):
            st.write(f"• **{guess['name']}**: {guess['guess_time']}")
    
    # Section 2: Actual Time Input (only show when all 3 friends have guessed)
    if len(today_guesses) == 3 and today_actual is None:
        st.header("⏰ Actual Leave Time")
        
        with st.form("actual_time_form"):
            actual_time = st.text_input(
                "Actual leave time (HH:MM):",
                placeholder="HH:MM (e.g., 17:45)"
            )
            
            submitted_actual = st.form_submit_button("Submit Actual Time")
            
            if submitted_actual and actual_time:
                # Validate time format
                try:
                    datetime.strptime(actual_time, "%H:%M")
                    
                    # Save actual time
                    data["actual_times"].append({
                        "date": get_today_string(),
                        "actual_time": actual_time
                    })
                    save_data(data)
                    st.success("Actual time recorded!")
                    st.rerun()
                    
                except ValueError:
                    st.error("Invalid time format. Please use HH:MM format.")
    
    # Section 3: Results and Leaderboard (show after actual time is recorded)
    if today_actual:
        st.header("🏆 Today's Results")
        
        actual_minutes = time_to_minutes(today_actual["actual_time"])
        st.write(f"**Actual leave time:** {today_actual['actual_time']}")
        
        # Calculate differences for today
        differences = []
        for guess in today_guesses:
            guess_minutes = time_to_minutes(guess["guess_time"])
            diff_minutes = abs(actual_minutes - guess_minutes)
            differences.append({
                "name": guess["name"],
                "guess": guess["guess_time"],
                "difference": diff_minutes
            })
        
        # Sort by difference (closest first)
        differences.sort(key=lambda x: x["difference"])
        
        st.subheader("Today's Rankings:")
        for i, result in enumerate(differences):
            emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            hours = result["difference"] // 60
            mins = result["difference"] % 60
            diff_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
            st.write(f"{emoji} **{result['name']}**: {result['guess']} (off by {diff_str})")
        
        # Overall Leaderboard
        st.header("📊 Overall Leaderboard")
        leaderboard = calculate_leaderboard(data)
        
        # Sort by wins (descending)
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        
        for i, (friend, wins) in enumerate(sorted_leaderboard):
            emoji = "👑" if i == 0 else "🏅" if i == 1 else "🎖️"
            st.write(f"{emoji} **{friend}**: {wins} wins")
    
    # Reset button
    st.header("🔄 Reset")
    if st.button("Reset today's guesses", type="secondary"):
        reset_today_data()
        st.success("Today's data has been reset!")
        st.rerun()
    
    # Show data file info
    with st.expander("📁 Data File Info"):
        if os.path.exists(DATA_FILE):
            st.write(f"Data file: `{DATA_FILE}` exists")
            st.write(f"Total guesses: {len(data['guesses'])}")
            st.write(f"Total actual times: {len(data['actual_times'])}")
        else:
            st.write(f"Data file: `{DATA_FILE}` will be created on first use")

if __name__ == "__main__":
    main()
