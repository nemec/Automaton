#!/usr/bin/python

import sys

import automaton.lib.imaplib2 as imaplib2
import os
import re
import smtplib
import threading
import time
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

import pgdb

import automaton.lib.settings_loader as settings_loader
from automaton.lib.logger import log

import automaton.client.thrift

# This script reads the inbox of the given IMAP server,
# checks for mail from the specified email address (in
# this case, a phone SMS number) and executes the command
# sent in the body of the text based on the functions
# imported from the command module.

# Settings are provided in the file Textecute.conf

# Created by Daniel Nemec, sources attributed when necessary
# For help or questions, email me at djnemec@gmail.com
# Putting a related subject in the email will help me
# reply to you more quickly.

'''''''''''''''''''''
@TODO Doesn't alert on error. Maybe implement
        error return values for commands?
'''''''''''''''''''''

def handle_message(body, frm):

  global op

  # This for-loop is a quick hack to ignore
  # extra data that a gmail address puts in the
  # body of an email when sending. There are no
  # guarantees on correct parsing for all
  # mail servers.
  for line in body.split("\n"):
      line=line.strip()
      if len(line) >0 and not line[0] == "-" \
        and line.find(":") == -1:
          body=line
          break
  # Program automatically lower-cases all text
  # in the command. To override the functionality,
  # prepend the message with an @ symbol.
  if body[0]=='@':
      body=body[1:]
  else:
      body=body.lower()
  ix=body.find(' ')
  returned = ''
  # Split command and arguments if there are any.
  if ix > -1:
    args = body[ix+1:]
    body = body[0:ix]
  else:
    args = ''

  try:
    if op['THRIFT_SERVER']!='':
      client = thrift.ClientWrapper(op['THRIFT_SERVER'], appname="textecute")
    else:
      client = thrift.ClientWrapper()
    client.open()

    if client.isPlugin(body):
      client.registerPlugin(body)
      result = client.execute(body, args)
    else:
      result = "Command not found.\nDid you forget to import it?"

    client.close()

  except thrift.ClientException as tx:
    result =  str(tx.message)

  if len(returned) > 160:
      result = result[0:160]
  print result
  if len(result) > 0: # If there's a returned value, send it back
      send_mail(frm, "Textecute", result)

def send_mail(to, subject, text):
    # Mail function example found at http://kutuma.blogspot.com
    msg = MIMEMultipart()
    SMTP_SERVER=op['SMTP_SERVER']
    SMTP_PORT=op['SMTP_PORT']
    SMTP_USER=op['SMTP_USER']
    SMTP_PASSWORD=op['SMTP_PASSWORD']
    msg['From'] = SMTP_USER+"@"+SMTP_SERVER[SMTP_SERVER.find('.')+1:]
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(text))
    mailServer = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(SMTP_USER, SMTP_PASSWORD)
    mailServer.sendmail(SMTP_USER, to, msg.as_string())
    mailServer.close()

def validate_address(db, frm):
  cursor = db.cursor()
  query='select "Username" from "Users"."view_Email"where \'{0}\'=ANY("Users"."view_Email"."Email");'.format(frm)
  try:
    cursor.execute(query)
  except Exception as e:
    print e
    cursor.close()
    db.rollback()
    return None
  name = cursor.fetchone()
  cursor.close()
  if name != None:
    name =  " ".join(name)
  return name

# Initialize empty list of settings
op={'IMAP_SERVER': 'imap.gmail.com',
    'IMAP_PORT':993,
    'IMAP_USER':'', 'IMAP_PASSWORD':'',
    'SMTP_SERVER':'smtp.gmail.com',
    'SMTP_PORT':587,
    "DBHOST":"localhost",
    "DBUSER":"Textecute",
    "DBPASS":""
   }

op.update(settings_loader.load_app_settings(sys.argv[0]))

# Fail if authentication info is not present.
for operator in ('IMAP_USER', 'IMAP_PASSWORD', 'DBPASS'):
  if op[operator] == '':
    log("Missing necessary credentials to log in to Textecute.")
    sys.exit()

# Set SMTP authentication to the same as IMAP
# if none has been provided.
if not op.has_key('SMTP_USER'):
  op['SMTP_USER']=op['IMAP_USER']
if not op.has_key('SMTP_PASSWORD'):
  op['SMTP_PASSWORD']=op['IMAP_PASSWORD']

try:
  db = pgdb.connect(user=op["DBUSER"], password=op["DBPASS"], host=op["DBHOST"], database="Automaton")
except Exception as e:
  log("Error connecting to database: %s" % e)
  sys.exit() 

connectionTries = 3
while connectionTries > 0:
  try:
    # connect to server
    server = imaplib2.IMAP4_SSL(op['IMAP_SERVER'], op['IMAP_PORT']) # gmail uses SSL on port 993
    server.login(op['IMAP_USER'], op['IMAP_PASSWORD'])
    server.select()
    break
  except Exception as e:
    connectionTries = connectionTries - 1
    log("Error connecting to IMAP server: retries left (%s)" % connectionTries)
    time.sleep(5)

if connectionTries <= 0:
  log("Error connecting to IMAP server: %s" % e)
  sys.exit()

try:
  while True:
    # list items on server
    typ, data = server.search(None, "UNSEEN")

    # check for new messages
    for num in data[0].split():
        typ, data = server.fetch(num, '(BODY[HEADER.FIELDS (FROM)])')
        frm=re.search("[\w.]*@[\w.]*", data[0][1][6:].strip()).group() # Parses the FROM string so that just the email address is used
        user=validate_address(db, frm)
        if user != None:
          typ, dat = server.fetch(num, '(BODY[TEXT])')
          handle_message(dat[0][1].strip(),frm)
          #threading.Thread(target=handle_message, args=(dat[0][1].strip(),frm)).start()
        # Mark as read and archive - doesn't actually delete the message.
        server.store(num, '+FLAGS', '\\Seen')
        server.store(num, '+FLAGS', '\\Deleted')
    try:
      server.idle()
    except IOError as e:
      log("Error with idle: %s" %e)
except Exception as e:
  log("Error during execution: %s" % e)

server.expunge()
server.logout()

