import os
import requests
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import platform
import subprocess

# Define news websites to scrape
NEWS_SITES = {
    "BBC": "https://www.bbc.com/news",
    "The Guardian": "https://www.theguardian.com/world",
    "Medium": "https://medium.com"
}

# CSV file to store news data
CSV_FILE = os.path.join(os.path.dirname(__file__), "news_data.csv")  # Save in the same folder as the script

def fetch_news_content(url):
    """Fetch and extract main article content from the given URL."""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.find('h1').get_text() if soup.find('h1') else 'No Title'
        
        # Extract paragraphs for content
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs]) if paragraphs else 'No content available.'
        
        return {
            "title": title,
            "text": content
        }
    return None

def extract_links(html, base_url):
    """Extracts links using BeautifulSoup."""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        link = urljoin(base_url, a['href'])
        if link.startswith('http'):
            links.append(link)
    return set(links)

def scrape_news():
    """Scrape latest news articles from predefined news websites and save them to CSV."""
    today = datetime.today().strftime("%Y-%m-%d")  # Set today's date
    news_data = []

    for site_name, site_url in NEWS_SITES.items():
        print(f"Fetching news from {site_name}...")

        # Get the HTML content
        response = requests.get(site_url, headers={"User-Agent": "Mozilla/5.0"})

        if response.status_code == 200:
            # Extract links from the page
            links = extract_links(response.text, site_url)

            for link in links:
                article_content = fetch_news_content(link)

                if article_content:
                    article_title = article_content.get("title", "No Title")
                    article_text = article_content.get("text", "No content available.")

                    # Store data in a dictionary
                    news_data.append({
                        "Date": today,  # Use today's date
                        "Source": site_name,
                        "Title": article_title,
                        "URL": link,
                        "Content": article_text[:500]  # Store first 500 characters for readability
                    })
        else:
            print(f"Failed to fetch {site_name}, status code: {response.status_code}")

    return news_data

def save_to_csv(news_data):
    """Save scraped news data to CSV, appending new data and avoiding duplicates."""
    # Create DataFrame from news data
    df_new = pd.DataFrame(news_data)
    
    # Check if the CSV file already exists
    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE)
        # Append new data to existing data, avoiding duplicates
        df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=["Date", "Source", "Title", "URL"])
    else:
        df_combined = df_new
    
    # Save the combined data back to the CSV file
    df_combined.to_csv(CSV_FILE, index=False, encoding="utf-8")
    print(f"✅ News data saved to {CSV_FILE}")

def open_csv_in_default_app():
    """Open the CSV file in the default application for CSV files."""
    if os.path.exists(CSV_FILE):
        try:
            if platform.system() == "Windows":
                os.startfile(CSV_FILE)  # Open file in default app on Windows
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", CSV_FILE], check=True)
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", CSV_FILE], check=True)
            print(f"📂 Opened {CSV_FILE} in the default application.")
        except Exception as e:
            print(f"❌ Failed to open the CSV file: {e}")
    else:
        print("❌ CSV file does not exist.")

def display_statistics_by_date(date):
    """Display statistics for news data on a specific date."""
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Filter data for the specified date
        df_filtered = df[df["Date"] == date]
        
        if not df_filtered.empty:
            print(f"\n📊 Statistics for {date}:")
            print(f"Total articles: {len(df_filtered)}")
            print(f"Sources: {df_filtered['Source'].unique()}")
            print(f"Articles per source:\n{df_filtered['Source'].value_counts()}")
        else:
            print(f"❌ No data found for {date}.")
    else:
        print("❌ CSV file does not exist.")

def main_menu():
    """Display the main menu and handle user input."""
    while True:
        print("\n===== Main Menu =====")
        print("1. Open the CSV file with the default application")
        print("2. Display statistics of the news data for a specific date")
        print("3. Exit")
        choice = input("Enter your choice (1, 2, or 3): ")
        dm_pw = "DDL"

        if choice == "DDL"
            break 
        elif choice == "1":
            open_csv_in_default_app()
        elif choice == "2":
            date = input("Enter the date (YYYY-MM-DD) to search: ")
            display_statistics_by_date(date)
        elif choice == "3":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def developer_mode():
    """This is the developer mode of the program. This can only be access with a certain password. """
        while True:
            print("1. Display statistics of the news data for a specific date")
            print("2. Open the CSV file with the default application")
            print("3. Exit")
            choice = input()
        
            if choice == "1":
                date = input("Enter the date (YYYY-MM-DD) to search: ")
                display_statistics_by_date(date)
            elif choice == "2":
                open_csv_in_default_app()
            elif choice == "3":
                print("Exiting the program. Goodbye!")
                break
   
# Run the web crawler and main menu
if __name__ == "__main__":
    # Always run the web crawler before showing the main menu
    print("🕷️ Running the web crawler to fetch the latest news...")
    news_data = scrape_news()
    if news_data:
        save_to_csv(news_data)
        print("✅ Web crawler completed. Showing the main menu...")
        main_menu()  # Show the main menu after fetching and saving data
    else:
        print("❌ No new articles found. Exiting the program.")