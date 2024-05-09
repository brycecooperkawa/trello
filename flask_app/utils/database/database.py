import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['boards', 'lists', 'cards', 'users']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        # Create query and parameters that will be used to check if a user with the entered email exists
        query = "SELECT * FROM users WHERE email = %(email)s"
        parameters = {"email": email}

        # Query and check if user with given email exists
        check = self.query(query, parameters)

        # If a user exists then fail
        if check:
            return {'failure': 0}
        # If a user doesn't exist then insert the row with new user info and return success
        else:
            self.insertRows('users',['user_id','role','email','password'],[['0', role, email, self.onewayEncrypt(password)]])
            return {'success': 1}

    def authenticate(self, email='me@email.com', password='password'):
        # Create query and parameters that will be used to check if a user with the entered email and password exists
        query = "SELECT * FROM users WHERE email = %(email)s AND password = %(password)s"
        parameters = {"email": email, "password": self.onewayEncrypt(password)}

        # Query and check if user with given email and password exists
        check = self.query(query, parameters)

        # If they exist then return success
        if check:
            return {'success': 1}
        # If they don't exist return failure
        else:
            return {'failure': 0}
        

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message
    
#######################################################################################
# Boards related
#######################################################################################
    # Gets all the boards related to the current user
    def getUserBoards(self, email='me@email.com'):
        # Query to find all boards associated with given email
        query = "SELECT board_ids FROM users WHERE email = %(email)s"
        parameters = {"email": email}
        # Query and get the result of the board search
        check = self.query(query, parameters)
        print(check)

        # Get just the board numbers from the return
        if check == [] or check == [{'board_ids': None}]:
            boards = ""
        else:
            boards = check[0]['board_ids']

        return boards
    
    # Creates a new board
    def createBoard(self, name, users):
        # Query to see if a board with the given name already exists
        query = "SELECT * FROM boards WHERE name = %(name)s"
        parameters = {"name": name}
        # Query and get the result of the board name search
        check = self.query(query, parameters)

        if check != []:
            return {'failure': 0}

        # Create the board entry in the table
        self.insertRows('boards',['board_id','name'],[['0', name]])

        # Query to get the board_id from the newly created board
        query = "SELECT * FROM boards WHERE name = %(name)s"
        parameters = {"name": name}
        # Query and get the result of the newly created board
        check = self.query(query, parameters)

        # Extract board_id from the board
        board_id = check[0]['board_id']

        # Create default lists for board
        self.insertRows('lists',['list_id','board_id','name'],[['0', board_id, "To Do"]])
        self.insertRows('lists',['list_id','board_id','name'],[['0', board_id, "Doing"]])
        self.insertRows('lists',['list_id','board_id','name'],[['0', board_id, "Completed"]])

        # Update 'board_ids' for the specified users (Connect users to board)
        for user in users:
            query = "SELECT * FROM users WHERE email = %(email)s"
            parameters = {"email": user}
            # Query and get the result of the specified user
            check = self.query(query, parameters)

            # Extract existing board_ids or create an empty list if it's None
            existing_board_ids = check[0].get('board_ids')
            # If nothing entered then make a blank list
            if existing_board_ids is None:
                existing_board_ids = []
            # Convert to string to list if not none
            else:
                string = existing_board_ids[1:-1] 
                string = string.split(',')
                existing_board_ids = [int(num) for num in string] 

            # Check if board_id already exists in the list
            if board_id not in existing_board_ids:
                # Append the new board_id to the list
                existing_board_ids.append(board_id)

                # Update 'board_ids' for the user
                update_query = "UPDATE users SET board_ids = %(board_ids)s WHERE email = %(email)s"
                update_parameters = {"board_ids": json.dumps(existing_board_ids), "email": user}
                self.query(update_query, update_parameters)

        return {'success': 1}
    
    # Checks all users associated with created board, if a user is not valid then will fail
    def checkAssociatedUsers(self, users):
        # Will return success if all users are valid
        status = {'success': 1}

        # Go through all users and check that they exist
        for user in users:
            # Query to check that user exists in users table
            query = "SELECT * FROM users WHERE email = %(email)s"
            parameters = {"email": user}
            # Query and check if user with given email exists
            check = self.query(query, parameters)

            if check == []:
                status = {'failure': 0}
        
        return status
    
    # Gets all data related to the current board and stores it in a dict
    def getBoardData(self, board_id):
            # Connect to mySQL database
            cnx = mysql.connector.connect(host     = self.host,
                                        user     = self.user,
                                        password = self.password,
                                        port     = self.port,
                                        database = self.database,
                                        )
            cursor = cnx.cursor()

            # Will store all board data in a dictionary
            board_dict = {}

            # Get all list rows
            cursor.execute("SELECT * FROM lists WHERE board_id = " + str(board_id))
            list_rows = cursor.fetchall()

            # Organize list information into dictionary
            for list in list_rows:
                list_id, board_id, name = list
                board_dict[list_id] = {
                    'board_id' : board_id,
                    'name' : name,
                    'cards' : {}
                }

                # Get all cards for each list
                cursor.execute("SELECT * FROM cards WHERE list_id=%s", (list_id,))
                card_rows = cursor.fetchall()

                # Organize position information into corresponding section of dictionary
                for card in card_rows:
                    card_id, list_id, description = card
                    board_dict[list_id]['cards'][card_id] = {
                        'card_id' : card_id,
                        'list_id' : list_id,
                        'description' : description,
                    }
            
            # Commit changes to database and close connection
            cursor.close()
            cnx.close()

            return board_dict

    # Creates a new card
    def createCard(self, list_id, description):
        # Create the card in the table
        self.insertRows('cards',['card_id', 'list_id', 'description'],[['0', list_id, description]])

        # Get card id to pass back as well
        query = "SELECT * FROM cards ORDER BY card_id DESC LIMIT 1;"
        check = self.query(query, None)

        status = {'success': 1, 'card_id': check[0]['card_id']}
        return status
    
    # Edits the card with the given id's description
    def editCard(self, card_id, description):
        # Update card description
        query = "UPDATE cards SET description = %(description)s WHERE card_id = %(card_id)s"
        parameters = {"description": description, "card_id": card_id}
        self.query(query, parameters)

        return {'success': 1}
    
    # Delete card with given id
    def deleteCard(self, card_id):
        # Delete card query
        query = "DELETE FROM cards WHERE card_id = %(card_id)s"
        parameters = {"card_id": card_id}
        self.query(query, parameters)

        return {'success': 1}
    
    # Move card with given id and list id
    def moveCard(self, card_id, list_id):
        # Move card query
        query = "UPDATE cards SET list_id = %(list_id)s WHERE card_id = %(card_id)s"
        parameters = {"list_id": list_id, "card_id": card_id}
        self.query(query, parameters)

        return {'success': 1}
