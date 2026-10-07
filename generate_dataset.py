import pandas as pd
import random

users = []

for i in range(5000):

    age = random.randint(18, 70)

    category = random.choice([
        "Poor",
        "Average",
        "Good",
        "Excellent"
    ])

    # print("Target Category:", category)

    if category == "Poor":

        income = random.randint(10000, 50000)

        expense_percentage = random.uniform(0.80, 0.95)

        expenses = int(income * expense_percentage)

        monthly_surplus = income - expenses

        savings = monthly_surplus * random.randint(0, 6)

    elif category == "Average":

        income = random.randint(30000, 100000)

        expense_percentage = random.uniform(0.65, 0.85)

        expenses = int(income * expense_percentage)

        monthly_surplus = income - expenses

        savings = monthly_surplus * random.randint(3, 18)

    elif category == "Good":

        income = random.randint(60000, 180000)

        expense_percentage = random.uniform(0.45, 0.70)

        expenses = int(income * expense_percentage)

        monthly_surplus = income - expenses

        savings = monthly_surplus * random.randint(12, 48)

    else:

        income = random.randint(100000, 300000)

        expense_percentage = random.uniform(0.30, 0.60)

        expenses = int(income * expense_percentage)

        monthly_surplus = income - expenses

        savings = monthly_surplus * random.randint(24, 120)

    goal = random.choice([
        "House",
        "Education",
        "Retirement",
        "Investment",
        "Vehicle",
        "Emergency Fund"
    ])

    risk = random.choice([
        "Low",
        "Medium",
        "High"
    ])

    savings_rate = (income - expenses) / income

    expense_ratio = expenses / income

    emergency_fund_coverage = savings / expenses

    # Savings Score (0-40)

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

    # Expense Score (0-30)

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

    # Emergency Fund Score (0-20)

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

    # Risk Alignment Score (0-10)

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

    health_score = (
        savings_score +
        expense_score +
        emergency_score +
        risk_score
    )

    if health_score <= 40:
        final_category = "Poor"
    elif health_score <= 60:
        final_category = "Average"
    elif health_score <= 80:
        final_category = "Good"
    else:
        final_category = "Excellent"

    users.append({
        "Age": age,
        "Income": income,
        "Expenses": expenses,
        "Savings": savings,
        "Goal": goal,
        "Risk": risk,
        "Savings_Rate": round(savings_rate, 2),
        "Expense_Ratio": round(expense_ratio, 2),
        "Emergency_Fund_Coverage": round(emergency_fund_coverage, 2),
        "Health_Score": health_score,
        "Target_Category": category,
        "Category": final_category
    })

    # print(age)
    # print(category)
    # print(income)
    # print(goal)
    # print(risk)
    # print(expenses)
    # print(savings)
    # print(savings_rate)
    # print(expense_ratio)
    # print(emergency_fund_coverage)
    # print("Savings Score:", savings_score)
    # print("Risk Alignment Score:", risk_score)
    # print("Expense Score:", expense_score)
    # print("Emergency Fund Score:", emergency_score)
    # print("Financial Health Score:", health_score)
    # print("Financial Category:", final_category)

df = pd.DataFrame(users)

print(df)

df.to_csv(
    "dataset/financial_dataset.csv",
    index=False
)

print("Dataset Saved Successfully!")