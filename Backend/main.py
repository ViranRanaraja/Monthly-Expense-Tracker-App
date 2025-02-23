from flask import Flask, request, jsonify
from expense import Expense
import calendar
import datetime
import mysql.connector
import os


connection = mysql.connector.connect(
    host = "127.0.0.1",
    user = "root",
    password = "root@2001",
    database = "expense_tracker"
)

if connection.is_connected():
    print("Successfully connected to MySQL database.")
else:
    print("Error connecting to MySQL database.")


app = Flask(__name__)

EXPENSE_FILE_PATH = "expenses.csv"
BUDGET = 2000

def save_expense_to_file(expense, file_path):
    with open(file_path, "a") as f:
        f.write(f"{expense.name},{expense.amount},{expense.category}\n")

def read_expenses_from_file(file_path):
    expenses = []
    with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            expense_name, expense_amount, expense_category = line.strip().split(",")
            expenses.append(
                Expense(
                    name=expense_name,
                    amount=float(expense_amount),
                    category=expense_category,
                )
            )
    return expenses

@app.route("/api/expense", methods=["POST"])
def add_expense():
    data = request.json

    try:
        expense_name = data["name"]
        expense_amount = float(data["amount"])
        expense_category = data["category"]

        expense = Expense(
            name=expense_name, amount=expense_amount, category=expense_category
        )

        save_expense_to_file(expense, EXPENSE_FILE_PATH)

        return jsonify({"message": "Expense added successfully!"}), 201

    except (KeyError, ValueError) as e:
        return jsonify({"error": "Invalid input", "details": str(e)}), 400

@app.route("/api/summary", methods=["GET"])
def get_summary():
    expenses = read_expenses_from_file(EXPENSE_FILE_PATH)

    amount_by_category = {}
    for expense in expenses:
        amount_by_category[expense.category] = (
            amount_by_category.get(expense.category, 0) + expense.amount
        )

    total_spent = sum(expense.amount for expense in expenses)
    remaining_budget = BUDGET - total_spent

    now = datetime.datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    remaining_days = days_in_month - now.day
    daily_budget = remaining_budget / remaining_days if remaining_days > 0 else 0

    return jsonify(
        {
            "total_spent": total_spent,
            "remaining_budget": remaining_budget,
            "daily_budget": daily_budget,
            "expenses_by_category": amount_by_category,
        }
    )

@app.route("/api/categories", methods=["GET"])
def get_categories():
    categories = ["🍔 Food", "🏠 Home", "💼 Work", "🎉 Fun", "✨ Misc"]
    return jsonify(categories)


if __name__ == "__main__":
    app.run(debug=True)
