# Properties

## ann

| name       | type     | changes when       | used for   |
| ---------- | -------- | ------------------ | ---------- |
| id         | b67 str  | never              |            |
| level      | Ann.L    | never              |            |
| poster_id  | user id  | never              |            |
| expiration | datetime | never              |            |
| deleted    | bool     | ann is deleted     |            |
| ver        | int      | new version posted |            |
| content    | text     | new version posted |            |
| at         | datetime | new version posted |            |
| history    | json     | new version posted | change log |

## chat

| name        | type     | changes when       | used for                   |
| ----------- | -------- | ------------------ | -------------------------- |
| id          | b67 str  | never              |                            |
| order       | int      | new version posted | sort (even if "at" changes |
| proj_id     | proj id  | never              |                            |
| pink_id     | user id  | never              |                            |
| reply_to_id | chat id  | never              |                            |
| deleted     | bool     | chat is deleted    |                            |
| ver         | int      | new version posted |                            |
| content     | text     | new version posted |                            |
| at          | datetime | new version posted |                            |
| history     | json     | new version posted | change log                 |

## duck

| name    | type    | changes when       | used for                                                               |
| ------- | ------- | ------------------ | ---------------------------------------------------------------------- |
| pink_id | user id | never              |                                                                        |
| node    | str     | never              |                                                                        |
| allow   | bool    | never              |                                                                        |
| scopes  | array   | permission changes | the range that permission applys<br>empty scopes will allow / deny ALL |

## lemon

| name       | type     | changes when    | used for                                    |
| ---------- | -------- | --------------- | ------------------------------------------- |
| id         | b67 str  | never           |                                             |
| key        | b85 str  | never           | secret key                                  |
| pink_id    | user id  | never           |                                             |
| ip         | str      | never           | determine the city where the user locate    |
| device_id  | uuid     | never           | prevent from copying token to other devices |
| expiration | datetime | token refreshed | revoke unused tokens                        |
| timestamp  | datetime | never           | record init login time                      |

## mango

| name        | type             | changes when         | used for                                   |
| ----------- | ---------------- | -------------------- | ------------------------------------------ |
| id          | id from onedrive | never                | fetch files                                |
| pit_id      | pit id           | never                |                                            |
| ver         | int              | new version submited |                                            |
| mime        | str              | never                |                                            |
| sha1        | sha1 str         | never                |                                            |
| modified_at | datetime         | never                | record "last modified" time one filesystem |
| timestamp   | datetime         | never                | record submitting time                     |

## pink

| name   | type         | changes when                 | used for                   |
| ------ | ------------ | ---------------------------- | -------------------------- |
| id     | b67 str      | never                        |                            |
| name   | str          | sometimes                    |                            |
| email  | str          | sometimes                    | sending messages from olea |
| qq     | str          | sometimes                    | contact detials            |
| other  | str          | sometimes                    | contact detials            |
| deps   | array of Dep | join / quit from departments |                            |
| \_pwd  | hash         | sometimes                    |                            |
| active | bool         | deactivated                  |                            |

## pit

| name      | type            | changes when                                               | used for                                        |
| --------- | --------------- | ---------------------------------------------------------- | ----------------------------------------------- |
| id        | b67 str         | never                                                      |                                                 |
| role_id   | role id         | never                                                      |                                                 |
| pink_id   | user id         | never                                                      |                                                 |
| state     | Pit.S           | state changes<br>pits from pervios department are all done |                                                 |
| start_at  | datetime        | pit shift                                                  |                                                 |
| finish_at | datetime        | never                                                      | find if following pits need to shift ot cascade |
| due       | datetime        | pit shift / cascade                                        | deadline                                        |
| timestamp | datetime        | never                                                      | record picked time                              |
| track     | array of string | state changes, shift, cascade                              | record state history                            |

## proj

| name       | type            | changes when                           | used for                                                                                                                |
| ---------- | --------------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| id         | b67 str         | never                                  | id                                                                                                                      |
| title      | str             | never                                  | search, display                                                                                                         |
| source     | str             | never                                  |                                                                                                                         |
| cat        | Proj.C          | never                                  |                                                                                                                         |
| suff       | str             | never                                  | allow diff version of same source under the same cat                                                                    |
| state      | Proj.S          | start, freeze, finish, ready to upload |                                                                                                                         |
| leader_id  | user id         | re-open with different user            |                                                                                                                         |
| word_count | int             | never                                  |                                                                                                                         |
| url        | str             | finish                                 |                                                                                                                         |
| start_at   | datetime        | enter pre and working state            | calculate schecdual of pits<br>find if following pits need to shift ot cascade<br>freeze project that prepared too long |
| finish_at  | datetime        | finish                                 |                                                                                                                         |
| timestamp  | datetime        | never                                  | record project creation                                                                                                 |
| track      | array of string | state changes                          | record state changes                                                                                                    |

## role

| name    | type    | changes when  | used for |
| ------- | ------- | ------------- | -------- |
| id      | b67 str | never         |          |
| proj_id | proj id | never         |          |
| dep     | Dep     | never         |          |
| name    | str     | naver         |          |
| note    | text    | never         |          |
| taken   | bool    | role is taked |          |
