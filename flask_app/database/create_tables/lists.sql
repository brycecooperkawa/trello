CREATE TABLE IF NOT EXISTS `lists` (
`list_id`      int(11)       NOT NULL AUTO_INCREMENT 	COMMENT 'The list id',
`board_id`     int(11)       NOT NULL	                COMMENT 'FK:References the board id',
`name`         varchar(100)  NOT NULL					COMMENT 'The name of the list',
PRIMARY KEY (`list_id`),
FOREIGN KEY (board_id) REFERENCES boards(board_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Lists on boards";