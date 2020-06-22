-- every monday, 00:00
DELETE FROM
    lemon
WHERE
    expiration <= now() :: timestamp;
