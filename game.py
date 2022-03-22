from os import remove
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
MAX_DX = 100
MAX_DY = 100
DDX = 800
DDY = 800

T_STEP = 50000 #50 milliseconds
TIMEOUT_TIME = 10 #seconds

mspf = 0

class Game:

    def __init__(self, roomId):
        self.roomId = roomId
        self.timeOfLastBroadcast = dt.now()
        self.players = {} #playerId : Player
        self.player1 = None
        self.player2 = None
        self.player3 = None
        self.player4 = None

    def addPlayer(self, name, playerId):
        # playerId = id
        # n = len(self.players)
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
        # try:
        if self.player1 != None and playerId == self.player1.playerId:
            self.player1 = None
        if self.player2 != None and playerId == self.player2.playerId:
            self.player2 = None
        if self.player3 != None and playerId == self.player3.playerId:
            self.player3 = None
        if self.player4 != None and playerId == self.player4.playerId:
            self.player4 = None
        del self.players[playerId]
        # except:
        #     return 'remove player error'


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
            playerDict['players'][player.playerNumStr] = { 'name' : player.name, 'x' : player.x, 'y' : player.y, 'dx' : player.dx, 'dy' : player.dy, 'hasEgg' : player.hasEgg, 'dying' : player.dying, 'remove' : False }
        return playerDict


    def movePlayer(self, playerId, keysPressed):
        player = self.players[playerId]
        #slowing down if no keys pressed
        # maxing out at 0 or max
        delta_t = (dt.now() - player.timeOfLastResponse).microseconds / 1000000
        if keysPressed['leftPressed']:
            if player.dx > MAX_DX * -1:
                player.dx -= DDX * delta_t
                if player.dx < MAX_DX * -1:
                    player.dx = MAX_DX * -1
        elif keysPressed['rightPressed']:
            if player.dx < MAX_DX:
                player.dx += DDX * delta_t
                if player.dx > MAX_DX:
                    player.dx = MAX_DX
        else:
            if player.dx < 0:
                player.dx += DDX * delta_t
                if player.dx > 0:
                    player.dx = 0
            elif player.dx > 0:
                player.dx -= DDX * delta_t
                if player.dx < 0:
                    player.dx = 0
        if keysPressed['upPressed']:
            if player.dy > MAX_DY * -1:
                player.dy -= DDY * delta_t
                if player.dy < MAX_DY * -1:
                    player.dy = MAX_DY * -1
        elif keysPressed['downPressed']:
            if player.dy < MAX_DY:
                player.dy += DDY * delta_t
                if player.dy > MAX_DY:
                    player.dy = MAX_DY
        else:
            if player.dy < 0:
                player.dy += DDY * delta_t
                if player.dy > 0:
                    player.dy = 0
            elif player.dy > 0:
                player.dy -= DDY * delta_t
                if player.dy < 0:
                    player.dy = 0
        
        player.x += player.dx * delta_t
        player.y += player.dy * delta_t
        if player.x > MAX_X:
            player.x = MAX_X
            player.dx = 0
        elif player.x < 0:
            player.x = 0
            player.dx - 0
        if player.y > MAX_Y:
            player.y = MAX_Y
            player.dy = 0
        elif player.y < 0:
            player.y = 0
            player.dy = 0

        return player

    def checkCollisions(self):
        pass

    #keysPressed - { 'leftPressed' : bool, 'rightPressed' : bool, etc. }
    def handleInput(self, playerId, keysPressed):
        player = self.movePlayer(playerId, keysPressed)
        player.updateResponseTime()
        gameUpdate = None
        # if end of time step, check for collisions ?
        delta_t = dt.now() - self.timeOfLastBroadcast
        if delta_t.microseconds >= T_STEP or delta_t.seconds >= 1:
            self.timeOfLastBroadcast = dt.now()
            self.checkCollisions()
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
        return player, gameUpdate

class Player:
    def __init__(self, name, id, playerNumber, x, y):
        self.name = name
        self.playerId = id
        self.playerNumber = playerNumber
        self.playerNumStr = 'player' + str(playerNumber)
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.hasEgg = False
        self.dying = False
        self.timeOfLastResponse = dt.now()

    def updateResponseTime(self):
        self.timeOfLastResponse = dt.now()