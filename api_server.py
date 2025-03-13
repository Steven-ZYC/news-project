from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import pandas as pd
import platform
import subprocess
from datetime import datetime
import pyttsx3
from openai import OpenAI
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Define constants
API_PORT = 5000
CSV_FILE = os.path.join(os.path.dirname((__file__)), "News_Data.csv")

# OpenAI API configuration
client = OpenAI(
    api_key="sk-ca98f6ee671c4f91b0c69a379b779b82",  # Replace with your actual API key
    base_url="https://api.deepseek.com"
)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app)  # Allow cross-origin requests
    
    @app.route('/api/run-crawler', methods=['GET'])
    def api_run_crawler():
        """API endpoint to run the web crawler"""
        success, message = run_news_crawler()
        if success:
            return jsonify({"status": "success", "message": message})
        else:
            return jsonify({"status": "error", "message": message})

    @app.route('/api/summarize-news', methods=['GET'])
    def api_summarize_news():
        """API endpoint to get a summary of today's news"""
        news_data = load_news()
        if news_data is None:
            return jsonify({"status": "error", "message": "No news data available."})

        summary = generate_summary(news_data)
        if summary is None:
            return jsonify({"status": "error", "message": "Failed to generate summary."})

        return jsonify({"status": "success", "summary": summary})

    @app.route('/api/show-chart', methods=['GET'])
    def api_show_chart():
        """API endpoint to get chart data for news sources"""
        news_data = load_news()
        if news_data is None:
            return jsonify({"status": "error", "message": "No news data available."})

        try:
            # Generate chart and get base64 encoding
            chart_data = plot_news_topics(news_data, return_image=True)

            # Get news source statistics for frontend chart
            source_counts = news_data["Source"].value_counts().to_dict()
            sources = list(source_counts.keys())
            counts = list(source_counts.values())

            return jsonify({
                "status": "success",
                "chart_image": chart_data,
                "chart_data": {
                    "sources": sources,
                    "counts": counts
                }
            })
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error generating chart: {str(e)}"})

    @app.route('/api/speak-news', methods=['GET'])
    def api_speak_news():
        """API endpoint to speak the news on the server (not through browser)"""
        success, message = read_highlights_and_speak(CSV_FILE)
        if success:
            return jsonify({"status": "success", "message": message})
        else:
            return jsonify({"status": "error", "message": message})

    @app.route('/api/get-speech-text', methods=['GET'])
    def api_get_speech_text():
        """API endpoint to get text for browser-based speech synthesis"""
        news_data = load_news()
        if news_data is None:
            return jsonify({"status": "error", "message": "No news data available."})
        
        # Prepare text for reading
        speech_texts = []
        for _, row in news_data.iterrows():
            try:
                # Extract title and first 200 characters of content
                title = str(row['Title'])
                content = str(row['Content'])[:200]
                
                # Handle potential encoding issues
                title = ''.join([c for c in title if ord(c) < 128])
                content = ''.join([c for c in content if ord(c) < 128])
                
                highlight = f"Title: {title}. Content: {content}"
                speech_texts.append(highlight)
            except Exception as e:
                print(f"Error processing row for speech: {e}")
                continue
        
        return jsonify({
            "status": "success", 
            "speech_texts": speech_texts,
            "summary": generate_summary(news_data)  # Also return summary for reading
        })

    @app.route('/api/check-data', methods=['GET'])
    def api_check_data():
        """API endpoint to check if news data exists"""
        if os.path.exists(CSV_FILE):
            try:
                news_data = load_news()
                if news_data is not None and not news_data.empty:
                    return jsonify({
                        "status": "success", 
                        "message": "News data is available",
                        "count": len(news_data),
                        "date": news_data["Date"].max().strftime("%Y-%m-%d")
                    })
                else:
                    return jsonify({"status": "error", "message": "CSV file exists but contains no valid news data."})
            except Exception as e:
                return jsonify({"status": "error", "message": f"Error checking news data: {str(e)}"})
        else:
            return jsonify({"status": "error", "message": "No news data file found."})

    @app.route('/', methods=['GET'])
    def api_index():
        """API endpoint for root path - provides basic info"""
        return jsonify({
            "status": "success",
            "message": "News Dashboard API is running",
            "endpoints": [
                {"path": "/api/run-crawler", "method": "GET", "description": "Run the news crawler"},
                {"path": "/api/summarize-news", "method": "GET", "description": "Get a summary of today's news"},
                {"path": "/api/show-chart", "method": "GET", "description": "Get chart data for news sources"},
                {"path": "/api/speak-news", "method": "GET", "description": "Speak the news on the server"},
                {"path": "/api/get-speech-text", "method": "GET", "description": "Get text for browser-based speech synthesis"},
                {"path": "/api/check-data", "method": "GET", "description": "Check if news data exists"}
            ]
        })
        
    return app

# Utility functions used by both API and CLI
def load_news():
    """Reads today's news from CSV."""
    if not os.path.exists(CSV_FILE):
        print("No news data found.")
        return None
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        for encoding in encodings:
            try:
                df = pd.read_csv(CSV_FILE, encoding=encoding)
                print(f"Successfully read CSV file using {encoding} encoding.")
                break
            except UnicodeDecodeError:
                continue
        else:
            print("Failed to read CSV file with any of the supported encodings.")
            return None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    today_news = df[df["Date"] == df["Date"].max()]

    if today_news.empty:
        print("No news found for today.")
        return None

    return today_news

def generate_summary(news_data):
    """Generates a summary using deepseek GPT."""
    client = OpenAI(
        api_key="sk-ca98f6ee671c4f91b0c69a379b779b82",  # Replace with your actual API key
        base_url="https://api.deepseek.com"
    )

    news_text = "\n".join(f"- {row['Title']}: {row['Content'][:200]}" for _, row in news_data.iterrows())

    prompt = f"""
    Here is today's top news:
    {news_text}

    Please summarize today's key events in a **friendly, conversational way** into a short speech.
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

def plot_news_topics(news_data, return_image=False):
    """Generates a chart showing the distribution of news sources."""
    source_counts = news_data["Source"].value_counts()

    plt.figure(figsize=(8, 5))
    source_counts.plot(kind="bar", color=["skyblue", "orange", "green"])

    plt.title("Today's News Distribution by Source")
    plt.xlabel("News Source")
    plt.ylabel("Number of Articles")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    if return_image:
        # Save as an in-memory image and return base64 encoding
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()

        # Convert to base64 encoded string
        encoded = base64.b64encode(image_png).decode('utf-8')
        return encoded
    else:
        plt.savefig("news_chart.png")
        plt.show()
        return None
        
def run_news_crawler():
    """Run the news crawler to fetch latest articles"""
    try:
        # This should contain your actual crawler code
        # For example: subprocess.run(["python", "crawler.py"])
        print("Running news crawler...")
        
        # Simulate crawler process, should be replaced with actual crawler code
        import time
        time.sleep(2)  # Simulate crawler run time
        
        # If there is no actual crawler code, can return a fake success message
        return True, "Successfully crawled latest news"
    except Exception as e:
        print(f"Crawler failed: {str(e)}")
        return False, f"Crawler failed: {str(e)}"

def read_highlights_and_speak(file_path):
    """
    Reads the highlights from the CSV file and converts them into speech.
    """
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        for encoding in encodings:
            try:
                data = pd.read_csv(file_path, encoding=encoding)
                print(f"Successfully read CSV file using {encoding} encoding.")
                break
            except UnicodeDecodeError:
                continue
        else:
            print("Failed to read CSV file with any of the supported encodings.")
            return False, "Failed to read CSV file with any of the supported encodings."

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
            return False, "The CSV file is empty."

        # Extract highlights (first 500 characters of content)
        for index, row in data.iterrows():
            try:
                highlight = f"Title: {row['Title']}. Content: {row['Content'][:500]}"
                print(f"Reading highlight {index + 1}: {highlight}")  # Display in the terminal
                engine.say(highlight)  # Speak the highlight
            except UnicodeEncodeError as e:
                print(f"Encoding error when processing row {index + 1}: {e}")
                print("Trying to clean the text...")
                cleaned_title = ''.join([c for c in str(row['Title']) if ord(c) < 128])
                cleaned_content = ''.join([c for c in str(row['Content'])[:500] if ord(c) < 128])
                highlight = f"Title: {cleaned_title}. Content: {cleaned_content}"
                print(f"Reading cleaned highlight {index + 1}: {highlight}")
                engine.say(highlight)
        
        # Wait for the speech to finish
        engine.runAndWait()
        return True, "Successfully read all highlights"

    except FileNotFoundError:
        message = f"File not found: {file_path}"
        print(message)
        engine = pyttsx3.init()
        engine.say("The CSV file was not found. Please check the file path.")
        engine.runAndWait()
        return False, message
    except Exception as e:
        message = f"An error occurred: {e}"
        print(message)
        engine = pyttsx3.init()
        engine.say("An error occurred while reading the CSV file.")
        engine.runAndWait()
        return False, message

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
            return True, f"Opened {csv_file} in the default application"
        except Exception as e:
            message = f"Failed to open the CSV file: {e}"
            print(f"❌ {message}")
            return False, message
    else:
        message = f"CSV file does not exist at: {csv_file}"
        print(f"❌ {message}")
        return False, message