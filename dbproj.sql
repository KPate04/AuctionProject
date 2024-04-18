CREATE TABLE items (
	itemid		 BIGSERIAL,
	name		 VARCHAR(512),
	bid_amt		 DOUBLE PRECISION,
	seller_users_userid BIGINT NOT NULL,
	PRIMARY KEY(itemid)
);

CREATE TABLE buyer (
	buyerid	 BIGSERIAL,
	bid_amt	 DOUBLE PRECISION,
	bids_bidid	 BIGINT NOT NULL,
	users_userid BIGINT,
	PRIMARY KEY(users_userid)
);

CREATE TABLE seller (
	sellerid	 BIGSERIAL,
	min_price	 DOUBLE PRECISION,
	auction_end	 TIMESTAMP,
	users_userid BIGINT,
	PRIMARY KEY(users_userid)
);

CREATE TABLE auction (
	auctionid		 BIGSERIAL,
	auction_end	 TIMESTAMP,
	sellerdesc		 VARCHAR(512),
	items_itemid	 BIGINT NOT NULL,
	seller_users_userid BIGINT NOT NULL,
	PRIMARY KEY(auctionid)
);

CREATE TABLE bids (
	bidid	 BIGSERIAL,
	bid_amt DOUBLE PRECISION,
	PRIMARY KEY(bidid)
);

CREATE TABLE users (
	userid	 BIGSERIAL,
	password VARCHAR(512),
	usertype BIGINT,
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
	auction_auctionid BIGINT NOT NULL,
	PRIMARY KEY(postid)
);

CREATE TABLE bids_auction (
	bids_bidid	 BIGINT,
	auction_auctionid BIGINT,
	PRIMARY KEY(bids_bidid,auction_auctionid)
);

CREATE TABLE buyer_items (
	buyer_users_userid BIGINT,
	items_itemid	 BIGINT,
	PRIMARY KEY(buyer_users_userid,items_itemid)
);

ALTER TABLE items ADD CONSTRAINT items_fk1 FOREIGN KEY (seller_users_userid) REFERENCES seller(users_userid);
ALTER TABLE buyer ADD CONSTRAINT buyer_fk1 FOREIGN KEY (bids_bidid) REFERENCES bids(bidid);
ALTER TABLE buyer ADD CONSTRAINT buyer_fk2 FOREIGN KEY (users_userid) REFERENCES users(userid);
ALTER TABLE seller ADD CONSTRAINT seller_fk1 FOREIGN KEY (users_userid) REFERENCES users(userid);
ALTER TABLE auction ADD CONSTRAINT auction_fk1 FOREIGN KEY (items_itemid) REFERENCES items(itemid);
ALTER TABLE auction ADD CONSTRAINT auction_fk2 FOREIGN KEY (seller_users_userid) REFERENCES seller(users_userid);
ALTER TABLE inbox ADD CONSTRAINT inbox_fk1 FOREIGN KEY (users_userid) REFERENCES users(userid);
ALTER TABLE posts ADD CONSTRAINT posts_fk1 FOREIGN KEY (auction_auctionid) REFERENCES auction(auctionid);
ALTER TABLE bids_auction ADD CONSTRAINT bids_auction_fk1 FOREIGN KEY (bids_bidid) REFERENCES bids(bidid);
ALTER TABLE bids_auction ADD CONSTRAINT bids_auction_fk2 FOREIGN KEY (auction_auctionid) REFERENCES auction(auctionid);
ALTER TABLE buyer_items ADD CONSTRAINT buyer_items_fk1 FOREIGN KEY (buyer_users_userid) REFERENCES buyer(users_userid);
ALTER TABLE buyer_items ADD CONSTRAINT buyer_items_fk2 FOREIGN KEY (items_itemid) REFERENCES items(itemid);

