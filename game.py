import random
import string
from datetime import datetime as dt


PLAYER1X0 = 20
PLAYER1Y0 = 20
PLAYER2X0 = 930
PLAYER2Y0 = 630
PLAYER3X0 = 20
PLAYER3Y0 = 630
PLAYER4X0 = 930
PLAYER4Y0 = 20

MAX_X = 946
MAX_Y = 659
DX = 100
DY = 100

T_STEP_PHYS = 25000 #25 milliseconds
T_STEP_BROADCAST = 50000 #50 milliseconds
TIMEOUT_TIME = 10 #seconds

mspf = 0

class Game:

    def __init__(self, roomId):
        self.roomId = roomId
        self.timeOfLastPhys = dt.now()
        self.timeOfLastBroadcast = dt.now()
        self.players = {} #playerId : Player
        self.player1 = None
        self.player2 = None
        self.player3 = None
        self.player4 = None

    def addPlayer(self, name, playerId):
        if self.player1 == None:
            player = Player(name, playerId, 1, PLAYER1X0, PLAYER1Y0)
            self.player1 = player
            self.players[player.playerId] = player
        elif self.player2 == None:
            player = Player(name, playerId, 2, PLAYER2X0, PLAYER2Y0)
            self.player2 = player
            self.players[player.playerId] = player
        elif self.player3 == None:
            player = Player(name, playerId, 3, PLAYER3X0, PLAYER3Y0)
            self.player3 = player
            self.players[player.playerId] = player
        elif self.player4 == None:
            player = Player(name, playerId, 4, PLAYER4X0, PLAYER4Y0)
            self.player4 = player
            self.players[player.playerId] = player
        else:
            return None
        return player

    def removePlayer(self, playerId):
        if self.player1 != None and playerId == self.player1.playerId:
            self.player1 = None
        if self.player2 != None and playerId == self.player2.playerId:
            self.player2 = None
        if self.player3 != None and playerId == self.player3.playerId:
            self.player3 = None
        if self.player4 != None and playerId == self.player4.playerId:
            self.player4 = None
        del self.players[playerId]


    def generateNewPlayerId(self):
        digits = string.digits
        id = ''.join(random.choice(digits) for i in range(10))
        while id in self.players.keys():
            id = ''.join(random.choice(digits) for i in range(10))
        return id


    def getPlayerDict(self):
        playerDict = {}
        playerDict['players'] = {}
        for playerId in self.players.keys():
            player = self.players[playerId]
            playerDict['players'][player.playerNumStr] = { 'name' : player.name, 'x' : player.x, 'y' : player.y, 'walking' : player.walking, 'hasEgg' : player.hasEgg, 'dying' : player.dying, 'lastInputNum' : player.lastReceivedInputNum, 'remove' : False }
        return playerDict


    def movePlayer(self, playerId, keyPressed, delta_t):
        player = self.players[playerId]
        if keyPressed == 'leftPressed':
            player.x -= DX * delta_t
        elif keyPressed == 'rightPressed':
            player.x += DX * delta_t
        elif keyPressed =='upPressed':
            player.y -= DY * delta_t
        elif keyPressed == 'downPressed':
            player.y += DY * delta_t
            
        if player.x > MAX_X:
            player.x = MAX_X
        elif player.x < 0:
            player.x = 0
        if player.y > MAX_Y:
            player.y = MAX_Y
        elif player.y < 0:
            player.y = 0

    def checkCollisions(self):
        pass

    #keysPressed - { 'leftPressed' : bool, 'rightPressed' : bool, etc. }
    def handleInput(self, playerId, keysPressed, inputNum):
        self.players[playerId].addInput(keysPressed, inputNum)
        gameUpdate = None
        phys_dt = dt.now() - self.timeOfLastPhys
        if phys_dt.microseconds >= T_STEP_PHYS or phys_dt.seconds >= 1:
            for playerKey in self.players.keys():
                pl = self.players[playerKey]
                
                if pl.inputCount > 0 and len(pl.inputCounts.keys()) == 0:
                    pl.walking = False
                elif len(pl.inputCounts.keys()) > 0:
                    pl.walking = True
                for inp in pl.inputCounts:
                    d_t = pl.inputCounts[inp] / pl.inputCount * phys_dt.microseconds / 1000000.0
                    self.movePlayer(playerKey, inp, d_t)
                pl.inputCount = 0
                pl.inputCounts = {}
            self.checkCollisions()
            self.timeOfLastPhys = dt.now()
        broadcast_dt = dt.now() - self.timeOfLastBroadcast
        if broadcast_dt.microseconds >= T_STEP_BROADCAST or broadcast_dt.seconds >= 1:
            self.timeOfLastBroadcast = dt.now()
            gameUpdate = self.getPlayerDict()
            removePlayerIdList = []
            removePlayer = False
            for playerKey in self.players.keys():
                pl = self.players[playerKey]
                if (dt.now() - pl.timeOfLastResponse).seconds >= TIMEOUT_TIME:
                    removePlayerIdList.append(playerKey)
                    removePlayer = True
                    gameUpdate['players'][pl.playerNumStr]['remove'] = True
            if removePlayer:
                for p_id in removePlayerIdList:
                    self.removePlayer(p_id)
        return gameUpdate

class Player:
    def __init__(self, name, id, playerNumber, x, y):
        self.name = name
        self.playerId = id
        self.playerNumber = playerNumber
        self.playerNumStr = 'player' + str(playerNumber)
        self.x = x
        self.y = y
        self.walking = False
        self.hasEgg = False
        self.dying = False
        self.timeOfLastResponse = dt.now()
        self.lastReceivedInputNum = 0
        self.inputCount = 0
        self.inputCounts = {}

    def addInput(self, keysPressed, inputNum):
        self.timeOfLastResponse = dt.now()
        self.inputCount += 1
        self.lastReceivedInputNum = inputNum
        for inp in keysPressed.keys():
            if keysPressed[inp]:
                if inp in self.inputCounts.keys():
                    self.inputCounts[inp] += 1
                else:
                    self.inputCounts[inp] = 1
