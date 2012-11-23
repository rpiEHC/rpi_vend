# cli.py
# The command line interface for all vending machine operations.
# This program is designed to run on a Raspberry Pi (RPi) under Linux.
#


import sys
import sqlite3
import time


class Machine(object):
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
		self.con.close()

	# Initialize sqlite tables
	def init_db(self):
		query = '''
			CREATE TABLE IF NOT EXISTS items(
				loc		integer,
				cost	real,
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


class Item(Machine):
	'''
	An Item object contains information about an item that the machine can
	vend.
	'''

	# Initialize the member vars for this Item
	def __init__(self, loc, cost, qty, name=None, long_name=None, desc=None):
		self.info = {
			'id'	: None,
			'loc'   : loc,				# shelf number item is located on
			'cost'  : cost,				# cost per unit
			'name'  : name,				# display name of item (optional)
			'long_name' : long_name,	# full name of item (optional)
			'desc'  : desc				# 72 words recommended (optional)
		}
		self.qty = qty					# quantity in stock for this item

	# Machine an Item in the table
	def save(self):
		query = '''
			INSERT INTO items(loc,cost,name,long_name,desc)
			values(?,?,?,?,?)'''
		values = (self.info['loc'], self.info['cost'], self.info['name'],
				  self.info['long_name'], self.info['desc'])
		self.cur.execute(query,values)
		self.con.commit()
		print 'Saved Item(' + self.info['name'] + ')'


class User(Machine):
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


class Purchase(Machine):
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
	loc = None					# Shelf number of physical dispenser
	itm	= None					# Unique Item loaded in dispenser
	typ = 'SMD'					# SMD, DIP, or bag dispenser? (default is SMD)

	# Initialize
	def __init__(self, loc, item, typ='SMD'):
		self.loc = loc
		self.itm = item
		self.typ = typ
		# todo: init IO pins
		return

	# Dispense a quantity of Items
	def dispense(self, qty=1):
		# todo: advance a qty of items, cut, unlock drawer, then indicate.
		return


def test_db_init():
	'''
	This simple test loads dummy rows in the 'items' and 'purchases' tables
	'''
	print '  -- TESTING DB --'
	dummy_machine = Machine()
	dummy_machine.init_db()
	dummy_item = Item(1, 5.00, 99, 'test')
	dummy_item.save()
	dummy_user = User(123456789)
	dummy_user_two = User(0)
	dummy_purchase = Purchase(dummy_user.iso,None)
	dummy_purchase.save()
	print '  -- DONE --'
	return


test_db_init()
