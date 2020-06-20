# data in Redis

| key                   | value                                        | life time                 |
| --------------------- | -------------------------------------------- | ------------------------- |
| {access token}        | user id                                      | 10 mins                   |
| rst-{reset pwd token} | user id                                      | 1 hour                    |
| ve-{token}            | user's new email                             | 1 hour                    |
| deps-{token}          | new user's departments, assigned by admin    | 1 day                     |
| --------------------- | -------------------------------------------- | ------------------------- |
| duckT-{user id}       | key: passwd permission<br>val: scopes string | untill permission changes |
| duckF-{user id}       | key: banded permission<br>val: scopes string | untill permission changes |
| --------------------- | -------------------------------------------- | ------------------------- |
| pstate-{pit id}       | UNSET, delayed or past-due                   | untill pit finished       |
| cTree-{chat id}       | replys' id (split by ;)                      | untill project finished   |
| cPath-{project id}    | key: chat id<br>val: path of the chat        | untill project finished   |
| --------------------- | -------------------------------------------- | ------------------------- |
| lass_access           | key: user id<br>val: last access time (unix) | untill next access        |
