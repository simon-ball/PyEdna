
import tkinter.ttk as ttk
import psutil
import os

class TTKTree(object):
    #https://pyinmyeye.blogspot.com/2012/07/tkinter-tree-demo.html
    def __init__(self, parent, frame):
        self.frame = frame
        self.parent = parent
        self.data_cols = ('fullpath', 'type', 'size')
        self.tree = ttk.Treeview(self.frame, columns=self.data_cols, displaycolumns='size')
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
                                      values=[cpath, 'directory'], tags=cpath)
                
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


    def select_folder(self, event):
        '''Selecting a directory within the file tree should have the same 
            effect as directly opening one via the load directory button'''
        curFocus = self.tree.focus()
        item = self.tree.item(curFocus)['values'][0]
        self.parent.folder = item
        self.parent.load_directory()
    
    def go_to_selected_folder(self, folder):
        # Automatically open the tree to the requested folder
        # Since the tree is populated lazily - i.e. as it is navigated,
        # the folder might not yet have been found
        # In that case, start at the root and go there
        # This function might be helpful
        # https://stackoverflow.com/questions/46176129/searching-in-treeview-and-highlight-select-the-row-that-contains-the-item-that-i
        found = self.tree.tag_has(folder) # either returns False or a list of items matching that tag
        if found:
            # Open that item and all its parents
            item = found[0]
            self.open_selected_folder(item)
        else:
            # TODO - this case doesn't work yet
            # Identify the largest fraction of the path that DOES exist in the tree: this will have dummy children
            # Startting at that largest path, open that node (triggering self._update_tree), and go ontwards from there
            '''
            #go to the beginning and work your way in
            # identify the closest folder known about, and work down the path from there
            head = os.path.split(folder)[0]
            tail = os.path.split(folder)[1]
            found = self.tree.tag_has(head)
            if not found:
                # Still haven't found a directory we've heard of -> step further back
                if not tail:
                    # We're at the root directory and still not found it
                    # We're lost, stop there
                    print("Folder not found")
                else:
                    self._populate_tree(found[0], head, os.listdir(head))
                    self.go_to_selected_folder(head)
            else:
                # We've found this directory, but not visited it ->  populate it
                self._populate_tree(found[0], folder, os.listdir(folder))
                self.go_to_selected_folder(folder)
            '''
            pass
                
        pass
    
    def open_selected_folder(self, item):
        # Open all the way to the item and select it
        # TODO: close everything else
        self.tree.item(item, open=True)
        self.tree.selection_set(item)
        while item:
            item = self.tree.parent(item)
            self.tree.item(item, open=True)
        pass