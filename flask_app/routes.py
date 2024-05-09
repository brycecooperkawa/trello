# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
import urllib.parse
from . import socketio
db = database()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
    # Reverse encryption of email
    if 'email' in session:
        user = session['email']
        email = db.reversibleEncrypt('decrypt', user)
        return email
    else:
	    return 'Unknown'

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signUp():
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('email', default=None)
    session.pop('users_board_names', default=None)
    session.pop('users_boards', default=None)
    session.pop('board_name', default=None)
    return redirect('/')

@app.route('/processlogin', methods = ["POST"])
def processlogin():
	# Get email and password from the request form data
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    email = form_fields['email']
    password = form_fields['password']

    # Authenticate user using the database
    authorize = db.authenticate(email, password)

    # If authorized then return success
    if authorize.get('success'):
        # Pass email to session for display
        session['email'] = db.reversibleEncrypt('encrypt', email)
        status = {'success': 1}
    # If not authorized return failure
    else:
        status = {'failure': 0, 'error': 'Invalid email or password'}
    
    return json.dumps(status)

@app.route('/processsignup', methods = ["POST"])
def processSignUp():
	# Get email and password from the request form data
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    email = form_fields['email']
    password = form_fields['password']

    # Authenticate user using the database
    createUser = db.createUser(email, password, role='user')

    # If authorized then return success
    if createUser.get('success'):
        # Pass email to session for display
        session['email'] = db.reversibleEncrypt('encrypt', email)
        status = {'success': 1}
    # If not authorized return failure
    else:
        status = {'failure': 0, 'error': 'User with this email already exists'}
    
    return json.dumps(status)


#######################################################################################
# CHATROOM RELATED
#######################################################################################
@socketio.on('joined', namespace='/chat')
def joined(message):
    current_room = message['room']
    join_room(current_room)
    user = getUser()
    emit('status', {'msg': user + ' has entered the room.', 'sender': user}, room=current_room)
    
@socketio.on('left', namespace='/chat')
def left(message):
    current_room = message['room']
    user = getUser()
    emit('status', {'msg': user + ' has left the room.', 'sender': user}, room=current_room)

@socketio.on('message', namespace='/chat')
def message(message):
    current_room = message['room']
    user = getUser()
    emit('status', {'msg': message['message'], 'sender': user}, room=current_room)


#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
    user = getUser()
    if user == "Unknown":
        return redirect('/login')
    else:
        return redirect('/home')

@app.route('/home')
@login_required
def home():
	return render_template('home.html', user=getUser())

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

#######################################################################################
# BOARD RELATED
#######################################################################################
@app.route('/board')
@login_required
def board():
    # Check that all neccessary info exists
    if not session['users_boards']:
        return json.dumps({'failure': 0, 'error': 'There was an error loading the users boards'})
    if not session['board_name']:
        return json.dumps({'failure': 0, 'error': 'There was an error loading the users board name'})

    # Pass board id to db to get all information related to that board, data stored in a dict
    board_data = db.getBoardData(session['users_boards'][session['board_name']])
    return render_template('board.html', board_data = board_data, board_name = session['board_name'], user = db.reversibleEncrypt('decrypt', session['email']))

@app.route('/existingboards')
def existingboards():
    # Navigate to existing boards and use the board names to display links to each existing board
    return render_template('existingboards.html', board_names=session['users_board_names'], user = db.reversibleEncrypt('decrypt', session['email']))

@app.route('/processcreateboard', methods = ["POST"])
def processCreateBoard():
	# Get board name and users from the request form data
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    name = form_fields['name']
    users = form_fields['users']

    # Convert the users string to a list
    users_list = eval(users)

    # Get the creator to add to the list of users and add to the list of users
    creator = getUser()
    if creator != "Unknown":
        users_list.append(creator)

    # Check to make sure that all users entered are existing/valid users
    check_users = db.checkAssociatedUsers(users_list)

    # If the check users fail return failure
    if check_users.get('success'):
        print("Users valid")
    else:
        status = {'failure': 0, 'error': 'There is an invalid user on this board'}
        return json.dumps(status)

    # Create the board using the database
    create_board = db.createBoard(name, users_list)

    # If created then return success
    if create_board.get('success'):
        # Update the users boards in session after creation
        boards = db.getUserBoards(creator)
        # Convert to list from string for easy iteration
        boards = eval(boards)
        # List that will store names
        board_names = []
        # Query to find the names of all boards
        for id in boards:
            query = "SELECT name FROM boards WHERE board_id = %(id)s"
            parameters = {"id": id}
            # Query and get the result of the board search
            check = db.query(query, parameters)
            board_names.append(check[0]['name'])
        # Store board names in session
        session['users_board_names'] = board_names
        # Dictionary of the boards with the key as name and value as id
        board_dict = dict(zip(board_names, boards))
        # Store dict in session
        session['users_boards'] = board_dict

        status = {'success': 1}
    # If not created return failure
    else:
        status = {'failure': 1, 'error': 'A board with this name is already registered'}

    return json.dumps(status)

@app.route('/processgetexistingboards', methods = ["POST"])
def processGetExistingBoards():
    # Use the current user to get associated boards
    user = getUser()
    boards = db.getUserBoards(user)

    # Convert to list from string for easy iteration, check if any boards exist
    if boards != "":
        boards = eval(boards)
    else:
        status = {'failure': 1}
        return json.dumps(status)

    # List that will store names
    board_names = []

    # Query to find the names of all boards
    for id in boards:
        query = "SELECT name FROM boards WHERE board_id = %(id)s"
        parameters = {"id": id}
        # Query and get the result of the board search
        check = db.query(query, parameters)
        board_names.append(check[0]['name'])

    # Store board names in session
    session['users_board_names'] = board_names

    # Dictionary of the boards with the key as name and value as id
    board_dict = dict(zip(board_names, boards))

    # Store dict in session
    session['users_boards'] = board_dict


    # Return board names to the js function
    status = {'success': 1}
    return json.dumps(status)

@app.route('/processboardname', methods = ["POST"])
def processboardname():
	# Get board selected name from the data
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    name = form_fields['name']
    
    # Store board name in session
    session['board_name'] = name

    status = status = {'success': 1}
    return json.dumps(status)

@app.route('/processcreatecard', methods = ["POST"])
def processCreateCard():
    # Get board selected name from the data
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    list_id = form_fields['list_id']
    description = form_fields['description']

    # Create the card in the database
    create_card = db.createCard(list_id, description)
    
    # Return check
    if create_card.get('success'):
        # Emit socket.io event to notify all users about the new card
        socketio.emit('new_card', {'list_id': list_id, 'description': description, 'card_id': create_card.get('card_id')}, namespace='/board')
        status = {'success': 1}
    else:
        status = {'failure': 0}
    
    return json.dumps(status)

@app.route('/processeditcard', methods = ["POST"])
def processEditCard():
    # Get board selected name from the data
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    card_id = form_fields['card_id']
    description = form_fields['description']

    # Create the card in the database
    edit_card = db.editCard(card_id, description)
    
    # Return check
    if edit_card.get('success'):
        # Emit socket.io event to notify all users about the edited card
        socketio.emit('edit_card', {'card_id': card_id, 'description': description}, namespace='/board')
        status = {'success': 1}
    else:
        status = {'failure': 0}
    
    return json.dumps(status)

@app.route('/processdeletecard', methods = ["POST"])
def processDeleteCard():
    # Get board selected name from the data
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    card_id = form_fields['card_id']

    # Deletes the card in the database
    delete_card = db.deleteCard(card_id)
    
    # Return check
    if delete_card.get('success'):
        # Emit socket.io event to notify all users about the deleted card
        socketio.emit('delete_card', {'card_id': card_id}, namespace='/board')
        status = {'success': 1}
    else:
        status = {'failure': 0}
    
    return json.dumps(status)

@app.route('/processmovecard', methods = ["POST"])
def processMoveCard():
    # Get board selected name from the data
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    card_id = form_fields['card_id']
    list_id = form_fields['list_id']

    print(card_id, list_id)

    # Moves the card in the database
    move_card = db.moveCard(card_id, list_id)
    
    # Return check
    if move_card.get('success'):
        # Emit socket.io event to notify all users about the deleted card
        socketio.emit('move_card', {'card_id': card_id, 'list_id': list_id}, namespace='/board')
        status = {'success': 1}
    else:
        status = {'failure': 0}
    
    return json.dumps(status)

#######################################################################################
# BOARD RELATED SOCKET STUFF
#######################################################################################
@socketio.on('new_card', namespace='/board')
def handle_new_card(data):
    # Broadcast the new card data to all clients
    emit('new_card', data)

