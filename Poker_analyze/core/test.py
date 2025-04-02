import mysql.connector

# 測試連接
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Tim0986985588=",
    database="poker_db",
    port=3306
)
print("連接成功")
connection.close()