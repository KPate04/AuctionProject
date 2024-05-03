## ITCS 3160-0002, Spring 2024
## Marco Vieira, marco.vieira@charlotte.edu
## University of North Carolina at Charlotte
 
## IMPORTANT: this file includes the Python implementation of the REST API
## It is in this file that yiu should implement the functionalities/transactions   

import flask
import logging, psycopg2, time
from functools import wraps
import random
from datetime import datetime

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
    statement = 'INSERT INTO auction (auctiontitle, auction_end, sellerdesc, users_userid, items_itemid, auction_winner) VALUES (%s, %s, %s, %s, %s, NULL)'
    values = (payload['auctiontitle'], payload['auction_end'], payload['sellerdesc'], payload['users_userid'], payload['items_itemid'], payload['auction_winner'])

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
        cur.execute('SELECT auctionid, auctiontitle, auction_end, sellerdesc, users_userid, items_itemid, auction_winner FROM auction')
        rows = cur.fetchall()

        logger.debug('GET /auctions - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auctionid': row[0], 'auctiontitle': row[1], 'auction_end': row[2], 'sellerdesc': row[3],'users_userid': row[4],'items_itemid': row[5], 'auction_winner': row[6]}
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
        cur.execute("SELECT auctionid, auctiontitle, auction_end, sellerdesc, users_userid, items_itemid, auction_winner FROM auction where sellerdesc like '%"+keyword+"%' or auctiontitle like '%"+keyword+"%'") #+?+'%'", ('keyword',))
        rows = cur.fetchall()

        logger.debug('GET /auctions/{keyword} - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auctionid': row[0], 'auctiontitle': row[1], 'auction_end': row[2], 'sellerdesc': row[3],'users_userid': row[4],'items_itemid': row[5], 'auction_winner': row[6]}
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

@app.route('/auction/<auctionId>/', methods=['GET'])
@token_required
def get_auction(current_user,auctionId):
    logger.info('GET /auction/{auctionId}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT auctionid, auctiontitle, auction_end, sellerdesc, auction_winner FROM auction where auctionid='+str(auctionId))
        rows = cur.fetchall()

        logger.debug('GET /auction/auctionid - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            auction_posts = []
            cur.execute('SELECT * FROM posts WHERE auction_auctionid = %s', (auctionId,))
            prows = cur.fetchall()
            for prow in prows:
                content = {'postid': prow[0], 'post': prow[1]}
                auction_posts.append(content)
            content = {'auctionid': row[0], 'auctiontitle': row[1], 'auction_end': row[2], 'sellerdesc': row[3], 'auction_winner': row[4], 'posts': auction_posts}
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
        cur.execute('SELECT a.auctionid, a.auctiontitle, a.auction_end, a.sellerdesc, a.users_userid, a.items_itemid, a.auction_winner, b.users_userid FROM auction as a, bids as b where a.auctionid = b.auction_auctionid and b.users_userid = %s', (userId,))
        rows = cur.fetchall()

        logger.debug('GET /auctions/user/{userId} - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auctionid': row[0], 'auctiontitle': row[1], 'auction_end': row[2], 'sellerdesc': row[3], 'auction_winner': row[6]}
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
        if rows[0][6] is not None:
            response = {'status': StatusCodes['api_error'], 'results': 'auction winner already declared'}
            return flask.jsonify(response)
        cur.execute('SELECT auction_end FROM auction WHERE auctionid = %s', (auctionId,))
        end_time = cur.fetchone()[0]

        # Convert current_time to datetime object
        current_time = datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

        if current_time > end_time:
            response = {'status': StatusCodes['api_error'], 'results': 'auction has already ended'}
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

        cur.execute('SELECT MAX(bid_amt) FROM bids where users_userid = %s', (userId,))
        rows = cur.fetchall()

        highest_bid = rows[0][0]

        if float(bid) <= highest_bid:
            response = {'status': StatusCodes['api_error'], 'results': 'bid is not higher than the current highest bid'}
            return flask.jsonify(response)

        statement = 'INSERT INTO bids (auction_auctionid, bid_amt, users_userid) VALUES (%s, %s, %s)'
        values = (auctionId, float(bid), userId)

        cur.execute(statement, values)

        conn.commit()
        response = {'status': StatusCodes['success'], 'results': 'bid placed'}

        #select all distinct users that are not the user placing the bid and send all of them a message that a higher bid has been placed for auctionId
        cur.execute('SELECT DISTINCT users_userid FROM bids WHERE auction_auctionid = %s AND users_userid != %s', (auctionId, userId))
        users = cur.fetchall()
        for user in users:
            cur.execute('INSERT INTO posts (users_userid, auction_auctionid, post) VALUES (%s, %s, %s)', (user[0], auctionId, f'A higher bid of {bid} has been placed on auction {auctionId}'))  # Concatenate string values properly
            conn.commit()

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
@token_required
def edit_auction(current_user, auctionId, userId):
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
    
    cur.execute('SELECT usertype FROM users WHERE userid = %s', (userId))
    user_type = cur.fetchone()[0]

    if user_type != 'seller':
        response = {'status': StatusCodes['api_error'], 'results': 'Only sellers can update auctions'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    cur.execute("SELECT auctiontitle, auction_end, sellerdesc, users_userid, items_itemid FROM auction WHERE auctionid = %s", (auctionId,))
    row = cur.fetchone()

    oauction_title = row[0]
    oauction_end = row[1]
    osellerdesc = row[2]
    ousers_userid = row[3]
    oitems_itemid = row[4]

    ostatement = 'INSERT INTO old_auction (auctionid, auctiontitle, auction_end, sellerdesc, users_userid, items_itemid) VALUES (%s, %s, %s, %s, %s, %s)'
    ovalues = (auctionId, oauction_title, oauction_end, osellerdesc, ousers_userid, oitems_itemid)

    statement = 'UPDATE auction SET auctiontitle = %s, auction_end = %s, sellerdesc = %s, users_userid = %s, items_itemid = %s WHERE auctionid = %s'
    values = (payload['auctiontitle'], payload['auction_end'], payload['sellerdesc'], payload['users_userid'], payload['items_itemid'], auctionId)

    try:
        cur.execute(ostatement, ovalues)
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
## GET http://localhost:8080/inbox/{userId}

@app.route('/inbox/<userId>', methods=['GET'])
@token_required
def get_messages(current_user, userId):
    conn = db_connection()
    cur = conn.cursor()

    logger.info('GET /inbox/{userId}')

    try:
        cur.execute('SELECT * FROM posts WHERE users_userid = %s', (userId,))
        rows = cur.fetchall()

        logger.debug('GET /inbox/{userId} - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'post_type': 'Posted by Me', 'postid': row[0], 'post': row[1], 'auction_auctionid': row[3]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

        ## if the usertype based on the userid is seller, show all posts related to the auctions of the seller
        cur.execute('SELECT usertype FROM users WHERE userid = %s', (userId,))
        user_type = cur.fetchone()[0]

        # if the user is a buyer, show all posts related to the auctions the buyer has placed a bid on
        if user_type == 'buyer':
            cur.execute('SELECT auction_auctionid FROM bids WHERE users_userid = %s', (userId,))
            auctions = cur.fetchall()
            for auction in auctions:
                cur.execute('SELECT * FROM posts WHERE auction_auctionid = %s', (auction[0],))
                rows = cur.fetchall()
                for row in rows:
                    content = {'post_type': 'Posts in Auctions I am Active in', 'postid': row[0], 'post': row[1], 'auction_auctionid': row[3]}
                    Results.append(content)
        
        if user_type == 'seller':
            cur.execute('SELECT auctionid FROM auction WHERE users_userid = %s', (userId,))
            auctions = cur.fetchall()
            for auction in auctions:
                cur.execute('SELECT * FROM posts WHERE auction_auctionid = %s', (auction[0],))
                rows = cur.fetchall()
                for row in rows:
                    content = {'post_type': 'Posts in Auctions I am Hosting', 'postid': row[0], 'post': row[1], 'auction_auctionid': row[3]}
                    Results.append(content)

    except (Exception, psycopg2.DatabaseError) as error:
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


## Outbid notification
## In the place_bid method


## Close auction
## PUT http://localhost:8080/auction/{auctionId}/close
## req: none
## res: updated auction information
@app.route('/auction/<auctionId>/close/<userId>', methods=['PUT'])
@token_required
def close_auction(current_user, auctionId, userId):
    logger.info('PUT /auction/<auctionId>/close/<userId>')

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Check if the user type is seller
        cur.execute('SELECT usertype FROM users WHERE userid = %s', (userId,))
        user_type = cur.fetchone()[0]

        if user_type != 'seller':
            response = {'status': StatusCodes['api_error'], 'errors': 'Only sellers can close auctions'}
            return flask.jsonify(response)

        # Get the current date and time
        current_datetime = time.strftime('%Y-%m-%d %H:%M:%S')

        # Get the highest bid in the auction
        cur.execute('SELECT MAX(bid) FROM bids WHERE auctionid = %s', (auctionId,))
        highest_bid = cur.fetchone()[0]

        # Get the user who placed the highest bid
        cur.execute('SELECT userid FROM bids WHERE auctionid = %s AND bid = %s', (auctionId, highest_bid))
        winner = cur.fetchone()[0]

        # Update the auction with the winner
        cur.execute('UPDATE auction SET auction_winner = %s WHERE auctionid = %s', (winner, auctionId))

        # Update the auction with the closing date and time
        cur.execute('UPDATE auction SET auction_end = %s WHERE auctionid = %s', (current_datetime, auctionId))

        # Commit the transaction
        conn.commit()

        response = {'status': StatusCodes['success'], 'results': f'Auction {auctionId} closed successfully'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /auction/<auctionId>/close - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # An error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

## Cancel auction
## PUT http://localhost:8080/auction/{auctionId}/cancel
## req: none
## res: updated auction information
@app.route('/auction/<auctionId>/cancel/<userId>', methods=['PUT'])
@token_required
def cancel_auction(current_user, auctionId, userId):
    logger.info('PUT /auction/<auctionId>/cancel/<userId>')

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Check if the user type is seller
        cur.execute('SELECT usertype FROM users WHERE userid = %s', (userId,))
        user_type = cur.fetchone()[0]

        if user_type != 'seller':
            response = {'status': StatusCodes['api_error'], 'errors': 'Only sellers can close auctions'}
            return flask.jsonify(response)

        # Update the auction status to "cancelled"
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('UPDATE auction SET auction_end = %s WHERE auctionid = %s', (current_time, auctionId))
        conn.commit()

        # Get the details of the cancelled auction
        cur.execute('SELECT * FROM auction WHERE auctionid = %s', (auctionId,))
        row = cur.fetchone()

        # Get the users who have placed a bid on this auction
        cur.execute('SELECT DISTINCT users_userid FROM bids WHERE auction_auctionid = %s', (auctionId,))
        users = cur.fetchall()

        # Insert a post for each user telling them the auction has cancelled
        for user in users:
            cur.execute('INSERT INTO posts (users_userid, auction_auctionid, post) VALUES (%s, %s, %s)', (user[0], auctionId, 'The auction has been cancelled.'))
            conn.commit()

        response = {'status': StatusCodes['success'], 'results': 'Auction cancelled successfully.'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /auction/<auctionId>/cancel - error: {error}')
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
