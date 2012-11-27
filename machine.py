#!/usr/bin/env python
#
# cli.py
# The command line interface for all vending machine operations.
# This program is designed to run on a Raspberry Pi (RPi) under Linux.
#


import sys
import sqlite3
import time


class Store(object):
    '''
    Base class for Objects comprising the virtual store inside the machine.
    Note that the RPi rev 2.0 has 512MB of RAM and stores only on an SD card.
    '''

    # Database objects
    con = sqlite3.connect('local.db')   # use :memory: to put in RAM
    cur = con.cursor()

    def __init__(self):
        '''
        Initialize interface objects
        '''
        return

    def __del__(self):
        '''
        Terminate connections
        '''
        #print "Killed " + str(self)
        #self.con.close()
        return

    def init_db(self):
        '''
        Initialize sqlite tables. This function is safe to call at any time
        because it uses 'IF NOT EXISTS' syntax.
        '''
        query = '''
            CREATE TABLE IF NOT EXISTS items(
                loc     integer UNIQUE,
                cost    real,
                qty     integer,
                name    text,
                long_name text,
                desc    text
            );'''
        self.cur.execute(query)
        query = '''
            CREATE TABLE IF NOT EXISTS users(
                uid     integer UNIQUE,
                name    text,
                tab     real
            );'''
        self.cur.execute(query)
        query = '''
            CREATE TABLE IF NOT EXISTS purchases(
                date    integer,
                uid     integer,
                total   real,
                cart    blob
            );'''
        self.cur.execute(query)
        self.con.commit()


class Item(Store):
    '''
    An Item object contains information about an item that the machine can
    vend.
    '''

    dispenser   = None                  # Physical dispenser associated w/ Item
    info        = {                     # Dict of table contents
        'id'            : 0,
        'loc'           : 0,
        'cost'          : 0.0,
        'qty'           : 0,
        'name'          : None,
        'long_name'     : None,
        'desc'          : None,
    }

    def __init__(self, loc, cost=0, qty=0, name='', long_name='', desc=''):
        '''
        Initialize the member vars for this Item. The default values are
        included to allow the initialization of empty/dummy objects, but all
        members are populated upon pull from db.
        '''
        self.info = {
            'id'        : None,         # table auto index
            'loc'       : loc,          # shelf number item is located on
            'cost'      : cost,         # cost per unit
            'qty'       : qty,          # quantity in stock for this item
            'name'      : name,         # display name of item (optional)
            'long_name' : long_name,    # full name of item (optional)
            'desc'      : desc          # 72 words recommended (optional)
        }
        self.dispenser = Dispenser(loc)

    def find(self):
        '''
        Search the table (by loc) for a given Item
        '''
        query = '''SELECT * FROM items WHERE loc==? LIMIT 1'''
        self.cur.execute(query,[self.info['loc']])
        result = self.cur.fetchone()
        if result:
            print "Found Item(" + str(self.info['loc']) + ")"
            for row in result:
                self.info['row'] = row
            return self
        else:
            print 'Found no Item with loc==' + str(self.info['loc'])
            return None

    @staticmethod
    def listItems(self):
        '''
        Return all Item() rows in the database
        '''
        templist = []
        query = '''SELECT * FROM items'''
        self.cur.execute(query)
        result = self.cur.fetchall()
        if result:
            print "Items Found"
            for row in result:
                x = Item(0)
                x.info['row'] = row
                templist.append(x)
        return templist

    def dispense(self, qty):
        '''
        Reduce the quantity of an item remaining, else return an error.
        Fetch the result and store the zeroth item in the result tuple
        (which has a size of one) in the (already configured) member var
        '''
        query = '''SELECT qty FROM items WHERE loc==? LIMIT 1'''
        self.cur.execute(query,[self.info['loc']])
        self.info['qty'] = self.cur.fetchone()[0]
        if self.info['qty'] >= qty:
            new_qty = self.info['qty'] - qty
            self.update(new_qty)
            self.dispenser.dispense(qty)
            return
        else:
            print ('Impossible to vend '+str(qty)+' Items (because only '+
                str(self.info['qty'])+' remain) !')
            return None

    def update(self, new_qty):
        '''
        Store a new Item in the table
        '''
        print 'Saving QTY change: '+str(self.info['qty'])+' --> '+str(new_qty)
        self.info['qty'] = new_qty
        query = '''UPDATE items SET qty=? WHERE loc=?'''
        self.cur.execute(query,[new_qty,self.info['loc']])
        self.con.commit()
        return

    def save(self):
        '''
        Store a new Item in the table
        '''
        query = '''
            INSERT OR IGNORE INTO items(loc,cost,qty,name,long_name,desc)
            values(?,?,?,?,?,?)'''
        values = (self.info['loc'], self.info['cost'], self.info['qty'],
                  self.info['name'], self.info['long_name'], self.info['desc'])
        self.cur.execute(query,values)
        self.con.commit()
        print 'Saved Item('+str(self.info['loc'])+','+self.info['name']+')'
        return


class User(Store):
    '''
    A User object accesses information about a club member that is registered
    in the database.
    '''

    # User info is fetched from the db, not set by the program
    uid  = None                         # From a club member's RPI RFID
    name = None                         # From club member list
    verified = 0                        # Is the User verified as an EHC member?

    def __init__(self, uid=0):
        '''
        Initialize member vars
        '''
        self.uid = uid
        return

    def verify(self):
        '''
        Verify that the User exists by getting an 11-char hex string from the
        RFID reader and then checking it against the 'users' table.
        '''
        query = '''SELECT uid,name FROM users WHERE uid==? LIMIT 1'''
        self.cur.execute(query,[self.uid])
        result = self.cur.fetchone()
        if result:
            self.uid  = result[0]
            self.name = result[1]
            self.verified = 1
            print "Verified User(" + str(self.uid) + ",'" + self.name + "')"
        else:
            self.verified = 0
            print 'Could not verify User with uid==' + str(self.uid)
            return None
        return

    def charge(self, amount):
        '''
        Charge a given amount to the User's tab
        '''
        query = '''UPDATE users SET tab=tab+? WHERE uid=?'''
        self.cur.execute(query,[amount,self.uid])
        self.con.commit()
        return


class Purchase(Store):
    '''
    A Purchase object is constructed and logged when the machine vends
    Items to a user that already paid.
    '''

    def __init__(self, uid, cart):
        '''
        Initialize member vars
        '''
        self.info = {
            'id'    : None,             # ROWID from db
            'date'  : None,             # datetime of transaction
            'uid'   : uid,              # ISO of User
            'total' : 0.00,             # Computed total transaction
            'cart'  : cart              # List of each [loc,qty] to purchase
        }
        self.user = User(uid)
        return

    def addToCart(self, loc, qty):
        '''
        Add a single entry to the cart by providing the loc,qty of an Item.
        Don't bother checking if there's enough qty in stock because that's
        done by the GUI and before vending.
        '''
        entry = Item(loc)
        if not entry.find():
            return None
        return self.info['cart'].append((loc,qty))

    def compute_total(self):
        '''
        Compute the total dollar amount of the purchase, given the cart as a
        list of tuples.
        '''
        for x in self.info['cart']:             # Iterate through the cart object which is a list of items
            query = '''SELECT qty FROM items WHERE loc==? LIMIT 1'''        # Searches for the item in the database using the location
            result=self.cur.execute(query,x['loc'])                 # Stores the result. There should be only one item at that location
            self.info['total']+=result[0]*x['qty']                  # Takes the cost (I think it's located in element 0 of results and multiply it by the quanitity. This gets added to the total
        return self.info['total']                           # Returns the total

    def save(self):
        '''
        Commit the Purchase to the table
        '''
        query = '''
            INSERT OR IGNORE INTO purchases(date,uid,total,cart)
            values(strftime('%s','now'),?,?,?)'''
        blob = unicode(self.info['cart'])  # todo: store this properly (pickle?)
        values = (self.info['uid'],self.info['total'],blob)
        self.cur.execute(query,values)
        self.con.commit()
        print 'Saved Purchase(' + str(self.info['uid']) + ')'
        return

    def vend(self):
        '''
        Handle the Vend: Dispense an Item from the correlated Dispenser and
        then charge the User the total amount. This function should not be
        called unless the requested Items have enough quantity in stock.
        '''

        # Is the user a club member?
        self.user.verify()
        if self.user.verified==0:
            print "VEND ERROR - User is not a club member"
            return None

        # Dispense the requested quantity of each Item
        for key,value in self.info['cart'].items():
            key.dispense(value)

        # Charge the Purchase to the verified User
        total = self.compute_total()
        self.user.charge(total)

        # Log the purchase. That's it!
        self.save()
        return


class Hardware(object):
    '''
    Objects interfacing the physical vending machine. Note that python is an
    interpreted language and a poor choice for real-time applications.
    It's still good enough here.
    Also, this is the only class that should interface directly with GPIO.
    See <http://code.google.com/p/raspberry-gpio-python/> for RPi.GPIO usage.
    '''

    # Hardware Info
    #import RPi.GPIO as GPIO            # requires Raspian OS and root user
    pin  = None                         # Pin number of this device
    mode = 1#GPIO.OUT                   # Input/Output mode configuration
    cur  = None                         # Current value

    def __init__(self, loc, pin, mode='out'):
        '''
        Initialize the one pin for this device.
        '''
        self.pin = pin
        if mode=='in':
            self.mode==0#GPIO.IN
        else:
            self.mode==1#GPIO.OUT
        #GPIO.setup(self.pin, self.mode)  # config pin mode
        return

    def getValue(self):
        '''
        Return the input value on this pin
        '''
        if self.mode != 0:#GPIO.IN:
            return None
        #cur = GPIO.input(self.pin)
        return cur

    def toggle(self):
        '''
        Toggle the output signal on this pin (HIGH or LOW)
        '''
        if self.mode!=1:#GPIO.OUT:
            return None
        if cur==1:#GPIO.HIGH:
            cur = 0#GPIO.LOW
        else:
            cur = 1#GPIO.HIGH
        #GPIO.output( self.pin, cur )
        return cur

    def clear(self):
        '''
        For debugging only (the finished program doesn't need this)
        '''
        print "  "+self+".clear() called"
        #GPIO.cleanup()
        return



class Dispenser(object):
    '''
    A dispenser on a given shelf location. Each dispenser has a feed motor,
    a cutting mechanism, a drawer lock, and indicators. Dispensers contain
    GPIO components that are installed on consecutive pins.
    (TODO-- MUX dispensers so that more can be installed)
    '''

    # Initialize relational info and (physical) child objects
    loc     = 0                         # Shelf number of physical dispenser
    hw_feed = None                      # Feed servo which advances the tape
    hw_cut  = None                      # Cutting mechanism
    hw_lock = None                      # Lock/Unlock of Drop Tray
    hw_led0 = None                      # Indicator LED on this shelf

    def __init__(self, loc):
        '''
        Connect Store.Item() and Hardware() pins to this Dispenser().
        Initialize IO using provided loc to determine number and order of pins
        and provided starting pin number to determine which GPIO to init.
        '''
        self.loc = loc
        self.hw_feed = Hardware(loc  ,0)
        self.hw_cut  = Hardware(loc+1,0)
        self.hw_lock = Hardware(loc+2,0)
        self.hw_led0 = Hardware(loc+3,0)
        return

    def dispense(self, qty=1):
        '''
        Dispense a quantity of Items from the machine, if possible.
        This function is called last when vending an Item().
        '''
        print 'Dispensing '+str(qty)+' Item(s)...'
        # todo: advance a qty of items
        # todo: cut tape
        # todo: unlock drawer
        # todo: indicate.
        return


def test_db():
    '''
    This simple test loads example Store data
    '''
    print '  -- TESTING DB --'
    mach = Store()
    mach.init_db()
    it = Item(1, 5.00, 99, 'test')
    it.save()
    it2 = Item(1)
    it2.find()
    us = User(0)
    purch = Purchase(us.uid,None)
    purch.save()
    print '  -- DONE --'
    return


def test_purchase():
    '''
    Using example data, verify and vend a Purchase in the Store and Dispenser
    '''
    print '  -- TESTING PURCHASE --'
    mach2 = Store()
    it = Item(1, 5.00, 99, 'test')
    it.save()
    disp = Dispenser(1)
    us = User(123456789)
    cart = { Item(1) : 1 }
    purch = Purchase(us.uid,cart)
    purch.vend()
    print '  -- DONE --'


test_db()
test_purchase()
