import mysql.connector
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, Y, X, BOTH, END, W, CENTER, TOP, RIGHT
import tkintermapview
import requests

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'app',
    'port': 3306
}
# Secret token that the desktop admin can include when creating/modifying markers.
# Change this value to a strong secret in production and keep it out of source control.
MAP_ADMIN_SECRET = 'please-change-me'