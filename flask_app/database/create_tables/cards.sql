CREATE TABLE IF NOT EXISTS `cards` (
`card_id`           int(11)       NOT NULL AUTO_INCREMENT 	COMMENT 'The card id',
`list_id`           int(11)       NOT NULL	                COMMENT 'FK:References the list id',
`description`       varchar(500)  NOT NULL                  COMMENT 'A description shown on the card',
PRIMARY KEY (`card_id`),
FOREIGN KEY (list_id) REFERENCES lists(list_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Experiences I have had";