BFG represents attacks as modules, which are really basic Python packages.
This document briefly describes the structure and content of attack modules
to assist contributors with the development process.

See `src/bfg/modules/testing/fake/module.py` for a succinct example module.

# Module Organization

- From the root of this repository, all modules are stored in the
`src/bfg/modules` directory.
- Subdirectories should be the targeted file type or protocol.
  - For instance, modules that target HTTP applications are stored
    in `src/bfg/modules/http`
- Module packages should be stored under the proper protocol directory.

# Module (Package) Structure

Minimally, a module package must contain the following two files:

- `__init__.py` - Can be empty. Exists to ensure that the directory is
  treated as a Python package.
- `module.py` - The actual module that will be called by BFG.

So an example module may be deployed like:

```
$ ls -l bfg/modules/http/o365_graph/
total 8
-rw-r--r-- 1 archangel archangel    0 Feb 11 08:03 __init__.py
-rw-r--r-- 1 archangel archangel 6385 Feb 12 09:00 module.py
```

# The Module File

## Module Inheritance

The `module.py` file must contain a `Module` class that inherits
from `bfg.module.Module`, which provides basic validation and
interface construction functionality.

```python
from bfg.module import Module
class Module(Module):
	pass
```

The `bfg.shortcuts` may also provide child classes that inherit
from `Module` to provide foundational initizialization functions.
See `src/bfg/shortcuts/http.py` for an example of this.

```python
from bfg.shortcuts.http import HTTPModule
class Module(HTTPModule):
    pass
```

## Module Attributes

Module-level attributes are parsed at runtime and their values are
used to describe its various characteristics. The following list
details each supported attribute.

- `name` - `str` - Name of the module that will appear in the help menu.
- `description` - `str` - Brief description that will appear in the module listing.
- `args` - `[argparse.ArgumentParser]` - A list of `ArgumentParser` objects
  that produce the CLI interface when executed via BFG.
- `contributors` - `[dict]` - A list of `dict` objects. Each instance describes
  an individual contributor and must have a `name` member. Additional information
  can be supplied as a `dict` object in the `additional` member for each
  contributor.
- `references` - `[str]` - A list of `str` values that will be printed to the
  help menu.

## Module Configuration Parameters (Arguments)

tbd

## The `__call__` Method

> This is where your module checks to determine if credentials are
valid.

- All modules _must_ have a `__call__` method, making instances of
  that module "callable", i.e. can be treated like a function.
- The signature of that method must define a `username` and `password`
  arguments:

```python
from bfg.shortcuts.http import HTTPModule
class Module(HTTPModule):
	def __call__(self, username, password, *args, **kwargs):
		pass
```

- It's on the module developer to define logic that verifies the
  credentials.
- This method _must_ return a dictionary with simple data types.
- The following would be a valid module:

```python
from bfg.module import Module
class Module(Module):

	def __call__(self, username, password, *args, **kwargs):

		if username == 'admin' and password == 'admin':

			return dict(
				outcome=1,
				username=username,
				password=password)

		else:

			return dict(
				outcome=0,
				username=username,
				password=password)
```

### `__call__` Output

Output from the `__call__` method must a dictionary with the following
elements:

```python
{
	"outcome": 0,
	"username": "username value",
	"password": "password value",
	"events":[
		"Optional list of events that should be logged"
	]
}
```

- `outcome` determines if authenitacation was successful. One of three
  integer values can be supplied:
  - `-1` - Authentication failed and should be retried.
  - `0`  - Bad credentials.
  - `1`  - Good credentials.
- `username` is the string username value that was checked.
- `password` is the string password value that was checked.
