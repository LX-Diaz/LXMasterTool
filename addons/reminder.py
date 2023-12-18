# encoding utf-8

'''
This module is a calendar tool made to help me keep track of tasks simply and efficiently. I hope ot make it with a simple GUI, limiting distractions. The intent is to have it store and restore data from an excel spreadsheet I can manage from the cloud. I want it to send me email and text reminders at the set time and date (Or however much time before I specify)

~Author Luis X. Diaz-Guilbee (Xavier)
'''
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import *
from tkinter.ttk import *
from winsound import *
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
        self.minutes = None
        self.padding = 5
        # Initialize imported Classes and instantiate variables
        self.config = configparser.ConfigParser()
        self.config.read('timeconfig.ini')
        self.log = open('log.txt', 'a')

        self.total_seconds = tk.IntVar()

        self.TimerStatus = False
        self.PomodoroStatus = False

        # Create Main Window
        self.resizable(False, False)
        self.attributes('-fullscreen', False)
        # self.geometry('800x480')
        self.grid_columnconfigure(7, weight=3)
        self.grid_rowconfigure(7, weight=3)
        self.title('LX_Clock')
        sv_ttk.set_theme("light")
        self.weather = weather.WeatherData()

        # Define Frames
        self.ClockFrame = ttk.LabelFrame(self, text='Time and Date')
        self.ToDoListFrame = ttk.LabelFrame(self, text='To-Do')
        self.TimerFrame = ttk.LabelFrame(self, text='Timer')
        self.PomodoroFrame = ttk.LabelFrame(self, text='Pomodoro')
        self.MessageFrame = ttk.Frame(self)

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
        # ###Timer
        # =========================================
        self.Timer_Clock_Inner_Frame = ttk.Frame(
            self.TimerFrame)  # To house the clock and reset button withing the entire Timer frame
        self.hours_field = ttk.Entry(self.Timer_Clock_Inner_Frame, width=3)
        self.hours_field.insert(0, '00')
        self.minutes_field = ttk.Entry(self.Timer_Clock_Inner_Frame, width=3)
        self.minutes_field.insert(0, '00')
        self.seconds_field = ttk.Entry(self.Timer_Clock_Inner_Frame, width=3)
        self.seconds_field.insert(0, '00')
        self.reset_button = ttk.Button(self.Timer_Clock_Inner_Frame, text="↻", command=self.resetTimer)
        self.five_sec_button = ttk.Button(self.TimerFrame, text='+5', width=2, command=self.addFive)
        self.ten_sec_button = ttk.Button(self.TimerFrame, text='+10', width=2, command=self.addTen)
        self.fifteen_sec_button = ttk.Button(self.TimerFrame, text='+15', width=2, command=self.addFifteen)
        self.start_toggle_button = ttk.Button(self.Timer_Clock_Inner_Frame, text="⏯", command=self.startTimer)
        self.progress_bar = ttk.Progressbar(self.TimerFrame, mode="indeterminate")

        # =========================================
        # ###Pomodoro
        # =========================================
        self.pom_minutes = ttk.Entry(self.PomodoroFrame)
        self.pom_minutes.insert(0, '000')
        self.pom_minutes_label = ttk.Label(self.PomodoroFrame, text='mins.')
        self.pom_start = ttk.Button(self.PomodoroFrame, text='⏯')
        self.pom_progress_bar = ttk.Progressbar(self.PomodoroFrame)

        # =========================================
        # ###To-Do List
        # =========================================
        self.to_do_top = ttk.LabelFrame(self.ToDoListFrame, text='Tasks', labelanchor='n')
        self.to_do_bottom = ttk.LabelFrame(self.ToDoListFrame, text='Reminders', labelanchor='n')

        # Top Frame
        self.TitleLabel = ttk.Label(self.to_do_top, text='Title:', foreground="light blue", font=("Arial", 12), width=18)
        self.TitleEntry = ttk.Entry(self.to_do_top)

        self.DateLabel = ttk.Label(self.to_do_top, text='Date:', foreground="light blue", font=("Arial", 12), width=18)
        self.DateEntry = ttk.Entry(self.to_do_top)
        self.DateEntry.insert(0,'mm/dd/yyyy')

        self.TimeLabel = ttk.Label(self.to_do_top, text='Time:', foreground="light blue", font=("Arial", 12), width=18)
        self.TimeEntry = ttk.Entry(self.to_do_top)
        self.TimeEntry.insert(0, 'hh:mm')

        self.DescLabel = ttk.Label(self.to_do_top, text='Description:', foreground="light blue", font=("Arial", 12),
                              width=18)
        self.DescEntry = scrolledtext.ScrolledText(self.to_do_top,
                                                   wrap=tk.WORD,
                                                   undo=True,
                                                   maxundo=-1,
                                                   autoseparators=True,
                                                   width=5,
                                                   height=5,
                                                   font=('Arial', 12))
        self.EntryButton = ttk.Button(self.to_do_top, text='Submit')
        self.DeleteButton = ttk.Button(self.to_do_top, text='Delete')
        self.EditButton = ttk.Button(self.to_do_top, text='✎')

        self.Schedule = ttk.Treeview(self.to_do_top)
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

        # Bottom Frame
        self.TitleLabel_b = ttk.Label(self.to_do_bottom, text='Title:', foreground="light blue", font=("Arial", 12),
                                    width=18)
        self.TitleEntry_b = ttk.Entry(self.to_do_bottom)

        self.DateLabel_b = ttk.Label(self.to_do_bottom, text='Date:', foreground="light blue", font=("Arial", 12), width=18)
        self.DateEntry_b = ttk.Entry(self.to_do_bottom)
        self.DateEntry_b.insert(0, 'mm/dd/yyyy')

        self.TimeLabel_b = ttk.Label(self.to_do_bottom, text='Time:', foreground="light blue", font=("Arial", 12), width=18)
        self.TimeEntry_b = ttk.Entry(self.to_do_bottom)
        self.TimeEntry_b.insert(0, 'hh:mm')

        self.DescLabel_b = ttk.Label(self.to_do_bottom, text='Description:', foreground="light blue", font=("Arial", 12),
                                   width=18)
        self.DescEntry_b = scrolledtext.ScrolledText(self.to_do_bottom,
                                                   wrap=tk.WORD,
                                                   undo=True,
                                                   maxundo=-1,
                                                   autoseparators=True,
                                                   width=5,
                                                   height=5,
                                                   font=('Arial', 12))
        self.EntryButton_b = ttk.Button(self.to_do_bottom, text='Submit')
        self.DeleteButton_b = ttk.Button(self.to_do_bottom, text='Delete')
        self.EditButton_b = ttk.Button(self.to_do_bottom, text='✎')

        self.Schedule_b = ttk.Treeview(self.to_do_bottom)
        self.Schedule_b['columns'] = ("Title", "Date", "Time", "Description")

        # #######Format Columns
        self.Schedule_b.column("#0", width=120, minwidth=10)
        self.Schedule_b.column("Title", width=120, minwidth=10)
        self.Schedule_b.column("Date", width=120, minwidth=10)
        self.Schedule_b.column("Time", width=120, minwidth=10)
        self.Schedule_b.column("Description", width=120, minwidth=10)

        # #######Add column headers
        self.Schedule_b.heading('#0', text='blank', anchor=CENTER)
        self.Schedule_b.heading('Title', text='Title', anchor=CENTER)
        self.Schedule_b.heading('Date', text='Date', anchor=CENTER)
        self.Schedule_b.heading('Time', text='Time', anchor=CENTER)
        self.Schedule_b.heading('Description', text='Description', anchor=CENTER)

        # =========================================
        # ###Message frame
        # =========================================
        self.messageLabel = ttk.Label(self.MessageFrame)

        # ====================================================
        # Add Frames and Widgets to Grid
        # ====================================================
        # Clock Frame
        self.ClockFrame.grid(column=0, row=0, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.date.grid(column=0, row=0, padx=self.padding, pady=self.padding, sticky='NW')
        self.clock.grid(column=0, row=1, padx=self.padding, pady=self.padding, sticky='NW')
        self.temp_label.grid(column=0, row=2, padx=self.padding, pady=self.padding, sticky='NW')
        self.feels_like_label.grid(column=0, row=3, padx=self.padding, pady=self.padding, sticky='NW')
        self.min_max_temp_label.grid(column=0, row=4, padx=self.padding, pady=self.padding, sticky='NW')
        self.condition_label.grid(column=0, row=5, padx=self.padding, pady=self.padding, sticky='NW')
        self.humidity_label.grid(column=0, row=6, padx=self.padding, pady=self.padding, sticky='NW')

        # Timer Frame
        self.TimerFrame.grid(column=0, row=1, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.Timer_Clock_Inner_Frame.grid(column=0, row=0, columnspan=5, padx=self.padding, pady=self.padding,
                                          sticky='NSWE')
        self.reset_button.grid(column=0, row=0, padx=self.padding, pady=self.padding,
                               sticky='NSWE')  # in Timer_Clock_Inner_Frame
        self.hours_field.grid(column=1, row=0, padx=self.padding, pady=self.padding,
                              sticky='NSWE')  # in Timer_Clock_Inner_Frame
        self.minutes_field.grid(column=2, row=0, padx=self.padding, pady=self.padding,
                                sticky='NSWE')  # in Timer_Clock_Inner_Frame
        self.seconds_field.grid(column=3, row=0, padx=self.padding, pady=self.padding,
                                sticky='NSWE')  # in Timer_Clock_Inner_Frame
        self.start_toggle_button.grid(column=4, row=0, padx=self.padding, pady=self.padding,
                                      sticky='NSWE')  # in Timer_Clock_Inner_Frame
        self.five_sec_button.grid(column=1, row=1, padx=self.padding, pady=self.padding,
                                  sticky='NSWE')  # below Timer_Clock_Inner_Frame
        self.ten_sec_button.grid(column=2, row=1, padx=self.padding, pady=self.padding,
                                 sticky='NSWE')  # below Timer_Clock_Inner_Frame
        self.fifteen_sec_button.grid(column=3, row=1, padx=self.padding, pady=self.padding,
                                     sticky='NSWE')  # below Timer_Clock_Inner_Frame
        self.progress_bar.grid(column=0, row=2, columnspan=5, padx=self.padding, pady=self.padding,
                               sticky='NSWE')  # below buttons

        # Pomodoro Frame
        self.PomodoroFrame.grid(column=0, row=2, rowspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.pom_minutes.grid(column=0, row=0, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.pom_minutes_label.grid(column=1, row=0, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.pom_start.grid(column=2, row=0, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.pom_progress_bar.grid(column=0, row=3, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')

        # To-Do Frame
        self.ToDoListFrame.grid(column=1, row=0, columnspan=2, rowspan=7, padx=self.padding, pady=self.padding,
                                sticky='NS' + 'EW')
        self.to_do_top.grid(column=0,row=0, padx=self.padding, pady=self.padding,
                                sticky='NS' + 'EW')
        self.to_do_bottom.grid(column=0,row=1, padx=self.padding, pady=self.padding,
                                sticky='NS' + 'EW')

        # ###Top
        self.TitleLabel.grid(column=0, row=0, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.TitleEntry.grid(column=0, row=1, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.DateLabel.grid(column=0, row=2, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.DateEntry.grid(column=0, row=3, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.TimeLabel.grid(column=0, row=4, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.TimeEntry.grid(column=0, row=5, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.DescLabel.grid(column=0, row=6, columnspan=3, padx=self.padding, pady=self.padding, sticky='N' + 'EW')
        self.DescEntry.grid(column=0, row=7, columnspan=3, padx=self.padding, pady=self.padding, sticky='N' + 'EW')
        self.EntryButton.grid(column=0, row=8, padx=self.padding, pady=self.padding, sticky='N' + 'W')
        self.DeleteButton.grid(column=1, row=8, padx=self.padding, pady=self.padding, sticky='N' + 'W')
        self.EditButton.grid(column=2, row=8, padx=self.padding, pady=self.padding, sticky='N' + 'W')
        self.Schedule.grid(column=3, row=0, rowspan=14, padx=self.padding, pady=self.padding, sticky='NS')

        # ###Bottom
        self.TitleLabel_b.grid(column=0, row=0, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.TitleEntry_b.grid(column=0, row=1, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.DateLabel_b.grid(column=0, row=2, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.DateEntry_b.grid(column=0, row=3, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.TimeLabel_b.grid(column=0, row=4, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.TimeEntry_b.grid(column=0, row=5, columnspan=3, padx=self.padding, pady=self.padding, sticky='NSWE')
        self.DescLabel_b.grid(column=0, row=6, columnspan=3, padx=self.padding, pady=self.padding, sticky='N' + 'EW')
        self.DescEntry_b.grid(column=0, row=7, columnspan=3, padx=self.padding, pady=self.padding, sticky='N' + 'EW')
        self.EntryButton_b.grid(column=0, row=8, padx=self.padding, pady=self.padding, sticky='N' + 'W')
        self.DeleteButton_b.grid(column=1, row=8, padx=self.padding, pady=self.padding, sticky='N' + 'W')
        self.EditButton_b.grid(column=2, row=8, padx=self.padding, pady=self.padding, sticky='N' + 'W')
        self.Schedule_b.grid(column=3, row=0, rowspan=14, padx=self.padding, pady=self.padding, sticky='NS')


        # Message Frame
        self.MessageFrame.grid(column=0, row=8, columnspan=2,padx=self.padding, pady=self.padding, sticky='EW')
        self.messageLabel.grid(column=0, row=0, columnspan=2,padx=self.padding, pady=self.padding, sticky='EW')
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

    def startTimer(self):
        if self.TimerStatus == False:
            try:
                self.hours = (int(self.hours_field.get()))
                if self.hours_field.get == NONE or self.hours_field == 000:
                    self.hours = 0

                self.minutes = int(self.minutes_field.get())
                if self.minutes_field.get == NONE or self.minutes_field == 000:
                    self.minutes = 0

                self.seconds = (int(self.seconds_field.get()))
                if self.seconds_field.get == NONE or self.seconds_field == 000:
                    self.seconds = 0

            except ValueError:
                self.messageLabel.config(text="Please enter valid numeric values for the timer.")

            self.total_seconds = self.hours * 3600 + self.minutes * 60 + self.seconds
            self.messageLabel.config(text="Timer Started.")
            self.reset_button['state'] = tk.DISABLED
            self.five_sec_button['state'] = tk.DISABLED
            self.ten_sec_button['state'] = tk.DISABLED
            self.fifteen_sec_button['state'] = tk.DISABLED
            self.TimerStatus = True
            self.progress_bar.start(1000)
            self.updateTimer(self.total_seconds)


        elif self.TimerStatus == True:
            self.messageLabel.config(text="Timer Paused!")
            self.hours = (int(self.hours_field.get()))

            self.minutes = int(self.minutes_field.get())

            self.seconds = (int(self.seconds_field.get()))

            self.TimerStatus = False
            self.progress_bar.stop()
            self.reset_button['state'] = tk.NORMAL
            self.five_sec_button['state'] = tk.NORMAL
            self.ten_sec_button['state'] = tk.NORMAL
            self.fifteen_sec_button['state'] = tk.NORMAL
            pass


    def updateTimer(self, remaining_seconds):
        if self.TimerStatus == True:
            if remaining_seconds > 0:
                self.hours_field.delete(0, END)
                self.hours_field.insert(0, str((int(remaining_seconds) // 3600)).zfill(2))
                self.minutes_field.delete(0, END)
                self.minutes_field.insert(0, str(int((remaining_seconds % 3600) // 60)).zfill(2))
                self.seconds_field.delete(0, END)
                self.seconds_field.insert(0, str(int(remaining_seconds % 60)).zfill(2))

                self.after(1000, self.updateTimer, remaining_seconds - 1)
            else:
                self.messageLabel.config(text="Timer expired!")
                self.progress_bar.stop()

        elif self.TimerStatus == False:
            pass

    def addFive(self):
        # In Minutes
        self.minutes = str(int(self.minutes_field.get()) + 5)
        self.minutes_field.delete(0, END)
        self.minutes_field.insert(0, self.minutes)


    def addTen(self):
        # In Minutes
        self.minutes = str(int(self.minutes_field.get()) + 10)
        self.minutes_field.delete(0, END)
        self.minutes_field.insert(0, self.minutes)

    def addFifteen(self):
        # In Minutes
        self.minutes = str(int(self.minutes_field.get()) + 15)
        self.minutes_field.delete(0, END)
        self.minutes_field.insert(0, self.minutes)

    def resetTimer(self):
        self.hours_field.delete(0, END)
        self.hours_field.insert(0, str(0).zfill(2))
        self.minutes_field.delete(0, END)
        self.minutes_field.insert(0, str(0).zfill(2))
        self.seconds_field.delete(0, END)
        self.seconds_field.insert(0, str(0).zfill(2))
        self.progress_bar.stop()

    def startPomodoro(self):
        pass

    def updatePomodoro(self):
        pass



if __name__ == '__main__':
    app = Clock_Scheduler()
    app.mainloop()
