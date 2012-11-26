#!/usr/bin/env python

# example buttonbox.py

import pygtk
pygtk.require('2.0')
import gtk

class startWindow:
    # Create a Button Box with the specified parameters
    def create_bbox(self, horizontal, spacing, layout):
        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_NONE)

        if horizontal:
            bbox = gtk.HButtonBox()
        else:
            bbox = gtk.VButtonBox()

        bbox.set_border_width(5)
        frame.add(bbox)

        # Set the appearance of the Button Box
        bbox.set_layout(layout)
        bbox.set_spacing(spacing)

        button = gtk.Button(stock=gtk.STOCK_YES)
        button.set_size_request(100,70)
        bbox.add(button)

        #button = gtk.Button(stock=gtk.STOCK_CANCEL)
        #bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_NO)
        button.set_size_request(100,70)
        bbox.add(button)

        return frame

    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_size_request(640,480)

        window.connect("destroy", lambda x: gtk.main_quit())

        window.set_border_width(10)

        main_vbox = gtk.VBox(False, 0)
        window.add(main_vbox)


## warning messages or error messages here
        
        frame_horzTop = gtk.Frame()
        frame_horzTop.set_shadow_type(gtk.SHADOW_IN)
        main_vbox.pack_start(frame_horzTop, False, False, 10)

        testBox = gtk.VBox(False, 10)
        testBox.set_border_width(10)
        frame_horzTop.add(testBox)
        
        title = gtk.Label("Welcome to the EHC vending machine")
        testBox.pack_start(title, 0,0)

        title2 = gtk.Label("Please follow the prompts on screen to purchase your items")
        testBox.pack_start(title2, 0,0)


##Changes with button press

    
        frame_horzBot = gtk.Frame()
        frame_horzBot.set_shadow_type(gtk.SHADOW_IN)
        main_vbox.pack_start(frame_horzBot, True, True, 0)

        vbox = gtk.VBox(False, 0)
        vbox.set_border_width(0)
        frame_horzBot.add(vbox)

        title3 = gtk.Label("Are you currently a EHC member?")
        vbox.pack_start(title3, 40, 40)

        vbox.pack_start(self.create_bbox(True, 40, gtk.BUTTONBOX_SPREAD), True, True, 0)


##        frame_vert = gtk.Frame("Vertical Button Boxes")
##        main_vbox.pack_start(frame_vert, True, True, 10)
##
##        hbox = gtk.HBox(False, 0)
##        hbox.set_border_width(10)
##        frame_vert.add(hbox)
##
##        hbox.pack_start(self.create_bbox(False, "Spread (spacing 5)",
##                                         5, gtk.BUTTONBOX_SPREAD),
##                        True, True, 0)
##
##        hbox.pack_start(self.create_bbox(False, "Edge (spacing 30)",
##                                         30, gtk.BUTTONBOX_EDGE),
##                        True, True, 5)
##
##        hbox.pack_start(self.create_bbox(False, "Start (spacing 20)",
##                                         20, gtk.BUTTONBOX_START),
##                        True, True, 5)
##
##        hbox.pack_start(self.create_bbox(False, "End (spacing 20)",
##                                         20, gtk.BUTTONBOX_END),
##                        True, True, 5)

        window.show_all()

def main():
    # Enter the event loop
    gtk.main()
    return 0

if __name__ == "__main__":
    startWindow()
    main()
