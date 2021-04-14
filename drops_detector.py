import cv2 as cv
import numpy as np


def is_intersect(min_x1, max_x1, min_x2, max_x2):
    if min_x1 <= min_x2 and max_x1 >= max_x2:
        # x1 is contained in x2
        return True
    if min_x2 <= min_x1 and max_x2 >= max_x1:
        # x2 is contained in x2
        return True
    if min_x1 <= min_x2 <= max_x1:
        # x1 starts before x2, but ends after x2 starts
        return True
    if min_x2 <= min_x1 <= max_x2:
        # x2 starts before x1, but ends after x1 starts
        return True
    return False


class DropsDetector:

    def __init__(self, player_detector):
        self.player_detector = player_detector

    def is_drop_nearby(self, im):
        """
        im is PIL image
        """
        im = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
        player_loc = self.player_detector.get_location_of_player(im)

        imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        ret, thresh = cv.threshold(imgray, 127, 255, 0)
        ans = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        approximate_height_of_player = int(im.shape[0] * 0.12)
        approximate_width_of_player = int(im.shape[1] * 0.04)

        min_x_player, max_x_player = player_loc[0] - approximate_width_of_player, player_loc[0] + \
                                     approximate_width_of_player
        min_y_player, max_y_player = player_loc[1] - approximate_height_of_player, player_loc[1]
        height_of_player = max_y_player - min_y_player
        min_y_for_drops = max_y_player - (max_y_player - min_y_player) // 2

        contours = ans[0]
        drops = []
        # first pass - we want to find all the relevant contours
        for contour in contours:
            min_x, min_y = list(np.min(contour, axis=0))[0]
            max_x, max_y = list(np.max(contour, axis=0))[0]

            # drop object must be more than 5 pixels long and less than 30 pixels long
            width_of_contour = max_x - min_x
            if width_of_contour < 5 or width_of_contour > 30:
                continue

            # drop inside player
            if max_x <= max_x_player and min_x >= min_x_player and max_y <= max_y_player and min_y >= min_y_for_drops:
                # if not is_line(contour):
                drops.append(contour)
            # drop is intersecting player from right
            elif max_x >= max_x_player and min_x <= min_x_player and max_y <= max_y_player and min_y >= min_y_for_drops:
                # if not is_line(contour):
                drops.append(contour)
            # drop is intersecting player from left
            elif min_x <= min_x_player and max_x >= min_x_player and max_y <= max_y_player and min_y >= min_y_for_drops:
                # if not is_line(contour):
                drops.append(contour)

        # second pass - we want to see if any of the contours in conjunction with another contour yields a drop
        for i, cntr1 in enumerate(drops):
            min_x1, min_y1 = list(np.min(cntr1, axis=0))[0]
            max_x1, max_y1 = list(np.max(cntr1, axis=0))[0]

            if max_y1 > min_y_player + height_of_player * 0.75:
                # cntr1 is way too down
                continue

            for j, cntr2 in enumerate(drops):
                if i == j:
                    continue

                min_x2, min_y2 = list(np.min(cntr2, axis=0))[0]
                max_x2, max_y2 = list(np.max(cntr2, axis=0))[0]

                if min_y1 >= min_y_for_drops and min_y2 >= min_y_for_drops and max_y1 <= max_y_player and max_y2 <= max_y_player and (
                        (max_y1 <= max_y2 and min_y1 <= min_y2) or (
                        max_y2 <= max_y1 and min_y2 <= min_y1)) and is_intersect(min_x1, max_x1, min_x2, max_x2):
                    return True

        return False
