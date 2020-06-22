-- per hour
UPDATE
    pit
SET
    state = 'past_due'
WHERE
    state IN ('working', 'delayed')
    AND due < now() :: timestamp
