from pydantic import BaseModel, Field
from typing import (
    List,
    Optional,
    Any
)
from yaml import (
    dump as dump_yaml,
    SafeDumper
)

TYPE_TEMP = '<< {opt} {type} >>'

class YamlModelMixin:
    '''Class methods to dump the schema from a model and dump it
    in YAML format.

    Warning:
      - This mixin is terribly naive. Anticipate errors/mistakes
        should schemas become overly complicated.
    '''

    definitions = dict()
    '''Parsed definitions from the model's schema.
    '''

    @classmethod
    def handle_property(cls, handle:str, prop:dict, required:list):
        '''Handle an individual schema property.

        Args:
            handle: The property's name as it appears in the schema.
            prop: Dictionary property data.
            required: List of required properties from the root of
              the target properties section.
        '''

        is_required = handle in required
        default = prop.get('default', None)
        opt_str = ["Optional", "Required",][is_required]


        # Get the property type
        # Aavailable only when the property is not a reference type
        if 'type' in prop:
            type = prop['type'].capitalize()

        if default is not None:

            return default

        elif '$ref' in prop:

            return cls.definitions[prop['$ref']]

        elif prop['type'] in ('string', 'integer', 'boolean',):

            return TYPE_TEMP.format(opt=opt_str, type=type)

        elif prop['type'] == 'array':

            return (
                default if default is not None else
                [prop['items']['type'].capitalize()]
            )

        elif prop['type'] == 'object':

            return default if default else TYPE_TEMP.format(
                opt=opt_str,
                type=type)

    @classmethod
    def handle_properties(cls, props:dict, required:list=None):
        '''Handle a set of properties from a model schema.

        Args:
          props: Dictionary of properties to handle.
          required: List of property names that are required.
        '''

        required = required if required is not None else list()

        out = dict()

        for handle, _def in props.items():

            out[handle] = cls.handle_property(
                handle=handle,
                prop=_def,
                required=required)

        return out

    @classmethod
    def dump(cls) -> str:
        '''Dump the schema in YAML format.
        '''

        schema = cls.schema()

        defs = schema.get('definitions', dict())
        for name, _def in defs.items():

            cls.definitions['#/definitions/'+name] = cls.handle_properties(
                props=_def['properties'],
                required=_def.get('required',list())
            )

        return dump_yaml(
            cls.handle_properties(
                props=schema.get('properties', dict()),
                required=schema.get('required', list())),
            Dumper=SafeDumper,
            sort_keys=False)

class Root(BaseModel):

    database: str
    'Path to the database file.'

    timezone: Optional[str]
    'Timezone string, e.g. America/New_York'

class ModuleValues(BaseModel):

    name: str
    'Name of the module to run, e.g. http.owa2016'

    args: dict
    'Module arguments to apply. Varies depending upon the module.'

class ManageCredentials(BaseModel):

    credentials: Optional[List[str]]
    'Individual credential values.'

    credential_files: Optional[List[str]] = Field(alias='credential-files')
    'List of file paths pointing to files containing credential values.'

    csv_files: Optional[List[str]] = Field(alias='csv-files')
    'List of file paths pointing to files containing CSV records.'

    credential_delimiter: Optional[str] = Field(alias='credential-delimiter')
    'A character or sequence used to split credential values.'

class ManageValues(BaseModel):

    usernames: Optional[List[str]]
    'Individual username values.'

    passwords: Optional[List[str]]
    'Individual password values'

    username_files: Optional[List[str]] = Field(alias='')
    'List of file paths pointing to files containing username values.'

    password_files: Optional[List[str]] = Field(alias='')
    'List of file paths pointing to files containing password values.'

class ManageSprayValues(ManageCredentials, ManageValues):
    pass

class ManageDBBase(BaseModel):

    import_spray_values: Optional[ManageSprayValues] = Field(
        alias='import-spray-values')
    'Manage spray values.'

    import_credential_values: Optional[ManageCredentials] = Field(
        alias='import-credential-values')
    'Import credential values.'

class BruteForceBase(BaseModel):
    
    parallel_guess_count: int = Field(1, alias='parallel-guess-count')
    'Number of processes to use during the attack.'

    auth_threshold: int = Field(1, alias='auth-threshold')
    'Authentication threshold.'

    stop_on_valid: bool = Field(False, alias='stop-on-valid')
    ('Determines if the attack should stop when valid credentials are '
    'recovered.')

    blackout_window: Optional[str] = Field(alias='blackout-window')
    'Window of time to freeze during the attack.'

    auth_jitter_min: Optional[str] = Field(alias='auth-jitter-min')
    'Minimum time to sleep between guesses.'

    auth_jitter_max: Optional[str] = Field(alias='auth-jitter-max')
    'Maximum time to sleep between guesses'

    threshold_jitter_min: Optional[str] = Field(
        alias='threshold-jitter-min')
    'Minimum time to sleep after auth threshold is met for a user.'

    threshold_jitter_max: Optional[str] = Field(
        alias='threshold-jitter-max')
    'Maximum time to sleep after auth threshold is met for a user.'

    log_file: Optional[str] = Field(alias='log-file')
    'Log file to receive records.'

    log_stdout: bool = Field(True, alias='log-stdout')
    'Determines if log records should be sent to stdout.'

#    log_format: str = Field(
#            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#            alias='log-format')
#    'Logging format.'

    log_level: str = Field('invalid-usernames', alias='log-level')
    'Global log level. Pre-configured for most verbose logging.'

    module: ModuleValues
    'Module configurations.'

class ManageDB(Root, YamlModelMixin):

    manage_db: ManageDBBase = Field(alias='manage-db')
    'Manage a database file.'

class BruteForce(Root, YamlModelMixin):

    brute_force: BruteForceBase = Field(alias='brute-force')
    'Brute force attack configurations.'

class KitchenSink(ManageDB, BruteForce):
    pass
