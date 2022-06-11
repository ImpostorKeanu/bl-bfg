# What is Credential Spraying/Stuffing

"Credential Guessing" involves guessing specific username to password
combinations. Each value represents a "credential."

"Credential Stuffing" is the same concept, except credential
values have been botained from data stores containing credentials
thought to be valid, such as from publicly available data dumps.

Given this data set, coupled credential records will be insert
into the database such that the passwords will not be used
as "password spray" values.

_Credentials_

```
user1:pass123
user2:pass1234
user3:pass123
```

# Importing Credential Values (`bfg manage-db import-credential-values`)

Though there are fewer formats and options, importing credential values
is as as simple as importing spray values.

The key principle to keep in mind is that these values are coupled
as unique username to password associations, meaning that the password
will not be used as a spray value.

Possible import options are:

- `--credentials`
- `--credential-files`
- `--csv-files`

Example:

```
bfg manage-db import-credential-values --database test.db \
    --credentials user1:pass1 user2:pass2 user3:pass1 \
    --credential-files creds1.txt creds2.txt
```

