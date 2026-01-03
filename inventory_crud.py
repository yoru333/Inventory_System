# -*- coding: utf-8 -*-
"""
Created on Fri Jun  6 16:49:34 2025

@author: 彥智
"""

from datetime import datetime
from flask import flash
from db import get_connection


def add_product(name, category, unit_price, stock, safe_stock):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
    #用三引號包住的多行字串，定義要執行的 SQL 語法
            sql="""
            INSERT INTO products(name, category, unit_price, stock, safe_stock)
            VALUES(%s, %s, %s, %s, %s)
            """
            #%s 是參數佔位符，表示之後會用變數代入，避免 SQL Injection（攻擊）。
            values = (name, category, unit_price, stock, safe_stock)
            #把函式的 5 個參數包成一個 tuple values，依序對應 SQL 語句中的 %s。
            cursor.execute(sql, values)
            conn.commit()
            print("商品新增成功")
    except Exception as e:
            print("新增商品時發生錯誤:", str(e))
    finally:
            conn.close()

def list_products():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products")
            rows = cursor.fetchall()
            return rows  # 一定要回傳資料
    except Exception as e:
        print("查詢商品時發生錯誤:", str(e))
        return []
    finally:
        conn.close()
        
def update_product_stock(product_id, new_stock):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "UPDATE products SET stock = %s WHERE product_id = %s"
            values = (new_stock, product_id)
            cursor.execute(sql, values)
            conn.commit()
            print(f'商品{product_id}的庫存已更改為{new_stock}')
    except Exception as e:
        print("更新庫存時發生錯誤:", str(e))
    finally:
        conn.close()

def delete_product(product_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql_stock_in = "DELETE FROM stock_in WHERE product_id = %s"
            cursor.execute(sql_stock_in, (product_id,))
    
    # 若你有 stock_out 表，也要一併處理
            sql_stock_out = "DELETE FROM stock_out WHERE product_id = %s"
            cursor.execute(sql_stock_out, (product_id,))
    
    # 最後才刪除 products 表中的資料
            sql_product = "DELETE FROM products WHERE product_id = %s"
            cursor.execute(sql_product, (product_id,))
    
            conn.commit()
            print(f'已刪除商品 ID: {product_id}')
            #在 Python 裡，要建立只有一個元素的 tuple（元組）時，必須加逗號，不然會被當成普通括號包起來的變數。
            #因為 cursor.execute 第二個參數要的是一個「tuple」或「list」，用來對應 SQL 裡的 %s 佔位符。
    except Exception as e:
        print("刪除商品時發生錯誤:", str(e))
    finally:
        conn.close()

def add_stock_in(product_id, quantity, in_date=None):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            if in_date is None:
                in_date = datetime.now()
            sql = """
            INSERT INTO stock_in(product_id, quantity, in_date)
            VALUES(%s, %s, %s)
            """
            values = (product_id, quantity, in_date)
            cursor.execute(sql, values)
            
            sql_update_stock = "UPDATE products SET stock = stock + %s WHERE product_id = %s"
            cursor.execute(sql_update_stock, (quantity, product_id))
            
            sql_check_stock = "SELECT stock, safe_stock, name FROM products WHERE product_id = %s"
            cursor.execute(sql_check_stock, (product_id,))
            result = cursor.fetchone()
            if result:
                stock, safe_stock, name = result
    # 你可以先做些事情

            conn.commit()
            #✅ (a, b)：這是兩個元素的 tuple → 不用特別加逗號
            #✅ (a,)：這是一個元素的 tuple → 一定要加逗號
            print(f'商品{product_id}進貨{quantity}, 庫存已更新')
            sql_warn = "SELECT name, stock, safe_stock FROM products WHERE stock > safe_stock"
            cursor.execute(sql_warn)
            overstock_items = cursor.fetchall()
            for name, stock, safe_stock in overstock_items:
                    flash(f'⚠️警告:{name}目前庫存{stock}, 已高於安全庫存{safe_stock}', "warning")
                    #進貨時，我們反過來檢查，如果你進太多，庫存變得太多，也有可能導致「庫存壓力」
    except Exception as e:
        conn.rollback()
        flash(f'進貨時發生錯誤{str(e)}', "danger")
    finally:
        conn.close()
        
def list_stock_in():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM stock_in")
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print("查詢進貨紀錄錯誤:", str(e))
        return []
    finally:
        conn.close()
    
def update_stock_in(in_id, quantity):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "UPDATE stock_in SET quantity = %s WHERE in_id = %s"
            cursor.execute(sql, (quantity, in_id))
            conn.commit()
            print(f"進貨紀錄 {in_id} 已更新數量為 {quantity}")
    except Exception as e:
        print("更新進貨紀錄錯誤:", str(e))
    finally:
        conn.close()
def delete_stock_in(in_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "DELETE FROM stock_in WHERE in_id = %s"
            cursor.execute(sql, (in_id,))
            conn.commit()
            print(f'進貨紀錄{in_id}已刪除')
    except Exception as e:
        print("刪除進貨紀錄錯誤:", str(e))
    finally:
        conn.close()
def add_stock_out(product_id, quantity, out_date=None):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql_check_stock = """
            SELECT stock, safe_stock, name FROM products WHERE product_id = %s
            """
            cursor.execute(sql_check_stock, (product_id,))
            result = cursor.fetchone()
            if not result:
                print("查無此商品ID")
                return
            #return 就會讓這整個函式提早結束，不再往下執行。
    
            stock, safe_stock, name = result
            # 確定 result 有值之後，才可以解包
            #這裡的result是上面fetchone的查詢結果，將查詢欄位資料拿出來做下面的比較
            
    
            if stock < quantity:
                flash(f'⚠️{name}商品庫存不足, 無法銷售 目前庫存{stock}, 欲銷售數量:{quantity}', "danger")
                print(f'⚠️{name}商品庫存不足, 無法銷售 目前庫存{stock}, 欲銷售數量:{quantity}')
            
            if out_date is None:
                out_date = datetime.now()
            sql = """
            INSERT INTO stock_out(product_id, quantity, out_date)
            VALUES(%s, %s, %s)
            """
            values = (product_id, quantity, out_date)
            cursor.execute(sql,values)
            
            sql_update_stock = """
            UPDATE products SET stock = stock - %s WHERE product_id = %s
            """
            cursor.execute(sql_update_stock, (quantity, product_id))
            conn.commit()
            print(f'銷售成功, 商品ID:{product_id}, 數量:{quantity}, 剩餘庫存:{stock - quantity}')
            
            sql_warn = "SELECT name, stock, safe_stock FROM products WHERE stock < safe_stock"
            cursor.execute(sql_warn)
            low_stock_items = cursor.fetchall()
            
            for name, stock, safe_stock in low_stock_items:
                flash(f'⚠️警告:商品{name}目前庫存:{stock - quantity}, 低於安全庫存:{safe_stock}, 請盡快補貨', "danger")
                print(f'⚠️警告:商品{name}目前庫存:{stock - quantity}, 低於安全庫存:{safe_stock}, 請盡快補貨')
            
    except Exception as e:
        conn.rollback()
        flash(f'出貨時發生錯誤{str(e)}', "danger")
    finally:
        conn.close()
        
def list_stock_out():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM stock_out")
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print("查詢銷貨紀錄錯誤:", str(e))
        return []
    finally:
        conn.close()
        
def update_stock_out(out_id, quantity):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "UPDATE stock_out SET quantity = %s WHERE out_id = %s"
            cursor.execute(sql, (quantity, out_id))
            conn.commit()
            print(f'銷售紀錄{out_id}已更新數量為{quantity}')
    except Exception as e:
        print("更新銷貨紀錄錯誤:", str(e))
    finally:
        conn.close()
        
def delete_stock_out(out_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            sql = "DELETE FROM stock_out WHERE out_id = %s"
            cursor.execute(sql, (out_id,))
            conn.commit()
            print(f'銷售紀錄{out_id}已刪除')
    except Exception as e:
        print("刪除銷貨紀錄錯誤:", str(e))
    finally:
        conn.close()

    
    
    
    
    
    
    
    
    
    
    

