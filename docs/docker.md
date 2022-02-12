# Running BFG in Docker

BFG can be executed from a docker container as well. A
`compose.yml` file is present to simplify building and
running it as individual commands.

# Dependencies

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://github.com/docker/compose/releases) (Pre-packaged with Docker for Mac/Windows)

# Quickstart

1. Create a directory to contain the attack's configuration
file and output artifacts, e.g. `mkdir bfg_output`.
2. Create a YAML configuration file named `brute.yml` in that
directory. Below is a working example that you can execute
without attacking a target.

```yml
database: brute.db
brute-force:

  # =====================
  # ATTACK CONFIGURATIONS
  # =====================

  log-file: brute.log

  stop-on-valid: false
  parallel-guess-count: 4
  auth-threshold: 2
  log-level: valid-credentials

  auth-jitter-min: 1s
  auth-jitter-max: 6s

  threshold-jitter-min: 3s
  threshold-jitter-max: 8s

  module:
    name: testing.fake
    args:
      username: user@domain1.com
      password: password2

manage-db:

  # =====================
  # DATABASE INPUT VALUES
  # =====================

  import-spray-values:

    usernames:
      - user@domain1.com
      - user@domain2.com
      - user@domain3.com

    passwords:
      - password1
      - password2
      - password3
      - password4
      - password5
```

3. Set the environment variable to point to the directory
containing the new YAML file.

**Warning:** Use an absolute path for this variable.

_cmd.exe_

```batch
set OUTPUT_DIRECTORY=bfg_output
``` 

_PowerShell_

```ps1
$env:OUTPUT_DIRECTORY=bfg_output
```

_Bash_

```bash
export OUTPUT_DIRECTORY=bfg_output
```

4. Enter the `docker` directory at the root of the `bl-bfg` repository
and run the following command. Note that output will be written to the
`bfg_output` directory.

```bash
docker-compose run --rm bfg
```

# Overriding the Entrypoint to access Help

The entrypoint can be overridden to access the CLI and get help output.

```bash
OUTPUT_DIRECTORY=junk docker-compose run --rm --entrypoint bfg bfg --help
```

Try this command ff an attack module listing is desired:

```bash
OUTPUT_DIRECTORY=junk docker-compose run --rm --entrypoint bfg bfg cli brute-force --help
```

# Behavioral Notes

## Default Execution Mode (ENTRYPOINT is `bfg yaml`)

_The current default is to execute from a YAML file._
Override the entrypoint if CLI is preferred. This value
should produce the desired behavior: `bfg cli`

## Working Directory (`/bfg/`)

BFG commands are executed in `/bfg/`, the container's
`WORKDIR`. Configuration values within the YAML file
can be supplied as relative paths. Below would be a
valid configuration for input files.

```yml
database: brute.db
brute-force:
  log-file: brute.log
```

# Environment Variables

The following table outlines environment variables used
to configured the container's execution environment.

| Variable | Default | Use |
| -------- | ------- | --- |
| `YAML_FILE` | `brute.yml` | Indicates the name of the YAML file used to execute BFG. |
| `OUTPUT_DIRECTORY` | `null` | A value _must_ be supplied to this environment variable. It mounts the target host directory to `/bfg/` within the container, allowing for attack artifacts to be persisted to disk. |
