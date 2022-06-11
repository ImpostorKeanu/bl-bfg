# Installation

## PyPi

Each release is uploaded to PyPi for easy installation:

```bash
pip3 install bl-bfg
```

## From Source

Installation from source is just as easy as PyPi:

```bash
git clone https://github.com/arch4ngel/bl-bfg
pip3 install bl-bfg/
```

## Testing the Installation

So long as one of the two installation methods above were used,
the `bfg` script should be deployed in your path. Confirm this by
issuing the following command:

```
bfg --help
# Output similar to the following should be received....
           _               _          _
          / /\            /\ \       /\ \
         / /  \          /  \ \     /  \ \
        / / /\ \        / /\ \ \   / /\ \_\
       / / /\ \ \      / / /\ \_\ / / /\/_/
      / / /\ \_\ \    / /_/_ \/_// / / ______
     / / /\ \ \___\  / /____/\  / / / /\_____\
    / / /  \ \ \__/ / /\____\/ / / /  \/____ /
   / / /____\_\ \  / / /      / / /_____/ / /
  / / /__________\/ / /      / / /______\/ /
  \/_____________/\/_/       \/___________/

     https://github.com/arch4ngel/bruteloops
     https://github.com/arch4ngel/bl-bfg

usage: bfg [-h] {cli,yaml} ...

A brute force attack framework.

optional arguments:
  -h, --help  show this help message and exit
```
