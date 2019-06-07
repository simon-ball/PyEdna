
import tkinter.ttk as ttk
import psutil
import os

class TTKTree(object):
    #https://pyinmyeye.blogspot.com/2012/07/tkinter-tree-demo.html
    def __init__(self, parent):
        self.parent = parent
        self.data_cols = ('fullpath', 'type', 'size')
        self.tree = ttk.Treeview(parent, columns=self.data_cols, displaycolumns='size')
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
        self.tree.grid(in_=self.parent, row=1, column=0, sticky="nsew")
        ysb.grid(in_=self.parent, row=1, column=1, sticky="ns")
        xsb.grid(in_=self.parent, row=2, column=0, sticky="ew")
        
        # set frame resizing priorities
        self.parent.rowconfigure(1, weight=1)
        self.parent.columnconfigure(0, weight=1)
        
        # action to perform when a node is expanded
        self.tree.bind('<<TreeviewOpen>>', self._update_tree)
        
    def _populate_root(self):
        # use all mountpoints as root nodes
        for dev in psutil.disk_partitions():
            path = dev.mountpoint
            parent = self.tree.insert('', 'end', text=path,
                                  values=[path, 'directory'])
            self._populate_tree(parent, path, os.listdir(path))

        
    def _populate_tree(self, parent, fullpath, children):
        # parent   - id of node acting as parent
        # fullpath - the parent node's full path 
        # children - list of files and sub-directories
        #            belonging to the 'parent' node
        
        for child in children:
            # build child's fullpath
            cpath = os.path.join(fullpath, child).replace('\\', '/')
    
            if os.path.isdir(cpath):
                # directory - only populate when expanded
                # (see _create_treeview() 'bind')
                cid =self.tree.insert(parent, 'end', text=child,
                                      values=[cpath, 'directory'])
                
                # add 'dummy' child to force node as expandable
                self.tree.insert(cid, 'end', text='dummy')  
            else:
                # must be a 'file'
                size = self._format_size(os.stat(cpath).st_size)
                self.tree.insert(parent, 'end', text=child,
                                 values=[cpath, 'file', size])
                
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
                self._populate_tree(nodeId, path, os.listdir(path))


        