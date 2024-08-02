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
    
class SingleSelector(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, options:list, *, selected:str=None, apply_btn:bool=False, sorted:bool=True) -> None:
        super().__init__(frm, borderwidth=2, relief='groove')

        self.frm = frm
        self.name = name
        self.options = options
        self.apply_btn = apply_btn
        self.sorted = sorted

        self.listeners = []

        self.selected = tk.StringVar()
        self.btns = list[ttk.Radiobutton]()

        ttk.Label(self,text=self.name).grid(row=0,column=0,columnspan=2,sticky='news')
        self.__place_buttons()

        if self.apply_btn:
            ttk.Button(self, text='Apply', command=self.value_update).grid(row=len(self.options)+1,column=0,columnspan=2,sticky='news')
        if selected is not None and selected in self.options:
            self.selected.set(selected)

    def __place_buttons(self):
        if self.sorted:
            self.options.sort()
        r = 1
        for option in self.options:
            if self.apply_btn:
                self.btns.append(ttk.Radiobutton(self, text=option, variable=self.selected, value=option))
            else:
                self.btns.append(ttk.Radiobutton(self, text=option, variable=self.selected, value=option, command=self.value_update))
            self.btns[-1].grid(row=r,column=0,sticky='news')
            r += 1
        self.selected.set(self.options[0])

    """
    Return the selected value
    """
    def get_selected(self) -> str:
        return self.selected.get()

    """
    Notify any listeners that the values have been updated
    Passes the list of selected values to all listeners
    """
    def value_update(self) -> None:
        for listener in self.listeners:
            listener.update_value(self.name, self.get_selected())

    """
    Adds a listener that will be updated everytime different values are selected
    Listeners use update_value(name, value) to listen
    """
    def add_listener(self, listener) -> None:
        self.listeners.append(listener)

    def select(self, option:str, like_click:bool=True) -> bool:
        if option in self.options:
            self.selected.set(option)
            if not self.apply_btn and like_click:
                self.value_update()
            return True
        return False

    def clear_options(self) -> None:
        for button in self.btns:
            button.destroy()
        self.btns.clear()
        self.options.clear()
        self.selected.set('')

    def remove_option(self, option:str) -> bool:
        if option in self.options:
            index = self.options.index(option)
            btn = self.btns.pop(index)
            btn.destroy()
            self.options.pop(index)
            for i in range(index,len(self.btns)):
                btn.grid(row=i,column=0,sticky='news')
            if self.selected.get() == option:
                if len(self.btns) > 0:
                    self.selected.set(self.options[0])
                    self.value_update()
                else:
                    self.selected.set('')
            return True
        return False
    
    def add_option(self, option:str) -> None:
        if self.sorted:
            if 0:
                print("Error: Multiselector.add_option not implemented for sorted selections")
        else:
            self.options.append(option)
            if self.apply_btn:
                self.btns.append(ttk.Radiobutton(self, text=option, variable=self.selected, value=option))
            else:
                self.btns.append(ttk.Radiobutton(self, text=option, variable=self.selected, value=option, command=self.value_update))
            self.btns[-1].grid(row=len(self.options),column=0,sticky='news')

    def add_options(self, options:list[str]) -> None:
        for option in options:
            self.add_option(option)

    def set_options(self, options:list[str]) -> None:
        self.clear_options()
        self.options.extend(options)
        self.__place_buttons()
