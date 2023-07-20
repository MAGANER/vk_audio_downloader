from tkinter import *
from tkinter import messagebox
from audio_downloader import *
import tkinter.filedialog as fd
import db
from create_album_dict import *

class Window:

    def __init_window(self,geometry,title):
        window = Tk()
        window.title(title)
        window.geometry(geometry)

        window.resizable(0,0)

        frame = Frame(window)
        frame.pack(expand=True)
        return window, frame
    
    def __init__(self):
        self.session = None
        self.window, self.frame = self.__init_window("480x300","Vk audio downloader: auth")
        self.font = lambda s:("Courier", s)

        self.mdb = None
        self.all_selected = False
        
    def run_enter_menu(self,get_session):
        login = Label(self.frame,text="login:",font=self.font(20))
        login.grid(row=3, column=1)

        password = Label(self.frame,text="password:",font=self.font(20))
        password.grid(row=4, column=1)

        enter_login = Entry(self.frame,width=30,show="*",font=self.font(12))
        enter_login.grid(row=3,column=2)
        enter_login.focus()

        enter_password = Entry(self.frame,width=30,show="*",font=self.font(12))
        enter_password.grid(row=4,column=2)
   
        enter_btn = Button(self.frame,text='enter',width=20,command=lambda: self.try_to_enter(enter_login,enter_password,get_session,self.window))
        enter_btn.grid(row=5, column=2)

        self.window.bind("<Return>",lambda event: self.try_to_enter(enter_login,enter_password,get_session,self.window) )
        self.window.bind("<Up>",lambda event: enter_login.focus())
        self.window.bind("<Down>",lambda event: enter_password.focus())
        
        self.window.mainloop()

        return self.session

    
    def try_to_enter(self,enter_login,enter_password,get_session, window):
        login = enter_login.get()
        password = enter_password.get()

        def break_function(error_message):
            messagebox.showinfo("error!",error_message)
            
        self.session = get_session(login,password,break_function)
        
        if not self.session is None:
            window.destroy()

    def __compute_window_geometry(self,width,height):
        root = Tk()
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws/2) - width/2
        y = (hs/2) - height/2
        root.destroy()
        return "{}x{}+{}+{}".format(width,height,int(x),int(y))
    
    def run_main_menu(self,functions_table,mdb,vk_audio):
        self.window, self.frame = self.__init_window(self.__compute_window_geometry(230,220),"Vk audio downloader: main menu")
        self.session = vk_audio
        self.mdb = mdb
        
        scan_btn = Button(self.frame,text='scan',width=20,command = lambda: self.__run_scan_submenu(functions_table["scan"]))
        scan_btn.grid(row=2,column=2)
        
        find_btn = Button(self.frame,text='find',width=20,command= lambda: self.find(functions_table["find"]))
        find_btn.grid(row=3,column=2)
        
        get_btn = Button(self.frame,text='get',width=20, command = lambda:self.__run_get_submenu(functions_table["get"]))
        get_btn.grid(row=4,column=2)      
    
        self.window.mainloop()
        
    def __setActive(self,window):
        window.lift()
        window.focus_force()
        window.grab_set()
        window.grab_release()
        
    def find(self,find_function):
        window,frame = self.__init_window(self.__compute_window_geometry(330,250),"Vk audio downloader: find")
        self.__setActive(window)

        search_entry = Entry(frame,width=15,font=self.font(10))
        search_entry.grid(row=1,column=2)

        search_label = Label(frame,text="search substring:",font=self.font(10))
        search_label.grid(row=1,column=1)

        target_val = BooleanVar()
        target_val.set(True)

        target_label = Label(frame,text="search what:",font=self.font(10))
        target_label.grid(row=2,column=1)
        
        target_artist = Radiobutton(frame,text="artist",variable=target_val,value=True,command=lambda:target_val.set(True))
        target_artist.grid(row=2,column=2)

        target_track = Radiobutton(frame,text="track",variable=target_val,value=False,command=lambda:target_val.set(False))
        target_track.grid(row=2,column=3)

        conv_target = lambda: "artist" if bool(target_val.get()) else "track"

        place_val = BooleanVar()
        place_val.set(True)
        
        place_label = Label(frame,text="search where:",font=self.font(10))
        place_label.grid(row=3,column=1)

        place_albums = Radiobutton(frame,text="albums",variable=place_val,value=True,command=lambda:place_val.set(True))
        place_albums.grid(row=3,column=2)

        place_tracks = Radiobutton(frame,text="tracks",variable=place_val,value=False,command=lambda:place_val.set(False))
        place_tracks.grid(row=3,column=3)

        conv_place = lambda: "albums" if bool(place_val.get()) else "tracks"

        def execute_find():
            arguments = ['"'+search_entry.get()+'"',conv_target(),0,conv_place()]
            return find_function(arguments,self.mdb,self.session,False)
                
        find_btn = Button(frame,text="find",command = lambda:self.__show_items(execute_find(),conv_place()))
        find_btn.grid(row=4,column=2,pady=10)
        
        window.mainloop()
        
    def __fill_listbox(self,listbox,items):
        for i, item in enumerate(items):
            listbox.insert(i,item)
    def select_all(self,listbox):
        if self.all_selected:
            listbox.selection_clear(0,END)
            self.all_selected = False
        else:
            listbox.selection_set(0,END)
            self.all_selected = True
    
    def __show_album_items(self, albums,album_number):
        if not album_number is None:
            window = Tk()
            window.geometry(self.__compute_window_geometry(560,540))
            window.resizable(0,0)
            self.__setActive(window)
        
            n = tuple(albums.keys())[album_number]
            window.title(n)
        
            data = albums[n]
            items, downloading_data = [],[]
            for name, band, link in data:
                file_name = band+" "+name
                items.append(file_name)
                downloading_data.append((link,file_name))

            tracks = Listbox(window,selectmode=MULTIPLE)
            self.__fill_listbox(tracks,items)
            tracks.place(x=0,y=0,width=560,height=400)

            select_all_btn = Button(window,text="select all",command = lambda:self.select_all(tracks))
            select_all_btn.place(x=200,y=405)

            download_selected_btn = Button(window,text="download selected",command=lambda:self.download(self.prepare_downloading_data(tracks,downloading_data)))
            download_selected_btn.place(x=280,y=405)
            
        
            window.mainloop()
    def __show_items(self,get_function,title):
        #some kind of brute force, but it's required
        #because i can not place list box like i want using __init_window function
        window = Tk()
        window.title(title)
        window.geometry(self.__compute_window_geometry(560,540))
        window.resizable(0,0)
        self.__setActive(window)

            
        items = get_function([title],self.mdb,self.session,non_stop=True) if callable(get_function) else get_function
        if not callable(get_function) and title == "albums":
            items = cad(items)
        downloading_data = []
        if title == "tracks":
            downloading_data = [(link,band+"-"+name,album) for band,name,link, album in items]
            items = [band + ":"+name for band,name, _,_ in items]
        
        listbox = Listbox(window,selectmode=MULTIPLE) if title == "tracks" else Listbox(window)
        self.__fill_listbox(listbox,items)
        listbox.place(x=0,y=0,width=560,height=400)

        if title == "albums":
            def get_album_number():
                n = listbox.curselection()
                if n: return n[0]
                else: return None
            listbox.bind("<<ListboxSelect>>",lambda event:self.__show_album_items(items,get_album_number()))
            
                
        #if user's decision is to check albums, then he click on album and then choose which element of album he wants
        #to download
        if title == "tracks":
            download_selected_btn = Button(window,text="download selected",command=lambda:self.download(self.prepare_downloading_data(listbox,downloading_data)))
            download_selected_btn.place(x=220,y=410)
        
        window.mainloop()

    def prepare_downloading_data(self,listbox,downloading_data):
        return [downloading_data[i] for i in listbox.curselection()]
    def download(self,items):
        directory = fd.askdirectory(title="open folder:", initialdir="/")
        if directory:
            for link,name, album in items:
                meta_data = {}
                band, _name = name.split("-")
                album = "" if album == "none" else album
                meta_data["artist"] = band
                meta_data["title"] = _name
                meta_data["album"] = album
                download_m3u8(link,directory+"/"+name+".mp3",meta_data)
            messagebox.showinfo("downloading complete!","tracks are downloaded and can be found at {}".format(directory))
        
    def __run_get_submenu(self,get_function):
        window, frame = self.__init_window(self.__compute_window_geometry(230,220),"vk audio downloader: get menu")
        self.__setActive(window)
        
        get_tracks_btn = Button(frame,text="get tracks",width=20,command= lambda:self.__show_items(get_function,"tracks"))
        get_tracks_btn.grid(row=2,column=2)
        
        get_albums_btn = Button(frame,text="get albums",width=20,command= lambda:self.__show_items(get_function,"albums"))
        get_albums_btn.grid(row=3,column=2)

        
        window.mainloop()
        
    def __run_scan_submenu(self,scan_function):
        window, frame = self.__init_window(self.__compute_window_geometry(230,220),"vk audio downloader: scan menu")
        self.__setActive(window)
        
        r_val = BooleanVar()
        r_val.set(False)
        
        scan_albums_r_btn = Radiobutton(frame,text="albums",variable=r_val,value=True, command=lambda:r_val.set(True))
        scan_albums_r_btn.grid(row=2,column=2)
        
        scan_tracks_r_btn = Radiobutton(frame,text="tracks",variable=r_val,value=False,command=lambda:r_val.set(False))
        scan_tracks_r_btn.grid(row=2,column=3)
        
        scan_range_label = Label(frame,text="scan range",font=self.font(10))
        scan_range_label.grid(row=3,column=1)
        
        begin = Entry(frame,width=5,font=self.font(10))
        begin.focus()
        begin.grid(row=3,column=2)

        end = Entry(frame,width=5,font=self.font(10))
        end.grid(row=3,column=3)


        def __scan():
            if begin.get() == "" or end.get() == "":
                messagebox.showinfo("error!","you should enter scaning range first!")
            else:
                target =   "albums" if bool(r_val.get()) else "tracks"
                rng = begin.get()+","+end.get()
                scan_function([rng,target],self.mdb,self.session)
                
                messagebox.showinfo("complete task","scaning of {} is finished!".format(target))


        scan_btn = Button(frame,text='scan',width=10, command=__scan)
        scan_btn.grid(row=6,column=1)

        window.bind("<Return>",lambda event: __scan())
        window.bind("<Left>",lambda event: begin.focus())
        window.bind("<Right>",lambda event: end.focus())
        
        window.mainloop()

        
        

