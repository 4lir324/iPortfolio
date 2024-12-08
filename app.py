from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import requests

app = Flask(__name__)

# مسیر پایگاه داده
db_directory = "Database"
db_path = os.path.join(db_directory, "data.db")

# API Key برای CoinMarketCap
COINMARKETCAP_API_KEY = "69445e7c-3e87-4b37-a576-b6b3fc5dd0c3"
COINMARKETCAP_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

# بررسی و ایجاد پایگاه داده در صورت نیاز
if not os.path.exists(db_directory):
    os.makedirs(db_directory)

if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE coins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        symbol TEXT NOT NULL,
        wallet_name TEXT NOT NULL,
        buy_price REAL NOT NULL,
        quantity REAL NOT NULL DEFAULT 0
    )''')
    conn.commit()
    conn.close()

# دریافت قیمت فعلی از CoinMarketCap
def fetch_current_price(symbol):
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY,
    }
    params = {"symbol": symbol, "convert": "USD"}
    try:
        response = requests.get(COINMARKETCAP_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        price = data["data"][symbol][0]["quote"]["USD"]["price"]
        return round(price, 2)
    except Exception as e:
        print(f"Error fetching price: {e}")
        return 0

# صفحه اصلی: نمایش اطلاعات کوین‌ها
@app.route("/")
def index():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coins")
    coins = cursor.fetchall()
    conn.close()

    total_sum = 0  # متغیر برای جمع کل
    formatted_coins = []
    for coin in coins:
        current_price = fetch_current_price(coin[2])  # قیمت فعلی
        total_amount = round(current_price * coin[5], 2)  # قیمت فعلی * تعداد
        total_sum += total_amount  # افزودن مبلغ کل به جمع کل
        profit_percent = round(((current_price - coin[4]) / coin[4]) * 100, 2) if coin[4] > 0 else 0

        formatted_coins.append({
            "id": coin[0],
            "name": coin[1],
            "symbol": coin[2],
            "wallet_name": coin[3],
            "buy_price": coin[4],
            "quantity": coin[5],
            "current_price": current_price,
            "total_amount": total_amount,
            "profit_percent": profit_percent
        })

    return render_template("index.html", coins=formatted_coins, total_sum=round(total_sum, 2))

# صفحه ویرایش: مدیریت کوین‌ها
@app.route("/edit")
def edit_portfolio():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # تبدیل نتیجه به دیکشنری
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coins")
    coins = cursor.fetchall()
    conn.close()

    return render_template("edit.html", coins=coins)

# افزودن کوین جدید
@app.route("/add", methods=["GET", "POST"])
def add_coin():
    if request.method == "POST":
        name = request.form["name"]
        symbol = request.form["symbol"]
        wallet_name = request.form["wallet_name"]
        buy_price = float(request.form["buy_price"])
        quantity = float(request.form["quantity"])

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO coins (name, symbol, wallet_name, buy_price, quantity) VALUES (?, ?, ?, ?, ?)",
                       (name, symbol, wallet_name, buy_price, quantity))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add.html")

# به‌روزرسانی کوین
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_coin(id):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # تبدیل داده‌ها به دیکشنری
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        symbol = request.form["symbol"]
        wallet_name = request.form["wallet_name"]
        buy_price = float(request.form["buy_price"])
        quantity = float(request.form["quantity"])

        cursor.execute("UPDATE coins SET name = ?, symbol = ?, wallet_name = ?, buy_price = ?, quantity = ? WHERE id = ?",
                       (name, symbol, wallet_name, buy_price, quantity, id))
        conn.commit()
        conn.close()
        return redirect(url_for("edit_portfolio"))

    cursor.execute("SELECT * FROM coins WHERE id = ?", (id,))
    coin = cursor.fetchone()
    conn.close()

    if not coin:
        return "Coin not found", 404

    return render_template("update.html", coin=coin)

# حذف کوین
@app.route("/delete/<int:id>", methods=["POST"])
def delete_coin(id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM coins WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("edit_portfolio"))

if __name__ == "__main__":
    app.run(debug=True)