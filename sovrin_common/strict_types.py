import inspect

import typing

"""
Thanks to Ilya Peterov for the base code from
https://github.com/ipeterov/strict_types.
"""

if 'defaultShouldCheck' not in globals():
    defaultShouldCheck = False


class strict_types:

    def __init__(self, shouldCheck=None):
        if shouldCheck is not None:
            self.shouldCheck = shouldCheck
        else:
            self.shouldCheck = defaultShouldCheck

    def is_complex_type(self, type_):
        complex_types = [type(typing.Union), type(typing.Tuple)]
        return any(isinstance(type_, complex_type)
                   for complex_type in complex_types)

    def is_subtype(self, type_a, type_b):
        # This wouldn't work for nested Types (from typing package)
        # like Union[Tuple[...]] but since there is no such types in the
        # project (at least for now) this simple implementation is okay

        if self.is_complex_type(type_b):
            type_b = tuple(
                getattr(type_b, '__args__', None) or
                getattr(type_b, '__union_set_params__', None)
            )

        if self.is_complex_type(type_a):
            return type_a is type_b
        return issubclass(type_a, type_b)

    def __call__(self, function):

        if not self.shouldCheck:
            return function

        type_hints = typing.get_type_hints(function)

        def precheck(*args, **kwargs):

            all_args = kwargs.copy()
            all_args.update(dict(zip(function.__code__.co_varnames, args)))
            runtime_args = ((n, type(v)) for n, v in all_args.items())

            for arg_name, arg_type in runtime_args:
                if arg_name not in type_hints:
                    continue
                if not self.is_subtype(arg_type, type_hints[arg_name]):
                    raise TypeError('In {} type of {} is {} and not {}'.
                                    format(function.__qualname__,
                                           arg_name,
                                           arg_type,
                                           type_hints[arg_name]))

        def postcheck(result):
            if 'return' in type_hints:
                if not self.is_subtype(type(result), type_hints['return']):
                    raise TypeError('Type of result is {} and not {}'.
                                    format(type(result), type_hints['return']))
            return result

        if inspect.iscoroutinefunction(function):
            async def type_checker(*args, **kwargs):
                precheck(*args, **kwargs)
                result = await function(*args, **kwargs)
                return postcheck(result)
        else:
            def type_checker(*args, **kwargs):
                precheck(*args, **kwargs)
                result = function(*args, **kwargs)
                return postcheck(result)

        return type_checker


def decClassMethods(decorator):
    def decClass(cls):
        for name, m in inspect.getmembers(cls, inspect.isfunction):
            setattr(cls, name, decorator(m))
        return cls
    return decClass
