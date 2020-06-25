# data in Redis

| key                   | type   | value                                        | life time                 |
| --------------------- | ------ | -------------------------------------------- | ------------------------- |
| {access token}        | string | user id                                      | 10 mins                   |
| rst-{reset pwd token} | string | user id                                      | 1 hour                    |
| deps-{token}          | string | new user's departments, assigned by admin    | 1 day                     |
| --------------------- | ------ | -------------------------------------------- | ------------------------- |
| duckT-{user id}       | hash   | key: passwd permission<br>val: scopes string | untill permission changes |
| duckF-{user id}       | hash   | key: banded permission<br>val: scopes string | untill permission changes |
| --------------------- | ------ | -------------------------------------------- | ------------------------- |
| pStatus-{pit id}      | string | UNSET, delayed or past-due                   | untill pit finished       |
| cLog-{project id}     | list   | chang log of chats of the project            | untill project finished   |
| cPath-{project id}    | set    | all chats' path                              | untill project finished   |
| cAvbl-{project id}    | set    | all chats' id                                | untill project finished   |
| --------------------- | ------ | -------------------------------------------- | ------------------------- |
| last_access           | hash   | key: user id<br>val: last access time (unix) | untill next access        |
