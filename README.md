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

# Docker Support

A compose file is available for this project. See [this document](docs/docker.md) for more information.

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
- [Docker](docs/docker.md)

# Current Attack Modules

Below are the attack modules currently in BFG.

Most people will be interested in `http.o365_graph` as it can be used to attack
`login.microsoftonline.com`.

```
http.accellion_ftp  Accellion FTP HTTP interface login module
http.adfs           Active Directory Federated Services
http.basic_digest   Generic HTTP basic digest auth
http.basic_ntlm     Generic HTTP basic NTLM authentication
http.global_protect Global Protect web interface
http.lync           Brute force Microsoft Lync.
http.mattermost     Mattermost login web interface
http.netwrix        Netwrix web login
http.o365_graph     Office365 Graph API
http.okta           Okta JSON API
http.owa2010        OWA 2010 web interface
http.owa2016        OWA 2016 web interface
http.sap_webdynpro  SAP Netweaver Webdynpro, ver. 7.3007.20120613105137.0000
smb.smb             Target a single SMB server
testing.fake        Fake authentication module for training/testing
```

