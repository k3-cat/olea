-- per hour
UPDATE
    proj
SET
    status = 'freezed',
    start_at = null,
    track = array_append(track, concat('% - ', now() :: timestamp))
WHERE
    status == 'pre'
    AND start_at + interval '3 days' < now() :: timestamp
