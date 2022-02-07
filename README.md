# Big Friggen Gun (BFG)

BFG is a simple modular framework to perform brute-force attacks. It uses
the [BruteLoops](https://github.com/arch4ngel/BruteLoops) library for the
brute force and database management logic.

![command-example](docs/resources/command-output.png)

# Features

- *BruteLoops Capabilities*
  - Resumable attacks that _do not repeat previous guesses_
  - Simultaneous support for password spraying and credential stuffing
  - Parallel guessing
  - Lockout avoidance via two layers of jitter configurations
  - User/password prioritization
  - Universal protocol/application capabilities
  - Granular logging
    - Lockouts happen. It's part of life.
    - BruteLoops provides a log record for each guess, along with timestamp
    - Allows operators to reconstruct a timeline of events if things go bad
- *Modular Framework*
  - Simple class-based modules provide reusable arguments/components
- *YAML Attack Profiles*
  - YAML files can be used to supply configuration values to BFG
  - Avoids complex command line flags

# Supported Platforms

Only Linux is supported at the moment, however a Docker implementation will
soon follow.

# Quick Install

```bash
pip3 install bl-bfg
```

Then confirm installation:

```bash
bfg --help
```

# Documentation

See the docs directory for additional documentation:

- [Installation](docs/installation.md)
- [Example Attack](docs/example_attack.md)
- [YAML Attack Profiles](docs/yaml_attack_profiles.md)
