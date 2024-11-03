CREATE TABLE IF NOT EXISTS films (
    f_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    f_original_title VARCHAR(250),
    f_budget BIGINT(15) NOT NULL,
    f_revenue BIGINT(15) NOT NULL,
    f_runtime INT(15) NOT NULL,
    f_vote_count INT(15) NOT NULL,
    f_evaluation VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  u_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  u_user varchar(250) NOT NULL,
  u_pwd varchar(250) NOT NULL,
  u_category varchar(250) NOT NULL
);

