# encoding utf-8

'''
This module is a calendar tool made to help me keep track of tasks simply and efficiently. I hope ot make it with a simple GUI, limiting distractions. The intent is to have it store and restore data from an excel spreadsheet I can manage from the cloud. I want it to send me email and text reminders at the set time and date (Or however much time before I specify)

~Author Luis X. Diaz-Guilbee (Xavier)
'''
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from time import *
import configparser
import twilio
import openpyxl
import smtplib
import sys


class Clock_Scheduler(tk.Tk):
    def __init__(self):
        super().__init__()
        # Create Main Window
        self.resizable(False, False)
        self.attributes('-fullscreen', False)
        self.geometry('800x480')
        self.grid_columnconfigure(0, weight=2)
        self.grid_rowconfigure(0, weight=2)
        self.title('LX_ Alarm')
        #self.tk.call("source", "azure.tcl")
        #self.theme = self.config['OPTIONS']['Theme']
        #self.tk.call("set_theme", self.theme)

        # Define Frames
        self.ClockFrame = ttk.LabelFrame(text='Time and Date')
        self.ToDoEntryFrame = ttk.LabelFrame(text='Entry')
        self.ToDoListFrame = ttk.LabelFrame(text='To-Do')
        self.PomodoroTimerFrame = ttk.LabelFrame(text='Pomodoro')
        

        # Define Widgets

if __name__ == '__main__':
    app = Clock_Scheduler()
    app.mainloop()
