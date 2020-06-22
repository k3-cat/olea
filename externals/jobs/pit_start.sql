-- per hour
UPDATE
    pit
SET
    state = 'working'
WHERE
    state == 'pending'
    AND start_at < now() :: timestamp
