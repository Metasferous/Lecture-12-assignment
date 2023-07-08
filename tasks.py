import inspect
import datetime
import time

"""
 1. Write a decorator that ensures a function is only called
 by users with a specific role.
 Each function should have an user_type with a string type in kwargs.
  Example:

@is_admin
def show_customer_receipt(user_type: str):
    # Some very dangerous operation

show_customer_receipt(user_type='user')
> ValueError: Permission denied

show_customer_receipt(user_type='admin')
> function pass as it should be
"""


def is_admin(func):
    def wrapper(**kwargs):
        try:
            if kwargs.get('user_type') != 'admin':
                raise ValueError('Permission denied')
            func()
        except Exception as error:
            print(repr(error))
    return wrapper


@is_admin
def f():
    print("Ok")


f(snake='S', ring='O', user_type='admin')
f(snake='S', ring='O', user_type='fido')


"""
 2. Write a decorator that wraps a function
 in a try-except block and prints an error if any type of error has happened.
  Example:

@catch_errors
def some_function_with_risky_operation(data):
    print(data['key'])


some_function_with_risky_operation({'foo': 'bar'})
> Found 1 error during execution of your function: KeyError no such key as foo

some_function_with_risky_operation({'key': 'bar'})
> bar
"""


def catch_errors(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as error:
            print('Found error(s) during execution',
                  f'of your function : {repr(error)}')
    return wrapper


@catch_errors
def some_function_with_risky_operation(data):
    print(data['key'])


some_function_with_risky_operation({'key': 'bar'})
some_function_with_risky_operation({'foo': 'bar'})


"""
 3. Create a decorator that will check types.
 It should take a function with arguments and validate inputs with annotations.
 It should work for all possible functions.
 Don`t forget to check the return type as well

  Example:

@check_types
def add(a: int, b: int) -> int:
    return a + b

add(1, 2)
> 3

add("1", "2")
> TypeError: Argument a must be int, not str
"""


def check_types(func):
    def wrapper(*args):
        try:
            arg_names = inspect.signature(func).parameters
            req_arg_types = [arg_names[arg].annotation for arg in arg_names]
            given_arg_types = [type(arg) for arg in args]
            arg_comparisons = zip(arg_names, req_arg_types, given_arg_types)
            incorrect_args = {(name, r_type.__name__, g_type.__name__)
                              for name, r_type, g_type in arg_comparisons
                              if r_type != g_type}
            if len(incorrect_args) != 0:
                raise TypeError
            func(*args)
        except TypeError:
            print('TypeError(')
            for arg in incorrect_args:
                print(f'Argument {arg[0]} must be {arg[1]}, not {arg[2]}')
            print(')')
        except Exception as general_error:
            print(repr(general_error))
    return wrapper


@check_types
def add(a: int, b: int) -> int:
    return a + b


add(1, 2.)
add(2, 2)
add('2', 2.)


"""
 4. Create a function that caches the result of a function,
 so that if it is called with the same argument multiple times,
 it returns the cached result first instead of re-executing the function.
"""


def result_caching(func):
    cache = {}

    def wrapper(*args, **kwargs):
        f_name = func.__name__
        if f_name not in cache:  # check for function in cache dict
            cache[f_name] = {}
        if args not in cache[f_name]:  # check for args in cache subdict
            cache[f_name][args] = func(*args, **kwargs)
        return cache[f_name][args]
    return wrapper


def acknowledge_call(func):
    def wrapper(*args, **kwargs):
        print(f'{func.__name__.title()} has been called!')
        return func(*args, **kwargs)
    return wrapper


@result_caching
@acknowledge_call
def square(a: int) -> int:
    return a * a


@result_caching
@acknowledge_call
def mult(a: int, b: int) -> int:
    return a * b


print(square(2))
print(square(2))
print(square(3))
print(square(3))
print(square(8))
print(square(8))
print(mult(8, 2))
print(mult(8, 2))
print(mult(8, 2))


"""
 5. Write a decorator that adds a rate-limiter to a function,
 so that it can only be called a certain amount of times per minute
"""


def rate_limiter(limit_per_minute: int):
    log = {}

    def decorator(func):
        f_name = func.__name__
        if f_name not in log:
            log[f_name] = {'count': 0, 'minute': 61}

        def wrapper(*args, **kwargs):
            current_minute = datetime.datetime.now().minute
            if log[f_name]['minute'] != current_minute:
                log[f_name]['count'] = 0
                log[f_name]['minute'] = current_minute

            log[f_name]['count'] += 1
            if log[f_name]['count'] <= limit_per_minute:
                return func(*args, **kwargs)
            else:
                print("Limit for this function is exceeded for now")
        return wrapper
    return decorator


@rate_limiter(10)
def print_second():
    print(datetime.datetime.now().second)


for i in range(1000):
    print_second()
    time.sleep(1)
