-- Replace this by the SQL code needed to create your database
CREATE TABLE items (
    itemid     BIGSERIAL,
    name     VARCHAR(512),
    min_price     DOUBLE PRECISION,
    users_userid BIGINT NOT NULL,
    PRIMARY KEY(itemid)
);

CREATE TABLE auction (
    auctionid     BIGSERIAL,
    auctiontitle VARCHAR(512),
    auction_end     TIMESTAMP,
    sellerdesc     VARCHAR(512),
    users_userid BIGINT NOT NULL,
    items_itemid BIGINT NOT NULL,
    PRIMARY KEY(auctionid)
);

CREATE TABLE bids (
    bidid         BIGSERIAL,
    bid_amt         DOUBLE PRECISION,
    users_userid     BIGINT,
    auction_auctionid BIGINT,
    PRIMARY KEY(bidid,users_userid,auction_auctionid)
);

CREATE TABLE users (
    userid     BIGSERIAL,
    password VARCHAR(512),
    usertype VARCHAR(10) NOT NULL,
    PRIMARY KEY(userid)
);

CREATE TABLE posts (
    postid         BIGSERIAL,
    post         VARCHAR(512),
    users_userid     BIGINT NOT NULL,
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
ALTER TABLE posts ADD CONSTRAINT posts_fk1 FOREIGN KEY (users_userid) REFERENCES users(userid);
ALTER TABLE posts ADD CONSTRAINT posts_fk2 FOREIGN KEY (auction_auctionid) REFERENCES auction(auctionid);
ALTER TABLE items_users ADD CONSTRAINT items_users_fk1 FOREIGN KEY (items_itemid) REFERENCES items(itemid);
ALTER TABLE items_users ADD CONSTRAINT items_users_fk2 FOREIGN KEY (users_userid) REFERENCES users(userid);

INSERT into users (password, usertype) values ('buyer1', 'buyer');
INSERT into users (password, usertype) values ('buyer2', 'buyer');
INSERT into users (password, usertype) values ('seller1', 'seller');
INSERT into users (password, usertype) values ('seller2', 'seller');
INSERT into items (name, min_price, users_userid) values ('bike', 10.00, 3);
INSERT into items (name, min_price, users_userid) values ('kite', 5.00, 4);
INSERT into auction (auctiontitle, auction_end, sellerdesc, users_userid, items_itemid) values ('Bike Auction','2024-05-09 20:00:00', 'Seller Description', 3, 1);
INSERT into auction (auctiontitle, auction_end, sellerdesc, users_userid, items_itemid) values ('Kite Auction','2024-05-09 20:00:00', 'Seller Description', 4, 2);
INSERT into bids (bid_amt, users_userid, auction_auctionid) values (15.00, 1, 1);
INSERT into bids (bid_amt, users_userid, auction_auctionid) values (20.00, 2, 1);
INSERT into bids (bid_amt, users_userid, auction_auctionid) values (25.00, 4, 1);
INSERT into bids (bid_amt, users_userid, auction_auctionid) values (10.00, 1, 2);
INSERT into bids (bid_amt, users_userid, auction_auctionid) values (15.00, 2, 2);
INSERT into bids (bid_amt, users_userid, auction_auctionid) values (20.00, 3, 2);
INSERT into posts (post, users_userid, auction_auctionid) values ('I want this bike!', 1, 1);
INSERT into posts (post, users_userid, auction_auctionid) values ('I like this!', 2, 1);
INSERT into posts (post, users_userid, auction_auctionid) values ('So awesome!', 4, 1);
INSERT into posts (post, users_userid, auction_auctionid) values ('I love kites!', 1, 2);
INSERT into posts (post, users_userid, auction_auctionid) values ('I love kites more than you!', 2, 2);
INSERT into posts (post, users_userid, auction_auctionid) values ('Cool product!', 3, 2);
