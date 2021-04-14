from hp_mp_detector import get_percentages_of_hp_mp
import keyboard

from snapshoter import Snapshoter

PIC_INTERVAL_SEC = 0.15
POSSIBLE_BTNS = ['insert', 'delete', 'home', 'end', 'page down', 'page up']


class PotsSnapshoter(Snapshoter):

    def __init__(self, pipe_connection):
        super().__init__(pipe_connection, PIC_INTERVAL_SEC)
        self.hp_threshold = 0.45
        self.mp_threshold = 0.3
        self.hp_pots_button = None
        self.mp_pots_button = None

    def apply_request_from_pipe(self, split_request):
        if len(split_request) == 3:
            request_type, command, val = split_request

            if command == 'VAL':
                number = float(val)

                if number > 0.99 or number < 0:
                    return

                if request_type == 'HP':
                    self.hp_threshold = number
                elif request_type == 'MP':
                    self.mp_threshold = number

            elif command == 'BTN':
                if request_type == 'HP' and val in POSSIBLE_BTNS:
                    self.hp_pots_button = val
                elif request_type == 'MP' and val in POSSIBLE_BTNS:
                    self.mp_pots_button = val

    def do_each_round(self, pil_img):
        percentage_hp, percentage_mp = get_percentages_of_hp_mp(pil_img)

        if percentage_hp < self.hp_threshold and self.hp_pots_button is not None:
            keyboard.press_and_release(self.hp_pots_button)
        if percentage_mp < self.mp_threshold and self.mp_pots_button is not None:
            keyboard.press_and_release(self.mp_pots_button)
