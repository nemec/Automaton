#!/usr/bin/env python

import sys
from twisted.words.protocols import oscar
from twisted.internet import protocol, reactor
import Automaton.lib.settings_loader as settings_loader

import Automaton.lib.logger as logger

import ClientWrapper

op = {'HOST':'login.oscar.aol.com',
      'PORT':'5190'
     }

op.update(settings_loader.load_app_settings(sys.argv[0]))

# Fail if authentication info is not present.
for operator in ('USER', 'PASS', 'MASTER'):
  if op[operator] == '':
    logger.log("Missing necessary credentials to log in to AIM.")
    sys.exit()

class B(oscar.BOSConnection):
    capabilities = [oscar.CAP_CHAT]

    def __init__(self, s, p, **kwargs):
      self.client = ClientWrapper.ClientWrapper("tails.local")
      self.client.open()
      oscar.BOSConnection.__init__(self, s, p, **kwargs)

    def initDone(self):
        self.requestSelfInfo().addCallback(self.gotSelfInfo)
        self.requestSSI().addCallback(self.gotBuddyList)
    def gotSelfInfo(self, user):
        self.name = user.name
    def gotBuddyList(self, l):
        self.activateSSI()
        self.setIdleTime(0)
        self.clientReady()
        logger.log("Client online.")
    def receiveMessage(self, user, multiparts, flags):
        if user.name.upper() != op['MASTER'].upper():
          multiparts[0] = ("I don't take orders from you!",)
          self.lastUser = user.name
          self.sendMessage(user.name, multiparts)
        else:
          body = multiparts[0][0].strip()
          ix=body.find(' ')
          returned = ''
          args=''
          if ix > -1:
            args = body[ix+1:]
            body = body[0:ix]

          if self.client.isScript(body):
            self.client.registerScript(body)
            returned = self.client.execute(body, args)
          else:
            returned = "Command not found.\nDid you forget to import it?"

          multiparts[0] = (returned,)
          self.lastUser = user.name
          self.sendMessage(user.name, multiparts)

class OA(oscar.OscarAuthenticator):
   BOSClass = B

protocol.ClientCreator(reactor, OA, op['USER'], op['PASS']).connectTCP(op['HOST'], int(op['PORT']))
reactor.run()

