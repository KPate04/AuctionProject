## ITCS 3160-0002, Spring 2024
## Marco Vieira, marco.vieira@charlotte.edu
## University of North Carolina at Charlotte
 
## IMPORTANT: this file includes the Python implementation of the REST API
## It is in this file that yiu should implement the functionalities/transactions   

import flask
import logging, psycopg2, time
from functools import wraps
import random

app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(
        user = "scott",
        password = "tiger",
        host = "db",
        port = "5432",
        database = "dbproj"
    )
    
    return db


##########################################################
## TOKEN VERIFICATION
##########################################################

# Simple token (shown in class)

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'access-token' in flask.request.headers:
            token = flask.request.headers['access-token']

        if not token:
            return flask.jsonify({'message': 'invalid token X'})

        try:
            conn = db_connection()
            cur = conn.cursor()
            cur.execute("delete from tokens where \
               deadline<current_timestamp")
            conn.commit()

            cur.execute("select userid from tokens \
               where token_value= %s",(token,))

            if cur.rowcount==0:
                return flask.jsonify({'message': \
                   'invalid token XX'})
            else:
                current_user=cur.fetchone()[0]
        except (Exception) as error:
            logger.error(f'POST /users - error: {error}')
            conn.rollback()

            return flask.jsonify({'message': 'invalid token XXX'})

        return f(current_user, *args, **kwargs)

    return decorator


# login user using simple tokens
# curl -X PUT http://localhost:8080/login -H 'Content-Type: application/json' -d '{"username": "ssmith", "password": "ssmith_pass"}'

@app.route('/login', methods=['PUT'])
def login_user():
    auth = flask.request.get_json()

    if not auth or 'userid' not in auth \
    or 'password' not in auth:
        return flask.make_response('missing credentials', 401)

    try:
        conn = db_connection()
        cur = conn.cursor()

        statement = 'select 1 from users \
           where userid = %s and password = %s'
        values = (auth['userid'], auth['password'])

        cur.execute(statement, values)

        if cur.rowcount==0:
           response = ('could not verify', 401)
        else:
            response = auth['userid']+ \
               str(random.randrange(111111111,999999999))
            
            statement = "insert into tokens values( %s, %s , \
               current_timestamp + (60 * interval '1 min'))"
            values = (auth['userid'], response)

            cur.execute(statement, values)    

        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /users - error: {error}')
        response = {'status': \
           StatusCodes['internal_error'], \
           'errors': str(error)}

        conn.rollback()
    finally:
        if conn is not None:
            conn.close()

    return response 

##########################################################
## ENDPOINTS
##########################################################

## http://localhost:8080/

@app.route('/')
def landing_page():
    return """

    Hello World (Python)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    ITCS 3160-002, Spring 2024<br/>
    <br/>
    """

## Sign-up
##
## curl -X POST http://localhost:8080/user -H 'Content-Type: application/json' -d '{"usertype": "buyer", "userid": "0", "password": "petey4life"}'
##

@app.route('/users/', methods=['POST'])
def add_users():
    logger.info('POST /user')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /user - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'userid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'userid value not in payload'}
        return flask.jsonify(response)
    if 'password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'password value not in payload'}
        return flask.jsonify(response)
    if 'usertype' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'usertype value not in payload'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'INSERT INTO users (userid, password, usertype) VALUES (%s, %s, %s)'
    values = (payload['userid'], payload['password'], payload['usertype'])

    try:
        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted users {payload["userid"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


## Create a new auction
## POST http://localhost:8080/auction/
## req: itemId, minimumPrice, title, description ...
## res: auctionId

@app.route('/auction/', methods=['POST'])
def add_auction():
    logger.info('POST /auction')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /auction - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'auctiontitle' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'auctiontitle value not in payload'}
        return flask.jsonify(response)
    if 'auction_end' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'auction_end value not in payload'}
        return flask.jsonify(response)
    if 'sellerdesc' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'sellerdesc value not in payload'}
        return flask.jsonify(response)
    if 'users_userid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'users_userid value not in payload'}
        return flask.jsonify(response)
    if 'items_itemid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'items_itemid value not in payload'}
        return flask.jsonify(response)
    # parameterized queries, good for security and performance
    statement = 'INSERT INTO auction (auctiontitle, auction_end, sellerdesc, users_userid, items_itemid) VALUES (%s, %s, %s, %s, %s)'
    values = (payload['auctiontitle'], payload['auction_end'], payload['sellerdesc'], payload['users_userid'], payload['items_itemid'])

    try:
        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': 'Inserted auction'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /auction - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

## List all existing auctions
## GET http://localhost:8080/auctions
## req: none
## res: list of auctions

@app.route('/auctions/', methods=['GET'])
@token_required
def get_all_auctions(current_user):
    logger.info('GET /auctions')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT auctionid, auctiontitle, auction_end, sellerdesc, users_userid, items_itemid FROM auction')
        rows = cur.fetchall()

        logger.debug('GET /auctions - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auctionid': row[0], 'auctiontitle': row[1], 'auction_end': row[2], 'sellerdesc': row[3],'users_userid': row[4],'items_itemid': row[5]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /auctions - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

## Search existing auctions
## GET http://localhost:8080/auctions/{keyword}
## req: none
## res: list of auctions
@app.route('/auctions/<keyword>/', methods=['GET'])
@token_required
def get_auctions(current_user, keyword):
    logger.info('GET /auctions/{keyword}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT auctionid, auctiontitle, auction_end, sellerdesc, users_userid, items_itemid FROM auction where sellerdesc like '%"+keyword+"%' or auctiontitle like '%"+keyword+"%'") #+?+'%'", ('keyword',))
        rows = cur.fetchall()

        logger.debug('GET /auctions/{keyword} - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auctionid': row[0]} #, 'auctiontitle': row[1], 'auction_end': row[2], 'sellerdesc': row[3],'users_userid': row[4],'items_itemid': row[5]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /auctions/{keyword} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

## Retrieve details of an auction
##
## http://localhost:8080/auction/{auctionid}
##

@app.route('/auction/<auctionid>/', methods=['GET'])
@token_required
def get_auction(current_user,auctionid):
    logger.info('GET /auction/{auctionid}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT auctionid, auctiontitle, auction_end, sellerdesc FROM auction where auctionid='+str(auctionid))
        rows = cur.fetchall()

        logger.debug('GET /auction/auctionid - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auctionid': row[0], 'auctiontitle': row[1], 'auction_end': row[2], 'sellerdesc': row[3]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /auction/auctionid - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


## List all auctions in which the user has activity
## GET http://localhost:8080/auctions/user/{userId}
## req: none
## res: list of auctions
@app.route('/auctions/user/<userId>/', methods=['GET'])
@token_required
def get_auctions_user(current_user, userId):
    logger.info('GET /auctions/user/{userId}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT a.auctionid, a.auctiontitle, a.auction_end, a.sellerdesc, a.users_userid, a.items_itemid, b.users_userid FROM auction as a, bids as b where a.auctionid = b.auction_auctionid and b.users_userid = %s', (userId,))
        rows = cur.fetchall()

        logger.debug('GET /auctions/user/{userId} - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auctionid': row[0], 'auctiontitle': row[1], 'auction_end': row[2], 'sellerdesc': row[3]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /auctions/user/{userId} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


## Place a bid in an auction
## POST http://localhost:8080/auction/{auctionId}/{bid}
## req: none
## res: success or error code
@app.route('/auction/<auctionId>/<bid>/<userId>/', methods=['POST'])
def place_bid(auctionId, bid, userId):
    logger.info('POST /auction/{auctionId}/{bid}/{userId}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM auction where auctionid = %s', (auctionId,))
        rows = cur.fetchall()

        if len(rows) == 0:
            response = {'status': StatusCodes['api_error'], 'results': 'auction does not exist'}
            return flask.jsonify(response)

        cur.execute('SELECT * FROM bids where auction_auctionid = %s', (auctionId,))
        rows = cur.fetchall()

        if len(rows) == 0:
            response = {'status': StatusCodes['api_error'], 'results': 'auction does not have any bids'}
            return flask.jsonify(response)

        cur.execute('SELECT * FROM bids where bid_amt < %s and auction_auctionid = %s', (bid, auctionId))
        rows = cur.fetchall()

        if len(rows) == 0:
            response = {'status': StatusCodes['api_error'], 'results': 'bid is not higher than the current highest bid'}
            return flask.jsonify(response)

        statement = 'INSERT INTO bids (auction_auctionid, bid_amt, users_userid) VALUES (%s, %s, %s)'
        values = (auctionId, float(bid), userId)

        cur.execute(statement, values)

        conn.commit()
        response = {'status': StatusCodes['success'], 'results': 'bid placed'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /auction/{auctionId}/{bid} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

## Edit properties of an auction
## PUT http://localhost:8080/auction/{auctionId}
## req: information to be modified
## res: updated auction information
@app.route('/auction/<auctionId>/<userId>', methods=['PUT'])
def edit_auction(auctionId, userId):
    logger.info('PUT /auction/{auctionId}/{userId}')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /auction/{auctionId} - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'auctiontitle' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'auctiontitle value not in payload'}
        return flask.jsonify(response)
    if 'auction_end' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'auction_end value not in payload'}
        return flask.jsonify(response)
    if 'sellerdesc' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'sellerdesc value not in payload'}
        return flask.jsonify(response)
    if 'users_userid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'users_userid value not in payload'}
        return flask.jsonify(response)
    if 'items_itemid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'items_itemid value not in payload'}
        return flask.jsonify(response)

    cur.execute('SELECT usertype FROM users WHERE userid = %s', (payload['users_userid'],))
    user_type = cur.fetchone()[0]

    if user_type != 'seller':
        response = {'status': StatusCodes['api_error'], 'results': 'Only sellers can update auctions'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'UPDATE auction SET auctiontitle = %s, auction_end = %s, sellerdesc = %s, users_userid = %s, items_itemid = %s WHERE auctionid = %s'
    values = (payload['auctiontitle'], payload['auction_end'], payload['sellerdesc'], payload['users_userid'], payload['items_itemid'], auctionId)

    try:
        cur.execute(statement, values)

        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Updated auction {auctionId}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /auction/{auctionId} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

## Write a message on the auction's board
@app.route('/auction/<auctionId>/posts', methods=['POST'])
def write_message(auctionId):
    payload = flask.request.get_json()

    # Save the message to the auction's board in the database
    conn = db_connection()
    cur = conn.cursor()

    if 'post' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'post value not in payload'}
        return flask.jsonify(response)
    if 'users_userid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'users_userid value not in payload'}
        return flask.jsonify(response) 
    if 'auction_auctionid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'auction_auctionid value not in payload'}
        return flask.jsonify(response)

    try:
        statement = 'INSERT INTO posts (post, users_userid, auction_auctionid) VALUES (%s, %s, %s)'
        values = (payload['post'], payload['users_userid'], auctionId)
        cur.execute(statement, values)
        conn.commit()

        response = {'status': StatusCodes['success'], 'results': 'Message posted successfully'}

    except (Exception, psycopg2.DatabaseError) as error:
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

## Immediate Delivery of messages to users

## Outbid notification

## Close auction

## Cancel auction












































## FUNCTIONS THAT ARE NOT NEEDED IN THE FINAL PROJECT



## USERS
## Demo GET
##
## Obtain general list of users
## To use it, access:
##
## http://localhost:8080/usersall/
##

@app.route('/usersall/', methods=['GET'])
@token_required
def get_users(current_user):
    logger.info('GET /usersall')

    logger.debug('userid: {userid}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT userid, password, usertype FROM users')
        rows = cur.fetchall()

        users = []
        for row in rows:
            logger.debug('GET /users - parse')
            logger.debug(row)
            user_data = {'userid': row[0], 'password': row[1], 'usertype': row[2]}
            users.append(user_data)

        response = {'status': StatusCodes['success'], 'results': users}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

# ## USERS
# ## Demo GET
# ##
# ## Obtain user with username <username>
# ##
# ## To use it, access:
# ##
# ## http://localhost:8080/users/1
# ##

# @app.route('/users/<userid>/', methods=['GET'])
# def get_user(userid):
#     logger.info('GET /users/<userid>')

#     logger.debug('userid: {userid}')

#     conn = db_connection()
#     cur = conn.cursor()

#     try:
#         cur.execute('SELECT userid, password, usertype FROM users where userid = %s', (userid,))
#         rows = cur.fetchall()

#         row = rows[0]

#         logger.debug('GET /users/<userid> - parse')
#         logger.debug(row)
#         content = {'userid': row[0], 'password': row[1], 'usertype': row[2]}

#         response = {'status': StatusCodes['success'], 'results': content}

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(f'GET /users/<userid> - error: {error}')
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)



# ## USERS
# ## Demo PUT
# ##
# ## Update a user based on a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ##
# ## curl -X PUT http://localhost:8080/users/1 -H 'Content-Type: application/json' -d '{"userid":"1","password":"petey4life","usertype": "seller"}'
# ##

# @app.route('/users/<userid>', methods=['PUT'])
# def update_users(userid):
#     logger.info('PUT /users/<userid>')
#     payload = flask.request.get_json()

#     conn = db_connection()
#     cur = conn.cursor()

#     logger.debug(f'PUT /users/<userid> - payload: {payload}')

#     # do not forget to validate every argument, e.g.,:
#     if 'usertype' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'usertype is required to update'}
#         return flask.jsonify(response)
#     if 'userid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'userid is required to update'}
#         return flask.jsonify(response)
#     if 'password' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'password is required to update'}
#         return flask.jsonify(response)

#     # parameterized queries, good for security and performance
#     statement = 'UPDATE users SET usertype = %s WHERE userid = %s'
#     values = (payload['usertype'], userid)

#     try:
#         res = cur.execute(statement, values)
#         response = {'status': StatusCodes['success'], 'results': f'Updated: {cur.rowcount}'}

#         # commit the transaction
#         conn.commit()

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(error)
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#         # an error occurred, rollback
#         conn.rollback()

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)




# ## AUCTION
# ## Demo POST
# ##
# ## Add a new user in a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ##
# ## curl -X POST http://localhost:8080/auction/ -H 'Content-Type: application/json' -d '{"auctionid": "0", "auction_end": "20240613", "sellerdesc": "pretty vase very pretty plz buy", "items_itemid":"0", "seller_users_userid": "1"}'
# ##

# @app.route('/auction/', methods=['POST'])
# def add_auction():
#     logger.info('POST /auction')
#     payload = flask.request.get_json()

#     conn = db_connection()
#     cur = conn.cursor()
#     import time
#     time.strftime('%Y-%m-%d %H:%M:%S')

#     logger.debug(f'POST /auction - payload: {payload}')

#     # do not forget to validate every argument, e.g.,:
#     if 'auctionid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'auctionid value not in payload'}
#         return flask.jsonify(response)
#     if 'auction_end' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'auction_end value not in payload'}
#         return flask.jsonify(response)
#     if 'sellerdesc' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'sellerdesc value not in payload'}
#         return flask.jsonify(response)
#     if 'items_itemid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'item_itemid value not in payload'}
#         return flask.jsonify(response)
#     if 'seller_users_userid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'seller_users_userid value not in payload'}
#         return flask.jsonify(response)

#     # parameterized queries, good for security and performance
#     statement = 'INSERT INTO auction (auctionid, auction_end, sellerdesc, items_itemid, seller_users_userid) VALUES (%s, %s, %s, %s, %s)'
#     values = (payload['auctionid'], payload['auction_end'], payload['sellerdesc'], payload['items_itemid'], payload['seller_users_userid'])

#     try:
#         cur.execute(statement, values)

#         # commit the transaction
#         conn.commit()
#         response = {'status': StatusCodes['success'], 'results': f'Inserted auction {payload["auctionid"]}'}

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(f'POST /auction - error: {error}')
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#         # an error occurred, rollback
#         conn.rollback()

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)

# ## AUCTION
# ## Demo PUT
# ##
# ## Update a user based on a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ## curl -X PUT http://localhost:8080/auction/ -H 'Content-Type: application/json' -d '{"auctionid": "0", "auction_end": "20240613", "sellerdesc": "mediocre vase tbh", "items_itemid":"0", "seller_users_userid": "1"}'
# ##

# @app.route('/auction/<auctionid>', methods=['PUT'])
# def update_auction(auctionid):
#     logger.info('PUT /auction/<auctionid>')
#     payload = flask.request.get_json()

#     conn = db_connection()
#     cur = conn.cursor()

#     logger.debug(f'PUT /auction/<auctionid> - payload: {payload}')

#     # do not forget to validate every argument, e.g.,:
#     if 'auctionid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'auctionid is required to update'}
#         return flask.jsonify(response)
#     if 'auction_end' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'auction_end is required to update'}
#         return flask.jsonify(response)
#     if 'sellerdesc' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'sellerdesc is required to update'}
#         return flask.jsonify(response)
#     if 'items_itemid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'item_itemid value not in payload'}
#         return flask.jsonify(response)
#     if 'seller_users_userid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'seller_users_userid value not in payload'}
#         return flask.jsonify(response)

#     # parameterized queries, good for security and performance
#     statement = 'UPDATE auction SET auction_end = %s WHERE auctionid = %s'
#     values = (payload['auctionid'], auctionid)

#     try:
#         res = cur.execute(statement, values)
#         response = {'status': StatusCodes['success'], 'results': f'Updated: {cur.rowcount}'}

#         # commit the transaction
#         conn.commit()

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(error)
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#         # an error occurred, rollback
#         conn.rollback()

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)

# ## ITEMS
# ## Demo GET
# ##
# ## Obtain all items
# ##
# ## To use it, access:
# ##
# ## http://localhost:8080/items/
# ##

@app.route('/items/', methods=['GET'])
def get_items():
    logger.info('GET /items')

    logger.debug('itemid: {itemid}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT itemid, name, bid_amt, seller_users_userid FROM items')
        rows = cur.fetchall()

        if rows:
            row = rows[0]
            logger.debug('GET /itemid - parse')
            logger.debug(row)
            content = {'itemid': row[0], 'name': row[1], 'bid_amt': row[2], 'seller_users_userid': row[3]}
            response = {'status': StatusCodes['success'], 'results': content}
        else:
            response = {'status': StatusCodes['success'], 'results': []}  # No items found

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /items - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)



# ## ITEMS
# ## Demo GET
# ##
# ## Obtain user with username <username>
# ##
# ## To use it, access:
# ##
# ## http://localhost:8080/items/1
# ##

# @app.route('/items/<itemid>/', methods=['GET'])
# def get_items(itemid):
#     logger.info('GET /items/<itemid>')

#     logger.debug('itemid: {itemid}')

#     conn = db_connection()
#     cur = conn.cursor()

#     try:
#         cur.execute('SELECT itemid, name, bit_amt, seller_users_userid FROM items where itemid = %s', (itemid,))
#         rows = cur.fetchall()

#         row = rows[0]

#         logger.debug('GET /itemid/<itemid> - parse')
#         logger.debug(row)
#         content = {'itemid': row[0], 'name': row[1], 'bit_amt': row[2], 'seller_users_userid': row[3]}

#         response = {'status': StatusCodes['success'], 'results': content}

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(f'GET /items/<itemid> - error: {error}')
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)

# ## ITEMS
# ## Demo POST
# ##
# ## Add a new item in a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ##
# ## curl -X POST http://localhost:8080/itemsadd/ -H 'Content-Type: application/json' -d '{"itemid": "0", "name": "pretty vase wow", "bid_amt": "5000", "seller_users_userid": "1"}'
# ##

@app.route('/itemsadd/', methods=['POST'])
def add_items():
    logger.info('POST /itemsadd')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    import time
    time.strftime('%Y-%m-%d %H:%M:%S')

    logger.debug(f'POST /items - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'itemid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'itemid value not in payload'}
        return flask.jsonify(response)
    if 'name' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'name value not in payload'}
        return flask.jsonify(response)
    if 'bid_amt' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'bid_amt value not in payload'}
        return flask.jsonify(response)
    if 'seller_users_userid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'seller_users_userid value not in payload'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'INSERT INTO items (itemid, name, bid_amt, seller_users_userid) VALUES (%s, %s, %s, %s)'
    values = (payload['itemid'], payload['name'], payload['bid_amt'], payload['seller_users_userid'])

    try:
        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted auction {payload["itemid"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /items - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

# ## ITEMS
# ## Demo PUT
# ##
# ## Update a user based on a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ##
# ## curl -X PUT http://localhost:8080/items/ -H 'Content-Type: application/json' -d '{"itemid": "0", "name": "pretty vase wow", "bid_amt": "5000", "seller_users_userid": "1"}'
# ##

# @app.route('/items/<itemid>', methods=['PUT'])
# def update_items(itemid):
#     logger.info('PUT /item/<itemid>')
#     payload = flask.request.get_json()

#     conn = db_connection()
#     cur = conn.cursor()

#     logger.debug(f'PUT /items/<itemid> - payload: {payload}')

#     # do not forget to validate every argument, e.g.,:
#     if 'itemid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'itemid value not in payload'}
#         return flask.jsonify(response)
#     if 'name' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'name value not in payload'}
#         return flask.jsonify(response)
#     if 'bid_amt' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'bid_amt value not in payload'}
#         return flask.jsonify(response)
#     if 'seller_users_userid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'seller_users_userid value not in payload'}
#         return flask.jsonify(response)

#     # parameterized queries, good for security and performance
#     statement = 'UPDATE items SET name = %s WHERE itemid = %s'
#     values = (payload['itemid'], itemid)

#     try:
#         res = cur.execute(statement, values)
#         response = {'status': StatusCodes['success'], 'results': f'Updated: {cur.rowcount}'}

#         # commit the transaction
#         conn.commit()

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(error)
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#         # an error occurred, rollback
#         conn.rollback()

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)


# ## BIDS
# ## Demo GET
# ##
# ## Obtain all bids in JSON format
# ##
# ## To use it, access:
# ##
# ## http://localhost:8080/bids/
# ##

# @app.route('/bids/', methods=['GET'])
# def get_all_users():
#     logger.info('GET /bids')

#     conn = db_connection()
#     cur = conn.cursor()

#     try:
#         cur.execute('SELECT bidid, bid_amt FROM bids')
#         rows = cur.fetchall()

#         logger.debug('GET /bids - parse')
#         Results = []
#         for row in rows:
#             logger.debug(row)
#             content = {'bidid': row[0], 'bid_amt': row[1]}
#             Results.append(content)  # appending to the payload to be returned

#         response = {'status': StatusCodes['success'], 'results': Results}

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(f'GET /bids - error: {error}')
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)

# ## BIDS
# ## Demo POST
# ##
# ## Add a new user in a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ##
# ## curl -X POST http://localhost:8080/bid/ -H 'Content-Type: application/json' -d '{"bidid": "0", "bid_amt": "20240613"}'
# ##

@app.route('/bids/', methods=['POST'])
def add_bid():
    logger.info('POST /bids')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    import time
    time.strftime('%Y-%m-%d %H:%M:%S')

    logger.debug(f'POST /bids - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'bidid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'bidid value not in payload'}
        return flask.jsonify(response)
    if 'bid_amt' not in payload:
        response = {'status': StatusCodes['api_error'], 'bid_amt': 'auction_end value not in payload'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'INSERT INTO bids (bidid, bid_amt) VALUES (%s, %s)'
    values = (payload['bidid'], payload['bid_amt'])

    try:
        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted bid {payload["bidid"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /auction - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

# ## BIDS
# ## Demo PUT
# ##
# ## Update a user based on a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ##
# ## curl -X PUT http://localhost:8080/bid/0 -H 'Content-Type: application/json' -d '{"bidid": "0", "bid_amt": "20240613"}'
# ##

# @app.route('/bid/<bidid>', methods=['PUT'])
# def update_bid(bidid):
#     logger.info('PUT /bids/<bidid>')
#     payload = flask.request.get_json()

#     conn = db_connection()
#     cur = conn.cursor()

#     logger.debug(f'PUT /bid/<bidid> - payload: {payload}')

#     # do not forget to validate every argument, e.g.,:
#     if 'bidid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'bidid is required to update'}
#         return flask.jsonify(response)
#     if 'bid_amt' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'bid_amt is required to update'}
#         return flask.jsonify(response)

#     # parameterized queries, good for security and performance
#     statement = 'UPDATE bids SET bid_amt = %s WHERE bidid = %s'
#     values = (payload['bidid'], bidid)

#     try:
#         res = cur.execute(statement, values)
#         response = {'status': StatusCodes['success'], 'results': f'Updated: {cur.rowcount}'}

#         # commit the transaction
#         conn.commit()

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(error)
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#         # an error occurred, rollback
#         conn.rollback()

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)

# ## POSTS
# ## Demo GET
# ##
# ## Obtain specific post
# ##
# ## To use it, access:
# ##
# ## http://localhost:8080/posts/0
# ##

# @app.route('/posts/<postid>/', methods=['GET'])
# def get_post(postid):
#     logger.info('GET /posts/<postid>')

#     logger.debug('postid: {postid}')

#     conn = db_connection()
#     cur = conn.cursor()

#     try:
#         cur.execute('SELECT postid, post, auction_auctionid FROM posts where postid = %s', (postid,))
#         rows = cur.fetchall()

#         row = rows[0]

#         logger.debug('GET /posts/<postid> - parse')
#         logger.debug(row)
#         content = {'postid': row[0], 'posts': row[1], 'auction_auctionid': row[2]}

#         response = {'status': StatusCodes['success'], 'results': content}

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(f'GET /posts/<postid> - error: {error}')
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)

# ## POSTS
# ## Demo POST
# ##
# ## Add a new user in a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ##
# ## curl -X POST http://localhost:8080/posts/0 -H 'Content-Type: application/json' -d '{"postid": "0", "post": "This is for rachel", "auction_auctionid": "0"}'
# ##

# @app.route('/post/', methods=['POST'])
# def add_post():
#     logger.info('POST /post')
#     payload = flask.request.get_json()

#     conn = db_connection()
#     cur = conn.cursor()

#     logger.debug(f'POST /post - payload: {payload}')

#     # do not forget to validate every argument, e.g.,:
#     if 'postid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'postid value not in payload'}
#         return flask.jsonify(response)
#     if 'post' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'post value not in payload'}
#         return flask.jsonify(response)
#     if 'auction_auctionid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'auction_auctionid value not in payload'}
#         return flask.jsonify(response)

#     # parameterized queries, good for security and performance
#     statement = 'INSERT INTO posts (postid, post, auction_auctionid) VALUES (%s, %s, %s)'
#     values = (payload['postid'], payload['post'], payload['auction_auctionid'])

#     try:
#         cur.execute(statement, values)

#         # commit the transaction
#         conn.commit()
#         response = {'status': StatusCodes['success'], 'results': f'Inserted post {payload["postid"]}'}

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(f'POST /post - error: {error}')
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#         # an error occurred, rollback
#         conn.rollback()

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)


# ## POSTS
# ## Demo PUT
# ##
# ## Update a user based on a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ##
# ## curl -X PUT http://localhost:8080/posts/0 -H 'Content-Type: application/json' -d '{"postid": "0", "post": "This is for rachel", "auction_auctionid": "0"}'
# ##

# @app.route('/posts/<postid>', methods=['PUT'])
# def update_post(postid):
#     logger.info('PUT /post/<postid>')
#     payload = flask.request.get_json()

#     conn = db_connection()
#     cur = conn.cursor()

#     logger.debug(f'PUT /post/<postid> - payload: {payload}')

#     # do not forget to validate every argument, e.g.,:
#     if 'postid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'postid is required to update'}
#         return flask.jsonify(response)
#     if 'post' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'post is required to update'}
#         return flask.jsonify(response)
#     if 'auction_auctionid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'auction_auctionid is required to update'}
#         return flask.jsonify(response)

#     # parameterized queries, good for security and performance
#     statement = 'UPDATE posts SET post = %s WHERE postid = %s'
#     values = (payload['postid'], postid)

#     try:
#         res = cur.execute(statement, values)
#         response = {'status': StatusCodes['success'], 'results': f'Updated: {cur.rowcount}'}

#         # commit the transaction
#         conn.commit()

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(error)
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#         # an error occurred, rollback
#         conn.rollback()

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)

# ## INBOX
# ## Demo GET
# ##
# ## Obtain user with username <username>
# ##
# ## To use it, access:
# ##
# ## http://localhost:8080/inbox/
# ##

# @app.route('/inbox/<messageid>/', methods=['GET'])
# def get_inbox(messageid):
#     logger.info('GET /inbox/<messageid>')

#     logger.debug('messageid: {messageid}')

#     conn = db_connection()
#     cur = conn.cursor()

#     try:
#         cur.execute('SELECT messageid, reivewid, message, users_userid FROM inbox where messageid = %s', (messageid,))
#         rows = cur.fetchall()

#         row = rows[0]

#         logger.debug('GET /inbox/<messageid> - parse')
#         logger.debug(row)
#         content = {'messageid': row[0], 'reviewid': row[1], 'message': row[2], 'users_userid':row[3]}

#         response = {'status': StatusCodes['success'], 'results': content}

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(f'GET /inbox/<messageid> - error: {error}')
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)

# ## INBOX
# ## Demo POST
# ##
# ## Add a new user in a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ##
# ## curl -X POST http://localhost:8080/inbox/ -H 'Content-Type: application/json' -d '{"messageid": "0", "recieverid": "1", "message": "This is for rachel", "users_userid": "0"}'
# ##

# @app.route('/inbox/', methods=['POST'])
# def add_inbox():
#     logger.info('POST /inbox')
#     payload = flask.request.get_json()

#     conn = db_connection()
#     cur = conn.cursor()

#     logger.debug(f'POST /inbox - payload: {payload}')

#     # do not forget to validate every argument, e.g.,:
#     if 'messageid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'messageid value not in payload'}
#         return flask.jsonify(response)
#     if 'recieverid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'recieverid value not in payload'}
#         return flask.jsonify(response)
#     if 'message' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'message value not in payload'}
#         return flask.jsonify(response)
#     if 'users_userid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'users_userid value not in payload'}
#         return flask.jsonify(response)
    

#     # parameterized queries, good for security and performance
#     statement = 'INSERT INTO inbox (messageid, recieverid, message, users_userid) VALUES (%s, %s, %s, %s)'
#     values = (payload['messageid'], payload['recieverid'], payload['message'], payload['users_userid'])

#     try:
#         cur.execute(statement, values)

#         # commit the transaction
#         conn.commit()
#         response = {'status': StatusCodes['success'], 'results': f'Inserted post {payload["messageid"]}'}

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(f'POST /inbox - error: {error}')
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#         # an error occurred, rollback
#         conn.rollback()

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)


# ## INBOX
# ## Demo PUT
# ##
# ## Update a user based on a JSON payload
# ##
# ## To use it, you need to use postman or curl:
# ##
# ## curl -X PUT http://localhost:8080/inbox/ -H 'Content-Type: application/json' -d '{"messageid": "0", "recieverid": "1", "message": "This is for rachel", "users_userid": "0"}'
# ##

# @app.route('/inbox/<messageid>', methods=['PUT'])
# def update_inbox(messageid):
#     logger.info('PUT /inbox/<messageid>')
#     payload = flask.request.get_json()

#     conn = db_connection()
#     cur = conn.cursor()

#     logger.debug(f'PUT /inbox/<messageid> - payload: {payload}')

#     # do not forget to validate every argument, e.g.,:
#     if 'messageid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'messageid value not in payload'}
#         return flask.jsonify(response)
#     if 'recieverid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'recieverid value not in payload'}
#         return flask.jsonify(response)
#     if 'message' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'message value not in payload'}
#         return flask.jsonify(response)
#     if 'users_userid' not in payload:
#         response = {'status': StatusCodes['api_error'], 'results': 'users_userid value not in payload'}
#         return flask.jsonify(response)

#     # parameterized queries, good for security and performance
#     statement = 'UPDATE inbox SET message = %s WHERE messageid = %s'
#     values = (payload['messageid'], messageid)

#     try:
#         res = cur.execute(statement, values)
#         response = {'status': StatusCodes['success'], 'results': f'Updated: {cur.rowcount}'}

#         # commit the transaction
#         conn.commit()

#     except (Exception, psycopg2.DatabaseError) as error:
#         logger.error(error)
#         response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

#         # an error occurred, rollback
#         conn.rollback()

#     finally:
#         if conn is not None:
#             conn.close()

#     return flask.jsonify(response)



@app.route('/buyers', methods=['GET'])
def get_all_buyers():
    logger.info('GET /buyers')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM buyer')
        rows = cur.fetchall()

        buyers = []
        for row in rows:
            buyer = {
                'buyerid': row[0],
                'buyername': row[1],
                'buyeremail': row[2]
            }
            buyers.append(buyer)

        response = {'status': StatusCodes['success'], 'results': buyers}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /buyers - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/sellers', methods=['GET'])
def get_all_sellers():
    logger.info('GET /sellers')
    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM seller')
        rows = cur.fetchall()

        sellers = []
        for row in rows:
            seller = {
                'sellerid': row[0],
                'sellername': row[1],
                'selleremail': row[2]
            }
            sellers.append(seller)

        response = {'status': StatusCodes['success'], 'results': sellers}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /buyers - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# ##########################################################
# ## MAIN
# ##########################################################
if __name__ == "__main__":

    # Set up the logging
     logging.basicConfig(filename="logs/log_file.log")
     logger = logging.getLogger('logger')
     logger.setLevel(logging.DEBUG)
     ch = logging.StreamHandler()
     ch.setLevel(logging.DEBUG)

     # create formatter
     formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
     ch.setFormatter(formatter)
     logger.addHandler(ch)

     time.sleep(1) # just to let the DB start before this print :-)

     logger.info("\n---------------------------------------------------------------\n" + 
                   "API v1.1 online: http://localhost:8080/users/\n\n")

     app.run(host="0.0.0.0", debug=True, threaded=True)



