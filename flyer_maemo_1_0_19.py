import socket

debug = True

## Trace debugging messages.
#  @param aString String to be printed.
def printd( aString ):
    if debug:
        print aString

# FlyerSettings
# define the default settings
class FlyerSettings( dict ):
    ## The constructor
    #  @param self: The object pointer.
    def __init__( self ):
        dict.__init__(self)
        self["SERVER"]  = "127.0.0.1"
        self["PORT"]  = "843"
        self["MAX_CLIENT"] = 2000
        self["BUFFER_SIZE"] = 1024
        self["FLYER_VERSION"] = "1,0,19"
        self["POLICY_FILE"] = _policyFile ='<?xml version="1.0" encoding="UTF-8"?><cross-domain-policy xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.adobe.com/xml/schemas/PolicyFileSocket.xsd"><allow-access-from domain="*" to-ports="*" secure="false" /><site-control permitted-cross-domain-policies="master-only" /></cross-domain-policy>\0'
        
# Flyer Maemo
# Define the hello world application
class FlyerMaemo:
    ## The constructor.
    #  @param self: The object pointer.
    #  @param aFilePath: file path
    def __init__( self, aFilePath=None ):
        if(aFilePath is not None):
            self._filePath = aFilePath

    def _helloMaemo(self, aCallback=None):
        printd("Hello maemo")
        return "hello maemo"

# FlyerServerSocket
class FlyerServerSocket:
    ## The constructor.
    #  @param self: The object pointer.
    #  @param aHost: Host name to connect to.
    #  @param aPort: Port on the host to bind.
    #  @param aMaxClient: Maximum number of concurrent connection.
    def __init__( self, aHost, aPort, aMaxClient):
        self._connector = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self._connector.bind ( ( str(aHost), int(aPort) ) )
        self._connector.listen ( int(aMaxClient) )
        self._channel = None
        self._details = None
        self._running = 1
        self._iMaxClient = int(aMaxClient)
        self._setCommands()

        printd("Flyer Interface: (%s:%s) - concurrent connection: %s"%(aHost, 
                                                                     aPort, 
                                                                     aMaxClient))
    def _setCommands( self ):
        self._iFlyerMaemo = FlyerMaemo()
        self._iCommands = {}
        self._iCommands["sayHello"] = self._iFlyerMaemo._helloMaemo

    ## Broadcast the message to connected clients.
    #  @param self: The object pointer
    #  @param aText: Sends a message to the client
    def _broadcastMessage(self, aText):
        aText += '\0'
        self._channel.send(aText)

    ## Watch for channel incoming requests.
    #  @param self: The object pointer.
    #  @param aData: Data received from the client
    def _channelWatcher( self, aData ):
        msg = aData.replace("\0", "")
        arrData = msg.split("|")
        iParametersDict = {}

        # printd("\n\nMessage received: " + aData)

        if("policy-file-request" not in msg):
            if msg is not None:
                iParametersDict['COMMAND'] = arrData[0] # command name
                iParametersDict[''] = arrData[1]        # parameters
                # printd("Received command " + arrData[0])
            try:
                self._broadcastMessage( self._iCommands[iParametersDict['COMMAND']]() )
                block = ""
                while "exit" not in block:
                      # printd(len(block))
                      block = self._channel.recv( FlyerSettings()["BUFFER_SIZE"] )
                      if(len(block) > 0):
                         self._channelWatcher( block )
                         break
            except KeyError:
                printd("Invalid Command. Details Error #0001")
        else:
            self._channel.send( FlyerSettings()["POLICY_FILE"] )

        #self._channelWatcher( self._channel.recv( FlyerSettings()["BUFFER_SIZE"] ))

    ## Listen interface for incomming connection. Handle incomming connection request.
    #  @param self: The object pointer.
    def _connectionHandler( self ):
        printd("Wait for incoming connection...")
        while self._running:
            channel, details = self._connector.accept()
            self._channel = channel
            self._details = details
            if self._running:
                printd( 'New connection with: ' + str(details) )
                self._channel.setblocking( 1 )
                #self._channel.recv(FlyerSettings()["BUFFER_SIZE"], cb=self._channelWatcher)
                self._channelWatcher( self._channel.recv( FlyerSettings()["BUFFER_SIZE"] ))
                ##printd( 'host: ' + str(details[0]) )
                #printd( 'port: ' + str(details[1]) )
        printd("Closing incoming connection")

    ## Start the handler
    #  @param self the object pointer.
    def start( self ):
        printd( "Starting Flyer Framework for Maemo v." + FlyerSettings()["FLYER_VERSION"] )
        self._connectionHandler()
        
    ## Close server
    #  @param self The object pointer.
    #  @param aFrame Frame.    
    def close( self ):
        printd("Closing FlyerFramework")
        self._running = 0
  
## FlyerFramework singletong
class FlyerFramework( object ): 
    ## Stores the unique Singleton instance-
    _iInstance = None
    
    ## Flyer class declaration
    class FlyerFrameworkClass:
        ## The constructor.
        #  @param self: The object pointer.
        def __init__( self ):
            self._iSocketServer = None

        ## Start the server.
        #  @param self The object pointer.
        def start(self):
            self._iSocketServer = FlyerServerSocket(
                                            FlyerSettings()["SERVER"],
                                            FlyerSettings()["PORT"],
                                            FlyerSettings()["MAX_CLIENT"])
            self._iSocketServer.start()
            printd("FlyerFramework started")

        ## Stop the server.
        #  @param self The object pointer.
        def stop(self):
            if self._iSocketServer:
                self._iSocketServer.close()
                del self._iSocketServer
                self._iSocketServer = None
                printd("FlyerFramework stopped")
        
        ## Restart server.
        #  @param self The object pointer.    
        def restart(self):
            printd("Restarting FlyerFramework")
            self.stop()
            self.start()

        ## The destructor
        # @param self: The object pointer
        def __del__( self ):
            self.stop()
 
    ###########################################################################
    # Singleton accessors
    ###########################################################################
                
    ## The constructor
    #  @param self The object pointer.
    def __init__( self ):
        # Check whether we already have an instance
        if FlyerFramework._iInstance is None:
            # Create and remember instanc
            FlyerFramework._iInstance = FlyerFramework.FlyerFrameworkClass()
 
        # Store instance reference as the only member in the handle
        self.__dict__['_EventHandler_instance'] = FlyerFramework._iInstance
    
    
    ## Delegate access to implementation.
    #  @param self The object pointer.
    #  @param attr Attribute wanted.
    #  @return Attribute
    def __getattr__(self, aAttr):
        return getattr(self._iInstance, aAttr)
 
 
    ## Delegate access to implementation.
    #  @param self The object pointer.
    #  @param attr Attribute wanted.
    #  @param value Vaule to be set.
    #  @return Result of operation.
    def __setattr__(self, aAttr, aValue):
        return setattr(self._iInstance, aAttr, aValue )

## Flyer daemon server class.
class FlyerDaemon:
    ## Run the server
    #  @param self The object pointer.
    def run(self):
        #self._flyerLock = e32.Ao_lock()
        FlyerFramework().start()
        #self._flyerLock.wait()

    ## Destructor. Stops the networking servers
    #  @param self The object pointer.
    def close(self):
        printd("Closing Flyer Framework")
        FlyerFramework().stop()
        appuifw.app.set_exit()
        #self._flyerLock.signal()

flyerDaemon = FlyerDaemon()
flyerDaemon.run()
