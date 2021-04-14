from dataclasses import dataclass
from Levenshtein import distance as lev_distance
import cv2 as cv

import easyocr
import numpy as np

"""
This file detects the location of the player.
On the first image it gets, it uses OCR to detect the name of the player and to find a template of it's player tag.
On later images, it uses template matching to find the player tag.
"""

@dataclass
class OcrEntry:
    bbox: np.array
    text: str
    width: float
    height: float
    max_x: float
    min_x: float
    max_y: float
    min_y: float


def _find_name_of_player_bot_left(ocr_entries, width_of_img, height_of_img):
    """
    Finds the entry that contains the name of the player in the menus, at the bottom left of the screen
    """
    # get the entries on the bottom left of the screen
    entries_on_bottom_left = [entry for entry in ocr_entries if
                              entry.max_x < width_of_img * 0.4 and entry.min_y > height_of_img * 0.95]

    if len(entries_on_bottom_left) == 0:
        return None

    # get the most left label
    entry_with_name = sorted(entries_on_bottom_left, key=lambda entry: entry.min_x)[-1]
    return entry_with_name


def _find_other_entries_with_name(ocr_entries, entry_with_name_bot_left):
    # check that they are not exactly the same entry and they have relatively the same text
    other_entries_with_name = [entry for entry in ocr_entries if
                               lev_distance(entry.text, entry_with_name_bot_left.text) <= 2 and
                               not (entry.max_x == entry_with_name_bot_left.max_x and
                                    entry.min_x == entry_with_name_bot_left.min_x and
                                    entry.max_y == entry_with_name_bot_left.max_y and
                                    entry.min_y == entry_with_name_bot_left.min_y)]
    return other_entries_with_name


def _make_template_of_player_name_tag(other_entries_with_name, im):
    x_center = im.shape[1] // 2
    other_entries_with_name_x_center = [(entry.max_x + entry.min_x) // 2 for entry in other_entries_with_name]

    closest_to_center_i = np.argmin([abs(val - x_center) for val in other_entries_with_name_x_center])
    closest_to_center = other_entries_with_name[closest_to_center_i]

    template_of_name_tag = im[closest_to_center.min_y: closest_to_center.max_y + 1,
                              closest_to_center.min_x: closest_to_center.max_x + 1]
    return template_of_name_tag


class PlayerDetector:
    def __init__(self):
        self.reader = None
        self.name_tag_template = None

    def get_location_of_player(self, im):
        """
        im is OpenCV image
        on success returns a tuple
        on failure returns None
        """
        # will take about 6 seconds the first time.
        # the next times are almost immediate
        if self.reader is None or self.name_tag_template is None:
            self._prepare(im)

        return self._find_template_in_image(im)

    def _prepare(self, first_im):
        # loads the NN into the memory, and builds a name tag template
        if self.reader is None:
            self.reader = easyocr.Reader(['en'])  # need to run only once to load model into memory
        self.build_name_tag_template(first_im)

    def _read_and_filter(self, im):
        result = self.reader.readtext(im)

        processed_results = []
        for bbox, text, confidence in result:
            # We are not filtering results base on confidence.
            # This is because we know the approximate location of the text on the screen

            # according to easyOCR Github example (voodoo numbers)
            max_x = bbox[1][0]
            min_x = bbox[0][0]
            max_y = bbox[2][1]
            min_y = bbox[0][1]
            entry = OcrEntry(bbox, text, max_x - min_x, max_y - min_y, max_x, min_x, max_y, min_y)
            processed_results.append(entry)

        return processed_results

    def build_name_tag_template(self, im):
        """
        :param im: openCV img
        """
        ocr_entries = self._read_and_filter(im)
        if len(ocr_entries) == 0:
            return
        width_of_img, height_of_img = im.shape[1], im.shape[0]
        entry_with_name_bot_left = _find_name_of_player_bot_left(ocr_entries, width_of_img, height_of_img)

        if entry_with_name_bot_left is None:
            return
        
        other_entries_with_name = _find_other_entries_with_name(ocr_entries, entry_with_name_bot_left)
        self.name_tag_template = _make_template_of_player_name_tag(other_entries_with_name, im)

    def _find_template_in_image(self, im):
        """
        :param im: the image that was taken now
        :return: a tuple (X, Y) where X is the middle of the name tag left\right wise, and Y is the top of the name tag
        """
        x_center = im.shape[1] // 2

        res = cv.matchTemplate(im, self.name_tag_template, cv.TM_CCOEFF_NORMED)
        template_width, template_height = self.name_tag_template.shape[1], self.name_tag_template.shape[0]

        threshold = 0.5
        locs_of_candidates = np.where(res >= threshold)

        # voodoo from docs
        # now each candidate is a point (X, Y) of the top left corner of the start of the candidate
        candidates = list(zip(*locs_of_candidates[::-1]))

        if len(candidates) == 0:
            return None

        distance_of_candidates_from_x_center = [abs((left_x + template_width) // 2 - x_center)
                                                for left_x, top_y in candidates]

        candidate_closest_to_x_center_i = np.argmin(distance_of_candidates_from_x_center)

        best_candidate_min_x, best_candidate_min_y = candidates[candidate_closest_to_x_center_i]

        return (best_candidate_min_x + best_candidate_min_x + template_width) // 2, best_candidate_min_y

