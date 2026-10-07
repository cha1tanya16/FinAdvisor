from flask import Flask, flash, render_template, request, redirect, session, url_for
import joblib
import pandas as pd
import google.generativeai as genai
from flask import jsonify
from flask import send_from_directory
import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "financial123"
latest_user_data = {}
genai.configure(
        api_key=os.getenv("GEMINI_API_KEY")
)

gemini_model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ==========================
# LOAD MODEL & ENCODERS
# ==========================

model = joblib.load("models/financial_model.pkl")
goal_encoder = joblib.load("models/goal_encoder.pkl")
risk_encoder = joblib.load("models/risk_encoder.pkl")
category_encoder = joblib.load("models/category_encoder.pkl")

print("All Models Loaded Successfully!")


# ==========================
# HOME ROUTE
# ==========================

@app.route("/", methods=["GET", "POST"])
def home():
      # Only logged in users can access dashboard
    if "user_id" not in session:
        return redirect("/login")

    username = session.get("username", "User")

    prediction = None
    recommendation = None
    tip = None

    health_score = None
    savings_rate = None
    expense_ratio = None
    emergency_fund_coverage = None
    emergency_status = None
    income = None
    expenses = None
    savings = None

    goal = None
    risk = None

    chart_income = 0
    chart_expenses = 0
    chart_savings = 0

    goal_progress = 0
    target_amount = 0
    future_savings = 0
    if request.method == "POST":

        # ==========================
        # USER INPUT
        # ==========================

        age = int(request.form["age"])
        if age < 18:
           age = 18

        if age > 100:
         age = 100
        income = float(request.form["income"])
        expenses = float(request.form["expenses"])
        savings = float(request.form["savings"])
        if income <= 0:
         income = 1

        if expenses <= 0:
          expenses = 1

        if savings < 0:
         savings = 0

        goal = request.form["goal"]     
        risk = request.form["risk"]
        

        original_risk = risk

                # ==========================
        # GOAL TRACKER
        # ==========================

        goal_targets = {
            "House": 500000,
            "Vehicle": 300000,
            "Emergency Fund": 100000,
            "Retirement": 1000000,
            "Education": 200000,
            "Investment": 250000
        }
       

        target_amount = goal_targets.get(goal, 100000)

        goal_progress = round(
            (savings / target_amount) * 100,
            1
        )

        if goal_progress > 100:
            goal_progress = 100
        

        # ==========================
        # CONVERT UI RISK
        # ==========================

        if risk == "Conservative":
            risk = "Low"

        elif risk == "Balanced":
            risk = "Medium"

        elif risk == "Aggressive":
            risk = "High"

        # ==========================
        # DERIVED FEATURES
        # ==========================

        savings_rate = (income - expenses) / income
        expense_ratio = expenses / income
        future_savings =round(savings * 12,0)
       
        if expenses <= 0:
         expenses = 1
        emergency_fund_coverage = savings / expenses
        if emergency_fund_coverage >= 6:
         emergency_status = "Healthy"

        elif emergency_fund_coverage >= 3:
         emergency_status = "Moderate"

        else:
         emergency_status = "Weak"

         

        # ==========================
        # SAVINGS SCORE
        # ==========================

        if savings_rate < 0.05:
            savings_score = 5
        elif savings_rate < 0.10:
            savings_score = 10
        elif savings_rate < 0.20:
            savings_score = 20
        elif savings_rate < 0.30:
            savings_score = 30
        else:
            savings_score = 40

        # ==========================
        # EXPENSE SCORE
        # ==========================

        if expense_ratio > 0.90:
            expense_score = 5
        elif expense_ratio > 0.80:
            expense_score = 10
        elif expense_ratio > 0.70:
            expense_score = 15
        elif expense_ratio > 0.60:
            expense_score = 20
        elif expense_ratio > 0.50:
            expense_score = 25
        else:
            expense_score = 30

        # ==========================
        # EMERGENCY SCORE
        # ==========================

        if emergency_fund_coverage < 1:
            emergency_score = 2
        elif emergency_fund_coverage < 3:
            emergency_score = 5
        elif emergency_fund_coverage < 6:
            emergency_score = 10
        elif emergency_fund_coverage < 12:
            emergency_score = 15
        else:
            emergency_score = 20

        # ==========================
        # RISK SCORE
        # ==========================

        if (
            (goal == "Investment" and risk == "High") or
            (goal == "Retirement" and risk == "Low") or
            (goal == "Emergency Fund" and risk == "Low") or
            (goal == "House" and risk == "Medium") or
            (goal == "Education" and risk == "Medium") or
            (goal == "Vehicle" and risk == "Medium")
        ):
            risk_score = 10

        elif (
            (goal == "Investment" and risk == "Medium") or
            (goal == "Retirement" and risk == "Medium") or
            (goal == "Emergency Fund" and risk == "Medium") or
            (goal == "House" and risk == "Low") or
            (goal == "House" and risk == "High") or
            (goal == "Education" and risk == "Low") or
            (goal == "Education" and risk == "High") or
            (goal == "Vehicle" and risk == "Low") or
            (goal == "Vehicle" and risk == "High")
        ):
            risk_score = 5

        else:
            risk_score = 0

        # ==========================
        # HEALTH SCORE
        # ==========================

        health_score = (
            savings_score +
            expense_score +
            emergency_score +
            risk_score
        )

        # ==========================
        # MODEL INPUT
        # ==========================

        goal_encoded = goal_encoder.transform([goal])[0]
        risk_encoded = risk_encoder.transform([risk])[0]

        input_data = pd.DataFrame(
            [[
                age,
                income,
                expenses,
                savings,
                goal_encoded,
                risk_encoded,
                savings_rate,
                expense_ratio,
                emergency_fund_coverage,
                health_score
            ]],
            columns=[
                "Age",
                "Income",
                "Expenses",
                "Savings",
                "Goal",
                "Risk",
                "Savings_Rate",
                "Expense_Ratio",
                "Emergency_Fund_Coverage",
                "Health_Score"
            ]
        )

        # ==========================
        # PREDICTION
        # ==========================

        result = model.predict(input_data)

        prediction = category_encoder.inverse_transform(result)[0]

        # ==========================
        # GOAL-SPECIFIC RECOMMENDATIONS
        # ==========================

        if prediction == "Excellent":

            if goal == "Investment":
                recommendation = (
                    "Your finances are excellent. Consider diversifying into mutual funds, ETFs, and long-term investments."
                )

            elif goal == "House":
                recommendation = (
                    "You are financially prepared for a future house purchase. Continue strengthening your down-payment fund."
                )

            else:
                recommendation = (
                    "Maintain your strong financial habits and continue progressing toward your goal."
                )

            tip = "Diversify investments to balance risk and long-term returns."

        elif prediction == "Good":

            if goal == "Retirement":
                recommendation = (
                    "Increase retirement contributions and maintain a healthy emergency fund."
                )

            elif goal == "Investment":
                recommendation = (
                    "You have a strong base. Consider increasing monthly investment allocations."
                )

            else:
                recommendation = (
                    "Continue improving savings and stay focused on your financial objective."
                )

            tip = "Aim to save at least 20% of your monthly income."

        elif prediction == "Average":

            if goal == "House":
                recommendation = (
                    "Reduce unnecessary expenses and increase savings to reach your housing goal faster."
                )

            elif goal == "Emergency Fund":
                recommendation = (
                    "Build an emergency fund covering at least six months of expenses."
                )

            else:
                recommendation = (
                    "Your finances are stable but need improvement. Increase savings and reduce spending."
                )

            tip = "Track expenses weekly and identify unnecessary spending."

        else:

            recommendation = (
                "Focus on budgeting, debt reduction, and building a strong emergency fund."
            )

            tip = "Create a strict monthly budget and monitor every major expense."

        # ==========================
        # CHART VALUES
        # ==========================

        chart_income = income
        chart_expenses = expenses
        chart_savings = savings

        risk = original_risk
        global latest_user_data

        latest_user_data = {

    "income": income,
    "expenses": expenses,
    "savings": savings,

    "goal": goal,
    "risk": original_risk,

    "health_score": health_score,

    "prediction": prediction,

    "savings_rate": round(
        savings_rate * 100,
        2
    ),

    "emergency_fund": round(
        emergency_fund_coverage,
        2
    )
}

    return render_template(

        "index.html",
        username=username,
        email=session.get("email"),
        prediction=prediction,
        recommendation=recommendation,
        tip=tip,

        health_score=health_score,
        savings_rate=savings_rate,
        expense_ratio=expense_ratio,
        emergency_fund_coverage=emergency_fund_coverage,
        emergency_status=emergency_status,

        income=income,
        expenses=expenses,
        savings=savings,

        goal=goal,
        risk=risk,

        chart_income=chart_income,
        chart_expenses=chart_expenses,
        chart_savings=chart_savings,

        future_savings=future_savings,
        goal_progress=goal_progress,
        target_amount=target_amount
    )

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.","success")

    return redirect("/login")

@app.route("/advisor")
def advisor():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "advisor.html",
        username=session.get("username"),
        email=session.get("email")
    )

@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    if "user_id" not in session:

     return jsonify({

        "answer":"Please login first."
   })

    question = request.form.get("question", "")

    if question.strip() == "":
        return jsonify({
            "answer": "Please enter a question."
        })

    question_lower = question.lower()

    try:

        # ====================================
        # ANALYSIS REQUESTS
        # ====================================
        if latest_user_data == {}:

         return jsonify({
        "answer":
        "Please analyze your finances first from the dashboard."
    })

        if any(keyword in question_lower for keyword in [

    "analyse",
    "analyze",
    "analysis",

    "my data",
    "analyse my data",
    "analyze my data",

    "my finances",
    "assess my finances",
    "review my finances",

    "financial health",
    "health score",
    "check my score",

    "financial report",
    "review my profile",
    "current situation",

    "financial analysis",
    "analyze my profile",
    "analyse my profile",

    "evaluate my finances",
    "evaluate my profile",

    "how am i doing financially",
    "how is my financial health",

    "give me a report",
    "give me analysis",
    "show analysis",

    "check my financial status",
    "financial status"

]):
            

            prompt = f"""
You are an AI Financial Advisor.

User Financial Data:
{latest_user_data}

Provide a concise financial analysis.

Format EXACTLY:

📊 Score: X/100 (Category)

⚠ Main Problems
• Problem 1
• Problem 2

🎯 Priority Actions
• Action 1
• Action 2

📈 Verdict
One short sentence.

Rules:
- Maximum 80 words
- No long paragraphs
- No introductions
- No markdown symbols like **
"""

        # ====================================
        # NORMAL QUESTIONS
        # ====================================

        else:

            prompt = f"""
You are an AI Financial Advisor.

User Financial Data:
{latest_user_data}

User Question:
{question}

Answer naturally.

Rules:
- Maximum 80 words
- Direct answer
- Use bullets if useful
- No score card
- No analysis template
- No markdown **
- Be practical and concise
"""

        response = gemini_model.generate_content(prompt)

        return jsonify({
            "answer": response.text
        })

    except Exception as e:

     error_text = str(e)

    if "429" in error_text:

        return jsonify({
            "answer":
            "AI service is busy right now. Please try again in a few seconds."
        })

    return jsonify({
        "answer":
        "⚠ Something went wrong. Please try again."
    })

@app.route("/report")
def report():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "report.html",
        username=session.get("username"),
        email=session.get("email")
    )

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "profile.html",
        username=session.get("username"),
        email=session.get("email")
    )

@app.route('/eda_results/<path:filename>')
def eda_files(filename):
    return send_from_directory(
        'eda_results',
        filename
    )

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        if user:
            conn.close()
            flash("Email already exists!", "danger")
            return redirect("/register")

        # Hash password
        hashed_password = generate_password_hash(password)

        # Insert new user
        cursor.execute(
            "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )

        conn.commit()
        conn.close()

        flash("Registration Successful! Please Login.", "success")

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        email=request.form["email"]
        password=request.form["password"]

        conn=sqlite3.connect("users.db")
        cursor=conn.cursor()

        cursor.execute(
            "SELECT id,username,email,password FROM users WHERE email=?",
            (email,)
        )

        user=cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[3],password):

            session["user_id"]=user[0]
            session["username"]=user[1]
            session["email"]=user[2]

            flash("Login Successful!","success")

            return redirect("/")

        flash("Invalid Email or Password","danger")

        return redirect("/login")

    return render_template("login.html")
if __name__ == "__main__":
    print("STARTING FLASK...")
    app.run(host="0.0.0.0", port=5000, debug=True)    
