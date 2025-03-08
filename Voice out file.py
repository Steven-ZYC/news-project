import pandas as pd
import pyttsx3

def read_csv_and_speak(file_path):
    """
    讀取 CSV 文件並將內容語音化。
    """
    try:
        # 使用 pandas 讀取 CSV 文件
        data = pd.read_csv(file_path, encoding="utf-8")

        # 初始化語音引擎
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        male_voice_index = 1
        engine.setProperty('voice', voices[male_voice_index].id)
        engine.setProperty('rate', 150)  # 調整語速
        engine.setProperty('volume', 1.0)  # 調整音量
        

        # 確認文件是否有數據
        if data.empty:
            print("The CSV File is empty")
            engine.say("The CSV file is empty.")
            engine.runAndWait()
            return

        # 開始遍歷每行數據
        for index, row in data.iterrows():
            # 將每行數據轉化為文字
            row_text = ", ".join(f"{col}: {row[col]}" for col in data.columns)
            print(f"Reading row {index + 1}: {row_text}")  # 顯示在終端
            engine.say(row_text)  # 語音讀出

        # 等待語音播放完成
        engine.runAndWait()

    except FileNotFoundError:
        print(f"文件未找到：{file_path}")
        engine = pyttsx3.init()
        engine.say("The CSV file was not found. Please check the file path.")
        engine.runAndWait()
    except Exception as e:
        print(f"發生錯誤：{e}")
        engine = pyttsx3.init()
        engine.say("An error occurred while reading the CSV file.")
        engine.runAndWait()

# 測試程式
if __name__ == "__main__":
    file_path = "C:\\Users\\chngo\\OneDrive\\Desktop\\EdUHK\\2425\\S2\\Courses\\INT2093 Fundemental of Neural Networks\\INT2093 Group Project\\news-project\\News_Data.csv"# 替換為你的 CSV 文件路徑
    read_csv_and_speak(file_path)