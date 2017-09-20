from .layer import YowsupWebLayer
from yowsup.stacks import YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.axolotl.props import PROP_IDENTITY_AUTOTRUST
import sys


class YowsupWebStack(object):

    def __init__(self, encryptionEnabled=True):
        stackBuilder = YowStackBuilder()

        self.stack = stackBuilder\
            .pushDefaultLayers(encryptionEnabled)\
            .push(YowsupWebLayer)\
            .build()
        self.stack.setProp(PROP_IDENTITY_AUTOTRUST, True)

    def start(self):
        print("Starting the Yowsup Client Stack")
        self.stack.broadcastEvent(YowLayerEvent(YowsupWebLayer.EVENT_START))
        
        try:
            self.stack.loop(timeout=0.5, discrete=0.5)
        except AuthError as e:
            print("Auth Error, reason %s" % e)
        except KeyboardInterrupt:
            print("\nYowsdown")
            sys.exit(0)

    def set_credentials(self, credentials):
        self.stack.setCredentials(credentials)

    def get_web_layer(self):
        return self.stack.getLayer(-1)