**NOTE:** There are a lot of words here. See `brute_sample.yml` for an
easy to understand example.

BFG can accept attack profiles in YAML format, allowing you
to save repeatable attacks while minimizing complicated CLI
flags.

# Quick Start FAQ

## Where do configuration fields come from?

- Help output from `bfg.py` describe the subcommands and their
attack profile fields.
- Always use the long options for configurations.

## Which keys are required?

- Unless the `brute-force` field is set, only the `database`
field is required.
- If `brute-force` is set, then a `module`
map must appear under `brute-force`.

## Must `manage-db` and `brute-force` appear in an attack profile?

- No, these mappings independent.
- Populating a DB via the CLI and
passing it to the `brute-force` command via attack profile is
valid.

# Understanding Attack Profile Fields

Attack profiles aim to mirror CLI subcommands and flags found
in the `bfg.py` program. This means that the help output from
the CLI should be the primary source of guidance when crafting
a profile.

*Note:* Only long flag names can be used in attack profiles,
e.g. `auth-threshold` should be provided instead of `at`
when configuring a brute force attack.

For instance, the following output is returned when requesting
help for the `brute-force` subcommand. 

```
python3 bfg.py brute-force --help

...
Perform a brute force attack.

optional arguments:
  -h, --help            show this help message and exit
  --database DATABASE, -db DATABASE
                        Database to target.

General Parameters:
  Options used to configure general attack parameters

  --parallel-guess-count PROCESS_COUNT, -pgc PROCESS_COUNT
                        Number of processes to use during the attack, determinining the count of parallel authentication attempts that are performed. Default: 1.
  --auth-threshold MAX_AUTH_TRIES, -at MAX_AUTH_TRIES
                        Inclusive number of passwords to guess for a given username before jittering for a time falling within the bounds of the values specified for "Threshold Jitter". Default: 1
...
```

When embedded in a valid attack profile, the following configurations
would be accepted by BFG. It would send a single guess for five usernames
at a time before sleeping after all targets have been guessed once.

```yml
database: /tmp/test.db
brute-force:
  parallel-guess-count: 5
  auth-threshold: 1
```

## Deviations in the "Profile Fields Pattern"

The `database` key and the `module` field, a subkey of the root
`brute-force` mapping are currently the only instance that deviate from
the pattern described above.

- `database` is supplied as a mapping at the root of the profile to avoid
  requiring the user to supply the configuration twice.
- `module` is structured differently because input fields differ between
  attack modules. See [this section](#Module) for more information on this
  deviation.

# Required Keys

The following keys are required in an attack profile.

## Database (`database`)

A root `database` mapping that specifies the database to target must always
be set.

### Notes

- Only SQLite is currently supported by BruteLoops, so a file path
  pointing to the database file should be provided to this field. 

### Example

```yml
database: /tmp/test.db
```

## Module (`brute-force:module`)

The `module` map of under the root `brute-force` key is required and *must* follow
this structure:

```yaml
brute-force:
  module:

    # Name of the module
    name: <module name>

    # Arguments to pass to the module
    args:
      mod-arg-1: some value
      mod-arg-2: some value
```

Use the following command to identify arguments for the module:

```bash
python3 bfg.py cli brute-force module_name --help

# Working example
python3 bfg.py cli brute-force testing.fake --help
```
