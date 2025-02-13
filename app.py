from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

DATABASE = "cafe_app.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']

        if not name or not category or not price:
            flash("必須項目を入力してください", "danger")
            return redirect(url_for('add_product'))

        try:
            price = float(price)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO PRODUCTS (name, description, category, price) VALUES (?, ?, ?, ?)",
                (name, description, category, price)
            )
            conn.commit()
            conn.close()
            flash("商品を登録しました", "success")
            return redirect(url_for('add_product'))
        except ValueError:
            flash("価格は数値で入力してください", "danger")

    return render_template('add_product.html')

@app.route('/products')
def product_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PRODUCTS")
    products = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    conn = get_db_connection()
    cursor = conn.cursor()

    # プルダウン用のデータ取得
    cursor.execute("SELECT id, name FROM PRODUCTS")
    products = cursor.fetchall()

    cursor.execute("SELECT id, username FROM USERS")
    users = cursor.fetchall()

    conn.close()

    if request.method == 'POST':
        product_id = request.form['product_id']
        user_id = request.form['user_id']
        quantity = request.form['quantity']
        transaction_type = request.form['transaction_type']
        notes = request.form.get('notes', '')

        if not product_id or not user_id or not quantity or not transaction_type:
            flash("必須項目を入力してください", "danger")
            return redirect(url_for('transaction'))

        try:
            quantity = int(quantity)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO TRANSACTION_HISTORY (product_id, user_id, quantity, transaction_type, transaction_date, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (product_id, user_id, quantity, transaction_type, datetime.now(), notes)
            )
            conn.commit()
            conn.close()
            flash("入出庫を登録しました", "success")
            return redirect(url_for('transaction'))
        except ValueError:
            flash("数量は整数で入力してください", "danger")

    return render_template('transaction.html', products=products, users=users)

@app.route('/transaction_history')
def transaction_history():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 取引履歴データを取得（商品名とユーザー名を含む）
    cursor.execute("""
        SELECT t.id, p.name AS product_name, u.username AS user_name, 
               t.quantity, t.transaction_type, t.transaction_date, t.notes
        FROM TRANSACTION_HISTORY t
        JOIN PRODUCTS p ON t.product_id = p.id
        JOIN USERS u ON t.user_id = u.id
        ORDER BY t.transaction_date DESC
    """)
    transactions = cursor.fetchall()

    conn.close()
    return render_template('transaction_history.html', transactions=transactions)

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 各商品の最新在庫数を取得
    cursor.execute("""
        SELECT p.id, p.name, p.category, 
               COALESCE(SUM(CASE WHEN t.transaction_type = '入庫' THEN t.quantity 
                                 WHEN t.transaction_type = '出庫' THEN -t.quantity 
                                 ELSE 0 END), 0) AS stock_quantity
        FROM PRODUCTS p
        LEFT JOIN TRANSACTION_HISTORY t ON p.id = t.product_id
        GROUP BY p.id, p.name, p.category
    """)
    inventory_data = cursor.fetchall()
    
    conn.close()
    return render_template('inventory.html', inventory_data=inventory_data)


if __name__ == '__main__':
    app.run(debug=True)
