import os
import subprocess
import pandas as pd
import pyttsx3
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import backend

# Paths to the crawler and UI script
CRAWLER_SCRIPT = "crawler.py"
UI_SCRIPT = "backend.py"
CSV_FILE = "news_data.csv"

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# GUI Application
class UnifiedNewsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("News System")
        self.root.geometry("600x700")
        self.root.configure(bg="#1e1e2f")  # Dark background for a modern look

        # Title Label
        self.label = tk.Label(root, text="📰 News System", font=("Helvetica Neue", 24, "bold"), bg="#1e1e2f", fg="white")
        self.label.pack(pady=20)

        # Dotted Sphere Visualization
        self.canvas = tk.Canvas(root, width=200, height=200, bg="#1e1e2f", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.core = self.canvas.create_oval(50, 50, 150, 150, fill="#fffff9", outline="#ffffff", width=4, dash=(5, 5))

        # Buttons with modern styling
        self.create_button("🌐 Run Web Crawler", self.run_crawler, "#ffcc00")
        self.create_button("📜 Summarize News", self.summarize_news, "#66ccff")
        self.create_button("📊 Show News Chart", self.show_chart, "#99ff99")
        self.create_button("🚪 Exit", root.quit, "#ff6666")

    def create_button(self, text, command, bg_color):
        """Helper function to create styled buttons."""
        button = tk.Button(self.root, text=text, command=command, font=("Helvetica Neue", 14), bg=bg_color, fg="black", relief="raised", bd=3)
        button.pack(pady=10, fill=tk.X, padx=20)

    def expand_core(self):
        """Expands the dotted core when speaking."""
        self.canvas.coords(self.core, 10, 10, 500, 500)

    def shrink_core(self):
        """Shrinks the dotted core after speaking."""
        self.canvas.coords(self.core, 50, 50, 150, 150)

    def run_crawler(self):
        """Runs the web crawler script."""
        try:
            subprocess.run(["python", CRAWLER_SCRIPT], check=True)
            messagebox.showinfo("Success", "Web crawler executed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run crawler: {e}")

    def summarize_news(self):
        """Generates and displays a summary."""
        summary = backend.generate_summary(backend.load_news())
        if summary:
            self.expand_core()  # Expand animation
            engine.say(summary)  
            engine.runAndWait()
            self.shrink_core()
            messagebox.showinfo("News Summary", summary)
        else:
            messagebox.showinfo("Info", "No news summary available.")

    def show_chart(self):
        """Displays a bar chart of news sources."""
        if not os.path.exists(CSV_FILE):
            messagebox.showerror("Error", "CSV file not found!")
            return

        df = pd.read_csv(CSV_FILE, encoding="utf-8")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        today_news = df[df["Date"] == df["Date"].max()]

        if today_news.empty:
            messagebox.showinfo("Info", "No news found for today.")
            return

        source_counts = today_news["Source"].value_counts()
        plt.figure(figsize=(10, 6))
        source_counts.plot(kind="bar", color=["#ff4081", "#66ccff", "#99ff99"])
        plt.title("Today's News Distribution by Source", fontsize=16)
        plt.xlabel("News Source", fontsize=14)
        plt.ylabel("Number of Articles", fontsize=14)
        plt.xticks(rotation=45)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = UnifiedNewsApp(root)
    root.mainloop()