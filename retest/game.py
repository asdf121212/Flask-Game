import random
import string
from datetime import datetime as dt


PLAYER1X0 = 100
PLAYER1Y0 = 300
PLAYER2X0 = 400
PLAYER2Y0 = 100
PLAYER3X0 = 600
PLAYER3Y0 = 300
PLAYER4X0 = 400
PLAYER4Y0 = 300

MAX_X = 990
MAX_Y = 690
MAX_DX = 5
MAX_DY = 5
DDX = 0.7
DDY = 0.7

T_STEP = 50000 #milliseconds

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
        if playerId == self.player1.playerId:
            self.player1 = None
        if playerId == self.player2.playerId:
            self.player2 = None
        if playerId == self.player3.playerId:
            self.player3 = None
        if playerId == self.player4.playerId:
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
        for playerId in self.players.keys():
            player = self.players[playerId]
            playerDict[player.playerNumStr] = { 'name' : player.name, 'x' : player.x, 'y' : player.y }
        return playerDict


    def movePlayer(self, playerId, keysPressed):
        player = self.players[playerId]
        #slowing down if no keys pressed
        # maxing out at 0 or max
        if keysPressed['leftPressed']:
            if player.dx > MAX_DX * -1:
                player.dx -= DDX
                if player.dx < MAX_DX * -1:
                    player.dx = MAX_DX * -1
        elif keysPressed['rightPressed']:
            if player.dx < MAX_DX:
                player.dx += DDX
                if player.dx > MAX_DX:
                    player.dx = MAX_DX
        else:
            if player.dx < 0:
                player.dx += DDX
                if player.dx > 0:
                    player.dx = 0
            elif player.dx > 0:
                player.dx -= DDX
                if player.dx < 0:
                    player.dx = 0
        if keysPressed['upPressed']:
            if player.dy > MAX_DY * -1:
                player.dy -= DDY
                if player.dy < MAX_DY * -1:
                    player.dy = MAX_DY * -1
        elif keysPressed['downPressed']:
            if player.dy < MAX_DY:
                player.dy += DDY
                if player.dy > MAX_DY:
                    player.dy = MAX_DY
        else:
            if player.dy < 0:
                player.dy += DDY
                if player.dy > 0:
                    player.dy = 0
            elif player.dy > 0:
                player.dy -= DDY
                if player.dy < 0:
                    player.dy = 0
        
        player.x += player.dx
        player.y += player.dy
        if player.x > MAX_X:
            player.x = MAX_X
        elif player.x < 0:
            player.x = 0
        if player.y > MAX_Y:
            player.y = MAX_Y
        elif player.y < 0:
            player.y = 0

        return player

    def checkCollisions(self):
        pass

    #keysPressed - { 'leftPressed' : bool, 'rightPressed' : bool, etc. }
    def handleInput(self, playerId, keysPressed):
        player = self.movePlayer(playerId, keysPressed)

        # if end of time step, check for collisions ?
        if (dt.now() - self.timeOfLastBroadcast).microseconds >= T_STEP:
            self.checkCollisions()
            gameUpdate = self.getPlayerDict()

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