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

    MODEL_NAME      = 0
    MODEL_PRICE     = 1
    MODEL_AVAILABLE = 2
    MODEL_QUANTITY  = 3
    MODEL_INVENTORY = 4
    MODEL_LOC       = 5

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
            "on_MainWindow_destroy" : self.quit,
            "on_increment_button_clicked" : self.incrementButtonClicked,
            "on_decrement_button_clicked" : self.decrementButtonClicked,
            "on_quit_button_clicked" : self.quitButtonClicked,
            "on_page3_quit_clicked" : self.purchaseClicked,
            "on_purchase_button_clicked" : self.purchaseClicked

        }
        self.builder.connect_signals(dic)

        # We just init on applicaiton start - and maybe when the user wants to totally empty the cart
        self.initItemsView()

    def wait_for_tag_to_start(self, widget):
        '''
        This function polls the RFID reader continuously until a uid is
        obtained. If the uid is a verified EHC member then the user may
        proceed. Otherwise, an error screen should be displayed.
        '''
        reader = machine.TagReader()
        uid = reader.get()
        user = User(uid)    # also called User._verify()
        if user.verified==1:
            # go to the next screen
            notebook1 = self.builder.get_object("notebook1")
            notebook1.set_current_page(1)
        else:
            # go to an error screen
            self.initItemsView()
            notebook1.set_current_page(0)  # todo: set the right page (not 0)
        return

    def purchaseClicked(self, widget):
        '''
        This function is called when the user clicks the 'complete purchase'
        button. It uses the public methods from machine.py to instantiate a
        Store.Purchase() object, populate its cart, and then complete all the
        database, object, and hardware calls associated with vending the items.
        '''

        # Interface magic
        notebook1 = self.builder.get_object("notebook1")
        #notebook1.set_current_page(0)

        # Initialize interface
        purch = machine.Purchase(us.uid)

        # Build the cart
        for list_item in self.itemsListStore:
            if list_item[self.MODEL_QUANTITY]!=0:
                purch.add_to_cart(list_item[self.MODEL_LOC],
                                  list_item[self.MODEL_QUANTITY])

        # Vend the Purchase
        purch.vend()
        self.initItemsView()
        notebook1.set_current_page(0)
        return

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
        self.initItemsView()
        notebook1.set_current_page(0)

    def page3BackClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")
        notebook1.set_current_page(1)

    def quitButtonClicked(self, widget):
        notebook1 = self.builder.get_object("notebook1")


##        for listItem in self.itemsListStore:
##            if listItem[MODEL_QUANTITY] > 0:
##                #print (listItem[0],listItem[1],listItem[2],listItem[3],listItem[4])
##                listItem[MODEL_QUANTITY] = 0
##                listItem[MODEL_AVAILABLE] = listItem[MODEL_INVENTORY]
        self.initItemsView()
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
        #print (self.itemsListStore)

        checkoutView = self.builder.get_object("checkoutView")
        self.currentCostLabel2 = self.builder.get_object("current_cost_label2")
        self.currentCostLabel2.set_label(('Current Cost: $%0.2f' % self.currentCost()))
        finalString = ''
        for listItem in self.itemsListStore:
            if listItem[3] != 0:
            #print (listItem[0],listItem[1],listItem[2],listItem[3])
                #print ('Item:', listItem[0], 'PPU:', listItem[1], 'Quantity:', listItem[3])
                outputString = 'Item:\t', str(listItem[0]), '\t PPU:\t', str(listItem[1]), '\tQuantity:\t', str(listItem[3])
                finalString = finalString + ''.join( outputString )
                finalString = finalString + ''.join('\n')
        checkoutView.get_buffer().set_text(finalString)

    def initItemsView(self):
        self.itemsTreeView = self.builder.get_object("items_tree_view")
        self.itemsListStore = self.builder.get_object("items_list_store")
        self.currentCostLabel = self.builder.get_object("current_cost_label")

        self.store = machine.Store()
        items = machine.Item.listItems(self.store);

        self.itemsListStore.clear()
        for item in items:
            #print item.info.values()

            itemValues = item.info.values()
            itemInfo = itemValues[5]
            itemLoc = itemInfo[0]
            itemCost = itemInfo[1]
            itemQty = itemInfo[2]
            itemName = itemInfo[3]
            itemLongName = itemInfo[4]
            itemDesc = itemInfo[5]
            self.itemsListStore.append([itemName, itemCost, itemQty, 0, itemQty, itemLoc])

        self.itemsTreeView.get_selection().select_path(0)
        self.currentCostLabel.set_label(('Current Cost: $%0.2f' % 0))


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

    us = machine.User(123456789, 'Zachary')
##    us.save()
##    us.verify()

    hwg = VendingMachineGTK()
    hwg.window.show()
    gtk.main()

