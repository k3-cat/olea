-- per hour
UPDATE
    proj
SET
    state = 'freezed',
    start_at = null,
    track = array_append(track, concat('% - ', now() :: timestamp))
WHERE
    state == 'pre'
    AND start_at + interval '3 days' < now() :: timestamp
