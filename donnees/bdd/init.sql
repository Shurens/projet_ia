CREATE TABLE IF NOT EXISTS collect_films (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    original_title VARCHAR(250),
    budget BIGINT(15),
    revenue BIGINT(15),
    runtime INT(15),
    vote_count INT(15),
    evaluation VARCHAR(50)
);

INSERT INTO collect_films (id, original_title, budget, revenue, runtime, vote_count, evaluation) VALUES
(1, "Avatar", 237000000, 2787965087, 162, 11800, 'moyen'),
(2, "Pirates of the Caribbean: At World's End", 300000000, 961000000, 169, 4500, 'moyen'),
(3, "Spectre", 245000000, 880674609, 148, 4466, 'moyen'),
(4, "The Dark Knight Rises", 250000000, 1084939099, 165, 9106, 'bien'),
(5, "John Carter", 260000000, 284139100, 132, 2124, 'moyen');

CREATE TABLE IF NOT EXISTS films (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    original_title VARCHAR(250),
    budget BIGINT(15) NOT NULL,
    revenue BIGINT(15) NOT NULL,
    runtime INT(15) NOT NULL,
    vote_count INT(15) NOT NULL,
    evaluation VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user varchar(250) NOT NULL,
  pwd varchar(250) NOT NULL
);

INSERT INTO users (id, user, pwd) VALUES
(1, 'shuren', 'test');
