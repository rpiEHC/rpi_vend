#!/usr/bin/env python

import sys, string
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
    import machine
except:
    sys.exit(1)

class VendingMachineGTK:

    MODEL_NAME = 0
    MODEL_PRICE = 1
    MODEL_AVAILABLE = 2
    MODEL_QUANTITY = 3
    MODEL_INVENTORY = 4

    def __init__(self):
		
        self.filename = "InterfaceGTKGlade.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.filename)
        self.window = self.builder.get_object("MainWindow")
        #self.window.fullscreen()
        dic = {
            #"on_quantity_spinner_edited" : self.quantitySpinnerEdited,
            "on_start_button_clicked" : self.startButtonClicked,
            "on_page2_fwd_clicked" : self.page2FwdClicked,
            "on_page2_back_clicked" : self.page2BackClicked,
            "on_page3_back_clicked" : self.page3BackClicked,
            "on_page3_quit_clicked" : self.quit,
            "on_MainWindow_destroy" : self.quit,
            "on_increment_button_clicked" : self.incrementButtonClicked,
            "on_decrement_button_clicked" : self.decrementButtonClicked,
            "on_quit_button_clicked" : self.quitButtonClicked
            
        }
        self.builder.connect_signals(dic)

        # We just init on app licaiton start - and maybe when the user wants to totally empty the cart
        self.initItemsView()

    def incrementButtonClicked(self, widget):
        treeView = self.builder.get_object("items_tree_view")
        (model, path) = treeView.get_selection().get_selected()
        if self.itemsListStore[path][self.MODEL_AVAILABLE] > 0:
            self.itemsListStore[path][self.MODEL_QUANTITY] = self.itemsListStore[path][self.MODEL_QUANTITY] + 1   
            self.itemsListStore[path][self.MODEL_AVAILABLE] = self.itemsListStore[path][self.MODEL_INVENTORY] - self.itemsListStore[path][self.MODEL_QUANTITY]
            self.currentCostLabel = self.builder.get_object("current_cost_label")
            #print self.currentCostLabel.get_label()
            self.mytext = ('Current Cost: $%0.00f' % self.currentCost())
            #print self.mytext
            self.currentCostLabel.set_label(('Current Cost: $%0.2f' % self.currentCost()))

    def decrementButtonClicked(self, widget):
        treeView = self.builder.get_object("items_tree_view")
        (model, path) = treeView.get_selection().get_selected()
        if self.itemsListStore[path][self.MODEL_QUANTITY] > 0:
            self.itemsListStore[path][self.MODEL_QUANTITY] = self.itemsListStore[path][self.MODEL_QUANTITY] - 1   
            self.itemsListStore[path][self.MODEL_AVAILABLE] = self.itemsListStore[path][self.MODEL_INVENTORY] - self.itemsListStore[path][self.MODEL_QUANTITY]
            self.currentCostLabel = self.builder.get_object("current_cost_label")
            #print self.currentCostLabel.get_label()
            self.mytext = ('Current Cost: $%0.00f' % self.currentCost())
            #print self.mytext
            self.currentCostLabel.set_label(('Current Cost: $%0.2f' % self.currentCost()))
        
    def startButtonClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")
        notebook1.set_current_page(1)
        
    def page2FwdClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")
        self.initCheckoutView()
        notebook1.set_current_page(2)

    def page2BackClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")
        notebook1.set_current_page(0)

    def page3BackClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")
        notebook1.set_current_page(1)

    def quitButtonClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")

        for listItem in self.itemsListStore:
            if listItem[3] > 0:
                print (listItem[0],listItem[1],listItem[2],listItem[3],listItem[4])
                listItem[3] = 0
                listItem[2] = listItem[4]
        notebook1.set_current_page(0)

    def quit(self, widget):
        print 'QUIT'
        sys.exit(0)

    def currentCost(self):
        cost = 0.00
        for listItem in self.itemsListStore:
            cost = cost + (listItem[self.MODEL_PRICE] * listItem[self.MODEL_QUANTITY])
        return cost

    def initCheckoutView(self):
        print (self.itemsListStore)
        
        checkoutView = self.builder.get_object("checkoutView")
        self.currentCostLabel2 = self.builder.get_object("current_cost_label2")
        self.currentCostLabel2.set_label(('Current Cost: $%0.2f' % self.currentCost()))
        finalString = ''
        for listItem in self.itemsListStore:
            if listItem[3] != 0:
            #print (listItem[0],listItem[1],listItem[2],listItem[3])
                print ('Item:', listItem[0], 'PPU:', listItem[1], 'Quantity:', listItem[3])
                outputString = 'Item:\t', str(listItem[0]), '\t PPU:\t', str(listItem[1]), '\tQuantity:\t', str(listItem[3])
                finalString = finalString + ''.join( outputString )
                finalString = finalString + ''.join('\n') 
        checkoutView.get_buffer().set_text(finalString)

    #def initItemsView(self):
        #notebook1 = self.builder.get_object("notebook1")
        #self.itemsTreeView = self.builder.get_object("items_tree_view")
        
        #item1 = machine.Item(10, 5.00, 100, 'test10', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')
        #item2 = machine.Item(11, 4.00, 34, 'test11', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')
        #item3 = machine.Item(12, 2.00, 66, 'test12', 'long name', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam porttitor faucibus tempus. Nullam neque leo, ultricies sit amet rutrum quis, interdum et metus. In ac risus sapien, sed vestibulum felis. Maecenas luctus semper rutrum. In eget adipiscing mauris. Pellentesque ultricies mattis nunc eu luctus. In eget nisi neque. Ut sit amet dapibus mauris. Donec vel nulla nunc, non lacinia lacus. Pellentesque ac sapien lacinia arcu cursus dignissim. Suspendisse ut sapien sit amet.')

        #
        # For each item we set
        # Name, cost, available count, quantity to purchase, and inventory amount
        # Since this is init and called at the beginning of a session - all quantitues are 0 and available = inventory
        # As items are set to be purchased - available count + quantity to purchase = inventory amount
        # inventory ampount is for processing convenience and not displayed in a column
        #
        #self.itemsListStore = self.builder.get_object("items_list_store")
        
        #self.itemsListStore.append([item1.info['name'], item1.info['cost'], item1.info['qty'], 0, item1.info['qty']])
        #self.itemsListStore.append([item2.info['name'], item2.info['cost'], item2.info['qty'], 0, item2.info['qty']])
        #self.itemsListStore.append([item3.info['name'], item3.info['cost'], item3.info['qty'], 0, item3.info['qty']])

    def initItemsView(self):
        self.itemsTreeView = self.builder.get_object("items_tree_view")
        self.itemsListStore = self.builder.get_object("items_list_store")
        
        
        self.store = machine.Store()
        items = machine.Store.listItems(self.store);
        
        for item in items:
            itemValues = item.info.values()
            itemInfo = itemValues[5]
            itemLoc = itemInfo[0]
            itemCost = itemInfo[1]
            itemQty = itemInfo[2]
            itemName = itemInfo[3]
            itemLongName = itemInfo[4]
            itemDesc = itemInfo[5]
            self.itemsListStore.append([itemName, itemCost, itemQty, 0, itemQty])
            
        #self.store.con.close()
        
		

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
