from pickle import TRUE
from socket import socket
from flask import Flask, redirect, request, escape, render_template, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
# from html_page import entryPage, gamePage
from game import Game
import string
import random
from datetime import datetime as dt
import os

DEBUG_MODE = False
GAME_DELETE_SECS = 10

roomIds = []
games = {} #roomId : Game

def generateNewRoomId():
    if DEBUG_MODE:
        return 'A'
    chars = string.ascii_uppercase
    id = ''.join(random.choice(chars) for i in range(10))
    while id in roomIds:
        id = ''.join(random.choice(chars) for i in range(10))
    return id



#should check if input is in an acceptable list
def handleInput(roomId, playerId, keysPressed):
    player, gameUpdate = games[roomId].handleInput(playerId, keysPressed)
    if gameUpdate != None:
        socketio.emit("game update", {'gameState' : gameUpdate}, to=roomId)
    return player


# EB looks for an 'application' callable by default.
application = app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret808'
socketio = SocketIO(application)


@application.route("/")
def index():
    return send_file('entryPage.html')

@application.route("/linked")
def linkedJoin():
    if 'room' in request.args.keys():
        roomId = escape(request.args['room'])
        if roomId in roomIds:
            return render_template('linkedEntryPage.html', roomId=roomId)
        else:
            return '400'
    else:
        return '400'

@application.route('/create')
def create_game():
    roomIds_to_remove = []
    for roomId in roomIds:
        if (dt.now() - games[roomId].timeOfLastBroadcast).seconds >= GAME_DELETE_SECS:
            roomIds_to_remove.append(roomId)
    if len(roomIds_to_remove) > 0:
        for r_id in roomIds_to_remove:
            roomIds.remove(r_id)
            del games[r_id]
    if len(games) < 15:
        if 'name' in request.args.keys():
            name = escape(request.args['name'])
            if len(name) > 20:
                return '400'
            roomId = generateNewRoomId()
            roomIds.append(roomId)
            newGame = Game(roomId=roomId)
            games[roomId] = newGame
            playerId = newGame.generateNewPlayerId()
            player = newGame.addPlayer(name, playerId)
            if len(name) == 0:
                name = player.playerNumStr
            return redirect("/game?roomId={0}&name={1}&playerId={2}".format(roomId, name, playerId))
        else:
            return '400'
    else:
        return '500'


@application.route('/join')
def join_game():
    roomId = escape(request.args['existingGameId'])
    if roomId in roomIds and len(games[roomId].players) < 4:
        name = escape(request.args['name'])
        if len(name) > 20:
            return '400'
        playerId = games[roomId].generateNewPlayerId()
        player = games[roomId].addPlayer(name, playerId)
        return redirect("/game?roomId={0}&name={1}&playerId={2}".format(roomId, name, playerId))
    else:
        return '400'


@application.route('/game')
def test():
    if 'roomId' in request.args.keys() and 'name' in request.args.keys():
            roomId = escape(request.args['roomId'])
            userName = escape(request.args['name'])
            playerId = escape(request.args['playerId'])
            if roomId in roomIds:
                return render_template('gamePage.html', roomId=roomId, userName=userName, playerId=playerId)
            else:
                return '400'
    # return gamePage
    # return send_file('static/gamePage.html')

@socketio.on('connect')
def connect_client():
    emit('after connect')


@socketio.on('join event')
def client_join(data):
    #should have try blocks for phony roomIds
    try:
        if 'roomId' in data.keys() and 'name' in data.keys():
            room = escape(data['roomId'])
            name = escape(data['name'])
            playerId = escape(data['playerId'])
            if room not in roomIds:
                return '400'
            game = games[room]
            # if len(game.players) < 4:
                # player = game.addPlayer(name)
            player = game.players[playerId]
            join_room(room)
            emit('join gamestate', { 'playerNumber':player.playerNumStr, 'gamestate': game.getPlayerDict() })
        else:
            return '400'
    except Exception as e:
        if DEBUG_MODE:
            print(e)
        return '400'

@socketio.on('playerInput')
def player_input(data):
    try:
        #if room id or player id aren't a match- disconnect?
        roomId = escape(data['roomId'])
        if roomId not in roomIds:
            return '400'
        playerId = escape(data['playerId'])
        if playerId not in games[roomId].players:
            return '400'
        keysPressed = { 'leftPressed' : False, 'rightPressed': False, 'upPressed' : False, 'downPressed' : False }
        
        leftPressed = escape(data['leftPressed'])
        rightPressed = escape(data['rightPressed'])
        upPressed = escape(data['upPressed'])
        downPressed = escape(data['downPressed'])
        keysPressed['leftPressed'] = leftPressed == 'True'
        keysPressed['rightPressed'] = rightPressed == 'True'# and not (leftPressed == 'True')
        keysPressed['upPressed'] = upPressed == 'True'
        keysPressed['downPressed'] = downPressed == 'True'# and not (upPressed == 'True')
        player = handleInput(roomId, playerId, keysPressed)
        emit('input response', { 'x' : player.x, 'y' : player.y })
    except Exception as e:
        if DEBUG_MODE:
            print('player input error / handle player input error')
            print(e)
        return '400'


if __name__ == "__main__":
    application.debug = DEBUG_MODE
    application.jinja_env.autoescape = True
    if DEBUG_MODE:
        socketio.run(application)
    else:
        socketio.run(application, port=int(os.environ.get('PORT')))
    