import tkinter as tk
from tkinter import ttk
import random
import time

import visual_tools as vt

class View(ttk.Frame):
    def __init__(self, frm:ttk.Frame, borderwidth=2, relief='groove'):
        super().__init__(frm, borderwidth=borderwidth, relief=relief)

    def change_to(self):
        pass

    def change_from(self):
        pass

    def main_loop(self):
        pass

    def ready_to_leave(self):
        return True

class MainFrame(ttk.Frame):

    def __init__(self, frm:ttk.Frame, frames:dict[str,View], access:dict[str,list[str]], start_screen:str):
        super().__init__(frm, borderwidth=2, relief='groove')

        self.root = frm
        self.views = dict[str,View](frames)
        self.access = dict[str,list[str]](access)
        self.view = start_screen

        self.buttons = vt.ButtonGroup(self, "Screens", list(self.access[start_screen]))#,selected=start_screen)
        self.buttons.add_listener(self)
        self.buttons.pack()

        self.error_text = tk.StringVar()
        self.error_text.set("Welcome!")
        ttk.Label(self,textvariable=self.error_text).pack()

        for view in self.views:
            self.views[view].pack(fill='y',expand=True,side='top')
        for view in self.views:
            if not view == start_screen:
                self.views[view].forget()
        self.views[start_screen].change_to()

    def main_loop(self):
        self.views[self.view].main_loop()
        self.root.update()
        self.root.after(100,self.main_loop)

    def update_value(self, name, value):
        if name == 'Screens':
            self.change_view(value)

    def change_view(self,view:str) -> None:
        if not self.views[self.view].ready_to_leave():
            self.error_text.set("Error: Can't leave yet")
            self.buttons.set_highlight(self.view)
            return
        elif view in self.views and view != self.view:
            self.error_text.set("No Errors Detected")
            self.views[self.view].forget()
            self.views[self.view].change_from()
            self.view = view
            self.views[self.view].change_to()
            self.buttons.set_options(self.access[self.view])
            self.views[self.view].pack(fill='y',expand=True,side='top')

class GameSetFrame(View):

    def __init__(self, frm:ttk.Frame):
        super().__init__(frm, borderwidth=2, relief='groove')

    def change_to(self):
        pass

    def change_from(self):
        pass

    def main_loop(self):
        pass


class GameFrame(View):

    def __init__(self, frm:ttk.Frame, game_manager):
        super().__init__(frm, borderwidth=2, relief='groove')
        game_manager.env.viewers.append(self)
        self.reset(game_manager.env)
        self.update_env(game_manager.env)
        self.game_manager = game_manager

    def main_loop(self):
        self.game_manager.advance_play()
    
    def change_to(self):
        self.game_manager.on()

    def change_from(self):
        self.game_manager.off()

    def reset(self,env):
        self.scorebug = ScorebugFrame(self)
        self.scorebug.grid(row=0,column=1,sticky='news')
        self.field = FieldFrame(self,env.width,env.length)
        self.field.grid(row=1,column=0,columnspan=2,sticky='news')

    def update_env(self, env):
        self.scorebug.update_env(env)
        self.field.update_env(env)

class ScorebugFrame(ttk.Frame):

    def __init__(self, frm:ttk.Frame):
        super().__init__(frm, borderwidth=2, relief='groove')
        self.reset()

    def update_env(self, env):
        self.t1.set(env.t1())
        self.t2.set(env.t2())
        self.s1.set(env.s1())
        self.s2.set(env.s2())
        self.to1.set(env.to1())
        self.to2.set(env.to2())
        self.q.set(env.q()+1)
        self.time.set(env.time_str())
        self.down.set(env.down()+1)
        self.dist.set(env.dist())
        yd_str = "OWN " if (env.yd_line() <= 50 and env.dir() == 1) or (env.yd_line() > 50 and env.dir() == -1) else "OPP "
        yd_str += (str(env.yd_line()) if env.yd_line() <= 50 else str(100-env.yd_line()))
        self.yd_line.set(yd_str)
        self.dir.set('<' if env.dir() == -1 else '>')
        self.fg_dist.set(env.state.fg_dist())
        self.gain.set(env.gain())

    def reset(self):
        #self.destroy() TODO: need some kind of reset
        self.t1 = tk.StringVar()
        self.t2 = tk.StringVar()
        ttk.Label(self, textvariable=self.t1,font=('Sans',10,'bold')).grid(row=0,column=0,sticky='news')
        ttk.Label(self, textvariable=self.t2                        ).grid(row=0,column=2,sticky='news')

        self.s1 = tk.StringVar()
        self.s2 = tk.StringVar()
        ttk.Label(self, textvariable=self.s1).grid(row=0,column=1,sticky='news')
        ttk.Label(self, textvariable=self.s2).grid(row=0,column=3,sticky='news')

        self.to1 = tk.StringVar()
        self.to2 = tk.StringVar()
        ttk.Label(self, text="TOL"           ).grid(row=2,column=0,sticky='news')
        ttk.Label(self, text="TOL"           ).grid(row=2,column=2,sticky='news')
        ttk.Label(self, textvariable=self.to1).grid(row=2,column=1,sticky='news')
        ttk.Label(self, textvariable=self.to2).grid(row=2,column=3,sticky='news')

        self.q = tk.StringVar()
        ttk.Label(self, text='Q'           ).grid(row=0,column=4,sticky='news')
        ttk.Label(self, textvariable=self.q).grid(row=0,column=5,sticky='news')

        self.time = tk.StringVar()
        ttk.Label(self, textvariable=self.time).grid(row=0,column=6,sticky='news')

        self.down = tk.StringVar()
        ttk.Label(self, textvariable=self.down).grid(row=0,column=7,sticky='news')
        ttk.Label(self, text="&").grid(row=0,column=8,sticky='news')
        
        self.dist = tk.StringVar()
        ttk.Label(self, textvariable=self.dist).grid(row=0,column=9,sticky='news')

        self.yd_line = tk.StringVar()
        ttk.Label(self, textvariable=self.yd_line).grid(row=0,column=10,sticky='news')

        self.dir = tk.StringVar()
        ttk.Label(self, textvariable=self.dir).grid(row=0,column=11,sticky='news')

        self.fg_dist = tk.StringVar()
        ttk.Label(self, text="FG:").grid(row=0,column=12,sticky='news')
        ttk.Label(self, textvariable=self.fg_dist).grid(row=0,column=13,sticky='news')

        self.gain = tk.StringVar()
        ttk.Label(self, text="Current:").grid(row=0,column=14,sticky='news')
        ttk.Label(self, textvariable=self.gain).grid(row=0,column=15,sticky='news')

        
class FieldFrame(ttk.Frame):

    def __init__(self, frm:ttk.Frame, r:int, c:int, *,width=300,length=1000):
        super().__init__(frm, borderwidth=2, relief='groove')
        self.r = r
        self.c = c
        self.width = width
        self.length = length
        self.reset()

    def update_env(self, env): # TODO: this but more efficient
        for player in self.players:
            self.canvas.delete(player)

        self.players.clear()
        player = self.canvas.create_oval(*self.xy_to_coords(env.offense.x(),env.offense.y()),fill='black')
        self.players.append(player)
        for p in env.defense:
            player = self.canvas.create_oval(*self.xy_to_coords(p.x(),p.y()),fill='red')
            self.players.append(player)

    def unit_width(self):
        return self.width/self.r
    
    def unit_length(self):
        return self.length/self.c
    
    def xy_to_coords(self, x, y) -> tuple[int]:
        y1 = self.unit_width()/4 + self.unit_width()*y
        y2 = self.unit_width()*3/4 + self.unit_width()*y
        x1 = self.unit_length()/4 + self.unit_length()*x
        x2 = self.unit_length()*3/4 + self.unit_length()*x
        return x1,y1,x2,y2

    def reset(self):
        self.canvas = tk.Canvas(self, width=self.length, height=self.width)
        self.canvas.pack()

        # draw the retro field and lines
        self.canvas.create_rectangle(0,0,self.length,self.width,fill='green')
        for i in range(1,self.r):
            self.canvas.create_line(0,i*self.unit_width(),self.length,i*self.unit_width())
        for i in range(1,self.c):
            self.canvas.create_line(i*self.unit_length(),0,i*self.unit_length(),self.width)

        # draw the players
        self.players = []
        player = self.canvas.create_oval(*self.xy_to_coords(0,1),fill='black')
        self.players.append(player)
        player = self.canvas.create_oval(*self.xy_to_coords(3,0),fill='red')
        self.players.append(player)
        player = self.canvas.create_oval(*self.xy_to_coords(3,1),fill='red')
        self.players.append(player)
        player = self.canvas.create_oval(*self.xy_to_coords(3,2),fill='red')
        self.players.append(player)
        player = self.canvas.create_oval(*self.xy_to_coords(5,1),fill='red')
        self.players.append(player)
        player = self.canvas.create_oval(*self.xy_to_coords(8,1),fill='red')
        self.players.append(player)