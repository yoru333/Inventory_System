# -*- coding: utf-8 -*-
"""
Created on Sat Jun  7 14:15:17 2025

@author: 彥智
"""
import mysql.connector
from flask import Flask, render_template,request, redirect, url_for, flash, session
from inventory_crud import list_products, add_product, update_product_stock, delete_product, add_stock_in, list_stock_in, update_stock_in,delete_stock_in, add_stock_out, list_stock_out,update_stock_out, delete_stock_out
import bcrypt
#Flask（建立網站用）與 render_template（用來載入 HTML 模板檔案）
connection = mysql.connector.connect(
    host="bmqyzwntbftmo6pawady-mysql.services.clever-cloud.com",
    port="3306",
    user="ujljgigajyafh9zb",
    password="esXpq0EprRpPlRfx8hkD",
    database="bmqyzwntbftmo6pawady")


app = Flask(__name__)
app.secret_key = 'mysecretkey123'

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = connection.cursor()
        sql = """
        SELECT password FROM users WHERE username = %s
        """
        #找出對應username的password
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            stored_pw = result[0]
            #因為select只搜尋password 所以result[0] 就是password
            #如果要用特定欄位的值，才會寫 變數 = result[欄位索引]。
            if bcrypt.checkpw(password.encode(), stored_pw.encode() if isinstance(stored_pw, str) else stored_pw):
                #isinstance(變數, 類別) 判斷變數是否為指定的類別 傳出True or False
                session['user'] = username
                #用 session 可以保持用戶的登入狀態
                #把使用者名稱（username）存進 session 裡，代表這個用戶已經登入了
                flash("登入成功", "success")
                return redirect(url_for("index"))
            else:
                flash("密碼錯誤", "danger")
        else: 
            flash("帳戶不存在", "danger")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)  # 移除 session 中的 user，沒有 user 也不會報錯
    flash("已成功登出", "success")
    return redirect(url_for('login'))  # 登出後導回登入頁面       

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        if result:
            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_pw, username))
            connection.commit()
            cursor.close()
            flash("密碼已更新，請重新登入", "success")
            return redirect('login')
        else:
            cursor.close()
            flash("帳號不存在", "danger")
            
    return render_template("forgot_password.html")
    

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
        cursor = connection.cursor()
        sql = """
         INSERT INTO users(username, password) VALUES (%s, %s)
         """ 
        cursor.execute(sql, (username, hashed_pw))
        connection.commit()
        cursor.close()
         
        flash('註冊成功', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')
    

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    products = list_products()
    return render_template("index.html", products=products)
#第一個 products（等號左邊）：是傳給 HTML 模板的變數名稱。
#第二個 products（等號右邊）：是你 Python 裡的變數（就是那個商品列表）。
@app.route("/add_product", methods=["GET"])
def add_product_from():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("add_product.html")

@app.route("/add_product", methods=["POST"])
def add_product_submit():
    if 'user' not in session:
        return redirect(url_for('login'))
    name = request.form["name"]
    #從「使用者送來的表單資料」中取出欄位 name 的內容。
    category = request.form["category"]
    unit_price = float(request.form["unit_price"])
    #把使用者填的商品單價轉成 float（小數），因為表單傳過來的都是字串。
    stock = int(request.form["stock"])
    safe_stock = int(request.form["safe_stock"])
    
    add_product(name, category, unit_price, stock, safe_stock)
    #呼叫你自己寫的新增商品函式，把使用者填的資料存進資料庫。
    #在 Flask 中，url_for() 的參數不是路由字串，而是對應的函式名稱！
    return redirect(url_for("index"))

@app.route("/update_product", methods=["GET","POST"])
def update_product():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        product_id = request.form['product_id']
        new_stock = request.form['new_stock']
        update_product_stock(int(product_id), int(new_stock))
        return redirect('/') # # 更新完就導回首頁
    return render_template("update_product.html")
#新增完商品後，讓瀏覽器自動跳轉回首頁（index 函式對應的路由 /），你會看到商品列表更新了。

@app.route("/delete_product", methods=["GET", "POST"])
def delete_product_route():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        product_id = request.form['product_id']
        delete_product(int(product_id))
        return redirect('/')
    products = list_products()
    #如果不是送出表單（是 GET），就先把所有商品資料查出來，傳給表單頁面顯示。
    return render_template("delete_product.html", products=products)
    #把 products 商品清單傳給 delete_product.html 頁面，讓使用者可以選一個要刪除的商品。
 
@app.route("/add_stock_in", methods=["GET", "POST"])
def add_stock_form():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method =="POST":
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])
        add_stock_in(product_id, quantity)
        return redirect("/add_stock_in")
    products = list_products()
    return render_template("add_stock_in.html", products=products)

@app.route("/list_stock_in", methods=["GET"])
def list_stock_form():
    if 'user' not in session:
        return redirect(url_for('login'))
    stock_ins = list_stock_in()
    return render_template("list_stock_in.html",  stock_ins= stock_ins)

@app.route("/update_stock_in", methods=["GET", "POST"])
def in_update_stock():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        in_id = int(request.form["in_id"])
        quantity = int(request.form["quantity"])
        update_stock_in(in_id, quantity)
        return redirect("/")
    
    return render_template("update_stock_in.html")

@app.route("/delete_stock_in", methods=["GET", "POST"])
def in_delete_stock():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method =="POST":
        in_id = int(request.form["in_id"])
        delete_stock_in(in_id)
        return redirect("/")
    records = list_stock_in()
    return render_template("delete_stock_in.html", records=records)

@app.route("/add_stock_out", methods=["GET", "POST"])
def out_add_stock():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])
        add_stock_out(product_id, quantity)
        return redirect("/add_stock_out")
    products = list_products()
    return render_template("add_stock_out.html", products = products)
    
@app.route("/list_stock_out", methods=["GET"])
def stock_out_form():
    if 'user' not in session:
        return redirect(url_for('login'))
    stock_outs = list_stock_out()
    return render_template("list_stock_out.html", stock_outs = stock_outs)

@app.route("/update_stock_out", methods=["GET", "POST"])
def out_update_stock():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        out_id = int(request.form["out_id"])
        quantity = int(request.form["quantity"])
        update_stock_out(out_id, quantity)
        return redirect("/")
    
    return render_template("update_stock_out.html")
                     
@app.route("/delete_stock_out", methods=["GET", "POST"])
def out_delete_stock():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        out_id = int(request.form["out_id"])
        delete_stock_out(out_id)
        return redirect("/")
    records =  list_stock_out()
    return render_template("delete_stock_out.html", records = records)


if __name__ == '__main__':
    app.run(debug=True)
    
