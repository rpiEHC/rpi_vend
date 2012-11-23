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
	'''

	# Database objects
	con = sqlite3.connect("local.db")	# use :memory: to put in RAM
	cur = con.cursor()

	# Initialze interface objects
	def __init__(self):
		return

	# Terminate connections
	def __del__(self):
		#print "Killed " + str(self)
		self.con.close()

	# Initialize sqlite tables
	def init_db(self):
		query = '''
			CREATE TABLE IF NOT EXISTS items(
				loc		integer,
				cost	real,
				qty		integer,
				name	text,
				long_name text,
				desc	text
			);'''
		self.cur.execute(query)
		query = '''
			CREATE TABLE IF NOT EXISTS users(
				iso		integer,
				name	text
			);'''
		self.cur.execute(query)
		query = '''
			CREATE TABLE IF NOT EXISTS purchases(
				date	integer,
				uid		integer,
				total	real,
				cart	blob
			);'''
		self.cur.execute(query)
		self.con.commit()


class Item(Store):
	'''
	An Item object contains information about an item that the machine can
	vend.
	'''

	# Initialize the member vars for this Item
	def __init__(self, loc,
	             cost=0.00, qty=0, name=None, long_name=None, desc=None):
		self.info = {
			'id'	: None,
			'loc'   : loc,				# shelf number item is located on
			'cost'  : cost,				# cost per unit
			'qty'	: qty,				# quantity in stock for this item
			'name'  : name,				# display name of item (optional)
			'long_name' : long_name,	# full name of item (optional)
			'desc'  : desc				# 72 words recommended (optional)
		}

	# Search the table (by loc) for a given Item
	def find(self):
		query = '''SELECT * FROM items WHERE loc==? LIMIT 1'''
		self.cur.execute(query,[self.info['loc']])
		result = self.cur.fetchone()
		if result:
			print "Found Item(" + str(self.info['loc']) + ")"
			for row in result:
				self.info['row'] = row
			return
		else:
			print 'Found no Item with loc==' + str(self.info['loc'])
			return None

	# Reduce the quantity of an item remaining, else return error
	def dispense(self, qty):
		query = '''SELECT qty FROM items WHERE loc==? LIMIT 1'''
		self.cur.execute(query,[self.info['loc']])
		result = self.cur.fetchone()
		if result[0] >= qty:
			self.info['qty'] = result[0] - qty
			print 'Saving that QTY is '+str(result[0])+'-->'+str(self.info['qty'])
			query = '''UPDATE items SET qty=? WHERE loc=?'''
			self.cur.execute(query,[self.info['qty'],self.info['loc']])
			self.con.commit()
			return
		else:
			print 'Impossible to vend '+str(qty)+' Items (because only '+str(result[0])+' remain) !'
			return None

	# Store a new Item in the table
	def save(self):
		query = '''
			INSERT INTO items(loc,cost,qty,name,long_name,desc)
			values(?,?,?,?,?,?)'''
		values = (self.info['loc'], self.info['cost'], self.info['qty'],
		          self.info['name'], self.info['long_name'], self.info['desc'])
		self.cur.execute(query,values)
		self.con.commit()
		print 'Saved Item('+str(self.info['loc'])+','+self.info['name']+')'


class User(Store):
	'''
	A User object accesses information about a club member that is registered
	in the database.
	'''

	# User info is fetched from the db, not set by the program
	iso	 = None							# From a club member's RPI RFID
	name = None							# From club member list

	# Initialize member vars
	def __init__(self, iso):
		query = '''SELECT iso,name FROM users WHERE iso==? LIMIT 1'''
		self.cur.execute(query,[iso])
		result = self.cur.fetchone()
		if result:
			self.iso = result[0]
			self.name= result[1]
			print "Found User(" + str(self.iso) + ",'" + self.name + "')"
		else:
			print 'Found no User with iso==' + str(iso)
			return None


class Purchase(Store):
	'''
	A Purchase object is constructed and logged when the machine vends
	Items to a user that already paid.
	'''

	# Initialize member vars
	def __init__(self, uid, cart):
		self.info = {
			'id'	: None,				# ROWID from db
			'date'	: None,				# datetime of transaction
			'uid'	: uid,				# ISO of User
			'total'	: 0.00,				# Computed total transaction
			'cart'	: cart				# List of Items in purchase
		}
		return

	# Compute the total dollar amount of the purchase, given the cart
	def compute_total(self):
		# todo
		return 0.00

	# Verify that the User exists
	def verify(self):
		# todo
		return

	# Commit the Purchase to the table
	def save(self):
		query = '''
			INSERT INTO purchases(date,uid,total,cart)
			values('now',?,?,?)'''
		values = (self.info['uid'],self.info['total'],self.info['cart'])
		self.cur.execute(query,values)
		self.con.commit()
		print 'Saved Purchase(' + str(self.info['uid']) + ')'
		return


class Hardware(object):
	'''
	Objects interfacing the physical vending mahcine.
	Note that python is an interpreted language and a poor choice for
	real-time applications. It's still good enough here.
	This is the only class that should interface directly with GPIO.
	See <http://code.google.com/p/raspberry-gpio-python/> for RPi.GPIO usage.
	'''

	# Hardware Info
	#import RPi.GPIO as GPIO	# this can only be run on a RPi
	pin = None

	# Initialize
	def __init__(self, loc, pin, mode='out'):
		self.pin = pin
		if mode=='in':
			mode=='GPIO.IN'
		else:
			mode='GPIO.OUT'
		#GPIO.setup(12, mode)	# config pin mode
		return


class Dispenser(object):
	'''
	A dispenser on a given shelf location. Each dispenser has a feed motor,
	a cutting mechanism, a drawer lock, and indicators. Dispensers contain
	GPIO components that are installed on consecutive pins.
	(TODO-- MUX dispensers so that more can be installed)
	'''

	# Info
	loc = 0						# Shelf number of physical dispenser
	contents = Item(loc)		# Item contained in dispenser

	# Connect Store Item, Hardware pins to Dispenser
	def __init__(self, loc):
		self.loc = loc
		self.contents = Item(loc)
		self.contents.find()
		# todo: init IO pins
		return

	# Dispense a quantity of Items from the machine, if possible
	def dispense(self, qty=1):
		if self.contents.dispense(qty)==None:
			return None
		# todo: advance a qty of items, cut, unlock drawer, then indicate.
		return


def test_db_init():
	'''
	This simple test loads dummy rows in the 'items' and 'purchases' tables
	'''
	print '  -- TESTING DB --'
	mach = Store()
	mach.init_db()
	it = Item(1, 5.00, 99, 'test')
	it.save()
	it2 = Item(1)
	it2.find()
	disp = Dispenser(1)
	disp.dispense(1)
	disp.dispense(100)
	us = User(123456789)
	us2 = User(0)
	purch = Purchase(us.iso,None)
	purch.save()
	print '  -- DONE --'
	return


test_db_init()
