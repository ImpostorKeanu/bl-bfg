# What is Password Spraying?

"Password Spraying" involves guessing all possible combinations
of values from a dataset.

Given this dataset...

_Usernames_

```
user1
user2
```

_Passwords_

```
pass1
pass2
```

The following guesses will be inserted in the database:

```
user1:pass1
user1:pass2
user2:pass1
user2:pass2
```

# Importing Spray Values (`bfg manage-db import-spray-values`)

Spray values can be imported from the following source formats via the
`cli` or `yaml` subcommands.

## The `--usernames` and `--passwords` Flags

These flags are used to import a list of username or password values:

```
bfg manage-db import-spray-values --datadase test.db \
    --usernames user1 user2 user3 \
    --passwords pass1 pass2 pass3
```

## The `--credentials` Flag

This flag can be used to import credentials into the database, **but each
credential is split to become a spray value**.

The same dataset that was imported in the section above for `--usernames`
and `--passwords` can be represented as:

```
bfg manage-db import-spray-values --datadase test.db \
    --credentials user1:pass1 user2:pass2 user3:pass3
```

This can also be joined with `--usernames` and `--passwords`:

```
bfg manage-db import-spray-values --datadase test.db \
    --credentials user1:pass1 user2:pass2 user3:pass3 \
    --usernames user4 user5 user6
    --passwords pass4
```

## Importing Spray Values from Files

Each of the above flags have a `-files` variant as well:

- `--username-files`
- `--password-files`
- `--credential-files`
- `--csv-files`

Simply pass one more file names to flag flag and each will be imported
accordingly:

```
bfg manage-db import-spray-values --database test.db \
    --usernames user1 user2 user3 \
    --username-files userfile1.txt userfile2.txt \
    --credential-files creds.txt
```

_Notes:_

- Files are expected to be **newline delimited**
- By default, credential values should be **colon delimited**:
(username:password)
- CSV files must contain one or both of these column headers:
**username**, **password**
