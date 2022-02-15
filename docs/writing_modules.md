BFG represents attacks as modules, which are really basic Python packages.
This document briefly describes the structure and content of attack modules
to assist contributors and operators when custom modules are needed.

# Quick Reference

These bullets should help get you started with developing custom attack
modules.

- `src/bfg/modules/testing/fake/module.py` for a succinct example module.
- [Base Template](#base-template) for a starting point on custom modules.
- [Module (Package) Structure](#module-package-structure) to see what is
  needed to deploy a custom module in the framework.
- [Module Parameters (Arguments)](#module-parameters-arguments) to learn
  about how module-level arguments are created and passed from the CLI
  to the module.
- [The `__call__` Method](#the-__call__-method) describes how each guess is
  performed.

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

## Base Template

This template can be used to jumpstart module development:

```python
from bfg.module import Module as BLModule
from bfg.args import argument

# bfg.args.argument deccorator is a fast method of creating
# arguments that will be supplied at runtime via bfg. These
# are typically used to configure the module itself at runtime.
@argument
def timeout(name_or_flags=('--timeout','-to',),
    type=int,
    default=3,
    help='Maximum period of time that can pass before '
      'abandoning the authentication guess.'):
    pass

# Module class must always be "Module"
class Module(BLModule):
   
    # Printed when modules are listed.
    brief_description = 'Short description here.'    
    
    # Printed when module arguments are listed.
    description = 'Lengthy description here.'
    
    # argparse.ArgumentParser objects, one for each argument.
    args = [timeout()]
    
    # List of contributors
    cocntributors = []
    
    # List of `str` references
    references = []
    
    def __init__(self, *args, **kwargs):
        '''Apply any module-level configurations that will persist
        throughout the attack here. If initialization is not required,
        then this method can be removed.        
        '''
        
        super().__init__(*args, **kwargs)
        
    def __call__(self, username:str, password:str, **kwargs) -> dict:
        '''This is the function that should guess the username and
        password.
        '''
        
        # Do authentication. It's on you to define this part :)
        is_valid = authenticate(username, password)
        
        # Assume that authenticate() returned an integer value
        return dict(
            outcome=is_valid,
            username=username,
            password=password)
```

## Module Inheritance

The `module.py` file must contain a `Module` class that inherits
from `bfg.module.Module`, which provides basic validation and
interface construction functionality.

```python
from bfg.module import Module
class Module(Module):
	pass
```

The `bfg.shortcuts` packages define child classes that inherit
from `Module` to provide foundational initizialization functions.
See `src/bfg/shortcuts/http.py` for an example of this, which provides
standard arguments for the `requests` library to make HTTP requests.
Most all of the packages under `src/bfg/modules/http` inherit from
the HTTP shortcut.

```python
from bfg.shortcuts.http import HTTPModule
class Module(HTTPModule):
    pass
```

## Module Attributes

Module-level attributes are parsed at runtime and their values are
used to describe its various characteristics. The following list
details each supported attribute.

- `brief_description` - `str` - Brief description that will appear in the module listing.
- `description` - `str` - Lengthy description that will appear when listing module arguments.
- `args` - `[argparse.ArgumentParser]` - A list of `ArgumentParser` objects
  that produce the CLI interface when executed via BFG.
- `contributors` - `[dict]` - A list of `dict` objects. Each instance describes
  an individual contributor and must have a `name` member. Additional information
  can be supplied as a `dict` object in the `additional` member for each
  contributor.
- `references` - `[str]` - A list of `str` values that will be printed to the
  help menu.

## Module Parameters (Arguments)

- Module parameters are values supplied to the CLI/YAML when starting an attack.
- Each argument is an individual `argparse.ArgumentParser` object.
  - This allows for a single parameter to be reused in different modules.
- Default parameters for _some_ protocols can be found in `src/bfg/args`,
  meaning that you can pull them into your modules without redefining them.
  
### Defining Custom Parameters

- Use the `bfg.args.argument` decorator to quickly create reusable parameters.
- The pattern is obtuse, but `@argument` effectively reads the signature of the
  decorated function and translates it to an `argparse.ArgumentParser` object
  with a single argument.

```python3
from bfg.args import argument

@argument
def customArgument('--custom',
        required=True,
        help='This is my custom argument.'):
    pass
```

- Then bind the argument to the module definition:

```python3
from bfg.module import Module as BLModule

class Module(BLModule):
    # ...other attributes above...
    args = [customArgument()]
    # ...rest of module defnition below...
```

## Reusing Pre-Defined Parameters

- Parameters for common protocols may be found in `src/bfg/args`, such as
  `src/bfg/args/http.py` containing common parameters for the `requests`
  library.
- These modules define callables that return parameters for attack modules.
- A `getDefaults` function should be defined in each argument module that
  is decorated with `bfg.args.getArgDefaults`, which allows module developers
  to specify which arguments should be bound to the newly defined attack
  module's argument list.
- This is an example of obtaining reusable arguments for an HTTP module:

```python3
from bfg.shortcuts.http import HTTPModule
from bfg.args import http as http_args

class Module(HTTPModule):
    # ...module definition
    args = http_args.getDefaults()
```

- See the HTTP modules directory for working examples of this pattern.

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
- `events` is a list of string values that will be logged after guessing the credentials.

## The `__post_init__` Method

- This method is called by `bfg.module.Module.initialize`, allowing for child
  classes to perform additional initialization steps without calling `super()`.
- This is particularly useful when inheriting from subclasses of `bfg.module.Module`
  that are defined with verbose/complex `__init__` method.
- The `__post_init__` method will be called with arguments specified in its
  method signature.
- The following example method would receive `client_id` and `resource_url`
  from upstream initialiation at runtime:
  
```python3
    def __post_init__(self, client_id, resource_url,
            *args, **kwargs):

        self.client_id = client_id
        self.resource_url = resource_url
```
