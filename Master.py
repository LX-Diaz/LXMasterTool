# encoding utf-8

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
        self.promptWindow = None
        self.app = None
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # Create Main Window
        self.resizable(False, False)
        self.title('LX Master Tool')
        self.tk.call("source", "azure.tcl")
        self.theme = self.config['OPTIONS']['Theme']
        self.tk.call("set_theme", self.theme)

        # Define Variables
        # =============================================
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
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

        self.AddButton = ttk.Button(self.text_frame, text='Add', command=self.AddTemplate)

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
        self.AddButton.grid(column=4, row=0, padx=3, pady=3, sticky='W' )
        self.text_area.grid(column=0, row=1, columnspan=5, padx=3, pady=3, sticky='EW')

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
            self.state.set(' Passwords Copied to Clipboard.')

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

    def AddTemplate(self):
        self.TemplateTitle_s = ''
        self.TemplateText_s = ''
        self.templateText = self.text_area.get('1.0', 'end')
        self.promptWindow = Toplevel(self)
        self.promptWindow.title("Template Entry")
        self.TitleLabel = ttk.Label(self.promptWindow, text='What\'s the title?')
        self.TemplateLabel = ttk.Label(self.promptWindow, text='Template')
        self.TitleEntry = ttk.Entry(self.promptWindow)
        self.TemplateContent = tk.Text(self.promptWindow)
        self.SaveButton = ttk.Button(self.promptWindow, style="Accent.TButton", text='Save💾', command=self.SaveTemplate)

        self.TitleLabel.grid(column=0, row=0, padx=2, pady=2, sticky='NW')
        self.TitleEntry.grid(column=0, row=1, padx=2, pady=2, sticky='NW')
        self.TemplateLabel.grid(column=0, row=2, padx=2, pady=2, sticky='NW')
        self.TemplateContent.grid(column=0, row=3, padx=2, pady=2, sticky='NW')
        self.SaveButton.grid(column=0, row=4, padx=2, pady=2, sticky='SE')

        self.TemplateContent.insert('1.0', self.templateText)

    def SaveTemplate(self):
        self.TemplateTitle_s = self.TitleEntry.get()
        self.TemplateText_s = self.TemplateContent.get('1.0', 'end')
        self.config.set('TEMPLATES', self.TemplateTitle_s, self.TemplateText_s)
        with open('config.ini','w') as configfile:
            self.config.write(configfile)
        self.promptWindow.destroy()
        self.destroy()
        self.app = App()
        self.app.mainloop()


if __name__ == "__main__":
    app = App()
    app.mainloop()

