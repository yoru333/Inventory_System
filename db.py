# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 16:34:19 2025

@author: 彥智
"""

import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="a25209293",
        database="inventory_db"
    )