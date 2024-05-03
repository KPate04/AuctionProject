-- Replace this by the SQL code needed to create your database
CREATE TABLE tokens (
    userid bigint,
    token_value TEXT NOT NULL,
	deadline timestamp
);

CREATE TABLE items (
	itemid	 BIGSERIAL,
	name	 VARCHAR(512),
	min_price	 DOUBLE PRECISION,
	users_userid BIGINT NOT NULL,
	PRIMARY KEY(itemid)
);

CREATE TABLE auction (
	auctionid	 BIGSERIAL,
	auctiontitle VARCHAR(512),
	auction_end	 TIMESTAMP,
	sellerdesc	 VARCHAR(512),
	users_userid BIGINT NOT NULL,
	items_itemid BIGINT NOT NULL,
	auction_winner BIGINT,
	PRIMARY KEY(auctionid)
);

CREATE TABLE bids (
	bidid		 BIGSERIAL,
	bid_amt		 DOUBLE PRECISION,
	users_userid	 BIGINT,
	auction_auctionid BIGINT,
	PRIMARY KEY(bidid,users_userid,auction_auctionid)
);

CREATE TABLE users (
	userid	 BIGSERIAL,
	password VARCHAR(512),
	usertype VARCHAR(10) NOT NULL,
	PRIMARY KEY(userid)
);

CREATE TABLE inbox (
	messageid	 BIGSERIAL,
	receiverid	 BIGINT,
	message	 VARCHAR(512),
	users_userid BIGINT NOT NULL,
	PRIMARY KEY(messageid)
);

CREATE TABLE posts (
	postid		 BIGSERIAL,
	post		 VARCHAR(512),
	users_userid	 BIGINT NOT NULL,
	auction_auctionid BIGINT NOT NULL,
	PRIMARY KEY(postid)
);

CREATE TABLE items_users (
	items_itemid BIGINT,
	users_userid BIGINT NOT NULL,
	PRIMARY KEY(items_itemid)
);

ALTER TABLE items ADD CONSTRAINT items_fk1 FOREIGN KEY (users_userid) REFERENCES users(userid);
ALTER TABLE auction ADD CONSTRAINT auction_fk1 FOREIGN KEY (users_userid) REFERENCES users(userid);
ALTER TABLE auction ADD CONSTRAINT auction_fk2 FOREIGN KEY (items_itemid) REFERENCES items(itemid);
ALTER TABLE bids ADD CONSTRAINT bids_fk1 FOREIGN KEY (users_userid) REFERENCES users(userid);
ALTER TABLE bids ADD CONSTRAINT bids_fk2 FOREIGN KEY (auction_auctionid) REFERENCES auction(auctionid);
ALTER TABLE inbox ADD CONSTRAINT inbox_fk1 FOREIGN KEY (users_userid) REFERENCES users(userid);
ALTER TABLE posts ADD CONSTRAINT posts_fk1 FOREIGN KEY (users_userid) REFERENCES users(userid);
ALTER TABLE posts ADD CONSTRAINT posts_fk2 FOREIGN KEY (auction_auctionid) REFERENCES auction(auctionid);
ALTER TABLE items_users ADD CONSTRAINT items_users_fk1 FOREIGN KEY (items_itemid) REFERENCES items(itemid);
ALTER TABLE items_users ADD CONSTRAINT items_users_fk2 FOREIGN KEY (users_userid) REFERENCES users(userid);


INSERT into users (password, usertype) values ('test123', 'buyer');
INSERT into users (password, usertype) values ('test321', 'seller');
INSERT into items (name, min_price, users_userid) values ('bike', 5.00, 2);
INSERT into auction (auctiontitle,auction_end,sellerdesc,users_userid,	items_itemid) values ('Auction Title','2024-05-02 20:00:00', 'Seller Description', 2, 1);
INSERT into bids (bid_amt, users_userid, auction_auctionid) values (10.00, 2, 1);
