import sys
import datetime
import os
import logging
import time
import threading
from yowsup.layers import YowLayerEvent, EventCallback
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.network import YowNetworkLayer

from yowsup.common import YowConstants
from yowsup.layers.protocol_groups.protocolentities import *
from yowsup.layers.protocol_presence.protocolentities import *
from yowsup.layers.protocol_messages.protocolentities import *
from yowsup.layers.protocol_ib.protocolentities import *
from yowsup.layers.protocol_iq.protocolentities import *
from yowsup.layers.protocol_contacts.protocolentities import *
from yowsup.layers.protocol_chatstate.protocolentities import *
from yowsup.layers.protocol_privacy.protocolentities import *
from yowsup.layers.protocol_media.protocolentities import *
from yowsup.layers.protocol_media.mediauploader import MediaUploader
from yowsup.layers.protocol_profiles.protocolentities import *
from yowsup.common.tools import Jid
from yowsup.common.optionalmodules import PILOptionalModule, AxolotlOptionalModule
from yowsup.env import YowsupEnv

logger = logging.getLogger(__name__)

class YowsupWebLayer(YowInterfaceLayer):
    EVENT_START = "org.openwhatsapp.yowsup.event.cli.start"
    DISCONNECT_ACTION_EXIT = 1

    def __init__(self):
        YowsupEnv.setEnv( 'android' )

        super(YowsupWebLayer, self).__init__()
        YowInterfaceLayer.__init__(self)

        self.connected = False
        self.username = None
        self.sendReceipts = True
        self.sendRead = True
        self.credentials = None

        self.jidAliases = {
            # "NAME": "PHONE@s.whatsapp.net"
        }

        # self.input_processing_Thread = threading.Thread(target = self.execute_commands)
        # self.input_processing_Thread.daemon = True

    ###########################################################################
    # LIB WHATSAPP FUNCTIONS
    ###########################################################################
    def aliasToJid(self, calias):
        ' Converts alias to Jid'
        for alias, ajid in self.jidAliases.items():
            if calias.lower() == alias.lower():
                return Jid.normalize(ajid)

        return Jid.normalize(calias)

    def jidToAlias(self, jid):
        ' Converts Jid to alias'
        for alias, ajid in self.jidAliases.items():
            if ajid == jid:
                return alias
        return jid

    def assertConnected(self):
        ' Checks if user is still logged in'
        if self.connected:
            return True
        else:
            return False

    @ProtocolEntityCallback("success")
    def onSuccess(self, entity):
        self.connected = True
        self.output("Logged in!", "Auth", prompt=False)

    @ProtocolEntityCallback("failure")
    def onFailure(self, entity):
        self.connected = False
        self.output("Login Failed, reason: %s" % entity.getReason(), prompt=False)

    @EventCallback(YowNetworkLayer.EVENT_STATE_DISCONNECTED)
    def onStateDisconnected(self, layerEvent):
        self.output("Disconnected: %s" % layerEvent.getArg("reason"))
        self.connected = False

    def output(self, message, tag="general", prompt=True):
        logging.debug(message)

    ###########################################################################
    # CORE  WHATSAPP  FUNCTIONS
    ###########################################################################

    @EventCallback(EVENT_START)
    def onStart(self, layerEvent):
        # self.input_processing_Thread.start()
        return True

    def setCredentials(self, username, password):
        'Sets up user using given credentials '
        self.getLayerInterface(YowAuthenticationProtocolLayer).setCredentials(username, password)
        return "%s@s.whatsapp.net" % username

    def login(self, username, b64password):
        'Login a certain user'
        if self.connected:
            self.output("Already connected as some user")
            return True
        self.setCredentials(username, b64password)
        self.getLayerInterface(YowNetworkLayer).connect()
        return self.assertConnected()

    def disconnect(self):
        'Logout a certain user'
        if self.assertConnected():
            self.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_DISCONNECT))

    def contacts_sync(self, contacts):
        if self.assertConnected():
            entity = GetSyncIqProtocolEntity(contacts)
            self.toLower(entity)

    def message_send(self, mobilenumber, content):
        'Send a single message to a given contact(if it is in contacts) and user is connected'
        if self.assertConnected():
            if sys.version_info >= (3, 0):
                content = content.encode("utf-8")

            entity = OutgoingChatstateProtocolEntity(ChatstateProtocolEntity.STATE_TYPING, self.aliasToJid(mobilenumber))
            self.toLower(entity)
            outgoingMessage = TextMessageProtocolEntity(content, to=self.aliasToJid(mobilenumber))
            self.toLower(outgoingMessage)
            logging.info("Sent A New Message" + str(mobilenumber) + str(content))
            return True
        return False
