# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 19:18:31 2025

@author: 彥智
"""
from db import get_connection
import bcrypt

def register_user(username, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO users(username, password) VALUES (%s, %s)
    """ 
    cursor.execute(sql, (username, hashed_pw))
    conn.commit()
    conn.close()
