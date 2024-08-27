SELECT
    a.username AS first_username,
    c.username AS second_username,
    b1.status
FROM 
	transcendence.user a
JOIN
	transcendence.is_cool_with b1 ON a.id = b1.first_user_id
JOIN
	transcendence.user c ON b1.second_user_id = c.id;

-- or you can add a WHERE clause like this to filter the results
WHERE
    a.username LIKE 'anatolii' OR c.username LIKE 'anatolii';

-- change 'anatolii' to the username you want to search for