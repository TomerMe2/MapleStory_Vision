import json
from os.path import isfile

import win32api
import win32con
import win32gui
import ctypes
from ctypes import c_int
import ctypes.wintypes
from ctypes.wintypes import HWND, DWORD

import win32process

dwmapi = ctypes.WinDLL("dwmapi")
DWMWA_CLOAKED = 14
isCloacked = c_int(0)

from dearpygui.core import set_main_window_size, set_global_font_scale, set_theme, set_style_window_padding, get_value, \
    set_value, add_spacing, add_text, add_slider_int, add_menu_item, add_button, start_dearpygui, set_start_callback, \
    mvMouseButton_Left, close_popup, set_main_window_title, add_window, end, delete_item
from dearpygui.simple import set_window_pos, window, menu, popup

PREF_FILE_NM = 'Auto Pots preferences.json'
SCREEN_WIDTH = 640
set_main_window_size(SCREEN_WIDTH, 500)
set_global_font_scale(1.5)
set_theme("Gold")
set_style_window_padding(30, 30)


def get_active_windows():
    def enum_cb(hwnd, results):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != '':
            dwmapi.DwmGetWindowAttribute(HWND(hwnd), DWORD(DWMWA_CLOAKED), ctypes.byref(isCloacked),
                                         ctypes.sizeof(isCloacked))
            if (isCloacked.value == 0):
                results.append((hwnd, win32gui.GetWindowText(hwnd)))

    toplist, winlist = [], []
    win32gui.EnumWindows(enum_cb, toplist)
    filtered_titles = []
    for hwnd, title in toplist:
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            hndl = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, 0, pid)
            path_of_exe = win32process.GetModuleFileNameEx(hndl, 0)
            last_in_path = path_of_exe.split('\\')[-1]

            # maplestories are always started from MapleStory.exe, unless the programmers of the server can do
            # some serious cyber
            if last_in_path == 'MapleStory.exe':
                filtered_titles.append(title)
        except:
            pass
    return filtered_titles


class GUI:

    def __init__(self, pipe_con):
        self.pipes = pipe_con
        # these two are needed for saving preferences only
        self.current_hp_btn = None
        self.current_mp_btn = None
        self.window_title = None

    def send_to_pipes(self, message):
        # Broadcast the message. If a snapshoter finds the message not relevant, it can ignore it.
        for pipe in self.pipes:
            pipe.send(message)

    def pick_maple_window(self, sender, data):

        def callback_on_picking_window(sender, data):
            self.window_title = sender
            self.send_to_pipes(f'WINDOW\\{sender}')
            set_value('Currently doing nothing. Pick MapleStory window.', f'Will work on {sender} window')
            delete_item('Pick Maple Window##1')

        def callback_on_refresh(sender, data):
            delete_item('Pick Maple Window##1')
            self.pick_maple_window(None, None)

        add_window("Pick Maple Window##1")
        add_text("Please make sure that your MapleStory")
        add_text("window is open. If your MapleStory")
        add_text("window is closed, click on refresh button")
        add_text("after opening your MapleStory window.")

        add_button('Refresh the windows', callback=callback_on_refresh)
        add_spacing(count=6)

        titles = get_active_windows()
        if len(titles) == 0:
            add_text('No active MapleStory windows')

        else:
            add_text('Please select one:')

        for window_title in titles:
            add_button(window_title, callback=callback_on_picking_window)
        end()

    def change_hp_percentage(self, sender, data):
        percentage = get_value('% HP')
        self.send_to_pipes(f'HP\\VAL\\{percentage / 100}')

        if get_value('Currently doing nothing on HP. Pick button.') != 'Currently doing nothing on HP. Pick button.':
            set_value('Currently doing nothing on HP. Pick button.', f'Taking HP on {get_value("% HP")}% by clicking on {self.current_hp_btn}.')

    def change_button(self, tp, selected):
        # tp should be HP or MP
        val = None

        if selected == 'PgUp':
            val = 'page up'
        elif selected == 'PgDn':
            val = 'page down'
        elif val is None:
            val = selected.lower()

        self.send_to_pipes(f'{tp}\\BTN\\{val}')

    def change_hp_keyboard_button(self, sender, data):
        self.current_hp_btn = sender
        self.change_button('HP', sender)
        set_value('Currently doing nothing on HP. Pick button.', f'Taking HP on {get_value("% HP")}% by clicking on {sender}.')

    def change_mp_percentage(self, sender, data):
        percentage = get_value('% MP')
        self.send_to_pipes(f'MP\\VAL\\{percentage / 100}')

        if get_value('Currently doing nothing on MP. Pick button.') != 'Currently doing nothing on MP. Pick button.':
            set_value('Currently doing nothing on MP. Pick button.',
                      f'Taking MP on {get_value("% MP")}% by clicking on {self.current_mp_btn.split("#")[0]}.')

    def change_mp_keyboard_button(self, sender, data):
        self.current_mp_btn = sender
        sender = sender.split('##')[0]
        self.change_button('MP', sender)
        set_value('Currently doing nothing on MP. Pick button.', f'Taking MP on {get_value("% MP")}% by clicking on {sender}.')

    def save_preferences(self, sender, data):
        prefs = {
            'HP_perc': get_value('% HP'),
            'MP_perc': get_value('% MP'),
            'HP_button': self.current_hp_btn,
            'MP_button': self.current_mp_btn,
            'window': self.window_title
        }
        try:
            with open(PREF_FILE_NM, 'w') as fd:
                json.dump(prefs, fd)
        except:
            pass

    def read_default_preferences(self):
        try:
            if isfile(PREF_FILE_NM):
                with open(PREF_FILE_NM, 'r') as fd:
                    prefs = json.load(fd)

                # Update the values in the GUI and in the snapshoter
                set_value('% HP', prefs['HP_perc'])
                self.change_hp_percentage(None, None)

                set_value('% MP', prefs['MP_perc'])
                self.change_mp_percentage(None, None)

                self.change_hp_keyboard_button(prefs['HP_button'], None)
                self.change_mp_keyboard_button(prefs['MP_button'], None)

                self.send_to_pipes(f'WINDOW\\{prefs["window"]}')
                set_value('Currently doing nothing. Pick MapleStory window.', f'Will work on {prefs["window"]} window')

        except:
            pass

    def run_gui(self):
        with window("Auto Pots"):
            set_start_callback(self.read_default_preferences)
            set_main_window_title('Auto Pots')
            set_window_pos("Auto Pots", 0, 0)
            add_spacing(count=12)

            add_button('Pick Maple Window', callback=self.pick_maple_window)
            add_text('Currently doing nothing. Pick MapleStory window.')
            add_spacing(count=12)

            add_text('Take HP Pot When Reaching', color=[232, 163, 33])
            add_slider_int("% HP", default_value=45, max_value=99, width=int(SCREEN_WIDTH * 0.8),
                           callback=self.change_hp_percentage)
            with menu('Select HP button on keyboard'):
                add_menu_item("Insert", callback=self.change_hp_keyboard_button)
                add_menu_item("Delete", callback=self.change_hp_keyboard_button)
                add_menu_item("Home", callback=self.change_hp_keyboard_button)
                add_menu_item("End", callback=self.change_hp_keyboard_button)
                add_menu_item("PgUp", callback=self.change_hp_keyboard_button)
                add_menu_item("PgDn", callback=self.change_hp_keyboard_button)

            add_spacing(count=12)
            add_text('Take MP Pot When Reaching', color=[232, 163, 33])
            add_slider_int("% MP", default_value=30, max_value=99, width=int(SCREEN_WIDTH * 0.8),
                           callback=self.change_mp_percentage)
            with menu('Select MP button on keyboard'):
                add_menu_item("Insert##1", callback=self.change_mp_keyboard_button)
                add_menu_item("Delete##1", callback=self.change_mp_keyboard_button)
                add_menu_item("Home##1", callback=self.change_mp_keyboard_button)
                add_menu_item("End##1", callback=self.change_mp_keyboard_button)
                add_menu_item("PgUp##1", callback=self.change_mp_keyboard_button)
                add_menu_item("PgDn##1", callback=self.change_mp_keyboard_button)

            add_spacing(count=12)
            add_button('Save Preferences As Default', callback=self.save_preferences)
            with popup("Save Preferences As Default", 'Save Popup', modal=True, mousebutton=mvMouseButton_Left):
                add_text('Your preferences has been saved')
                add_button("OK!", callback=lambda x, y: close_popup(item="Save Popup"))

            add_spacing(count=12)
            add_text('Currently doing nothing on HP. Pick button.')
            add_text('Currently doing nothing on MP. Pick button.')

        self.read_default_preferences()
        start_dearpygui(primary_window='Auto Pots')