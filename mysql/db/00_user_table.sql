CREATE TABLE user (
  id int NOT NULL AUTO_INCREMENT,
  username varchar(256) NOT NULL,
  password_hash char(60) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY username (username)
);
INSERT INTO user (username, password_hash)
VALUES ('seller', '$2b$12$XPn5mwb.qPBaF8UDlDZiBetOtCP89kGUPLG8.yxOTSgvzpE4NYtgu');