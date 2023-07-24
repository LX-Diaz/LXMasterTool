# LXMasterTool

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

--------------------------------
7/16/2023
--------------------------------
- Added copy, cut, paste functionality to text input/output box.
- Added Font and Font Size editing function to the config file for better user customization.

--------------------------------
7/24/2023
--------------------------------
- Added functionality to save new Templates with a GUI. 
