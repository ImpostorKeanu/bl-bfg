All database management commands are under the `bfg manage-db`
subcommand. Pass the `--help` flag to understand their function.

# Creating a Database

Use either of the following commands to create a database:

- `bfg manage-db import-spray-values` 
- `bfg manage-db import-credential-values`

# Inserting/Importing Database Values

See the following resources to learn about importing database
values:

- [Spray Values](<docs/Password Spraying.md>)
- [Credential Values](<docs/Credential Guessing and Stuffing.md>)

Keep in mind that YAML files can be used to import values as
well. See this file for an example:

- [DB Values from File](<yaml_examples/db_values_from_file.yml>)

# Diagrams

## Value Imports

``````mermaid
flowchart

bfg("bfg")
bfg-cli("cli")
bfg-yaml("yaml")

bfg --> bfg-sub-or{or}
bfg-sub-or --> bfg-cli
bfg-sub-or --> bfg-yaml
yaml-note("
  See yaml_examples
  directory for working
  inputs.")
bfg-yaml --> yaml-note

bfg-cli --> bfg-cli-manage-db

subgraph sg-cli-import-subs[Import Subcommands]

    bfg-cli-import-spray("import-spray-values")
    bfg-cli-import-credentials("import-credential-values")

    subgraph sg-cli-import-spray-parameters["Import Spray Parameters"]
      import-flag-spray-usernames("--usernames")
      import-flag-spray-username-files("--username-files")
      import-flag-spray-passwords("--passwords")
      import-flag-spray-password-files("--password-files")
      import-flag-spray-credentials("--credentials")
      import-flag-spray-credential-files("--credential-files")
      import-flag-spray-csv-files("--csv-files")
    end

    subgraph sg-cli-import-credential-parameters["Import Credential Parameters"]
      import-flag-cred-credentials("--credentials")
      import-flag-cred-files("--credential-files")
      import-flag-cred-csv-files("--csv-files")
    end

    bfg-import-spray-or{"
      One or
      more"}

    bfg-import-credentials-or{"
      One or
      more"}

    bfg-cli-import-spray --> bfg-import-spray-or
    --> sg-cli-import-spray-parameters
    bfg-cli-import-credentials --> bfg-import-credentials-or
    --> sg-cli-import-credential-parameters

end

bfg-cli-manage-db("manage-db")
bfg-cli-manage-db --> bfg-manage-db-sub-or{or}
bfg-manage-db-sub-or --> bfg-cli-import-spray
bfg-manage-db-sub-or --> bfg-cli-import-credentials

db-create-note("
  Either command will
  create a database.")
db-create-note -.-> bfg-cli-import-spray
db-create-note -.-> bfg-cli-import-credentials
``````
