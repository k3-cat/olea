# data in Redis

| key                   | value                                        | life time                   |
| --------------------- | -------------------------------------------- | --------------------------- |
| {access token}        | user id                                      | 10 mins                     |
| rst-{reset pwd token} | user id                                      | 1 hour                      |
| duckT-{user id}       | key: passwd permission<br>val: scopes string | untill permission changes   |
| duckF-{user id}       | key: banded permission<br>val: scopes string | untill permission changes   |
| ip2city-{ip}          | city where the ip locates                    | 60 days                     |
| ip-lock               | seconds untill the day ends                  | until the next day (in utc) |
