## ITCS 3160-0002, Spring 2024
## Marco Vieira, marco.vieira@charlotte.edu
## University of North Carolina at Charlotte
 
## IMPORTANT: this file includes the Python implementation of the REST API
## It is in this file that yiu should implement the functionalities/transactions   

import flask
import logging, psycopg2, time
import random
import jwt, datetime
from functools import wraps

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

# Simpole token (shown in class)

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'access-token' in flask.request.headers:
            token = flask.request.headers['access-token']

        if not token:
            return flask.jsonify({'message': 'invalid token'})

        try:
            conn = db_connection()
            cur = conn.cursor()
            cur.execute("delete from tokens where \
               timeout<current_timestamp")
            conn.commit()

            cur.execute("select username from tokens \
               where token= %s",(token,))

            if cur.rowcount==0:
                return flask.jsonify({'message': \
                   'invalid token'})
            else:
                current_user=cur.fetchone()[0]
        except (Exception) as error:
            logger.error(f'POST /users - error: {error}')
            conn.rollback()

            return flask.jsonify({'message': 'invalid token'})

        return f(current_user, *args, **kwargs)

    return decorator

# Version using JWT (not presented in class)

def token_required_jwt(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in flask.request.headers:
            token = flask.request.headers['x-access-tokens']

        #if 'Authorization' in request.headers:
        #    token = request.headers['Authorization']
        #    token=token.split(' ')[1]

        if not token:
            return flask.jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
            current_user = data['public_id']
        except:
            return flask.jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator

##########################################################
## ENDPOINTS
##########################################################

# login user using simple tokens
# curl -X PUT http://localhost:8080/login -H 'Content-Type: application/json' -d '{"username": "ssmith", "password": "ssmith_pass"}'

@app.route('/login', methods=['PUT'])
def login_user():
    auth = flask.request.get_json()

    if not auth or 'username' not in auth \
    or 'password' not in auth:
        return flask.make_response('missing credentials', 401)

    try:
        conn = db_connection()
        cur = conn.cursor()

        statement = 'select 1 from users \
           where username = %s and password = %s'
        values = (auth['username'], auth['password'])

        cur.execute(statement, values)

        if cur.rowcount==0:
           response = ('could not verify', 401)
        else:
            response = auth['username']+ \
               str(random.randrange(111111111,999999999))
            
            statement = "insert into tokens values( %s, %s , \
               current_timestamp + (60 * interval '1 min'))"
            values = (auth['username'], response)

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

# login user using JWT tokens
# curl -X PUT http://localhost:8080/loginJWT -u ssmith -H "Content-Type: application/json"

app.config['SECRET_KEY']='Th1s1ss3cr3t'

@app.route('/loginJWT', methods=['PUT'])
def login_user_jwt():
    auth = flask.request.authorization

    if not auth or not auth.username or not auth.password:
        return flask.make_response('could not verify', 401)

    try:
        conn = db_connection()
        cur = conn.cursor()

        statement = 'select 1 from users \
           where username = %s and password = %s'
        values = (auth.username, auth.password)

        cur.execute(statement, values)

        if cur.rowcount==0:
           response = ('could not verify', 401)
        else:
            token = jwt.encode({'public_id': 105, 'exp' : datetime.datetime.now() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'],algorithm='HS256')
            response = flask.jsonify({'token' : token})
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /users - error: {error}')
        response = {'status': \
           StatusCodes['internal_error'], \
           'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return response

# List departments using simpe tokens
# To use JWT tokens just modify @token_required to @token_required_jwt
# curl -X GET http://localhost:8080/departments -H "Content-Type: application/json" -H "access-token: ssmith513580758"

@app.route("/departments", methods=['GET'])
@token_required
def get_all_departments(current_user):
    logger.info("###   DEMO: GET /departments   ###");

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT deptno, dname, loc FROM dept")
    rows = cur.fetchall()

    payload = []
    logger.info("---- departments  ----")
    for row in rows:
        logger.info(row)
        content = {'deptno':int(row[0]), 'dname':row[1], \
		'loc':row[2]}
        payload.append(content) # payload to be returned

    conn.close ()

    return flask.jsonify(payload)

# Add empolyee
# To use JWT tokens just modify @token_required to @token_required_jwt
# curl -X POST http://localhost:8080/emp/ -H 'Content-Type: application/json' -H "access-token: ssmith513580758" -d '{"ename": "PETER", "job": "ANALYST", "sal": 100, "dname": "SALES"}'

@app.route('/emp/', methods=['POST'])
@token_required
def add_employee(current_user):
    logger.info('POST /users')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /users - payload: {payload}')

    if 'ename' not in payload or 'job' not in payload or 'sal' not in payload or 'dname' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'values missing in the payload'}
        return flask.jsonify(response)

    try:
        # get depnto from dname
        statement = 'select deptno from dept where dname = %s'
        values = (payload['dname'],)
        cur.execute(statement, values)

        if cur.rowcount==1:
            deptno=cur.fetchone()[0]

            # get new empno - may generate duplicate keys, wich will lead to an exception
            statement = 'select coalesce(max(empno),1) from emp'
            cur.execute(statement)
            empno = cur.fetchone()[0]+1

            statement = 'INSERT INTO emp (empno,ename,job,sal,deptno) VALUES (%s, %s, %s, %s, %s)'
            values = (empno, payload['ename'], payload['job'], payload['sal'],deptno)
            cur.execute(statement, values)

            conn.commit()
            response = {'status': StatusCodes['success'], 'empno': empno}
        else:
            response = {'status': StatusCodes['internal_error'], 'results': 'department does not exist'}
            conn.rollback()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

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



