## ITCS 3160-0002, Spring 2024
## Marco Vieira, marco.vieira@charlotte.edu
## University of North Carolina at Charlotte
 
## IMPORTANT: this file includes the Python implementation of the REST API
## It is in this file that yiu should implement the functionalities/transactions   

import flask
import logging, psycopg2, time

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
## ENDPOINTS
##########################################################


@app.route('/')
def landing_page():
    return """

    Hello World xxxxxx (Python)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    ITCS 3160-002, Spring 2024<br/>
    <br/>
    """

##
## Demo GET
##
## Obtain all users in JSON format
##
## To use it, access:
##
## http://localhost:8080/auction/
##

@app.route('/auction/', methods=['GET'])
def get_all_auctiosn():
    logger.info('GET /auction')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT auctionid, auction_end, sellerdesc FROM auction')
        rows = cur.fetchall()

        logger.debug('GET /auction - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auctionid': row[0], 'auction_end': row[1], 'sellerdesc': row[2]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /auction - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


##
## Demo GET
##
## Obtain all users in JSON format
##
## To use it, access:
##
## http://localhost:8080/users/
##

@app.route('/users/', methods=['GET'])
def get_all_users():
    logger.info('GET /users')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT userid, password, usertype FROM users')
        rows = cur.fetchall()

        logger.debug('GET /users - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'userid': row[0], 'password': row[1], 'usertype': row[2]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


##
## Demo GET
##
## Obtain user with username <username>
##
## To use it, access:
##
## http://localhost:8080/users/1
##

@app.route('/users/<userid>/', methods=['GET'])
def get_user(userid):
    logger.info('GET /users/<userid>')

    logger.debug('userid: {userid}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT userid, password, usertype FROM users where userid = %s', (userid,))
        rows = cur.fetchall()

        row = rows[0]

        logger.debug('GET /users/<userid> - parse')
        logger.debug(row)
        content = {'userid': row[0], 'password': row[1], 'usertype': row[2]}

        response = {'status': StatusCodes['success'], 'results': content}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /users/<userid> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


##
## Demo POST
##
## Add a new user in a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X POST http://localhost:8080/users/ -H 'Content-Type: application/json' -d '{"usertype": "buyer", "userid": "1", "password": "petey4life"}'
##

@app.route('/users/', methods=['POST'])
def add_users():
    logger.info('POST /users')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /users - payload: {payload}')

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


##
## Demo PUT
##
## Update a user based on a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X PUT http://localhost:8080/users/1 -H 'Content-Type: application/json' -d '{"userid":"1","password":"petey4life","usertype": "seller"}'
##

@app.route('/users/<userid>', methods=['PUT'])
def update_users(userid):
    logger.info('PUT /users/<userid>')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /users/<userid> - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'usertype' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'usertype is required to update'}
        return flask.jsonify(response)
    if 'userid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'userid is required to update'}
        return flask.jsonify(response)
    if 'password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'password is required to update'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'UPDATE users SET usertype = %s WHERE userid = %s'
    values = (payload['usertype'], userid)

    try:
        res = cur.execute(statement, values)
        response = {'status': StatusCodes['success'], 'results': f'Updated: {cur.rowcount}'}

        # commit the transaction
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


##
## Demo POST
##
## Add a new user in a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X POST http://localhost:8080/auction/ -H 'Content-Type: application/json' -d '{"auctionid": "0", "auction_end": "20240613", "sellerdesc": "pretty vase very pretty plz buy", "items_itemid":"0", "seller_users_userid": "1"}'
##

@app.route('/auction/', methods=['POST'])
def add_auction():
    logger.info('POST /auction')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    import time
    time.strftime('%Y-%m-%d %H:%M:%S')

    logger.debug(f'POST /auction - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'auctionid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'auctionid value not in payload'}
        return flask.jsonify(response)
    if 'auction_end' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'auction_end value not in payload'}
        return flask.jsonify(response)
    if 'sellerdesc' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'sellerdesc value not in payload'}
        return flask.jsonify(response)
    if 'items_itemid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'item_itemid value not in payload'}
        return flask.jsonify(response)
    if 'seller_users_userid' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'seller_users_userid value not in payload'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'INSERT INTO auction (auctionid, auction_end, sellerdesc, items_itemid, seller_users_userid) VALUES (%s, %s, %s, %s, %s)'
    values = (payload['auctionid'], payload['auction_end'], payload['sellerdesc'], payload['items_itemid'], payload['seller_users_userid'])

    try:
        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted auction {payload["auctionid"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /auction - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

##
## Demo POST
##
## Add a new user in a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X POST http://localhost:8080/items/ -H 'Content-Type: application/json' -d '{"itemid": "0", "name": "pretty vase wow", "bid_amt": "5000", "seller_users_userid": "1"}'
##

@app.route('/items/', methods=['POST'])
def add_items():
    logger.info('POST /items')
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

##########################################################
## MAIN
##########################################################
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



