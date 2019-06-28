
import tkinter.ttk as ttk
import psutil
import os
import time
import pathlib

class TTKTree(object):
    #https://pyinmyeye.blogspot.com/2012/07/tkinter-tree-demo.html
    def __init__(self, parent, frame):
        self.frame = frame
        self.parent = parent
        self.data_cols = ('fullpath', 'type', 'size')
        self.tree = ttk.Treeview(self.frame, columns=self.data_cols, displaycolumns='size')
        self.items = []
        self._ui_elements()
        self._populate_root()
        
    def _ui_elements(self):
        ysb = ttk.Scrollbar(orient="vertical", command= self.tree.yview)
        xsb = ttk.Scrollbar(orient="horizontal", command= self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set
        
        # setup column headings
        self.tree.heading('#0', text='Directory Structure', anchor="w")
        self.tree.heading('size', text='File Size', anchor="w")
        self.tree.column('size', stretch=0, width=70)
        
        # add tree and scrollbars to frame
        self.tree.grid(in_=self.frame, row=1, column=0, sticky="nsew")
        ysb.grid(in_=self.frame, row=1, column=1, sticky="ns")
        xsb.grid(in_=self.frame, row=2, column=0, sticky="ew")
        
        # set frame resizing priorities
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        
        # action to perform when a node is expanded
        self.tree.bind('<<TreeviewOpen>>', self._update_tree)
        self.tree.bind('<<TreeviewSelect>>', self.select_folder)
        
    def _populate_root(self):
        # use all mountpoints as root nodes
        for dev in psutil.disk_partitions():
            path = dev.mountpoint
            path = pathlib.Path(path)
            parent = self.tree.insert('', 'end', text=path,
                                  values=[path, 'directory'], tags=path.parts)
            self.items.append(parent)
            self._populate_tree(parent, path)



    def _populate_tree(self, parent, fullpath):
        # parent   - id of node acting as parent
        # fullpath - the parent node's full path  as a Path object
        # children - list of files and sub-directories
        #            belonging to the 'parent' node
        children = os.listdir(fullpath)
        for child in children:
            # build child's fullpath
            #cpath = os.path.join(fullpath, child).replace('\\', '/')
            cpath = fullpath / child
    
            if cpath.is_dir():
                # directory - only populate when expanded
                # (see _create_treeview() 'bind')
                cid =self.tree.insert(parent, 'end', text=child,
                                      values=[cpath, 'directory'], tags=cpath.parts)
                
                # add 'dummy' child to force node as expandable
                self.tree.insert(cid, 'end', text='dummy') 
            else:
                # must be a 'file'
                try:
                    size = self._format_size(os.stat(cpath).st_size)
                except FileNotFoundError:
                    size = self._format_size(0)
                cid = self.tree.insert(parent, 'end', text=child,
                                 values=[cpath, 'file', size])
            self.items.append(cid)
                
   
    
    def _update_tree(self, event): #@UnusedVariable
        # user expanded a node - build the related directory 
        nodeId = self.tree.focus()      # the id of the expanded node
        
        if self.tree.parent(nodeId):    # not at root
            topChild = self.tree.get_children(nodeId)[0]
            
            # if the node only has a 'dummy' child, remove it and 
            # build new directory; skip if the node is already
            # populated
            if self.tree.item(topChild, option='text') == 'dummy':
                self.tree.delete(topChild)
                path = self.tree.set(nodeId, 'fullpath')
                path = pathlib.Path(path)
                self._populate_tree(nodeId, path)


    def select_folder(self, event):
        '''Selecting a directory within the file tree should have the same 
            effect as directly opening one via the load directory button'''
        curFocus = self.tree.focus()
        item = self.tree.item(curFocus)['values'][0]
        self.parent.folder = item
        self.parent.load_directory()
    
    def go_to_selected_folder(self, folder):
        '''
        Parameters
        ----------
        folder : pathlib.Path
        '''
        head = pathlib.Path(folder.parts[0], folder.parts[1])
        for item in self.items:
            try:
                path = pathlib.Path(self.tree.item(item)['values'][0])
                
                if path.samefile(folder):
                    self.tree.see(item)
                    self.tree.focus(item)
                    self.tree.selection_set(item)
                    self.tree.event_generate('<<TreeviewOpen>>', when="now")
                    break
                elif str(path) in str(folder):
                    # On the right track
                    self.tree.focus(item)
                    self.tree.event_generate('<<TreeviewOpen>>', when="now")
                else:
                    pass
            except Exception as e:
                pass
                

    
    def _format_size(self, size):
        KB = 1024.0
        MB = KB * KB
        GB = MB * KB
        if size >= GB:
            return '{:,.1f} GB'.format(size/GB)
        elif size >= MB:
            return '{:,.1f} MB'.format(size/MB)
        elif size >= KB:
            return '{:,.1f} KB'.format(size/KB)
        return '{} bytes'.format(size)
        