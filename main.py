from fsm import State, StateTimerData, StateMachine

import curses
import builtins

#
# Curses Config
#

SCREEN = None
PRINT_Y = 0

def curses_print(*args, sep=" ", end="\n"):
    global SCREEN, PRINT_Y
    if SCREEN is None:
        # Fallback to normal print before curses starts
        builtins.print(*args, sep=sep, end=end)
        return

    text = sep.join(str(a) for a in args) + end
    for line in text.split("\n"):
        if line:
            SCREEN.addstr(PRINT_Y, 0, line + " " * 40)
            PRINT_Y += 1
    SCREEN.refresh()

builtins.print = curses_print

#
# States
#

class StillPlayer(State):
    direction = 0
    speed = 0

    def __init__(self):
        print('STILL')

    def move(self, direction, speed):
        self.direction = direction
        self.speed = speed
        self.__switch_state__('MovingPlayer')
        self.__timer__(
            'moving',
            StateTimerData(0.5, self.__switch_state__, 'StillPlayer')
        )

        return 'Moving'

    def dash(self):
        print('nodash - still')
        pass

class MovingPlayer(State):
    direction = 0
    speed = 0

    def __init__(self):
        print('MOVING')

    def move(self, direction, speed):
        self.direction = direction
        self.speed = speed
        return 'Still moving'

    def dash(self):
        self.__switch_state__('DashingPlayer')
        return 'Dashing'

class DashingPlayer(State):
    direction = 0
    speed = 0

    def __init__(self):
        self.__timer__(
            'dashing',
            StateTimerData(3, self.__switch_state__, 'StillPlayer'),
            [],
            ['moving']
        )
        print('DASHING')

    def move(self, direction, speed):
        print('cannot move while dashing')
        pass

    def dash(self):
        pass

#
# Curses Input
#

def wasd_curses(stdscr):
    global SCREEN
    SCREEN = stdscr
    stdscr.nodelay(True)
    stdscr.clear()

    print("Press WASD keys (Press 'q' to quit)")
    fsm = StateMachine(['direction', 'speed'], ['move', 'dash']) \
        .add_state(StillPlayer) \
        .add_state(MovingPlayer) \
        .add_state(DashingPlayer)

    fsm.spin('StillPlayer')

    while True:
        c = stdscr.getch()

        if c != -1:
            if c == ord('w'):
                fsm.call('move', 1, 5)
                print("W - Forward")
            elif c == ord('a'):
                fsm.call('move', 4, 5)
                print("A - Left")
            elif c == ord('s'):
                fsm.call('move', 3, 5)
                print("S - Backward")
            elif c == ord('d'):
                fsm.call('move', 2, 5)
                print("D - Right")
            elif c == ord('j'):
                fsm.call('dash')
                print("J - Dash")
            elif c == ord('q'):
                break
        
        curses.napms(10)

if __name__ == '__main__':
    curses.wrapper(wasd_curses)
