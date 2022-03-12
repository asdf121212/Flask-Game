# from gevent import monkey
from socket import socket
from flask import Flask, redirect, request, escape, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from html_page import entryPage, gamePage
from game import Game
import string
import random


roomIds = []
games = {} #roomId : Game

def generateNewRoomId():
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
    return entryPage


@application.route('/create')
def create_game():
    if len(games) < 10:
        if 'name' in request.args.keys():
            name = escape(request.args['name'])
            roomId = generateNewRoomId()
            roomIds.append(roomId)
            newGame = Game(roomId=roomId)
            games[roomId] = newGame
            playerId = newGame.generateNewPlayerId()
            player = newGame.addPlayer(name, playerId)
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
        playerId = games[roomId].generateNewPlayerId()
        player = games[roomId].addPlayer(name, playerId)
        return redirect("/game?roomId={0}&name={1}&playerId={2}".format(roomId, name, playerId))
    else:
        return '400'


@application.route('/game')
def test():
    return gamePage


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
            game = games[room]
            # if len(game.players) < 4:
                # player = game.addPlayer(name)
            player = game.players[playerId]
            join_room(room)
                # emit('playerId', {'playerId' : player.playerId, 'playerNumber': player.playerNumber, 'players': game.getPlayerDict()})
            emit('join gamestate', { 'playerNumber':player.playerNumStr, 'players': game.getPlayerDict() })
        else:
            return '400'
    except:
        return '400'

@socketio.on('playerInput')
def player_input(data):
    try:
        roomId = escape(data['roomId'])
        playerId = escape(data['playerId'])
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
    except:
        return '400'

# run the app.
if __name__ == "__main__":
    # monkey.patch_all()
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = False
    # application.run()
    socketio.run(application)

# @application.route("/app", methods = ['POST', 'GET'])
# def app_post():
#     if request.method == 'POST':
#         return '{ "response" : "asdf" }'
#     elif request.method == 'GET':
#         return '{ "response" : "vsdf" }'

# @application.route("/app/join")
# def app_join():
#     if request.method == 'GET':
#         return ''

# def authenticate(args):
#     return True

# @socketio.on('connect')
# def test_connect():
#     if not authenticate(request.args):
#         raise ConnectionRefusedError
#     emit('after connect', {'data':'test connect'})

# @socketio.on('message')
# def handle_json(message):
#     print('received message: ' + str(message))
#     emit('update value', message)

# The names message, json, connect and disconnect are reserved and cannot be used for named events.

#rooms-- join_room() and leave_room() -- Example:

        # from flask_socketio import join_room, leave_room

        # @socketio.on('join')
        # def on_join(data):
        #     username = data['username']
        #     room = data['room']
        #     join_room(room)
        #     send(username + ' has entered the room.', to=room)

        # @socketio.on('leave')
        # def on_leave(data):
        #     username = data['username']
        #     room = data['room']
        #     leave_room(room)
        #     send(username + ' has left the room.', to=room)

#emit and socketio.emit argument to="<room_name>"
#Since all clients are assigned a personal room, to address a message to a single client,
#the session ID of the client can be used as the to argument.

#socketio.emit is different from regular emit, needs no context and broadcast is assumed
#def broadcast_without_context():
    #socketio.emit('some event', {'data': 42})

# @socketio.on('slider value changed')
# def value_changed(message):
#     print(message)
#     emit('update value', message, broadcast=True)


# def start_emitting():
#     for i in range(15):
#         emit('skielbijel', broadcast=True)
