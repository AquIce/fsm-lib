# Finite State Machine

## StateTimerData

```
{
 duration: float,
 function: (...any) -> any,
 args: ...any,
}
```

## State

### `__switch_state__`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |
| `new_state` | `string` | The new state to switch to |

> Behavior

By default, raises a `ValueError`, will get overridden by the [`StateMachine`](#statemachine).

### `__timer__`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |
| `timer_name` | `string` | The name of the timer to create |
| `timer_data` | [`StateTimerData`](#statetimerdata) | The data of the timer to create |
| `blocked_by` | `[]string` | The other timers that can block this one |
| `cancels` | `[]string` | The other timers to cancel when starting this one |

> Behavior

By default, raises a `ValueError`, will get overridden by the [`StateMachine`](#statemachine).

### `repr`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |

> Behavior

Prints the name of the state.

## StateTimerCallbacks

```
{
 get_active: (name: string) -> bool,
 cancel: (name: string) -> void,
 remove_self: () -> void,
}
```

## StateTimer

```
{
 timer: Timer,
 blocked_by: []string,
 cancels: []string,
 callbacks: StateTimerCallbacks,
}
```

### `__init__`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |
| `timer_data` | [`StateTimerData`](#statetimerdata) | The data of the timer to create |
| `blocked_by` | `[]string` | The other timers that can block this one |
| `cancels` | `[]string` | The other timers to cancel when starting this one |
| `callbacks` | [`StateTimerCallbacks`](#statetimercallbacks) | The callbacks that will be available to the timer |

> Behavior

Creates a new `Timer` using the provided [`StateTimerData`](#statetimerdata) and adding the necessary callbacks.

### `start`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |

> Behavior

1. Checks that there are no blocking timers running (if so, throws a `ValueError`)
2. Cancels every timer that needs to be cancelled
3. Starts the timer

### `stop`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |

> Behavior

Stops the timer, then calls the `remove_self` callback.

## StateMachine

```
{
 states: []Type<State>,
 active: State,
 required_data: []string,
 required_bindings: []string,
 timers: { string -> StateTimer }
}
```

### `add_state`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |
| `state` | `Type<State>` | The state to add (needs to have required data and bindings) |

> Behavior

Adds the state to the state machine.

- If a state with the same name already exists, throw a `ValueError`
- If there is a missing data field (from `required_data`), throw a `ValueError`
- If there is a missing binding (from `required_bindings`), throw a `ValueError`

> [!NOTE]

When adding a new [`State`](#state), its `__switch_state__` and `__timer__` methods are redefined to be custom bindings to functions from the state machine.

### `spin`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |
| `default_state_name` | `string` | The name of the state to spin into. |

> Behavior

Spin the state machine into the wanted state (if it is already active, then nothing happens).

### `switch`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |
| `new_state` | `string` | The name of the state to switch to. |

> Behavior

Switch to the provided state, syncing any data in `required_data` when doing so.

- If the state machine hasn't been spun, throw a `ValueError`
- If the active state is the one provided, do nothing

### `call`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |
| `method` | `string` | The method to call on the active state. |
| `*args` | `...any` | The args to pass to the method. |

> Behavior

Call the provided method on the active state, using the provided arguments.

- If the state machine hasn't been spun, throw a `ValueError`

### `stop`

> Params

| Name | Type | Description |
| - | - | - |
| `self` | - | - |

> Behavior

Stop the state machine.

- If the state machine is already stopped, throw a `ValueError`
