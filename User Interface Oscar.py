import os
import pandas as pd
import platform
import subprocess
from datetime import datetime
import pyttsx3
from openai import OpenAI
import matplotlib.pyplot as plt

# Developer mode password
DEVELOPER_PASSWORD = "DDL"

# OpenAI API configuration
client = OpenAI(
    api_key="api-key",  # Replace with your actual API key
    base_url="https://api.deepseek.com"
)

# Constant CSV file name
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "News_Data.csv")

def load_news():
    """Reads today's news from CSV."""
    if not os.path.exists(CSV_FILE):
        print("No news data found.")
        return None

    df = pd.read_csv(CSV_FILE)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    today_news = df[df["Date"] == df["Date"].max()]

    if today_news.empty:
        print("No news found for today.")
        return None

    return today_news

def generate_summary(news_data):
    """Generates a summary using OpenAI GPT."""
    news_text = "\n".join(f"- {row['Title']}: {row['Content'][:200]}" for _, row in news_data.iterrows())

    prompt = f"""
    Here is today's top news:
    {news_text}

    Please summarize today's key events in a **friendly, conversational way**.
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # Update the model as needed
            messages=[{"role": "system", "content": "You are a helpful AI summarizing daily news."},
                      {"role": "user", "content": prompt}],
            stream=False
        )
    except Exception as e:
        print(f"API call failed: {e}")
        return None

    return response.choices[0].message.content.strip()

def plot_news_topics(news_data):
    """Generates a chart showing the distribution of news sources."""
    source_counts = news_data["Source"].value_counts()

    plt.figure(figsize=(8, 5))
    source_counts.plot(kind="bar", color=["skyblue", "orange", "green"])

    plt.title("Today's News Distribution by Source")
    plt.xlabel("News Source")
    plt.ylabel("Number of Articles")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    plt.savefig("news_chart.png")  # Save the chart
    plt.show()

def read_highlights_and_speak(file_path):
    """
    Reads the highlights from the CSV file and converts them into speech.
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

        # Extract highlights (first 500 characters of content)
        for index, row in data.iterrows():
            highlight = f"Title: {row['Title']}. Content: {row['Content'][:500]}"
            print(f"Reading highlight {index + 1}: {highlight}")  # Display in the terminal
            engine.say(highlight)  # Speak the highlight

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
        print("1. Read highlights from the CSV file and speak them")
        print("2. Generate a summary of today's news and display a chart")
        print("3. Exit")
        choice = input("Enter your choice (1, 2, or 3): ")

        if choice == "1":
            read_highlights_and_speak(csv_file)
        elif choice == "2":
            news_data = load_news()
            if news_data is not None:
                print("\n📢 **Today's News Summary:**")
                summary = generate_summary(news_data)
                print(summary)

                print("\n📊 **Generating News Chart...**")
                plot_news_topics(news_data)
            else:
                print("❌ No news data available.")
        elif choice == "3":
            print("Exiting the program. Goodbye!")
            break
        elif choice == DEVELOPER_PASSWORD:  # Developer mode activation
            developer_mode(csv_file)
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    if os.path.exists(CSV_FILE):
        print(f"✅ CSV file found at: {CSV_FILE}")
        main_menu(CSV_FILE)
    else:
        print(f"❌ No CSV file found at: {CSV_FILE}. Please run the news crawler first.")