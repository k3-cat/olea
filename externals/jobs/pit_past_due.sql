-- per hour
UPDATE
    pit
SET
    status = 'past_due',
    track = array_append(track, concat('<> - ', now() :: timestamp))
WHERE
    status IN ('working', 'delayed')
    AND due < now() :: timestamp
