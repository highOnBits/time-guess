import streamlit as st
import json
import os
from datetime import datetime, date, time
from typing import Dict, List, Optional
import time as time_module
import pytz

# Configuration
# Use absolute path to ensure data.json is always in the same directory as app.py
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
FRIENDS = ["Honor", "Dawn", "Pilgrim"]

def load_data() -> Dict:
    """Load data from JSON file, create empty structure if file doesn't exist"""
    # Historical dates
    july_31 = "2025-07-31"  # Honor won
    aug_2 = "2025-08-02"    # Pilgrim won (last Friday)
    
    default_data = {
        "guesses": [
            # July 31st game - Honor won
            {"date": july_31, "name": "Honor", "guess_time": "16:10"},
            {"date": july_31, "name": "Pilgrim", "guess_time": "16:20"},
            {"date": july_31, "name": "Dawn", "guess_time": "16:30"},
            # August 2nd game - Pilgrim won
            {"date": aug_2, "name": "Pilgrim", "guess_time": "14:30"},
            {"date": aug_2, "name": "Honor", "guess_time": "15:00"},
            {"date": aug_2, "name": "Dawn", "guess_time": "13:00"}
        ], 
        "actual_times": [
            {"date": july_31, "actual_time": "16:10"},
            {"date": aug_2, "actual_time": "14:23"}
        ],
        "initial_scores": {"Honor": 0, "Dawn": 0, "Pilgrim": 0}
    }
    
    if not os.path.exists(DATA_FILE):
        # Create initial data file with existing scores
        save_data(default_data)
        return default_data
    
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Ensure initial_scores exists in loaded data
            if "initial_scores" not in data:
                data["initial_scores"] = {"Honor": 0, "Dawn": 0, "Pilgrim": 0}
                save_data(data)
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        save_data(default_data)
        return default_data

def save_data(data: Dict) -> None:
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        # Verify the file was actually written
        if os.path.exists(DATA_FILE):
            file_size = os.path.getsize(DATA_FILE)
            print(f"DEBUG: Data saved successfully to {DATA_FILE} ({file_size} bytes)")
        else:
            print(f"ERROR: File {DATA_FILE} was not created after save attempt")
    except Exception as e:
        print(f"ERROR saving data: {e}")
        raise

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

def get_eastern_time() -> datetime:
    """Get current time in Eastern timezone (handles EST/EDT automatically)"""
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def is_guess_deadline_passed() -> bool:
    """Check if the 12:00 PM EST/EDT deadline for guesses has passed today"""
    now_eastern = get_eastern_time()
    # Create deadline at 12:00 PM Eastern time for today
    deadline_eastern = now_eastern.replace(hour=12, minute=0, second=0, microsecond=0)
    return now_eastern >= deadline_eastern

def get_time_until_deadline() -> Dict[str, int]:
    """Get time remaining until 12:00 PM EST/EDT deadline"""
    now_eastern = get_eastern_time()
    # Create deadline at 12:00 PM Eastern time for today
    deadline_eastern = now_eastern.replace(hour=12, minute=0, second=0, microsecond=0)
    
    if now_eastern >= deadline_eastern:
        return {"hours": 0, "minutes": 0, "seconds": 0, "passed": True}
    
    time_diff = deadline_eastern - now_eastern
    total_seconds = int(time_diff.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return {"hours": hours, "minutes": minutes, "seconds": seconds, "passed": False}

def get_user_guess(data: Dict, friend_name: str, today: str) -> Optional[Dict]:
    """Get a specific friend's guess for today"""
    for guess in data["guesses"]:
        if guess["date"] == today and guess["name"] == friend_name:
            return guess
    return None

def update_user_guess(data: Dict, friend_name: str, today: str, new_guess: str) -> None:
    """Update or add a friend's guess for today"""
    # Remove existing guess if any
    data["guesses"] = [g for g in data["guesses"] if not (g["date"] == today and g["name"] == friend_name)]
    
    # Add new guess
    data["guesses"].append({
        "date": today,
        "name": friend_name,
        "guess_time": new_guess
    })

def calculate_leaderboard(data: Dict) -> Dict[str, int]:
    """Calculate leaderboard showing wins for each friend across all days"""
    # Start with initial scores
    wins = data.get("initial_scores", {friend: 0 for friend in FRIENDS}).copy()
    
    # Group data by date
    dates_with_complete_data = set()
    
    # Find dates that have both all guesses and actual time
    for actual_entry in data["actual_times"]:
        date_str = actual_entry["date"]
        date_guesses = [g for g in data["guesses"] if g["date"] == date_str]
        
        # Check if all friends have guessed for this date
        guessed_friends = {g["name"] for g in date_guesses}
        if len(guessed_friends) == len(FRIENDS) and all(friend in guessed_friends for friend in FRIENDS):
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
        
        # Find all winners (closest guess - handle ties)
        if differences:
            min_difference = min(differences.values())
            winners = [name for name, diff in differences.items() if diff == min_difference]
            # Award 1 point to each person with the closest guess
            for winner in winners:
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
    
    # Main headline - show until all friends have guessed
    if len(today_guesses) < len(FRIENDS):
        st.title("🐭 When will the rat go home today?")
    else:
        st.title("🐭 Rat Office Time Guess")
    
    # Show current date and Eastern time
    eastern_time = get_eastern_time()
    st.write(f"**Date:** {get_today_string()}")
    st.write(f"**Current Eastern Time:** {eastern_time.strftime('%I:%M:%S %p %Z')}")
    
    # Show countdown timer
    deadline_info = get_time_until_deadline()
    if not deadline_info["passed"]:
        st.info(f"⏰ **Time left to submit guesses (until 12:00 PM EST/EDT):** {deadline_info['hours']:02d}:{deadline_info['minutes']:02d}:{deadline_info['seconds']:02d}")
        # Note: Removed auto-refresh to prevent data persistence issues
        # Users can manually refresh to update the timer
    else:
        st.warning("🚫 **Guess deadline has passed** (12:00 PM EST/EDT). No more guesses can be submitted today.")
    
    # Section 1: Friend Guesses
    st.header("📝 Submit Your Guess")
    
    # Check if deadline has passed
    deadline_passed = is_guess_deadline_passed()
    today = get_today_string()
    
    if not deadline_passed:
        # Show input fields for all friends to submit/update guesses
        st.write("Enter or update your guess for when the rat will leave (HH:MM format):")
        
        for friend in FRIENDS:
            existing_guess = get_user_guess(data, friend, today)
            current_guess = existing_guess["guess_time"] if existing_guess else ""
            
            with st.form(f"guess_form_{friend}"):
                st.subheader(f"{friend}")
                if existing_guess:
                    st.write(f"Current guess: **{current_guess}**")
                
                new_guess = st.text_input(
                    "New guess:",
                    value=current_guess,
                    placeholder="HH:MM (e.g., 17:30)",
                    key=f"guess_input_{friend}"
                )
                
                action_text = "Update Guess" if existing_guess else "Submit Guess"
                submitted = st.form_submit_button(action_text)
                
                if submitted and new_guess:
                    # Validate time format
                    try:
                        datetime.strptime(new_guess, "%H:%M")
                        update_user_guess(data, friend, today, new_guess)
                        save_data(data)
                        action = "updated" if existing_guess else "submitted"
                        st.success(f"{friend}'s guess {action} successfully!")
                        st.rerun()
                    except ValueError:
                        st.error(f"Invalid time format. Please use HH:MM format.")
    else:
        st.write("⏰ **Guess submission deadline has passed for today (12:00 PM EST/EDT).**")
    
    # Show current guesses
    if today_guesses:
        st.subheader("Today's Guesses:")
        for guess in sorted(today_guesses, key=lambda x: x["name"]):
            st.write(f"• **{guess['name']}**: {guess['guess_time']}")
    
    # Always show leaderboard
    st.header("📊 Overall Leaderboard")
    leaderboard = calculate_leaderboard(data)
    
    # Sort by wins (descending)
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    
    for i, (friend, wins) in enumerate(sorted_leaderboard):
        emoji = "👑" if i == 0 else "🏅" if i == 1 else "🎖️"
        st.write(f"{emoji} **{friend}**: {wins} wins")
    
    # Section 2: Actual Time Input (only show when all friends have guessed)
    if len(today_guesses) == len(FRIENDS) and today_actual is None:
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
        

    
    # Reset section
    st.header("🔄 Reset Options")
    
    if not deadline_passed:
        st.write("**Individual Reset** (before 12:00 PM EST/EDT deadline):")
        
        # Individual reset buttons
        cols = st.columns(len(FRIENDS))
        for i, friend in enumerate(FRIENDS):
            with cols[i]:
                existing_guess = get_user_guess(data, friend, today)
                if existing_guess:
                    if st.button(f"Reset {friend}", key=f"reset_{friend}"):
                        # Remove this friend's guess
                        data["guesses"] = [g for g in data["guesses"] if not (g["date"] == today and g["name"] == friend)]
                        save_data(data)
                        st.success(f"{friend}'s guess has been reset!")
                        st.rerun()
                else:
                    st.write(f"{friend}: No guess yet")
        
        st.divider()
    
    # Admin reset (always available)
    st.write("**Admin Reset** (resets all today's data):")
    if st.button("Reset ALL today's data", type="secondary"):
        reset_today_data()
        st.success("All today's data has been reset!")
        st.rerun()
    
    # Show data file info
    with st.expander("📁 Data File Info"):
        st.write(f"**Data file path:** `{DATA_FILE}`")
        st.write(f"**File exists:** {os.path.exists(DATA_FILE)}")
        if os.path.exists(DATA_FILE):
            file_size = os.path.getsize(DATA_FILE)
            st.write(f"**File size:** {file_size} bytes")
            st.write(f"**Total guesses:** {len(data['guesses'])}")
            st.write(f"**Total actual times:** {len(data['actual_times'])}")
            
            # Show raw data for debugging
            with st.expander("Raw Data (Debug)"):
                st.json(data)
        else:
            st.write("Data file will be created on first use")
        
        # Show current working directory
        st.write(f"**Current working directory:** `{os.getcwd()}`")

if __name__ == "__main__":
    main()
