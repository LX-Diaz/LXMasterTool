# encoding utf-8

'''
This module is a calendar tool made to help me keep track of tasks simply and efficiently. I hope ot make it with a simple GUI, limiting distractions. The intent is to have it store and restore data from an excel spreadsheet I can manage from the cloud. I want it to send me email and text reminders at the set time and date (Or however much time before I specify)

~Author Luis X. Diaz-Guilbee (Xavier)
'''
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import *
from tkinter.ttk import *
from time import *
import configparser
import twilio
import openpyxl
import smtplib
import sys
import weather
import sv_ttk


class Clock_Scheduler(tk.Tk):
    def __init__(self):
        super().__init__()
        self.padding = 5
        # Initialize imported Classes and instantiate variables
        self.config = configparser.ConfigParser()
        self.config.read('timeconfig.ini')
        self.log = open('log.txt', 'a')

        # Create Main Window
        self.resizable(False, False)
        self.attributes('-fullscreen', False)
        # self.geometry('800x480')
        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.title('LX_Clock')
        sv_ttk.set_theme("dark")
        self.weather = weather.WeatherData()

        # Define Frames
        self.ClockFrame = ttk.LabelFrame(text='Time and Date')
        self.ToDoListFrame = ttk.LabelFrame(text='To-Do')
        self.PomodoroTimerFrame = ttk.LabelFrame(text='Pomodoro')

        # Define Widgets
        # =========================================
        # ###Clock Frame
        # =========================================
        self.weatherDataFontSize = 10
        self.clock = ttk.Label(self.ClockFrame, foreground="light blue", font=("Arial", 10), width=15)
        self.date = ttk.Label(self.ClockFrame, foreground="light blue", font=("Arial", 10), width=15)
        self.temp_label = ttk.Label(self.ClockFrame, font=("ds-digital", 10))
        self.feels_like_label = ttk.Label(self.ClockFrame, font=("ds-digital", self.weatherDataFontSize))
        self.min_max_temp_label = ttk.Label(self.ClockFrame, font=("ds-digital", self.weatherDataFontSize))
        self.condition_label = ttk.Label(self.ClockFrame, font=("ds-digital", self.weatherDataFontSize))
        self.humidity_label = ttk.Label(self.ClockFrame, font=("ds-digital", self.weatherDataFontSize))
        self.time()
        self.weather_data()

        # =========================================
        # ###Pomodoro
        # =========================================
        self.timerFrame = ttk.Frame(
            self.PomodoroTimerFrame)  # To house the clock and reset button withing the entire Pomodoro frame
        self.hours_field = ttk.Entry(self.timerFrame, width=3)
        self.minutes_field = ttk.Entry(self.timerFrame, width=3)
        self.seconds_field = ttk.Entry(self.timerFrame, width=3)
        self.reset_button = ttk.Button(self.timerFrame, text="↻")
        self.five_sec_button = ttk.Button(self.PomodoroTimerFrame, text='+5', width=2)
        self.ten_sec_button = ttk.Button(self.PomodoroTimerFrame, text='+10', width=2)
        self.fifteen_sec_button = ttk.Button(self.PomodoroTimerFrame, text='+15', width=2)
        self.start_toggle_button = ttk.Button(self.timerFrame, text="⏯")
        self.progress_bar = ttk.Progressbar(self.PomodoroTimerFrame)

        # =========================================
        # ###To-Do List
        # =========================================
        self.Title = ttk.Label(self.ToDoListFrame, text='Title', foreground="light blue", font=("Arial", 12), width=18)
        self.TitleEntry = ttk.Entry(self.ToDoListFrame)

        self.Desc = ttk.Label(self.ToDoListFrame, text='Description', foreground="light blue", font=("Arial", 12),
                              width=18)
        self.DescEntry = scrolledtext.ScrolledText(self.ToDoListFrame,
                                                   wrap=tk.WORD,
                                                   undo=True,
                                                   maxundo=-1,
                                                   autoseparators=True,
                                                   width=5,
                                                   height=5,
                                                   font=('Arial', 12))
        self.EntryButton = ttk.Button(self.ToDoListFrame, text='Submit')
        self.DeleteButton = ttk.Button(self.ToDoListFrame, text='Delete')
        self.EditButton = ttk.Button(self.ToDoListFrame, text='✎')

        self.Schedule = ttk.Treeview(self.ToDoListFrame)
        self.Schedule['columns'] = ("Title", "Date", "Time", "Description")

        # #######Format Columns
        self.Schedule.column("#0", width=120, minwidth=10)
        self.Schedule.column("Title", width=120, minwidth=10)
        self.Schedule.column("Date", width=120, minwidth=10)
        self.Schedule.column("Time", width=120, minwidth=10)
        self.Schedule.column("Description", width=120, minwidth=10)

        # #######Add column headers
        self.Schedule.heading('#0', text='blank', anchor=CENTER)
        self.Schedule.heading('Title', text='Title', anchor=CENTER)
        self.Schedule.heading('Date', text='Date', anchor=CENTER)
        self.Schedule.heading('Time', text='Time', anchor=CENTER)
        self.Schedule.heading('Description', text='Description', anchor=CENTER)

        # Add Frames and Widgets to Grid
        # Clock Frame
        self.ClockFrame.grid(column=0, row=0, padx=self.padding, pady=self.padding, sticky='NS' + 'EW')
        self.date.grid(column=0, row=0, padx=self.padding, pady=self.padding, sticky='NW')
        self.clock.grid(column=0, row=1, padx=self.padding, pady=self.padding, sticky='NW')
        self.temp_label.grid(column=0, row=2, padx=self.padding, pady=self.padding, sticky='NW')
        self.feels_like_label.grid(column=0, row=3, padx=self.padding, pady=self.padding, sticky='NW')
        self.min_max_temp_label.grid(column=0, row=4, padx=self.padding, pady=self.padding, sticky='NW')
        self.condition_label.grid(column=0, row=5, padx=self.padding, pady=self.padding, sticky='NW')
        self.humidity_label.grid(column=0, row=6, padx=self.padding, pady=self.padding, sticky='NW')

        # To-Do Frame
        self.ToDoListFrame.grid(column=1, row=0, columnspan=2, rowspan=4, padx=self.padding, pady=self.padding, sticky='NS'+'EW')
        self.Title.grid(column=0, row=0, columnspan=3, padx=self.padding, pady=self.padding, sticky='N' + 'EW')
        self.TitleEntry.grid(column=0, row=1, columnspan=3, padx=self.padding, pady=self.padding, sticky='N' + 'EW')
        self.Desc.grid(column=0, row=2, columnspan=3, padx=self.padding, pady=self.padding, sticky='N' + 'EW')
        self.DescEntry.grid(column=0, row=3, columnspan=3, padx=self.padding, pady=self.padding, sticky='N' + 'EW')
        self.EntryButton.grid(column=0, row=4, padx=self.padding, pady=self.padding, sticky='N' + 'W')
        self.DeleteButton.grid(column=1, row=4,padx=self.padding, pady=self.padding, sticky='N' + 'W')
        self.EditButton.grid(column=2, row=4,padx=self.padding, pady=self.padding, sticky='N' + 'W')
        self.Schedule.grid(column=3, row=0, rowspan=6, padx=self.padding, pady=self.padding, sticky='NS' + 'EW')

        # Pomodoro Frame
        self.PomodoroTimerFrame.grid(column=0, row=1, rowspan=3, padx=self.padding, pady=self.padding, sticky='NS' + 'EW')
        self.timerFrame.grid(column=0, row=0, columnspan=5, padx=self.padding, pady=self.padding, sticky='NW')
        self.reset_button.grid(column=0, row=0, padx=self.padding, pady=self.padding, sticky='NW')  # in timerFrame
        self.hours_field.grid(column=1, row=0, padx=self.padding, pady=self.padding, sticky='NW')  # in timerFrame
        self.minutes_field.grid(column=2, row=0, padx=self.padding, pady=self.padding, sticky='NW')  # in timerFrame
        self.seconds_field.grid(column=3, row=0, padx=self.padding, pady=self.padding, sticky='NW')  # in timerFrame
        self.start_toggle_button.grid(column=4, row=0, padx=self.padding, pady=self.padding, sticky='NW')  # in timerFrame
        self.five_sec_button.grid(column=1, row=1, padx=self.padding, pady=self.padding, sticky='EW')  # below timerFrame
        self.ten_sec_button.grid(column=2, row=1, padx=self.padding, pady=self.padding, sticky='EW')  # below timerFrame
        self.fifteen_sec_button.grid(column=3, row=1, padx=self.padding, pady=self.padding, sticky='EW')  # below timerFrame
        self.progress_bar.grid(column=0, row=2, columnspan=5, padx=self.padding, pady=self.padding, sticky='EW')  # below buttons

        # Define system Functions

    def time(self):
        self.date_String = strftime('%m/%d/%Y')
        self.string = strftime('%I:%M:%S %p')
        self.clock.config(text=self.string)
        self.date.config(text=self.date_String)
        self.clock.after(1000, self.time)

    def weather_data(self):
        self.wUpdtT = 60000
        self.weather.getWeatherData()
        self.temp_label.config(text=f'{self.weather.temperature}°F')
        self.feels_like_label.config(text=f'Feels Like: {self.weather.feels_temp}°F')
        self.min_max_temp_label.config(text=f'Temp-Range:{self.weather.min_temp}°F - {self.weather.max_temp}°F')
        self.condition_label.config(text=f'{self.weather.desc}')
        self.humidity_label.config(text=f'Humidity: {self.weather.humidity}%')

        self.temp_label.after(self.wUpdtT, self.weather_data)
        self.log = open('log.txt', 'a')
        self.log.write(
            f'{self.date_String} @ {self.string}\n-----------------------------------------------\n Updated weather data:\n{self.weather.data}\n\n')
        self.log.close()


if __name__ == '__main__':
    app = Clock_Scheduler()
    app.mainloop()
