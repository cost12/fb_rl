import tkinter as tk
from tkinter import ttk

class ButtonGroup(ttk.Frame):
    """
    Groups buttons together and highlights the most recently clicked button
    To use: call add_listener and implement update_value(name, value) in the listener
    """

    def __init__(self, frm:ttk.Frame, name:str, options:list[str]=None,selected:str=None):
        super().__init__(frm, borderwidth=2, relief='groove')

        self.name = name
        if options is None:
            self.options = list[str]()
        else:
            self.options = options
        self.selected = selected
        self.listeners = []
        self.buttons = dict[str,ttk.Button]()

        self.select_style=ttk.Style()
        self.select_style.map("Mod.TButton", background = [("active", "red"), ("!active", "blue")])#, foreground = [("active", "yellow"), ("!active", "green")])

        self.__display_buttons()

    def __display_buttons(self):
        c=0
        for option in self.options:
            def notify(o=option):
                self.value_update(o)
            style = 'TButton'
            if option == self.selected:
                style = 'Mod.TButton'
            self.buttons[option] = ttk.Button(self,text=option,command=notify,style=style)
            self.buttons[option].grid(row=0,column=c,sticky='news')
            c+=1

    def set_options(self, options:list[str], selected:str=None):
        for button in self.buttons.values():
            button.destroy()
        self.buttons.clear()
        self.options.clear()
        self.options.extend(options)
        self.selected = selected
        self.__display_buttons()

    def add_listener(self, listener):
        self.listeners.append(listener)

    def value_update(self, value:str):
        if self.selected is not None:
            self.buttons[self.selected].configure(style='TButton')
        self.selected = value
        self.buttons[self.selected].configure(style='Mod.TButton')

        for listener in self.listeners:
            listener.update_value(self.name, value)

    def set_highlight(self, value:str) -> bool:
        if value in self.buttons.keys():
            if self.selected is not None:
                self.buttons[self.selected].configure(style='TButton')
            self.selected = value
            self.buttons[self.selected].configure(style='Mod.TButton')
            return True
        return False