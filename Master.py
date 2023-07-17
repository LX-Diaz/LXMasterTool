#!C:/Users/luis.diaz-guilbee/OneDrive - AMN Healthcare, Inc/Documents/LXMasterTool/venv/Scripts/python.exe
"""
Main program in my LXMasterTool toolset. Handles GUI and overall functionality and will serve as the core program to access my tools.
Written by Luis X. Diaz
12/30/2020

--------------------------------
6/14/2021
--------------------------------
Usage Notes:
-The Document Organizer has been disabled;it's functionality is broken due to dependency on Service Now.
-To make new Template entries, add them to the TEMPLATES dictionary following the format shown with the examples.
  The Key designates the button label, the value shows the contents of the template to insert in clipboard.

--------------------------------
6/28/2023
--------------------------------
-The program has been rewritten to make use of the more approachable TkInter module instead of Pyglet and Glooey.
-The configparser module has been added to make use of .ini files for configuration storage, hopefully allowing for more
user-specific configuration and versatility.

--------------------------------
7/03/2023
--------------------------------
- Implemented themes to tkinter allowing users to switch between light and dark styling

--------------------------------
7/05/2023
--------------------------------
- Re-wrote template functionality to use the Combobox in Tkinter along with a textbox to allow editing of templates
before pasting.

--------------------------------
7/11/2023
--------------------------------
- Implemented the use of a Config.ini file to allow users the flexibility of changing settings as well as adding their
own templates.
- Renamed the program to CST Master Tool and created a logo.

--------------------------------
7/16/2023
--------------------------------
- Added copy, cut, paste functionality to text input/output box.
- Added Font and Font Size editing function to the config file for better user customization.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import *
import pyperclip as pc
import configparser
import string
import secrets
import re
import os
import sys
import webbrowser as wb
import multiprocessing as mp


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Initialize imported Classes
        self.app = None
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # Create Main Window
        self.resizable(False, False)
        self.title('CST Master Tool')
        self.iconbitmap('./theme/CST Assistant Logo.ico')
        self.tk.call("source", "azure.tcl")
        self.theme = self.config['OPTIONS']['Theme']
        self.tk.call("set_theme", self.theme)

        # Define Variables
        # =============================================

        self.letters = string.ascii_lowercase
        self.digits = string.digits
        self.alphabet = self.letters + self.digits
        self.exclude = ['1', 'i', 'l', '0', 'O', 'o']
        for items in self.exclude:
            self.alphabet = self.alphabet.replace(items, '')
        self.pwd = ''
        self.passwords = []
        self.password_length = int(self.config['OPTIONS']['PasswordLength'])
        self.clipBoard = ''
        self.state = tk.StringVar()
        self.state.set('Ready.')
        # =============================================

        # Define Frames
        # =============================================
        self.tools_frame = ttk.LabelFrame(text='Templates')
        self.text_frame = ttk.LabelFrame(text='Output')
        self.passwords_frame = ttk.LabelFrame(text='Passwords')
        self.status_frame = ttk.Frame()
        # =============================================

        # Define Widgets
        # =============================================
        #Templates Widgets
        self.templates_Keys = []
        self.selected_template = tk.StringVar()
        for key in self.config['TEMPLATES']:
            self.templates_Keys.append(key)

        self.templates_ComboBox = ttk.Combobox(self.tools_frame, width=25,
                                               textvariable=self.selected_template)
        self.templates_ComboBox['values'] = self.templates_Keys
        self.configure_button = ttk.Button(self.tools_frame, text='Configure', command=self.Configure)
        self.restart_button = ttk.Button(self.tools_frame, text='Update', command=self.RestartProgram)

        # Password Widgets
        self.passPromptLabel = ttk.Label(self.passwords_frame, text='How many?')

        self.quantity = tk.IntVar()
        self.quantity.set(5)
        self.quantityBox = ttk.Spinbox(self.passwords_frame,
                                       from_=1, to=100,
                                       increment=1, width=10,
                                       textvariable=self.quantity)

        self.GenerateButton = ttk.Button(self.passwords_frame,
                                             text='Generate',
                                             command=self.generateList,style="Accent.TButton")

        self.ClearButton = ttk.Button(self.text_frame,
                                          text='Clear',
                                          command=self.clearText)

        # Output Widgets
        self.text_area = scrolledtext.ScrolledText(self.text_frame,
                                                   wrap=tk.WORD,
                                                   undo= True,
                                                   maxundo=-1,
                                                   autoseparators=False,
                                                   width=40,
                                                   height=10,
                                                   font=(self.config['OPTIONS']['Text Font'], self.config['OPTIONS']['Font Size']))

        self.SeparateButton = ttk.Button(self.text_frame,
                                              text='Separate',
                                              command=self.separate)

        self.CopyButton = ttk.Button(self.text_frame,
                                      text='Copy',
                                      command=self.copyText)

        self.contextMenu = Menu(self.text_area, tearoff=0)
        self.contextMenu.add_command(label="Copy", command = self.copySelectedText)
        self.contextMenu.add_command(label="Cut", command=self.cutSelectedText)
        self.contextMenu.add_command(label="Paste", command = self.pasteText)

        def do_popup(event):
            try:
                self.contextMenu.tk_popup(event.x_root, event.y_root)
            finally:
                self.contextMenu.grab_release()

        self.text_area.bind("<Button-3>", do_popup)

        #Status Label
        self.statusLabel = ttk.Label(self.status_frame, textvariable=self.state)
        # =============================================

        # Add frames to grid
        # =============================================
        # Templates
        self.tools_frame.grid(column=0, row=0, padx=3, pady=3, sticky='NW')
        self.templates_ComboBox.grid(column=0, row=0, columnspan=2, padx=3, pady=3)
        self.templates_ComboBox.bind('<<ComboboxSelected>>', self.CopyTemplate)
        self.configure_button.grid(column=0, row=1, padx=3, pady=3, sticky='W')
        self.restart_button.grid(column=1, row=1, padx=3, pady=3, sticky='W')

        # Password Generation
        self.passwords_frame.grid(column=1, row=0, padx=3, pady=3, sticky='W')
        self.passPromptLabel.grid(column=0, row=0, padx=3, pady=3, sticky='W')
        self.quantityBox.grid(column=1, row=0, padx=3, pady=3)
        self.GenerateButton.grid(column=1, padx=3, pady=3, sticky='W')

        # Text output
        self.text_frame.grid(column=0, row=1, columnspan=4, padx=3, pady=3)
        self.CopyButton.grid(column=1, row=0, padx=3, pady=3, sticky='W')
        self.ClearButton.grid(column=2, row=0, padx=3, pady=3, sticky='W')
        self.SeparateButton.grid(column=3, row=0, padx=3, pady=3, sticky='W')
        self.text_area.grid(column=0, row=1, columnspan=4, padx=3, pady=3)

        # Status Output
        self.status_frame.grid(column=0, row=2, columnspan=4, padx=1, pady=1, sticky='W')
        self.statusLabel.grid(column=0, row=0, columnspan=4, padx=1, pady=1, sticky='W')

        # =============================================

    # Define Functions
    def CopyTemplate(self, event):
        self.entry = self.templates_ComboBox.get()
        pc.copy(self.config['TEMPLATES'][self.entry])
        self.text_area.delete('1.0', 'end')
        self.text_area.insert('end', self.config['TEMPLATES'][self.entry])
        self.state.set('Template copied to clipboard.')

    def createPassword(self):
        self.pwd = ''
        for i in range(self.password_length):
            self.pwd += ''.join(secrets.choice(self.alphabet))

        if len(set(self.pwd)) == len(self.pwd) and bool(re.search(r'\d', self.pwd)):
            return self.pwd

        else:
            self.createPassword()

    def generateList(self):
        self.passwords.clear()
        self.text_area.delete('1.0', 'end')

        for index in range(int(self.quantityBox.get())):
            self.createPassword()
            self.passwords.append(self.pwd)

        for items in self.passwords:
            self.text_area.insert('end', items + '\n')
            self.clipBoard += items + '\n'
            pc.copy(self.clipBoard)
            self.state.set('Copied to Clipboard.')

    def clearText(self):
        self.text_area.delete('1.0', 'end')
        self.passwords.clear()
        self.pwd = ''
        self.clipBoard = ''
        pc.copy('')
        self.state.set('Cleared.')

    def separate(self):
        self.input = self.text_area.get('1.0', 'end')
        x = self.input.split()
        self.separated = ','.join(x)
        self.text_area.delete('1.0', 'end')
        self.text_area.insert('1.0', self.separated)
        pc.copy(self.separated)
        self.state.set('Copied to Clipboard.')

    def copyText(self):
        pc.copy(self.text_area.get('1.0', 'end'))
        self.text = pc.copy(self.text_area.get('1.0', 'end'))
        self.state.set('Copied to Clipboard.')

    def copySelectedText(self):
        if self.text_area.selection_get():
            pc.copy(self.text_area.selection_get())
        self.state.set('Copied selected text to clipboard.')

    def cutSelectedText(self):  # Cut the selection of text to clipboard
        if self.text_area.selection_get():
            pc.copy(self.text_area.selection_get())  # copy selected text to clipboard
            self.text_area.delete('sel.first', 'sel.last')  # delete selected text


    def pasteText(self):
        self.text_area.insert(INSERT,pc.paste())
        self.state.set('Paste from Clipboard.')

    def Configure(self):
        wb.open('config.ini')

    def RestartProgram(self):
        self.destroy()
        self.app = App()
        self.app.mainloop()


if __name__ == "__main__":
    app = App()
    app.mainloop()

