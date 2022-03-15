from bruteloops.errors import Error, error

class ModuleError(Error):

    @staticmethod
    @error
    def invalidHTTPMethod(method:str, *args, **kwargs):
        '''An invalid HTTP method has been requested.

        Args:
            method: String HTTP method.

        Returns:
            ModuleError
        '''

        return (ModuleError,
                'Invalid HTTP method sent to module: {method}')

    @staticmethod
    @error
    def wrongArgType(arg_name:str, e_type:str, r_type:str,
            *args, **kwargs):
        '''An invalid argument was supplied to a module.

        Args:
            arg_name: Name of the argument.
            e_type: Expected type.
            r_type: Received type.

        Returns:
            ModuleError
        '''

        return (ModuleError,
                'Wrong argument type for {arg_name} received. '
                'Expected {e_type}, got {r_type}')
