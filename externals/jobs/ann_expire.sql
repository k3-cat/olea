-- per hour
UPDATE
    ann
SET
    deleted = TRUE
WHERE
    deleted == FALSE
    AND expiration < now() :: timestamp
