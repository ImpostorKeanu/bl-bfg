# Big F....un Gun (BFG)

BFG is a simple modular framework to perform brute-force attacks. It uses
the [BruteLoops](https://github.com/arch4ngel/BruteLoops) library for the
brute force and database management logic.

# Features

- *BruteLoops capabilities*
  - Resumable attacks that _do not repeat previous guesses_
  - Parallel guessing
  - Lockout avoidance via two layers of jitter configurations
  - Target/password prioritization
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
