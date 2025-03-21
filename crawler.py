import os
import requests
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

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
                        "Date": today,
                        "Source": site_name,
                        "Title": article_title,
                        "URL": link,
                        "Content": article_text[:500]  # Store first 500 characters for readability
                    })
        else:
            print(f"Failed to fetch {site_name}, status code: {response.status_code}")

    return news_data

def save_to_csv(news_data):
    """Save scraped news data to CSV, updating it each time the script runs."""
    file_exists = os.path.exists(CSV_FILE)
    
    # Create DataFrame from news data
    df = pd.DataFrame(news_data)
    
    # Remove duplicates based on Title and URL
    df = df.drop_duplicates(subset=["Title", "URL"])

    # Append data to CSV file
    df.to_csv(CSV_FILE, mode="a", index=False, header=not file_exists, encoding="utf-8")
    print(f"✅ News data saved to {CSV_FILE}")

# Run the scraper
if __name__ == "__main__":
    news_data = scrape_news()
    if news_data:
        save_to_csv(news_data)
    else:
        print("No new articles found.")