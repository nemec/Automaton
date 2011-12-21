#!/usr/bin/env python

import re
import sys
import htmlentitydefs
from twisted.words.protocols import oscar
from twisted.internet import protocol, reactor
from twisted.internet.error import ConnectionDone

import automaton.client.thrift as thrift_client
from automaton.lib import exceptions, logger, settings_loader


## unescape
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
# Provided by Fredrik Lundh at http://effbot.org/zone/re-sub.htm#unescape-html
def unescape(text):
  def fixup(m):
    text = m.group(0)
    if text[:2] == "&#":
      # character reference
      try:
        if text[:3] == "&#x":
          return unichr(int(text[3:-1], 16))
        else:
          return unichr(int(text[2:-1]))
      except ValueError:
        pass
    else:
      # named entity
      try:
        text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
      except KeyError:
        pass
    return text
  return re.sub("&#?\w+;", fixup, text)


op = {'HOST': 'login.oscar.aol.com',
      'PORT': '5190',
      'USER': '',
      'PASS': '',
      'MASTER': '',
      'THRIFT_SERVER': 'tails.local'
     }

op.update(settings_loader.load_app_settings(sys.argv[0]))

# Fail if authentication info is not present.
for operator in ('USER', 'PASS', 'MASTER'):
  if op[operator] == '':
    logger.log("Missing necessary credentials to log in to AIM.")
    sys.exit()


class B(oscar.BOSConnection):
    capabilities = [oscar.CAP_CHAT]

    def __init__(self, s, p, f):
      self.factory = f
      oscar.BOSConnection.__init__(self, s, p)

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
        username = user.name.upper()
        # Strips HTML tags
        body = re.sub(r'<.*?>', '', multiparts[0][0].strip())
        if (username != op['MASTER'].upper() and
                       username not in self.factory.authenticated_users):
          if op.get('PASSPHRASE', None) == body:
            self.factory.authenticated_users.append(username)
            multiparts[0] = ("Passphrase accepted.", )
          else:
            multiparts[0] = ("I don't take orders from you!",)
        else:
          returned = ''
          if body == 'help':
            returned = ", ".join(self.factory.client.getAvailableServices())
          elif body.startswith('/logout'):
            self.factory.authenticated_users.remove(username)
            returned = "Logged out."
          else:
            try:
              returned = self.factory.client.interpret(body)
            except exceptions.ClientError as err:
              returned = str(err)
            except exceptions.UnknownIntentError:
              returned = "Could not understand your intent."
            except exceptions.ClientNotRegisteredError:
              returned = ("AIM Client not registered to "
                          "Automaton, please restart.")

          multiparts[0] = (returned,)
        self.lastUser = user.name
        self.sendMessage(user.name, multiparts)


class OA(oscar.OscarAuthenticator):
  def connectToBOS(self, server, port):
    c = protocol.ClientCreator(reactor, B, self.username, self.cookie,
          self.factory)
    return c.connectTCP(server, int(port))


class AIMClientFactory(protocol.ReconnectingClientFactory):

  def __init__(self):
    self.authenticated_users = []
    self.client = thrift_client.ClientWrapper(op['THRIFT_SERVER'],
                                              appname='AIM')
    self.client.open()
    self.client.allowAllServices()

  def buildProtocol(self, addr):
    #return protocol.ClientCreator(reactor, OA, op['USER'], op['PASS'])
    proto = OA(op['USER'], op['PASS'])
    proto.factory = self
    return proto

  def clientConnectionLost(self, connector, reason):
    logger.log("Lost connection: " + str(reason))
    if reason.check([exceptions.ClientError]):
      reactor.stop()

  def clientConnectionFailed(self, connector, reason):
    logger.log("Connection failed: " + str(reason))
    protocol.ReconnectingClientFactory.clientConnectionFailed(self,
                                                    connector, reason)


reactor.connectTCP(op['HOST'], int(op['PORT']), AIMClientFactory())
reactor.run()
