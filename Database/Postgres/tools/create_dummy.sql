-- Populate tables with dummy data

\! echo -e "\e[1m Populating 'user' table with dummy data \e[0m"
INSERT INTO barelyaschema.user (id, username, pswd) VALUES
(1, 'Alê', 'hashed_password_1'),
(2, 'Alex', 'hashed_password_2'),
(3, 'Anatolii', 'hashed_password_3'),
(4, 'Francisco', 'hashed_password_4'),
(5, 'Rajh', 'hashed_password_5');

\! echo -e "\e[1m Populating 'is_cool_with' table with dummy data \e[0m"

\! echo -e "\e[1m Populating 'no_cool_with' table with dummy data \e[0m"
