import tkinter as tk
from functools import partial
import sc_loading
import sc_plot

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry('800x1000+1100+20')
        self.amenities = ['school','theatre','hospital']
        self.vars = []
        self.amenitiesToColor = dict()
        self.availableColors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255)]
        self.create_widgets()
        
    def create_widgets(self):
        self.create_area_input(0,0)
        self.create_data_input(0,210)

    def create_data_input(self,xoff,yoff):
        data=tk.Label(self.master,text='Data')
        data.place(x=xoff+10,y=yoff+10)
        var = tk.Label(self.master,text='Variable')
        var.place(x=xoff+85,y=yoff+35)
        self.var_entry = tk.Entry(self.master)
        self.var_entry.place(x=xoff+150,y=yoff+35,width=75)
        path = tk.Label(self.master,text='Path')
        path.place(x=xoff+250,y=yoff+35)
        self.path_entry = tk.Entry(self.master)
        self.path_entry.place(x=xoff+300,y=yoff+35,width=100)
        add_var = tk.Button(self.master, text='+', fg='white',bg='green',
                              command=self.add_var)
        add_var.place(x=xoff+410,y=yoff+35,width=20,height=20)
        self.var_list_x = xoff+90
        self.var_list_y = yoff+55
        self.add_var_list()

    def create_area_input(self,xoff,yoff):
        areas = tk.Label(self.master,text='Areas')
        areas.place(x=xoff+10,y=yoff+10)
        add_area = tk.Button(self.master,bg='black',command=self.add_area_action)
        add_area.place(x=xoff+55,y=yoff+10,width=20,height=20)
        clear = tk.Button(self.master, text='Clear', fg='white',bg='gray',
                              command=self.clear_action)
        clear.place(x=xoff+350,y=yoff+10)
        start = tk.Button(self.master, text='Start the monitor', fg='white',bg='green',
                              command=self.start_action)
        start.place(x=xoff+425,y=yoff+10)
        city_name = tk.Label(self.master,text='City Name')
        city_name.place(x=xoff+85,y=yoff+45)
        self.city_entry = tk.Entry(self.master)
        self.city_entry.place(x=xoff+170,y=yoff+45,width=100)
        OR = tk.Label(self.master,text='OR')
        OR.place(x=xoff+60,y=yoff+65)
        coords = tk.Label(self.master,text='Coordinates')
        coords.place(x=xoff+85,y=yoff+85)
        self.coords_entry = tk.Entry(self.master)
        self.coords_entry.place(x=xoff+170,y=yoff+85,width=100)
        rangel = tk.Label(self.master,text='Range')
        rangel.place(x=xoff+280,y=yoff+65)
        self.range_entry = tk.Entry(self.master)
        self.range_entry.place(x=xoff+330,y=yoff+65,width=50)
        km = tk.Label(self.master,text='km')
        km.place(x=xoff+380,y=yoff+65)
        show_map = tk.Button(self.master, text='Show Map', fg='black',bg='white',
                              command=self.show_map)
        show_map.place(x=xoff+410,y=yoff+60)
        pois = tk.Label(self.master,text='Point Of Interests Label')
        pois.place(x=xoff+50,y=yoff+120)
        self.menu_x=xoff+210
        self.menu_y=yoff+115
        self.poi_list_x=xoff+50
        self.poi_list_y=yoff+155
        self.add_poi_menu_and_list()
        add_label = tk.Button(self.master,text='+',fg='white',bg='green',command=self.add_label_action)
        add_label.place(x=self.menu_x+90,y=self.menu_y+5,width=20,height=20)
        add_loc_txt = tk.Label(self.master,text='Add a location')
        add_loc_txt.place(x=self.menu_x+130,y=self.menu_y+5)
        add_loc = tk.Button(self.master,text='+',fg='white',bg='green',command=self.add_loc_action)
        add_loc.place(x=self.menu_x+230,y=self.menu_y+5,width=20,height=20)
        
    def add_poi_menu_and_list(self):
        self.poi_menu_input = tk.StringVar(self.master)
        if len(self.amenities):
            self.poi_menu_input.set(self.amenities[0])
        else:
            self.poi_menu_input.set('')
        self.poi_menu = tk.OptionMenu(self.master,self.poi_menu_input,*tuple(self.amenities))
        self.poi_menu.place(x=self.menu_x,y=self.menu_y)
        self.poi_list_widgets = []
        cur_x = self.poi_list_x
        cur_y = self.poi_list_y
        for i in range(len(self.amenities)):
            a = self.amenities[i]
            action = partial(self.remove_amenity,a)
            remove = tk.Button(self.master,command=action ,bg='white',fg='red',text='x')
            text = tk.Label(self.master,text=a)
            canvas = tk.Canvas(self.master)
            if a in self.amenitiesToColor:
                color = self.amenitiesToColor[a]
            else:
                color = self.availableColors.pop(0)
                self.amenitiesToColor[a] = color
            hexFormat = '#%02x%02x%02x' % color
            canvas.create_rectangle(0,0,20,20,fill=hexFormat)
            remove.place(x=cur_x,y=cur_y,height=20,width=20)
            text.place(x=cur_x+22,y=cur_y)
            canvas.place(x=cur_x+22+len(a)*7.5,y=cur_y)
            cur_x+=22+len(a)*7.5+45
            self.poi_list_widgets.extend([remove,text,canvas])

    def refresh_poi_menu_and_list(self):
        self.poi_menu.destroy()
        for w in self.poi_list_widgets:
            w.destroy()
        self.add_poi_menu_and_list()

    def remove_amenity(self,amenity):
        self.amenities.remove(amenity)
        self.availableColors.append(self.amenitiesToColor[amenity])
        self.amenitiesToColor.pop(amenity,None)
        self.refresh_poi_menu_and_list()

    def show_map(self):
        city_entered = self.city_entry.get()
        rang = int(self.range_entry.get())*1000
        if len(city_entered):
            graph = sc_loading.get_graph_city(city_entered.lower(),self.amenities,rang)
            sc_plot.plot(graph,self.amenitiesToColor)
        else:
            pass
        self.city_entry.delete(0,'end')

    def start_action(self):
        print('start') 

    def clear_action(self):
        print('clear')
    
    def add_var_list(self):
        self.var_list_widgets = []
        cur_x = self.var_list_x
        cur_y = self.var_list_y
        for i in range(len(self.vars)):
            v = self.vars[i]
            action = partial(self.remove_var,v)
            remove = tk.Button(self.master,command=action ,bg='white',fg='red',text='x')
            text = tk.Label(self.master,text=v)
            remove.place(x=cur_x,y=cur_y,height=20,width=20)
            text.place(x=cur_x+22,y=cur_y)
            cur_x+=22+len(v)*7.5+25
            self.var_list_widgets.extend([remove,text])

    def refresh_var_list(self):
        for w in self.var_list_widgets:
            w.destroy()
        self.add_var_list()

    def remove_var(self,var):
        self.vars.remove(var)
        self.refresh_var_list()

    def add_var(self):
        self.vars.append(self.var_entry.get()) 
        self.var_entry.delete(0,'end')
        self.refresh_var_list()

    def add_area_action(self):
        add_area_root = tk.Tk()
        add_app = AreaApp(add_area_root)
        add_app.mainloop()
        
    def add_label_action(self):
        add_label_root = tk.Tk()
        add_app = AddLabelApp(add_label_root)
        add_app.mainloop()

    def add_loc_action(self):
        add_loc_root = tk.Tk()
        add_app = AddLocApp(add_loc_root)
        add_app.mainloop()

class AreaApp(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.master = master
        self.master.geometry('500x200+100+100')

class AddLabelApp(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.master = master
        self.master.geometry('500x200+100+100')
        
class AddLocApp(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.master = master
        self.master.geometry('500x200+100+100')

root = tk.Tk()
app = Application(master=root)
app.mainloop()

