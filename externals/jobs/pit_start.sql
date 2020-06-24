-- per hour
UPDATE
    pit
SET
    status = 'working'
WHERE
    status == 'pending'
    AND start_at < now() :: timestamp
