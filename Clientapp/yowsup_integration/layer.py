import sys
import datetime
import os
from yowsup.layers import YowLayerEvent, EventCallback
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.network import YowNetworkLayer
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
from yowsup.env import YowsupEnv
from Clientapp.models import *



class YowsupWebLayer(YowInterfaceLayer):
    EVENT_START = "org.openwhatsapp.yowsup.event.cli.start"
    DISCONNECT_ACTION_EXIT = 1

    def __init__(self):
        YowsupEnv.setEnv('android')

        super(YowsupWebLayer, self).__init__()
        YowInterfaceLayer.__init__(self)

        self.connected = False
        self.username = None
        self.sendReceipts = False
        self.sendRead = False
        self.credentials = None

        self.jidAliases = {
            # "NAME": "PHONE@s.whatsapp.net"
        }

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

    # (lv4) Send a request to lower layer to send a file to given ip
    def doSendMedia(self, mediaType, filePath, url, to, ip=None, object=None):
        if mediaType == RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE:
            entity = ImageDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to)
            if (object is not None):
                object.whatsapp_message_id = entity._id
                object.save()
        # elif mediaType == RequestUploadIqProtocolEntity.MEDIA_TYPE_AUDIO:
        #     entity = AudioDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to)
        # elif mediaType == RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO:
        #     entity = VideoDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to, caption = caption)
        self.toLower(entity)

    # (lv3) From a given (number,file) , find upload status or start a new upload
    def onRequestUploadResult(self, jid, mediaType, filePath, resultRequestUploadIqProtocolEntity, requestUploadIqProtocolEntity, object=None):
        if resultRequestUploadIqProtocolEntity.isDuplicate():
            self.doSendMedia(mediaType, filePath, resultRequestUploadIqProtocolEntity.getUrl(), jid,
                             resultRequestUploadIqProtocolEntity.getIp(),  object)
        else:
            def successFn(filePath, jid, url):
                return self.doSendMedia(mediaType, filePath, url, jid, resultRequestUploadIqProtocolEntity.getIp(), object)
            mediaUploader = MediaUploader(jid, self.getOwnJid(), filePath,
                                          resultRequestUploadIqProtocolEntity.getUrl(),
                                          resultRequestUploadIqProtocolEntity.getResumeOffset(),
                                          successFn, self.onUploadError, self.onUploadProgress, async=False)
            mediaUploader.start()

    # (lv2) Send a media file to a number
    def media_send(self, number, path, mediaType, object=None):
        if self.assertConnected():
            entity = OutgoingChatstateProtocolEntity(ChatstateProtocolEntity.STATE_TYPING, self.aliasToJid(number))
            self.toLower(entity)

            jid = self.aliasToJid(number)
            entity = RequestUploadIqProtocolEntity(mediaType, filePath=path)

            def successFn(successEntity, originalEntity):
                return self.onRequestUploadResult(jid, mediaType, path, successEntity, originalEntity, object)

            def errorFn(errorEntity, originalEntity):
                return self.onRequestUploadError(jid, path, errorEntity, originalEntity)
            self._sendIq(entity, successFn, errorFn)
        return None

    def onRequestUploadError(self, jid, path, errorRequestUploadIqProtocolEntity, requestUploadIqProtocolEntity):
        self.output("Request upload for file %s for %s failed" % (path, jid))

    def onUploadError(self, filePath, jid, url):
        self.output("Upload file %s to %s for %s failed!" % (filePath, url, jid))

    def onUploadProgress(self, filePath, jid, url, progress):
        sys.stdout.write("%s => %s, %d%% \r" % (os.path.basename(filePath), jid, progress))
        sys.stdout.flush()

    def output(self, message, tag="general", prompt=True):
        print(message)

    ###########################################################################
    # CORE  WHATSAPP  FUNCTIONS
    ###########################################################################
    @EventCallback(EVENT_START)
    def onStart(self, layerEvent):
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

    def send_text_message(self, mobilenumber, content):
        'Send a single message to a given contact(if it is in contacts) and user is connected'
        entity = OutgoingChatstateProtocolEntity(ChatstateProtocolEntity.STATE_TYPING, self.aliasToJid(mobilenumber))
        self.toLower(entity)

        outgoingMessage = TextMessageProtocolEntity(content, to=self.aliasToJid(mobilenumber))
        self.toLower(outgoingMessage)
        return outgoingMessage._id

    def send_message(self, object):
        mobilenumber = object.to_number.number

        if self.assertConnected():
            ## Find type of message (text, image, vcard)
            if hasattr(object , 'text_delivery'):
                if sys.version_info >= (3, 0):
                    text_message = object.text_delivery.message_text.text.encode("utf-8")

                object.whatsapp_message_id = self.send_text_message(mobilenumber, text_message)
                object.save()
                
            elif hasattr(object, 'image_delivery') and os.path.isfile(object.image_delivery.message_image.image.path):
                image = object.image_delivery.message_image.image.path
                self.media_send(mobilenumber, image, RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE, object=object)
            
            elif hasattr(object , 'vcard_delivery'):
                pass
    
            # self.output("Sent A New Message" + str(mobilenumber) + str(content))
            return True
        return False

    @ProtocolEntityCallback("ack")
    def onAck(self, entity):
        date = datetime.datetime.fromtimestamp(int(entity.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        if ((entity.getClass() == "message") and (entity.tag == "ack")):
            object = Delivery_Status.objects.filter(whatsapp_message_id=entity._id)
            if len(object) > 0:
                object = object[0]
                object.delivery_status = 1
                object.delivered_time = date
                object.save()
            print(entity.getParticipant(), entity.getClass(), entity.tag, date)
