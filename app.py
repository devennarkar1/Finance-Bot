from flask import Flask, request, render_template, session
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq
from datetime import timedelta
import markdown2
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Loaded from .env
app.permanent_session_lifetime = timedelta(minutes=30)

# Initialize Groq client with API key from .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Google Sheets setup
# Change the data as you want
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "your_google_creds.json", scope
)
gclient = gspread.authorize(creds)
sheet = gclient.open("Finance_data").sheet1

def get_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# def process_question(question):
#     df = get_data()
#     q = question.lower()

#     if "preferred" in q or "popular" in q:
#         top = df["Avenue"].value_counts().idxmax()
#         return f"<b>📊 Most Preferred Investment:</b><br>• {top}"

#     if "average age" in q and "mutual" in q:
#         avg_age = df[df["Avenue"].str.lower().str.contains("mutual")]["age"].mean()
#         return f"<b>👤 Avg Age of Mutual Fund Investors:</b><br>• {round(avg_age, 2)} years"

#     if "female" in q and "preferred" in q:
#         top_female = df[df["gender"].str.lower() == "female"]["Avenue"].value_counts().idxmax()
#         return f"<b>👩‍🦰 Female's Favorite Avenue:</b><br>• {top_female}"

#     if "male" in q and "preferred" in q:
#         top_male = df[df["gender"].str.lower() == "male"]["Avenue"].value_counts().idxmax()
#         return f"<b>👨 Male's Favorite Avenue:</b><br>• {top_male}"

#     if "reason" in q and "mutual" in q:
#         reason = df["Reason_Mutual"].value_counts().idxmax()
#         return f"<b>📌 Top Reason for Mutual Funds:</b><br>• {reason}"

#     if "savings objective" in q:
#         obj = df["What are your savings objectives?"].value_counts().idxmax()
#         return f"<b>🎯 Common Savings Goal:</b><br>• {obj}"

#     return None  # fallback to LLaMA



@app.route("/", methods=["GET", "POST"])
def chat():
    if "messages" not in session:
        session["messages"] = []

    if request.method == "POST":
        user_input = request.form["message"]
        session["messages"].append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": """
You are a powerful AI Financial Advisor built for Indian users 🇮🇳.
You know the best Indian investment options, tax-saving strategies, budgeting, and money growth tips.
Use emojis ✅ and bold markdown for key points. Keep replies short, smart, and bullet-style like a top-tier AI.
"""}
            ] + session["messages"]
        )

        bot_reply_raw = response.choices[0].message.content
        bot_reply_html = markdown2.markdown(bot_reply_raw)
        session["messages"].append({"role": "assistant", "content": bot_reply_html})

    return render_template("chat.html", messages=session["messages"])

@app.route("/test-sheet")
def test_sheet():
    df = get_data()
    return df.head().to_html()


if __name__ == "__main__":
    app.run(debug=True)
