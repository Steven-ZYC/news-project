import os
import pandas as pd
import platform
import subprocess

# Developer mode password
DEVELOPER_PASSWORD = "DDL"

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
        print("❌ CSV file does not exist.")

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
        print("❌ CSV file does not exist.")

def developer_mode():
    """Developer mode for additional functionality."""
    print("\n🔧 Developer mode activated.")
    # Add developer-specific functions here
    print("Developer mode functionality will be added later.")
    print("Exiting developer mode. Goodbye!")

def main_menu(csv_file):
    """Display the main menu and handle user input."""
    while True:
        print("\n===== Main Menu =====")
        print("1. Open the CSV file with the default application")
        print("2. Display statistics of the news data for a specific date")
        print("3. Exit")
        choice = input("Enter your choice (1, 2, or 3): ")

        if choice == "1":
            open_csv_in_default_app(csv_file)
        elif choice == "2":
            date = input("Enter the date (YYYY-MM-DD) to search: ")
            display_statistics_by_date(csv_file, date)
        elif choice == "3":
            print("Exiting the program. Goodbye!")
            break
        elif choice == DEVELOPER_PASSWORD:  # Developer mode activation
            developer_mode()
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    # Set the CSV file name to the current date
    today = datetime.today().strftime("%Y-%m-%d")
    csv_file = os.path.join(os.path.dirname(__file__), f"{today}.csv")
    
    if os.path.exists(csv_file):
        main_menu(csv_file)
    else:
        print("❌ No CSV file found. Please run the news crawler first.")