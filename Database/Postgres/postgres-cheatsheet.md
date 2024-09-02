# Those are usefull postgress cmds:

| Command | Description	                                        | Example Usage           |
| :---:   |-----------------------------------------------------|-------------------------|
\c        | Connect to a specific database                      | \c mydatabase
\l        | List all databases                                  | \l
\dt       | List all tables in the current database             | \dt
\d        | Describe a table's structure (columns, types, etc.) | \d mytable
\du       | List all roles (users)                              | \du
\dn       | List all schemas in the current database            | \dn
\dv       | List all views in the current database              | \dv
\df       | List all functions                                  | \df
\dx       | List all installed extensions                       | \dx
\i        | Execute commands from a SQL file                    | \i /path/to/file.sql
\timing   | Toggle timing of queries                            | \timing
\q        | Quit the psql session                               | \q
\x        | Toggle expanded display mode                        | \x
\!        | Execute a shell command                             | \! ls
\copy     | Copy data between a file and a table                | \copy mytable TO 'file.csv' CSV
