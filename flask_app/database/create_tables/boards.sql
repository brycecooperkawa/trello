CREATE TABLE IF NOT EXISTS `boards` (
`board_id`      int(11)       NOT NULL AUTO_INCREMENT 	COMMENT 'The board id',
`name`          varchar(100)  NOT NULL					COMMENT 'The name of the board',
PRIMARY KEY (`board_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Boards that exist";