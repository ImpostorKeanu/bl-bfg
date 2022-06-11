# Example Attack

**Note:** Keep in mind that each command outlined below can be supplied
via YAML file, making it significantly easier to manage complex lockout
configurations.

## 1. Install BFG

```bash
pip3 install bl-bfg
```

## 2. Select an attack module

View them by running this command. A section titled "Brute Force Modules"
will be displayed. I'll use `testing.fake` as an example, which allows us
to sample BFG/BruteLoops functionality without attacking a live service.

```bash
bfg cli brute-force --help
```

## 3. Create a database of attack values (usernames/passwords)

Use the `manage-db` subcommand to insert values into an SQLite database.
There are quite a few import methods here, but I'll demonstrate use of
`import-spray-values` for simplicity:

```bash
bfg cli manage-db import-spray-values -db /tmp/test.db \
  --usernames username1 username2 \
  --passwords password1 password2
```

## 4. Run the attack

Use the `brute-force` subcommand to start the attack.

```bash
bfg cli brute-force -db /tmp/test.db \
  --parallel-guess-count 4 \
  --threshold-jitter-min 15s --threshold-jitter-max 30s \
  testing.fake \
  --username username1 --password password2
```

This should result in an attack being executed where a 15-30 second wait
occurs between guess attempts for each user.

