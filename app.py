from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

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

if __name__ == '__main__':
    app.run(debug=True)
