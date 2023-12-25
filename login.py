import tkinter as tk
from tkinter import messagebox
import requests

def login():
    username = username_entry.get()
    password = password_entry.get()
    # Add your login logic here
    messagebox.showinfo("Login info", f"Username: {username}\nPassword: {password}")

def register():
    # Add your register logic here
    messagebox.showinfo("Register info", "Register button clicked")

def run_login_ui():
    global root, username_entry, password_entry

    root = tk.Tk()

    username_label = tk.Label(root, text="Username")
    username_label.pack()

    username_entry = tk.Entry(root)
    username_entry.pack()

    password_label = tk.Label(root, text="Password")
    password_label.pack()

    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    login_button = tk.Button(root, text="Login", command=login)
    login_button.pack()

    register_button = tk.Button(root, text="Register", command=register)
    register_button.pack()

    root.mainloop()