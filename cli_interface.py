import os
import platform
import subprocess
from api_server import (
    load_news, 
    generate_summary, 
    plot_news_topics, 
    read_highlights_and_speak, 
    open_csv_in_default_app
)

# Developer mode password
DEVELOPER_PASSWORD = "DDL"

def developer_mode(csv_file):
    """Developer mode for additional functionality."""
    print("\n🔧 Developer mode activated.")
    # Add developer-specific functions here
    while True:
        print("1. Open the CSV file with the default application")
        print("2. Exit developer mode")
        dm_choice = input("Enter your choice: ")

        if dm_choice == "1":
            open_csv_in_default_app(csv_file)
        elif dm_choice == "2":
            print("Exiting developer mode.")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def main_menu(csv_file):
    """Display the main menu and handle user input."""
    while True:
        print("\n===== News Dashboard CLI =====")
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