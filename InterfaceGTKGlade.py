#!/usr/bin/env python

import sys
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)
try:
    import cli
except:
    sys.exit(1)

class ItemPurchase(cli.Item):
        avaliableToBuy = 9
        quantityToBuy = 0

class VendingMachineGTK:

    def __init__(self):
		
        #Set the Glade file
        #self.gladefile = "InterfaceGTKGlade.glade"  
        #self.wTree = gtk.glade.XML(self.gladefile)
        
        #Get the Main Window, and connect the "destroy" event
        #self.window = self.wTree.get_widget("MainWindow")
        #if (self.window):
        #    self.window.connect("destroy", gtk.main_quit)
        #    #self.window.fullscreen()
        #    self.window.show()

        self.filename = "InterfaceGTKGlade.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.filename)
        self.window = self.builder.get_object("MainWindow")
        #self.window.fullscreen()
        dic = {
            "on_quantity_spinner_edited" : self.quantitySpinnerEdited,
            "on_start_button_clicked" : self.startButtonClicked,
            "on_page2_fwd_clicked" : self.page2FwdClicked,
            "on_page2_back_clicked" : self.page2BackClicked,
            "on_page3_back_clicked" : self.page3BackClicked,
            "on_page3_quit_clicked" : self.quit,
            "on_MainWindow_destroy" : self.quit,
        }
        self.builder.connect_signals(dic)


    def quantitySpinnerEdited(self, widget):
        print "quantitySpinnerEdited: ", widget
        
    def startButtonClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")
        self.initItemsView()
        notebook1.set_current_page(1)
        
        
    def page2FwdClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")
        notebook1.set_current_page(2)

    def page2BackClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")
        notebook1.set_current_page(0)

    def page3BackClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")
        self.initItemsView()
        notebook1.set_current_page(1)

    def quit(self, widget):
        print 'QUIT'
        sys.exit(0)

    def initItemsView(self):
        notebook1 = self.builder.get_object("notebook1")
        self.itemsTreeView = self.builder.get_object("items_tree_view")
        self.itemsListStore = self.builder.get_object("items_list_store")
        
        item1 = ItemPurchase(10, 5.00, 99, 'test10', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')
        item2 = ItemPurchase(11, 4.00, 99, 'test11', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')
        item3 = ItemPurchase(12, 2.00, 99, 'test12', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')

        self.itemsListStore.append([item1.info['name'], item1.info['cost'], item1.avaliableToBuy, item1.quantityToBuy])
        self.itemsListStore.append([item2.info['name'], item2.info['cost'], item2.avaliableToBuy, item2.quantityToBuy])
        self.itemsListStore.append([item3.info['name'], item3.info['cost'], item3.avaliableToBuy, item3.quantityToBuy])

##    def initItemsView(self):
##        self.itemsTreeView = self.builder.get_object("items_tree_view")
##        self.itemsListStore = self.builder.get_object("items_list_store")
##        self.itemsListStore.append([0,"zero"])
##        self.itemsListStore.append([1,"one"])
##        self.itemsListStore.append([2,"two"])
        
##        self.store = cli.Store()
##        items = cli.Item.listItems(self.store);
##        
##        for item in items:
##            itemValues = item.info.values()
##            itemInfo = itemValues[5]
##            itemLoc = itemInfo[0]
##            itemCost = itemInfo[1]
##            itemQty = itemInfo[2]
##            itemName = itemInfo[3]
##            itemLongName = itemInfo[4]
##            itemDesc = itemInfo[5]
##            itemsListStore.append([itemName,itemQty,0,0])
##            
##        self.store.con.close()
        
		

if __name__ == "__main__":

##    it = cli.Item(10, 5.00, 99, 'test10', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')
##    it.save()
##    it = cli.Item(11, 5.00, 99, 'test11', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')
##    it.save()
##    it = cli.Item(12, 5.00, 99, 'test12', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')
##    it.save()
##    it = cli.Item(13, 5.00, 99, 'test13', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')
##    it.save()
##    it = cli.Item(14, 5.00, 99, 'test14', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')
##    it.save()
##    it = cli.Item(15, 5.00, 99, 'test15', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')
##    it.save()
##
##    store = cli.Store()
##    items = cli.Item.listItems(store)
##    #store.con.close()
##
##    print 'Items: ', items

    
    hwg = VendingMachineGTK()
    hwg.window.show()
    gtk.main()
##    store.con.close()
