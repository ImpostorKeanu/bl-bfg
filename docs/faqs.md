# Attack FAQs

_How can I stop an attack?_

- `CTRL+C`

_Can I safely stop and resume an attack?_

- Yes!
- Each guessed credential is persisted in the attack database, 
  preventing repeated guesses.
- Timestamps ensure that guesses are properly scheduled between
  attacks.

_How does BFG manage guess timing?_

- Timestamps are maintained for each username and credential:
  - `credentials.guess_time` tracks when the guess occurred.
  - `usernames.last_time` tracks when the last guess occurred
    for a username.
  - `usernames.future_time` tracks when the NEXT guess can occur
    for a username.
- SQL queries are used to select user accounts where
  `current_time > usernames.future_time`

_Is it safe to adjust timing configurations between attacks?_

- Yes!
- Timestamps are adjusted at initial execution time accordingly.
