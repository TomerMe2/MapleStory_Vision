import numpy as np
import cv2 as cv
from dataclasses import dataclass


def get_percentages_of_hp_mp(pil_img_of_game_window):
    # pil to cv
    im = cv.cvtColor(np.array(pil_img_of_game_window), cv.COLOR_RGB2BGR)
    # take only the bottom of the image, this is where the bars are at
    im = im[int(im.shape[0] * 0.9):, :, :]
    contours = _get_contours(im)
    candidates_for_bars = _find_candidates_for_bars(contours)
    bars = _find_bars_from_candidates(candidates_for_bars)
    if len(bars) == 0:
        # couldn't find
        return None, None

    hp_bar, mp_bar = _find_hp_mp_bars(bars)
    hp_percentage = _percentage_of_full_in_bar(hp_bar, im)
    mp_percentage = _percentage_of_full_in_bar(mp_bar, im)

    return hp_percentage, mp_percentage


def _get_contours(im):
    imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(imgray, 127, 255, 0)
    ans = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    return ans[0]  # contours are at ans[0]


def _find_candidates_for_bars(contours):
    candidates_for_bars = []
    for i, contour in enumerate(contours):
        number_of_dots = contour.shape[0]
        min_x, min_y = list(np.min(contour, axis=0))[0]
        max_x, max_y = list(np.max(contour, axis=0))[0]

        width = max_x - min_x
        height = max_y - min_y

        # these are the features of a bar
        # small number of dots is a feature because a bar is mostly straight lines
        if number_of_dots < 10 and width > 50 and height > 10:
            bar_candidate = Bar(contour, width, height, max_x, min_x, min_y)
            candidates_for_bars.append(bar_candidate)

    return candidates_for_bars


def _find_bars_from_candidates(candidates):
    def is_legit_to_add(matching, maybe_add):
        for member in matching:
            # check that these lines doesn't intersect
            is_ok = (maybe_add.max_x > member.max_x and maybe_add.min_x > member.max_x) or \
                    (maybe_add.max_x < member.min_x and maybe_add.min_x < member.max_x)

            if not is_ok:
                return False

        return True

    width_error = 18  # in pixels
    height_error = 3  # in pixels

    for candidate1 in candidates:
        if candidate1.width / candidate1.height < 3:
            # this candidate is probably the shop, menu... buttons.
            # it's not thin shaped enough
            continue

        matching = [candidate1]
        for candidate2 in candidates:
            # check that they are in the same width and height
            if candidate1 is not candidate2 and \
                    abs(candidate1.width - candidate2.width) <= width_error and \
                    abs(candidate1.height - candidate2.height) <= height_error and \
                    is_legit_to_add(matching, candidate2):
                matching.append(candidate2)

        if len(matching) == 3:
            return matching

    return []


def _percentage_of_full_in_bar(bar, im):
    # look only at the middle of the bar
    line_y = bar.min_y + bar.height // 2

    black_clr = np.array([255, 0, 0])
    # kind of black is instead of grey when the bar is flashing
    kind_of_black_clr = np.array([60, 60, 60])
    # there are 2 shades of grey that we should accept
    grey_clr1 = np.array([190, 190, 190])
    grey_clr2 = np.array([200, 200, 200])

    line = im[line_y]
    number_of_prefixes_or_suffixes_pixels = 0
    number_of_grey = 0

    for clr in line[bar.min_x: bar.max_x + 1]:
        if np.allclose(clr, black_clr, atol=1):
            # it's still black and it made into our bar by mistake
            number_of_prefixes_or_suffixes_pixels += 1

        elif np.allclose(clr, grey_clr1, atol=7) or np.allclose(clr, grey_clr2, atol=7) \
                or np.allclose(clr, kind_of_black_clr, atol=7):
            # it's grey or kind of black
            number_of_grey += 1

    pixels_in_bar = bar.max_x - bar.min_x - number_of_prefixes_or_suffixes_pixels
    return (pixels_in_bar - number_of_grey) / pixels_in_bar


def _find_hp_mp_bars(bars):
    # returns a tuple, the first is the HP bar and the second is the MP bar
    # we know the the HP bar is the left bar, MP bar is the middle bar and XP is the right bar
    bars_left_to_right = sorted(bars, key=lambda bar: bar.min_x)
    return bars_left_to_right[0], bars_left_to_right[1]


@dataclass
class Bar:
    contour: np.array
    width: float
    height: float
    max_x: float
    min_x: float
    min_y: float
