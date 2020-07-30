import pygame as pg

# TODO add disclaimer and credit to nerdparadise, also to credits


def wait_for_return(callback, *args, **kwargs):
    returned = None
    while returned is None:
        returned = callback(*args, **kwargs)
        pg.time.wait(17)
    return returned


class JoystickWrapperKeyboard:
    def __init__(self):
        raise NotImplementedError("A joystick wrapper for the keyboard has "
                                  "not been implemented yet. Please use a "
                                  "joystick or controller.")


class Control:
    AXIS_DIRECTIONS = ('pos', 'neg', 'fullpos', 'fullneg')
    HAT_DIRECTIONS = ('left', 'right', 'up', 'down')

    def __init__(self, index, is_button=False, is_axis=False, direction=None,
                 is_hat=False):
        """Value is typically the index of the button or hat or joystick"""
        self.index = index
        if not (is_button or is_axis or is_hat):
            raise ValueError("Control must be either button, axis or hat")
        self.is_button = is_button
        self.is_axis = is_axis
        self.is_hat = is_hat
        if is_axis and direction not in self.AXIS_DIRECTIONS:
            raise ValueError("Control of axis type must have direction one "
                             f" of {self.AXIS_DIRECTIONS}")
        if is_axis:
            self.direction = direction
        if is_hat:
            if direction not in self.HAT_DIRECTIONS:
                raise ValueError("Control of hat type must have direction one "
                                 f" of {self.HAT_DIRECTIONS}")
            self.direction = direction


class JoyStickStats:
    def __init__(self, index, numbuttons, numhats, numaxes):
        self.index = index
        self.numbuttons = numbuttons
        self.numaxes = numaxes
        self.numhats = numhats


class InputManager:  # TODO I don't think I need this class?
    CONTROLS_MANAGERS = []  # Perhaps I could use something like this
    USED_JOYSTICKS = []  # To check if joysticks are used already?
    EVENTS = []
    KEYS_PRESSED = []

    def __init__(self):
        pass

    def add_joystick(self, joy_index):
        joystick = pg.joystick.Joystick(joy_index)
        self.USED_JOYSTICKS.append(
            JoyStickStats(
                joy_index,
                joystick.get_numbuttons,
                joystick.get_numhats,
                joystick.get_numaxes
            )
        )

    def refresh_events(self):
        pass

    def get_all_events(self):
        pass


class ControlsManager:
    def __init__(self, controls_list, default_keymap=None):
        """
        Controls in controls_list can all be mapped to either a button
        or an axis. Value is returned as a float between 0 and 1.
        0 means not pressed, 1 means (fully) pressed.
        Axes are configured for half travel mapping to one control by default.
        """
        self.controls_list = controls_list
        self.controls_map = {}
        self.states = {}
        self.init_device()
        self.map_controls(default_keymap)

    def init_device(self):
        if not pg.joystick.get_init():
            pg.joystick.init()
        # Which device? One of the joysticks or the keyboard?
        self.joystick = self.get_used_joystick()

    def map_controls(self, default_keymap):
        # Use default keymap?
        if default_keymap is not None:
            print("Do you want to use the default keymapping?\n")
            print(*[
                f'{func}: Button{key}\n'
                for func, key in default_keymap.items()
                ])
            response = input("Yes or no? [Y/n] (Don't forget to press Enter) ")
            response = response.strip().lower()
            if response == '' or response == 'y':
                self.controls_map = default_keymap
                return

            # Ask for mapping of controls
            for ctrl in self.controls_list:
                print(f"What do you want to map to {ctrl}?")
                print("Press the button or move the axis to its limit.")
                self.controls_map[ctrl] = wait_for_return(
                    self.get_active_btn_or_axis)

            # TODO
            #response = input("Do you want to save this mapping?")

    def get_active_btn_or_axis(self):
        events = pg.event.get()
        # check buttons for activity...
        for button_index in range(self.joystick.get_numbuttons()):
            button_pushed = self.joystick.get_button(button_index)
            if button_pushed:
                while True:
                    pg.time.wait(17)  # wait until button is released again
                    pg.event.pump()
                    if self.joystick.get_button(button_index) == 0:
                        return Control(button_index, is_button=True)

        # check hats for activity...
        # (hats are the basic direction pads)
        for hat_index in range(self.joystick.get_numhats()):
            hat_x, hat_y = self.joystick.get_hat(hat_index)
            if hat_x < -.5:
                return Control(hat_index, is_hat=True, direction='left')
            elif hat_x > .5:
                return Control(hat_index, is_hat=True, direction='right')
            if hat_y < -.5:
                return Control(hat_index, is_hat=True, direction='down')
            elif hat_y > .5:
                return Control(hat_index, is_hat=True, direction='up')

        # check axes for activity...
        for axis_index in range(self.joystick.get_numaxes()):
            axis_status = self.joystick.get_axis(axis_index)
            if axis_status < -.8 and self._axis_move_in(events, axis_index):
                if self._ask_full_range():
                    direction = 'fullneg'
                else:
                    direction = 'neg'
                return Control(axis_index, is_axis=True, direction=direction)
            elif axis_status > .8 and self._axis_move_in(events, axis_index):
                if self._ask_full_range():
                    direction = 'fullpos'
                else:
                    direction = 'pos'
                return Control(axis_index, is_axis=True, direction=direction)

    def _axis_move_in(self, events, axis_index):
        result = False
        for ev in events:
            if ev.type == pg.JOYAXISMOTION:
                if ev.joy == self.joy_index and ev.axis == axis_index:
                    result = True
        return result

    def _ask_full_range(self):
        print('Do you want to use the full range of the axis or only half?')
        response = input("Press 'f', then Enter for full range,"
                         " just Enter for half.")
        if response.strip().lower() == 'f':
            return True
        return False

    def get_used_joystick(self):
        print("Press a button on your joystick or controller to continue")
        button_pushed = False
        while not button_pushed:
            pg.event.pump()
            # Check keyboard
            #if any(pg.key.get_pressed()):
            #    return JoystickWrapperKeyboard()

            # Check joysticks
            joystick_count = pg.joystick.get_count()
            for i in range(joystick_count):

                joystick = pg.joystick.Joystick(i)
                joystick.init()

                # Check buttons on each joystick
                for button_index in range(joystick.get_numbuttons()):
                    button_pushed = joystick.get_button(button_index)
                    if button_pushed:
                        self.joy_index = i
                        return joystick

                # check hats for activity...
                # (hats are the basic direction pads)
                for hat_index in range(joystick.get_numhats()):
                    hat_x, hat_y = joystick.get_hat(hat_index)
                    if hat_x < -0.5 or hat_x > 0.5 \
                            or hat_y < -0.5 or hat_y > 0.5:
                        return joystick

    def get_states(self):
        for name, ctrl in self.controls_map.items():
            if ctrl.is_button:
                self.states[name] = self.joystick.get_button(ctrl.index)
            elif ctrl.is_axis:
                measured = self.joystick.get_axis(ctrl.index)
                if ctrl.direction == 'pos':
                    self.states[name] = max(0., measured)
                elif ctrl.direction == 'neg':
                    self.states[name] = min(0., measured) * -1.
                elif ctrl.direction == 'fullpos':  # map [-1,..,1] to [0,..,1]
                    self.states[name] = (measured + 1.) / 2.
                elif ctrl.direction == 'fullneg':
                    self.states[name] = (measured + 1.) / 2. * -1.
            elif ctrl.is_hat:
                measured_x, measured_y = self.joystick.get_hat(ctrl.index)
                if ctrl.direction == 'left':
                    self.states[name] = min(0., measured_x) * -1.
                elif ctrl.direction == 'right':
                    self.states[name] = max(0., measured_x)
                elif ctrl.direction == 'down':
                    self.states[name] = min(0., measured_y) * -1.
                elif ctrl.direction == 'up':
                    self.states[name] = max(0., measured_y)
