import os
import pandas as pd
from openai import OpenAI
import matplotlib.pyplot as plt

# ✅ Set OpenAI API Key
client = OpenAI(
    api_key="api-key",
    base_url="https://api.deepseek.com"
)

# ✅ Load News Data
CSV_FILE = "news_data.csv"

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
        print(f"API调用失败: {e}")
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

# ✅ Run the script
news_data = load_news()
if news_data is not None:
    print("\n📢 **Today's News Summary:**")
    summary = generate_summary(news_data)
    print(summary)

    print("\n📊 **Generating News Chart...**")
    plot_news_topics(news_data)
else:
    print("❌ No news data available.")