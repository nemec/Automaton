#!/bin/python

import Automaton.lib.settings_loader as settings_loader
import Automaton.lib.logger as logger
import serial
import sys

import pgdb

import Automaton.lib.ClientWrapper as ClientWrapper

def do_valid_tag(db, code):
  cursor = db.cursor()
  query = 'SELECT "User Data"."First Name", "User Data"."Last Name" FROM "Users"."User Data" WHERE "User Data"."Username" = \'%s\';' % code
  try:
    cursor.execute(query)
  except Exception, e:
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
  client.execute("say", "Welcome back %s" % name)

def checkid(db, idnum):
  cursor = db.cursor()
  query = 'SELECT "Registered Keys"."Username" from "RFID"."Registered Keys" WHERE "Registered Keys"."ID" = \'%s\'' % idnum
  try:
    cursor.execute(query)
  except Exception, e:
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
except Exception, e:
  print "Error connecting to database:",e
  sys.exit() 

client = ClientWrapper.ClientWrapper(op["THRIFT_SERVER"])
client.open()

try:
  client.registerScript("say")
except ClientWrapper.ScriptNotLoadedException:
    print "ScriptNotLoaded Exception"
except ClientWrapper.ServiceNotRegisteredException:
    print "Service not registered"

while True:
  try:
    # Enables the RFID Reader manually if plugged in
    # with the serial-USB converter, since it's backwards
    #for x in range(0,300):
    #  s.write(str(x))
    #print s.read(10)
    idnum = s.read(10)
    s.flushInput()

    username = checkid(db, idnum)
    if username != None:
      s.write("1")
      logger.log("Valid tag: "+idnum)
      do_valid_tag(db, username)
    else:
      s.write("0")
      logger.log("Invalid tag: "+idnum)
  except Exception, e:
    print e
    break

client.close()
db.close()
