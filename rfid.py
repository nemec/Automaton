#!/usr/bin/env/python

import automaton.lib.settings_loader as settings_loader
import automaton.lib.logger as logger
import serial
import sys
from struct import unpack
import time

import pgdb

from automaton.lib.client_wrapper_thrift import ClientWrapper

def do_valid_tag(db, code):
  cursor = db.cursor()
  query = 'SELECT "User Data"."First Name", "User Data"."Last Name" FROM "Users"."User Data" WHERE "User Data"."Username" = \'%s\';' % code
  try:
    cursor.execute(query)
  except Exception as e:
    print e
    cursor.close()
    db.rollback()
    return None
  name = cursor.fetchone()
  cursor.close()
  if name == None:
    return None
  name =  " ".join(name)
  global client
  client.execute("say", "Welcome back " + name)

def checkid(db, idnum):
  cursor = db.cursor()
  query = 'SELECT "Registered Keys"."Username" from "RFID"."Registered Keys" WHERE "Registered Keys"."ID" = \'{0}\''.format(idnum)
  try:
    cursor.execute(query)
  except Exception as e:
    print e
    cursor.close()
    db.rollback()
    return None
  if cursor.rowcount > 0:
    data=cursor.fetchone()[0]
  else:
    data = None
  cursor.close()
  return data

try:
  s = serial.Serial("/dev/ttyUSB0", 2400)
except serial.serialutil.SerialException:
  s = serial.Serial("/dev/ttyUSB1", 2400)

op = {"DBHOST":"localhost", "DBUSER":"RFID", "DBPASS":""}
op.update(settings_loader.load_app_settings(sys.argv[0]))

if op["DBPASS"]=="":
  logger.log("Error: no db password provided")
  sys.exit()

try:
  db = pgdb.connect(user=op["DBUSER"], password=op["DBPASS"], host=op["DBHOST"], database="Automaton")
except Exception as e:
  print "Error connecting to database:",e
  sys.exit() 

client = ClientWrapper.ClientWrapper(op["THRIFT_SERVER"])
client.open()

try:
  client.registerPlugin("say")
except ClientWrapper.PluginNotLoadedException:
    print "PluginNotLoaded Exception"
except ClientWrapper.ServiceNotRegisteredException:
    print "Service not registered"


# Enable the reader
s.setRTS(1)

while True:
  try:
    if unpack("B", s.read()) == (10, ):
      idnum = ''
      while len(idnum) < 10:
        char = s.read()
        val = unpack("B", char)
        if val == (10, ) or val == (13, ):
          break
        idnum += char
      
      if len(idnum) == 10:
        username = checkid(db, idnum)
        if username != None:
          logger.log("Valid tag: "+idnum)
          do_valid_tag(db, username)
        else:
          logger.log("Invalid tag: "+idnum)
        s.setRTS(0)
        time.sleep(2)
        s.setRTS(1)
  except Exception as e:
    print e
    break

#client.close()
db.close()
