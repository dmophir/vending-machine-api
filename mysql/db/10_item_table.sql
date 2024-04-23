CREATE TABLE item (
  id int NOT NULL AUTO_INCREMENT,
  productId varchar(256) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY productId (productId)
);

INSERT INTO item (productId, price)
VALUES ('Soda', 1.25);
INSERT INTO item (productId, price)
VALUES ('Water', 0.75);
INSERT INTO item (productId, price)
VALUES ('Chips', 1.85);