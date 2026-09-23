import mysql.connector
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, Y, X, BOTH, END, W, CENTER, TOP, RIGHT
import tkintermapview
import requests
from db import DB_CONFIG   # ← source unique : lit DB_HOST, DB_PORT... depuis .env / variables

# Secret token that the desktop admin can include when creating/modifying markers.
MAP_ADMIN_SECRET = 'please-change-me'