from typing import Any, Type 
from collections.abc import Callable
from threading import Timer

class StateTimerData:
    duration = 0
    function = None
    args = ()

    def __init__(self, duration: float, function: Callable, *args):
        self.duration = duration
        self.function = function
        self.args = args

class State:
    def __switch_state__(self, new_state: str):
        raise ValueError(f'Trying to switch to state {new_state} on default state class')
    def __timer__(self, timer_name: str, timer_data: StateTimerData, blocked_by: list[str] = [], cancels: list[str] = []):
        raise ValueError(f'Trying to create timer of {time} seconds on default state class')
    def repr(self) -> str:
        return type(self).__name__

class StateTimerCallbacks:
    get_active = None
    cancel = None
    remove_self = None

    def __init__(self, get_active: Callable, cancel: Callable, remove_self: Callable):
        self.get_active = get_active
        self.cancel = cancel
        self.remove_self = remove_self

class StateTimer:
    timer = None
    blocked_by = []
    cancels = []
    callbacks = None

    def __init__(self, timer_data: StateTimerData, blocked_by: list[str], cancels: list[str], callbacks: StateTimerCallbacks):
        self.timer = Timer(timer_data.duration, lambda: (
            timer_data.function(*timer_data.args),
            callbacks.remove_self()
        ))
        self.blocked_by = blocked_by
        self.cancels = cancels
        self.callbacks = callbacks

    def start(self):
        for blocker in self.blocked_by:
            if self.callbacks.get_active(blocker):
                raise ValueError(f'Found blocker "{blocker}"')
         
        for cancellable in self.cancels:
            self.callbacks.cancel(cancellable)
        self.timer.start()

    def stop(self):
        self.timer.cancel()
        self.callbacks.remove_self()

class StateMachine:
    states = []
    active = None
    required_data = []
    required_bindings = []
    timers = {}

    def __init__(self, required_data: list[str], required_bindings: list[str]):
        self.required_data = required_data
        self.required_bindings = required_bindings

    def add_state(self, state: Type[State]): # -> Self:

        for already_state in self.states:
            if already_state.__name__ == state.__name__:
                raise ValueError(f'State {state.__name__} already exists.')

        for required_data_name in self.required_data:
            attr = getattr(state, required_data_name, None)
            if attr == None:
                raise ValueError(f'Missing member {required_data_name} in state {state.__name__}')
            if callable(attr):
                raise ValueError(f'Method {required_data_name} should be a member instead, in state {state.__name__}')

        for required_binding_name in self.required_bindings:
            attr = getattr(state, required_binding_name, None)
            if attr == None:
                raise ValueError(f'Missing method {required_data_name} in state {state.__name__}')
            if not callable(attr):
                raise ValueError(f'Member {required_data_name} should be a method instead, in state {state.__name__}')

        setattr(
            state,
            '__switch_state__',
            lambda _, state: self.switch(state)
        )
        setattr(
            state,
            '__timer__',
            lambda _, timer_name, timer_data, blocked_by = [], cancels = []: (
                self.timer(timer_name, timer_data, blocked_by, cancels)
            )
        )

        self.states.append(state)
        return self

    def timer(self, timer_name: str, timer_data: StateTimerData, blocked_by: list[str], cancels: list[str]):

        if timer_name in self.timers:
            raise ValueError(f'Trying to create already existing timer "{timer_name}"')

        self.timers[timer_name] = StateTimer(timer_data, blocked_by, cancels, StateTimerCallbacks(
            lambda name: name in self.timers.keys(),
            lambda name: self.timers[name].stop(),
            lambda: self.timers.pop(timer_name)
        ))

        self.timers[timer_name].start()

    def spin(self, default_state_name: str) -> State:
        for state in self.states:
            if state.__name__ == default_state_name:
                self.active = state()
                return self.active
        raise ValueError(f'Trying to spin non-existing state {default_state_name}')

    def switch(self, new_state: str) -> State:

        if self.active == None:
            raise ValueError(f'Trying to switch to state {new_state} while StateMachine is stopped')

        if new_state == type(self.active).__name__:
            return

        newvalues = { name: getattr(self.active, name) for name in self.required_data }
        self.spin(new_state)
        for key, value in newvalues.items():
            setattr(self.active, key, value)
        return self.active

    def call(self, method: str, *args) -> Any:
        print(f'Calling {method} with args {args}')
        if self.active == None:
            raise ValueError(f'Trying to call method while StateMachine is stopped')
        return getattr(self.active, method)(*args)

    def stop(self):
        if self.active == None:
            raise ValueError('Trying to stop already stopped StateMachine')
        self.active = None

