BFG uses SQL queries to mesh password spraying and credential
guessing/stuffing attacks into a single utility. This document
provides key notes on attack behavior that may not be obvious
to users.

# After credentials are guessed for a username, they become spray targets

Credential imports take priority over spray imports. After
all possible credential guesses are exhausted for a given
username, that username, _assuming valid credentials were not
discovered_, will be targeted with password values that have
been imported for spray attacks.

# Priority username/password values

Prioritizing usernames and passwords via the `prioritize-values`
subcommand means those values will be guessed before all
others.
