import keyboard
from player_detector import PlayerDetector
from drops_detector import DropsDetector
from snapshoter import Snapshoter

PIC_INTERVAL_SEC = 0.1
PICKUP_BUTTON = 'z'


class DropsSnapshoter(Snapshoter):

    def __init__(self, pipe_connection):
        super().__init__(pipe_connection, PIC_INTERVAL_SEC)
        self.drops_detector = DropsDetector(PlayerDetector())

    def apply_request_from_pipe(self, split_request):
        # no need for any other requests here
        pass

    def do_each_round(self, pil_img):
        if self.drops_detector.is_drop_nearby(pil_img):
            keyboard.press_and_release(PICKUP_BUTTON)