import tkinter as tk
from functools import partial

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry('800x1000+1100+20')
        self.amenities = ['School','Theatre']
        self.create_widgets()
        
    def create_area_input(self,xoff,yoff):
        self.areas = tk.Label(self.master,text='Areas')
        self.areas.place(x=xoff+10,y=yoff+10)
        self.add_area = tk.Button(self.master,bg='black',command=self.add_area_action)
        self.add_area.place(x=xoff+55,y=yoff+10,width=20,height=20)
        self.clear = tk.Button(self.master, text='Clear', fg='white',bg='gray',
                              command=self.clear_action)
        self.clear.place(x=xoff+300,y=yoff+10)
        self.start = tk.Button(self.master, text='Start the monitor', fg='white',bg='green',
                              command=self.start_action)
        self.start.place(x=xoff+375,y=yoff+10)
        self.city_name = tk.Label(self.master,text='City Name')
        self.city_name.place(x=xoff+85,y=yoff+35)
        self.city_entry = tk.Entry(self.master)
        self.city_entry.place(x=xoff+170,y=yoff+35,width=100)
        self.OR = tk.Label(self.master,text='OR')
        self.OR.place(x=xoff+60,y=yoff+55)
        self.coords = tk.Label(self.master,text='Coordinates')
        self.coords.place(x=xoff+85,y=yoff+75)
        self.coords_entry = tk.Entry(self.master)
        self.coords_entry.place(x=xoff+170,y=yoff+75,width=100)
        self.range = tk.Label(self.master,text='Range')
        self.range.place(x=xoff+280,y=yoff+75)
        self.range_entry = tk.Entry(self.master)
        self.range_entry.place(x=xoff+330,y=yoff+75,width=50)
        self.km = tk.Label(self.master,text='km')
        self.km.place(x=xoff+380,y=yoff+75)
        self.show_map = tk.Button(self.master, text='Show Map', fg='black',bg='white',
                              command=self.show_map)
        self.show_map.place(x=xoff+445,y=yoff+70)
        self.pois = tk.Label(self.master,text='Point Of Interests Label')
        self.pois.place(x=xoff+50,y=yoff+110)
        self.menu_x=xoff+210
        self.menu_y=yoff+105
        self.list_x=xoff+50
        self.list_y=yoff+145
        self.addPoiMenuAndList()

    def addPoiMenuAndList(self):
        self.poi_menu_input = tk.StringVar(self.master)
        self.poi_menu_input.set(self.amenities[0])
        self.poi_menu = tk.OptionMenu(self.master,self.poi_menu_input,*tuple(self.amenities))
        self.poi_menu.place(x=self.menu_x,y=self.menu_y)
        self.poi_list_widgets = []
        cur_x = self.list_x
        cur_y = self.list_y
        colors = ['blue','orange','red']
        for i in range(len(self.amenities)):
            a = self.amenities[i]
            action = partial(self.removeAmenity,a)
            remove = tk.Button(self.master,command=action ,bg='white',fg='red',text='x')
            text = tk.Label(self.master,text=a)
            canvas = tk.Canvas(self.master)
            canvas.create_rectangle(0,0,20,20,fill=colors[i])
            remove.place(x=cur_x,y=cur_y,height=20,width=20)
            text.place(x=cur_x+22,y=cur_y)
            canvas.place(x=cur_x+22+len(a)*7.5,y=cur_y)
            cur_x+=22+len(a)*7.5+45
            self.poi_list_widgets.extend([remove,text,canvas])


    def refreshPoiMenuAndList(self):
        self.poi_menu.destroy()
        for w in self.poi_list_widgets:
            w.destroy()
        self.addPoiMenuAndList()

    def removeAmenity(self,amenity):
        self.amenities.remove(amenity)
        self.refreshPoiMenuAndList()

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
        add_app = AreaApp(add_area_root)
        add_app.mainloop()

root = tk.Tk()
app = Application(master=root)
app.mainloop()

class AreaApp(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.master = master
        self.master.geometry('500x200+100+100')
