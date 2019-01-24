import tkinter as tk
from functools import partial
from copy import deepcopy 
from collections import defaultdict
import sc_loading
import sc_plot
import sc_lib

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry('800x1000+1100+20')
        self.amenity_options = ['school','theatre','hospital']
        self.label_options = deepcopy(self.amenity_options)
        self.label_to_nodes = defaultdict(list)
        self.labels = []
        self.vars = []
        self.label_to_color = dict()
        self.available_colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
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
        add_label = tk.Button(self.master,bg='black',command=self.add_label_action)
        add_label.place(x=xoff+55,y=yoff+10,width=20,height=20)
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
        labels = tk.Label(self.master,text='Point Of Interests Label')
        labels.place(x=xoff+50,y=yoff+120)
        self.menu_x=xoff+210
        self.menu_y=yoff+115
        self.label_list_x=xoff+50
        self.label_list_y=yoff+155
        self.add_label_menu_and_list()
        add_existing_label = tk.Button(self.master,text='+',fg='white',bg='green',command=self.add_existing_label)
        add_existing_label.place(x=self.menu_x+110,y=self.menu_y+5,width=20,height=20)
        add_loc_txt = tk.Label(self.master,text='Add a location')
        add_loc_txt.place(x=self.menu_x+150,y=self.menu_y+5)
        add_loc = tk.Button(self.master,text='+',fg='white',bg='green',command=self.add_loc_action)
        add_loc.place(x=self.menu_x+250,y=self.menu_y+5,width=20,height=20)
        
    def add_label_menu_and_list(self):
        self.label_menu_input = tk.StringVar(self.master)
        if len(self.label_options):
            self.label_menu_input.set(self.label_options[0])
            self.selected_label = self.label_options[0]
        else:
            self.label_menu_input.set('')
            self.selected_label = ''
        self.label_menu = tk.OptionMenu(self.master,self.label_menu_input,*tuple(self.label_options),command=self.update_selected_label)
        self.label_menu.place(x=self.menu_x,y=self.menu_y,width=105)
        self.label_list_widgets = []
        cur_x = self.label_list_x
        cur_y = self.label_list_y
        for i in range(len(self.labels)):
            a = self.labels[i]
            action = partial(self.remove_label,a)
            remove = tk.Button(self.master,command=action ,bg='white',fg='red',text='x')
            text = tk.Label(self.master,text=a)
            canvas = tk.Canvas(self.master)
            if a in self.label_to_color:
                color = self.label_to_color[a]
            else:
                color = self.available_colors.pop(0)
                self.label_to_color[a] = color
            hexFormat = '#%02x%02x%02x' % color
            canvas.create_rectangle(0,0,20,20,fill=hexFormat)
            remove.place(x=cur_x,y=cur_y,height=20,width=20)
            text.place(x=cur_x+22,y=cur_y)
            canvas.place(x=cur_x+22+len(a)*7.5,y=cur_y,height=20,width=20)
            cur_x+=22+len(a)*7.5+45
            self.label_list_widgets.extend([remove,text,canvas])

    def update_selected_label(self,value):
        self.selected_label = value

    def refresh_label_menu_and_list(self):
        self.label_menu.destroy()
        for w in self.label_list_widgets:
            w.destroy()
        self.add_label_menu_and_list()

    def remove_label(self,label):
        self.labels.remove(label)
        self.label_options.append(label)
        self.available_colors.append(self.label_to_color[label])
        self.label_to_color.pop(label,None)
        self.refresh_label_menu_and_list()

    def show_map(self):
        city_entered = self.city_entry.get()
        rang = float(self.range_entry.get())*1000
        graph = None
        amenities = [l for l in self.labels if l in self.amenity_options]
        if len(city_entered):
            graph = sc_loading.get_graph_city(city_entered.lower(),amenities,rang)
        else:
            pass
        if graph:
            for label in self.labels:
                for node in self.label_to_nodes[label]:
                    graph.add_node(node)
        sc_plot.plot(graph,self.label_to_color)
        self.city_entry.delete(0,'end')
        self.range_entry.delete(0,'end')
        self.coords_entry.delete(0,'end')

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
            remove = tk.Button(self.master,command=action,bg='white',fg='red',text='x')
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

    def add_existing_label(self):
        self.labels.append(self.selected_label)
        self.label_options.remove(self.selected_label)
        self.refresh_label_menu_and_list()

    def add_label_action(self):
        add_label_root = tk.Tk()
        add_app = AddLabelApp(add_label_root,self)
        add_app.mainloop()

    def add_loc_action(self):
        add_loc_root = tk.Tk()
        add_app = AddLocApp(add_loc_root,self)
        add_app.mainloop()

class AddLocApp(tk.Frame):
    def __init__(self,master,parent):
        super().__init__(master)
        self.master = master
        self.master.geometry('550x75+100+100')
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        add_label = tk.Label(self.master,text='Add new location to monitor')
        add_label.place(x=5,y=10)
        name_label = tk.Label(self.master,text='Name')
        name_label.place(x=5,y=35)
        self.name_entry = tk.Entry(self.master)
        self.name_entry.place(x=50,y=35,width=100)
        gps_label = tk.Label(self.master,text='GPS Coordinates')
        gps_label.place(x=160,y=35)
        self.gps_entry = tk.Entry(self.master)
        self.gps_entry.place(x=275,y=35,width=170)
        add_button = tk.Button(self.master,command=self.add,bg='white',fg='black',text='Add')
        add_button.place(x=460,y=35)

    def add(self):
        name = self.name_entry.get()
        coords = tuple([float(a) for a in self.gps_entry.get().split(',')])
        self.parent.labels.append(name)
        new_node = sc_lib.node(name,coords)
        new_node.data_node=False
        new_node.add_tag(name)
        self.parent.label_to_nodes[name].append(new_node)
        self.gps_entry.delete(0,'end')
        self.name_entry.delete(0,'end')
        self.parent.refresh_label_menu_and_list()

class AddLabelApp(tk.Frame):
    def __init__(self,master,parent):
        super().__init__(master)
        self.master = master
        self.master.geometry('625x125+100+100')
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        create_label = tk.Label(self.master,text='Add new location to existing label')
        create_label.place(x=5,y=10)
        label_label = tk.Label(self.master,text='Label')
        label_label.place(x=5,y=35)
        self.label_entry = tk.Entry(self.master)
        self.label_entry.place(x=50,y=35,width=100)
        name_label = tk.Label(self.master,text='Name')
        name_label.place(x=160,y=35)
        self.name_entry = tk.Entry(self.master)
        self.name_entry.place(x=205,y=35,width=100)
        gps_label = tk.Label(self.master,text='GPS Coordinates')
        gps_label.place(x=310,y=35)
        self.gps_entry = tk.Entry(self.master)
        self.gps_entry.place(x=425,y=35,width=170)
        or_label = tk.Label(self.master,text='OR')
        or_label.place(x=5,y=55)
        create_label = tk.Label(self.master,text='Create a new label')
        create_label.place(x=5,y=75)
        self.create_entry = tk.Entry(self.master)
        self.create_entry.place(x=150,y=75,width=100)
        add_button = tk.Button(self.master,command=self.add_to_map,bg='white',fg='black',text='Add to Map')
        add_button.place(x=350,y=70)
    
    def add_to_map(self):
        new_label = self.create_entry.get()
        if len(new_label):
            self.parent.labels.append(new_label)
            self.parent.refresh_label_menu_and_list()
            self.create_entry.delete(0,'end')
        else:
            label = self.label_entry.get()
            name = self.name_entry.get()
            coords = tuple([float(a) for a in self.gps_entry.get().split(',')])
            new_node = sc_lib.node(name,coords)
            new_node.data_node=False
            new_node.add_tag(label)
            self.parent.label_to_nodes[label].append(new_node)
            self.gps_entry.delete(0,'end')
            self.label_entry.delete(0,'end')
            self.name_entry.delete(0,'end')

root = tk.Tk()
app = Application(master=root)
app.mainloop()

