import os
import pandas as pd
import platform
import subprocess
from datetime import datetime
import pyttsx3

# Developer mode password
DEVELOPER_PASSWORD = "DDL"

def read_csv_and_speak(file_path):
    """
    Read the CSV file and convert its content into speech.
    """
    try:
        # Read the CSV file using pandas
        data = pd.read_csv(file_path, encoding="utf-8")

        # Initialize the text-to-speech engine
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        male_voice_index = 1  # Index for male voice (may vary based on system)
        engine.setProperty('voice', voices[male_voice_index].id)
        engine.setProperty('rate', 150)  # Adjust speech rate
        engine.setProperty('volume', 1.0)  # Adjust volume

        # Check if the CSV file is empty
        if data.empty:
            print("The CSV file is empty.")
            engine.say("The CSV file is empty.")
            engine.runAndWait()
            return

        # Iterate through each row of the data
        for index, row in data.iterrows():
            # Convert each row into a string
            row_text = ", ".join(f"{col}: {row[col]}" for col in data.columns)
            print(f"Reading row {index + 1}: {row_text}")  # Display in the terminal
            engine.say(row_text)  # Speak the row content

        # Wait for the speech to finish
        engine.runAndWait()

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        engine = pyttsx3.init()
        engine.say("The CSV file was not found. Please check the file path.")
        engine.runAndWait()
    except Exception as e:
        print(f"An error occurred: {e}")
        engine = pyttsx3.init()
        engine.say("An error occurred while reading the CSV file.")
        engine.runAndWait()

def open_csv_in_default_app(csv_file):
    """Open the CSV file in the default application."""
    if os.path.exists(csv_file):
        try:
            if platform.system() == "Windows":
                os.startfile(csv_file)  # Open file in default app on Windows
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", csv_file], check=True)
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", csv_file], check=True)
            print(f"📂 Opened {csv_file} in the default application.")
        except Exception as e:
            print(f"❌ Failed to open the CSV file: {e}")
    else:
        print(f"❌ CSV file does not exist at: {csv_file}")

def display_statistics_by_date(csv_file, date):
    """Display statistics for news data on a specific date."""
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            df = df[df['Date'] == date]  # Filter by date
            print(f"\n📊 Statistics for {date}:")
            print(f"Total articles: {len(df)}")
            print(f"Sources: {df['Source'].unique()}")
            print(f"Articles per source:\n{df['Source'].value_counts()}")
        except Exception as e:
            print(f"❌ No data found for {date}: {e}")
    else:
        print(f"❌ CSV file does not exist at: {csv_file}")

def developer_mode(csv_file):
    """Developer mode for additional functionality."""
    print("\n🔧 Developer mode activated.")
    # Add developer-specific functions here
    while True:
        print("1. Open the CSV file with the default application")
        print("2. Display statistics of the news data for a specific date")
        print("3. Exit developer mode")
        dm_choice = input("Enter your choice: ")

        if dm_choice == "1":
            open_csv_in_default_app(csv_file)
        elif dm_choice == "2":
            date = input("Enter the date (YYYY-MM-DD) to search: ")
            display_statistics_by_date(csv_file, date)
        elif dm_choice == "3":
            print("Exiting developer mode.")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def main_menu(csv_file):
    """Display the main menu and handle user input."""
    while True:
        print("\n===== Main Menu =====")
        print("1. Read the CSV file and speak its content")
        print("2. Exit")
        choice = input("Enter your choice (1 or 2): ")

        if choice == "1":
            read_csv_and_speak(csv_file)
        elif choice == "2":
            print("Exiting the program. Goodbye!")
            break
        elif choice == DEVELOPER_PASSWORD:  # Developer mode activation
            developer_mode(csv_file)
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    # Set the CSV file name to a constant value
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
    csv_file = os.path.join(script_dir, "C:\\Users\\chngo\\OneDrive\\Desktop\\EdUHK\\2425\\S2\\Courses\\INT2093 Fundemental of Neural Networks\\INT2093 Group Project\\news-project\\News_Data.csv")  # Construct the full path to the CSV file
    
    if os.path.exists(csv_file):
        print(f"✅ CSV file found at: {csv_file}")
        main_menu(csv_file)
    else:
        print(f"❌ No CSV file found at: {csv_file}. Please run the news crawler first.")