import os
import sys
import webbrowser
from flask import Flask
from api_server import create_app, API_PORT
from cli_interface import main_menu
from pathlib import Path

# Constant CSV file name
CSV_FILE = os.path.join(os.path.dirname((__file__)), "News_Data.csv")
FRONTEND_HTML = os.path.join(os.path.dirname((__file__)), "frontend.html")

def check_csv_file():
    """Check if the CSV file exists and return status message"""
    if os.path.exists(CSV_FILE):
        return True, f"✅ CSV file found at: {CSV_FILE}"
    else:
        return False, f"❌ No CSV file found at: {CSV_FILE}. Please run the news crawler first."

def start_api_server():
    """Start the Flask API server"""
    print("Starting News Dashboard API server on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    has_csv, message = check_csv_file()
    if not has_csv:
        print(f"⚠️ Warning: {message}")
        print("API will return errors until data is available.")
    
    # Create and start the Flask app
    app = create_app()
    
    # Open the frontend HTML in the default browser
    if os.path.exists(FRONTEND_HTML):
        frontend_url = f"file://{os.path.abspath(FRONTEND_HTML)}"
        print(f"Opening frontend at: {frontend_url}")
        webbrowser.open(frontend_url)
    else:
        print(f"⚠️ Warning: Frontend HTML file not found at: {FRONTEND_HTML}")
        print("Please create the file or check the path.")
    
    # Start the Flask server
    app.run(debug=True, port=API_PORT)

def show_main_menu():
    """Display the main application selection menu"""
    print("\n===== News Dashboard =====")
    print("1. Launch Web Interface (API + Frontend)")
    print("2. Use Command Line Interface")
    print("3. Exit")
    
    while True:
        choice = input("Enter your choice (1, 2, or 3): ")
        
        if choice == "1":
            return "web"
        elif choice == "2":
            return "cli"
        elif choice == "3":
            return "exit"
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    # Check if any command line arguments are provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--api":
            start_api_server()
        elif sys.argv[1] == "--cli":
            has_csv, message = check_csv_file()
            print(message)
            if has_csv:
                main_menu(CSV_FILE)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Available options: --api, --cli")
    else:
        # No command line arguments, show the main menu
        choice = show_main_menu()
        
        if choice == "web":
            start_api_server()
        elif choice == "cli":
            has_csv, message = check_csv_file()
            print(message)
            if has_csv:
                main_menu(CSV_FILE)
        else:  # choice == "exit"
            print("Exiting the program. Goodbye!")