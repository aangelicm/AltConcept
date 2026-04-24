# from fastapi import FastAPI, Form
# import sqlite3
# #создаю приложение фаст апи

# app = FastAPI()
# @app.post("/redister") #отправляю данные на сервер 

# def redister(username: str = Form(...), password: str = Form(...)):
#     connection = sqlite3.connect("shpp.bd")
#     cursor = connection.cursor()

#     cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
#     connection.commit()
#     return {"message": "все крута"}


