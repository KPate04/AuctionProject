-- Replace this by the SQL code needed to create your database

CREATE TABLE USERS
    (USERNAME VARCHAR(10) CONSTRAINT PK_DEPT PRIMARY KEY,
	NAME VARCHAR(50) ,
	CITY VARCHAR(20));
INSERT INTO USERS VALUES ('ssmith','Scott Smith','New York');
INSERT INTO USERS VALUES ('aking','Allen King','Dallas');
INSERT INTO USERS VALUES ('jford','Jones Ford','Chicago');
INSERT INTO USERS VALUES ('mmiller','Martin Miller','Boston');

COMMIT;

