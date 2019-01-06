import tkinter as tk

class AreaApp(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry('500x200+100+100')

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry('800x1000+100+100')
        self.create_widgets()
        
    def create_area_input(self,xoff,yoff):
        self.areas = tk.Label(self.master,text='Areas')
        self.areas.place(x=xoff+10,y=yoff+10,width=50,height=25)
        self.add_area = tk.Button(self.master,bg='black',command=self.add_area_action)
        self.add_area.place(x=xoff+60,y=yoff+10,width=20,height=20)
        self.clear = tk.Button(self.master, text='Clear', fg='white',bg='gray',
                              command=self.clear_action)
        self.clear.place(x=xoff+300,y=yoff+10,width=50,height=25)
        self.start = tk.Button(self.master, text='Start the monitor', fg='white',bg='green',
                              command=self.start_action)
        self.start.place(x=xoff+350,y=yoff+10,width=125,height=25)
        self.city_name = tk.Label(self.master,text='City Name')
        self.city_name.place(x=xoff+85,y=yoff+30,width=80,height=25)
        self.city_entry = tk.Entry(self.master)
        self.city_entry.place(x=xoff+170,y=yoff+30,width=100,height=25)
        self.OR = tk.Label(self.master,text='OR')
        self.OR.place(x=xoff+60,y=yoff+50,width=25,height=25)
        self.coords = tk.Label(self.master,text='Coordinates')
        self.coords.place(x=xoff+85,y=yoff+70,width=80,height=25)
        self.coords_entry = tk.Entry(self.master)
        self.coords_entry.place(x=xoff+170,y=yoff+70,width=100,height=25)
        self.range = tk.Label(self.master,text='Range')
        self.range.place(x=xoff+270,y=yoff+70,width=50,height=25)
        self.range_entry = tk.Entry(self.master)
        self.range_entry.place(x=xoff+320,y=yoff+70,width=50,height=25)
        self.km = tk.Label(self.master,text='km')
        self.km.place(x=xoff+370,y=yoff+70,width=25,height=25)
        self.show_map = tk.Button(self.master, text='Show Map', fg='black',bg='white',
                              command=self.show_map)
        self.show_map.place(x=xoff+425,y=yoff+70,width=80,height=25)

    def show_map(self):
        print('show')

    def create_widgets(self):
        self.create_area_input(0,0)

    def start_action(self):
        print('start') 

    def clear_action(self):
        print('clear')

    def add_area_action(self):
        add_area_root = tk.Tk()
        add_app = AreaApp(master=add_area_root)
        add_app.mainloop()

root = tk.Tk()
app = Application(master=root)
app.mainloop()
