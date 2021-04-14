from abc import ABC, abstractmethod
from time import sleep
from PIL import ImageGrab
import win32gui


class Snapshoter(ABC):

    def __init__(self, pipe_connection, pic_interval_sec):
        self.maple_window_name = None
        self.maple_window_handler = None
        self.pic_interval_sec = pic_interval_sec  # in seconds

        self.pipe_connection = pipe_connection

    @abstractmethod
    def apply_request_from_pipe(self, split_request):
        pass

    @abstractmethod
    def do_each_round(self, pil_img):
        pass

    def listen_to_pipe(self):
        """
        Interface for comms:
        TYPE\COMMAND\VAL
        or:
        COMMAND\VAL
        For example:
        HP\VAL\50
        or
        HP\VAL\70
        or
        HP\BTN\insert
        or
        WINDOW\Beresheet 1.0
        """
        # read all the messages in the queue
        while self.pipe_connection.poll(0):
            # there's a message on the pipe!
            try:
                request = self.pipe_connection.recv()

                split_request = request.split('\\')

                if len(split_request) == 2:
                    command, val = split_request

                    if command == 'WINDOW':
                        self.maple_window_handler = None
                        self.maple_window_name = val
                else:
                    self.apply_request_from_pipe(split_request)

            except:
                pass

    def find_maple_window(self):
        def enum_cb(hwnd, results):
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

        maple_window = None
        while maple_window is None:
            toplist, winlist = [], []
            win32gui.EnumWindows(enum_cb, toplist)

            maple_window = [(hwnd, title) for hwnd, title in winlist if title == self.maple_window_name]
            if len(maple_window) == 0:
                maple_window = None
                sleep(10)
                continue

            maple_window = maple_window[0]
            self.maple_window_handler = maple_window[0]

    def picture_loop(self):
        while True:
            try:
                self.listen_to_pipe()

                if self.maple_window_handler is None and self.maple_window_name is not None:
                    self.find_maple_window()

                if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.maple_window_name:

                    win32gui.SetForegroundWindow(self.maple_window_handler)
                    bbox = win32gui.GetWindowRect(self.maple_window_handler)
                    img = ImageGrab.grab(bbox)

                    self.do_each_round(img)

            except:
                pass

            sleep(self.pic_interval_sec)
