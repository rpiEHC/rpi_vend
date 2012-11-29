#!/usr/bin/env python
#
# machine.py
# The command line interface for all vending machine operations.
# This program is designed to run on a Raspberry Pi (RPi) rev 2.0 under Linux.
#


import sys
import sqlite3
import time
import serial


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
            'desc'      : desc,         # 72 words recommended (optional)
        }
        self.dispenser = Dispenser(loc)
        self._find()
        return

    def _find(self):
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

    def _dispense(self, qty):
        '''
        Reduce the quantity of an item remaining, else return an error.
        Fetch the result and store the zeroth item in the result tuple
        (which has a size of one) in the (already configured) member var.
        '''
        query = '''SELECT qty FROM items WHERE loc==? LIMIT 1'''
        self.cur.execute(query,[self.info['loc']])
        self.info['qty'] = self.cur.fetchone()[0]
        if self.info['qty'] >= qty:
            new_qty = self.info['qty'] - qty
            self._update(new_qty)
            self.dispenser._dispense(qty)
            return
        else:
            print ('Impossible to vend '+str(qty)+' Items (because only '+
                str(self.info['qty'])+' remain) !')
            return None

    def _update(self, new_qty):
        '''
        Store a new Item in the table.
        '''
        print 'Saving QTY change: '+str(self.info['qty'])+' --> '+str(new_qty)
        self.info['qty'] = new_qty
        query = '''UPDATE items SET qty=? WHERE loc=?'''
        self.cur.execute(query,[new_qty,self.info['loc']])
        self.con.commit()
        return

    def save(self):
        '''
        Store a new Item in the table.
        This is used for debugging.
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
        self.loc     = loc
        self.hw_feed = Hardware(loc  ,0)
        self.hw_cut  = Hardware(loc+1,0)
        self.hw_lock = Hardware(loc+2,0)
        self.hw_led0 = Hardware(loc+3,0)
        return

    def _dispense(self, qty=1):
        '''
        Dispense a quantity of Items from the machine, if possible.
        This function is called last when vending an Item().
        '''
        print 'Dispensing '+str(qty)+' Item(s)...'

        # Make the LED blink
        self.hw_led0.toggle()
        time.sleep(.1)
        self.hw_led0.toggle()
        time.sleep(.1)
        self.hw_led0.toggle()
        time.sleep(.1)
        self.hw_led0.toggle()

        # todo: advance a qty of items
        #hw_feed

        # Cut tape
        self.hw_cut.set(1)
        time.sleep(.2)
        self.hw_cut.set(0)

        # Unlock drawer
        self.hw_lock.set(1)

        # Turn LED on for a few seconds
        self.hw_led0.set(1)
        time.sleep(3)
        self.hw_led0.set(0)

        return


class User(Store):
    '''
    A User object accesses information about a club member that is registered
    in the database.
    '''

    # User info is fetched from the db, not set by the program
    uid  = None                         # From a club member's RPI RFID
    name = None                         # From club member list
    verified = 0                        # Is User verified as an EHC member?

    def __init__(self, uid=0, name=None):
        '''
        Initialize member vars. Try to verify the user and note the result,
        but don't return an error if verification does not pass. This allows
        invalid Users to exist, even if they can't do anything.
        '''
        self.uid = uid
        self.name = name
        self._verify();
        return

    def _verify(self):
        '''
        Verify that the User exists by checking the uid against the database.
        This function has nothing to do with the RFID reader hardware.
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

    def _charge(self, amount):
        '''
        Charge a given amount to the User's tab
        '''
        query = '''UPDATE users SET tab=tab+? WHERE uid=?'''
        self.cur.execute(query,[amount,self.uid])
        self.con.commit()
        return

    def _save(self):
        '''
        Store a new User in the table
        '''
        query = '''
            INSERT OR IGNORE INTO users(uid,name,tab)
            values(?,?,?)'''
        values = (self.uid, self.name, 0.0)
        self.cur.execute(query,values)
        self.con.commit()
        print 'Saved User('+str(self.uid)+','+self.name+')'
        return


class Purchase(Store):
    '''
    A Purchase object is constructed and logged when the machine vends
    Items to a user that already paid.
    '''

    def __init__(self, uid):
        '''
        Initialize member vars
        '''
        self.info = {
            'id'    : None,             # ROWID from db
            'date'  : None,             # datetime of transaction
            'uid'   : uid,              # ISO of User
            'total' : 0.00,             # Computed total transaction
            'cart'  : [],               # List of each (loc,qty) to purchase
        }
        self.user = User(uid)
        return

    def add_to_cart(self, loc, qty):
        '''
        Add a single entry to the cart by providing the (loc,qty) of an Item.
        Don't bother checking if there's enough qty in stock because that's
        done by the GUI and before vending.
        '''
        entry = Item(loc)
        if not entry._find() or qty < 1:
            return None
        return self.info['cart'].append((int(loc),int(qty)))

    def _compute_total(self):
        '''
        Compute the total dollar amount of the purchase, given the cart as a
        list of tuples.
        '''
        self.info['total'] = 0
        for entry in self.info['cart']:
            loc = entry[0]
            qty = entry[1]
            entry = Item(loc)
            cost = entry.info['cost']
            self.info['total'] += qty*cost
        return self.info['total']

    def _save(self):
        '''
        Commit the Purchase to the table
        '''
        query = '''
            INSERT OR IGNORE INTO purchases(date,uid,total,cart)
            values(strftime('%s','now'),?,?,?)'''
        blob = unicode(self.info['cart'])
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
        #self.user._verify() # redundant check
        if self.user.verified==0:
            print "VEND ERROR - User is not a club member"
            return None

        # Dispense the requested quantity of each Item
        print self.info['cart']
        for entry in self.info['cart']:
            loc = entry[0]
            qty = entry[1]
            Item(loc)._dispense(qty)

        # Charge the Purchase to the verified User
        total = self._compute_total()
        self.user._charge(total)

        # Log the purchase. That's it!
        self._save()
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

    def set(self, signal):
        '''
        Set the output signal on this pin (HIGH or LOW)
        '''
        if self.mode!=1:#GPIO.OUT:
            return None
        if signal==1:
            self.cur = 1#GPIO.HIGH
        else:
            self.cur = 0#GPIO.LOW
        #GPIO.output(self.pin, self.cur)
        return self.cur

    def toggle(self):
        '''
        Toggle the output signal on this pin (HIGH or LOW)
        '''
        if self.mode!=1:#GPIO.OUT:
            return None
        if self.cur==1:#GPIO.HIGH:
            self.cur = 0#GPIO.LOW
        else:
            self.cur = 1#GPIO.HIGH
        #GPIO.output(self.pin, self.cur)
        return self.cur

    def clear(self):
        '''
        For debugging only (the finished program doesn't need this)
        '''
        print "  "+self+".clear() called"
        #GPIO.cleanup()
        return


class TagReader(object):
    '''
    The RFID reader is on Github at rpiEHC/RPI-RFID
    '''

    ser  = None                         # Serial port interface object
    port = None                         # Serial port location
    baud = 9600                         # Clock rate of port

    def __init__(self, port='/dev/ttyACM0', baud=9600, opts='timeout=0'):
        self.ser = serial.Serial(port, baud, opts)
        return

    def get(self):
        '''
        Poll the reader over the configured serial connection and return the
        valid result read, which is the uid of the person on the RFID card.
        '''
        uid = '--NO CHANGE--'
        uid = self.ser.readline()
        print 'TagReader.get() returns '+str(uid)
        return uid

    def puke_all(self):
        '''
        For debugging purposes...
        '''
        while True:
            output = self.ser.readline()
            print output


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
    it2._find()
    us = User(0)
    purch = Purchase(us.uid)
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
    purch = Purchase(us.uid)
    purch.add_to_cart(1,1)
    purch.vend()
    print '  -- DONE --'


def test_rfid():
    # The 'dialout' group can read to USB0, so do sudo usermod -a -G dialout pi;
    # also try option rtscts=1
    # via <http://raspberrypi.org/phpBB3/viewtopic.php?f=32&t=6832>
    print '  -- TESTING RFID READER --'
    reader = TagReader('/dev/ttyACM0',9600,'timeout=0,rtscts=1');
    uid = reader.get();
    user = User(uid)
    if not user.verified:
        reader.puke_all()
    # _verify() is called by User.__init__ and prints the result
    print '  -- DONE --'


#test_db()
#test_purchase()
test_rfid()
