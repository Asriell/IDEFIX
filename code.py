import cv2
import copy
import numpy as np


class Code:

    """
    This class is used in two different ways.\n
    - Hardcoded data to recognize and initialize a scan code.\n
    - Indication for the next intersection.
    """

    def __init__(self, scans):

        self.initialized = False

        # corresponding scan code
        self.scan = (0, 0, 0, 0)
        # left, up, right -> True = there is a road
        self.path = [False, False, False]
        # left, up, right -> True = they have priority
        self.wait = [False, False, False]
        # reference to the dictionary containing all the codes's scans
        self.scans = scans

    def __str__(self):
        if self.initialized:
            string = "Scan: " + str(self.scan) + "\n"
            string += "Path: " + str(self.path) + "\n"
            string += "Priority: " + str(self.wait) + "\n"
            return string
        else:
            return "Not initialized."

    def init_new_code_data(self, direction, priority, scan):
        """
        Create a new Code for data purpose.
        :param direction: bool[], the possible roads.
        :param priority: bool[], road with higher priority than our.
        :param scan: int[], scan code of the intersection.
        :return: None
        """
        for i in range(len(direction)):
            if direction[i]:
                self.open_path(i, priority[i])
        self.scans[to_tuple(scan)] = self

    def open_path(self, i, priority):
        """
        Add a branch to the intersection.
        :param i: int, the branch of the intersection.\n
        - 0: left\n
        - 1: up\n
        - 2: right.
        :param priority: bool, tell if this branch has priority on us.
        :return: None
        """
        if 0 <= i < 3:
            self.path[i] = True
            self.wait[i] = priority

    def scan_code(self, scan):
        """
        Recognize the given code and initialize the intersection with it.
        :param scan: tuple-4 int (colors). Index 0 is the closest color.
        :return: None
        """
        if scan in self.scans.keys():
            code = copy.deepcopy(self.scans[scan])
            self.path = code.path
            self.wait = code.wait
            self.scan = code.scan
            self.initialized = True


class CodeDataPack:

    def __init__(self):
        self.codes = dict()

    def init_new_code_data(self, direction, priority, scan):
        """
        Add a new code and the associated intersection to the database.
        :param direction: bool[], possible roads.
        :param priority: bool[], which road has a priority higher than mine.
        :param scan: tuple-4 int, the associated scan code.
        :return: None
        """
        if scan not in self.codes.keys():
            tmp_code = Code(self.codes)
            tmp_code.init_new_code_data(direction, priority, scan)
            self.codes[scan] = copy.deepcopy(tmp_code)

    def hardcoded_data_init(self):
        """
        Initialize the database with hardcoded data.
        :return: None
        """
        # straight line
        self.init_new_code_data([False, True, False],
                                [False, True, False],
                                (255, 255, 255, 255))  # 4 patches are white

        # 4-connect intersection
        self.init_new_code_data([True, True, True],
                                [False, False, True],
                                (0, 206, 255, 255))
        self.init_new_code_data([True, True, True],
                                [True, False, False],
                                (0, 114, 255, 255))
        self.init_new_code_data([True, True, True],
                                [True, True, False],
                                (0, 255, 114, 255))
        self.init_new_code_data([True, True, True],
                                [False, True, True],
                                (0, 255, 206, 255))
        self.init_new_code_data([True, True, True],
                                [True, False, True],
                                (0, 0, 255, 255))
        self.init_new_code_data([True, True, True],
                                [False, True, False],
                                (0, 255, 0, 255))
        self.init_new_code_data([True, True, True],
                                [True, True, True],
                                (0, 255, 255, 255))

        # 3-connect intersection
        self.init_new_code_data([True, True, False],
                                [False, True, False],
                                (206, 255, 0, 206))
        self.init_new_code_data([True, True, False],
                                [True, False, False],
                                (206, 114, 255, 114))
        self.init_new_code_data([False, True, True],
                                [False, False, True],
                                (206, 206, 255, 114))
        self.init_new_code_data([True, True, False],
                                [True, True, False],
                                (206, 255, 114, 0))
        self.init_new_code_data([False, True, True],
                                [False, True, True],
                                (206, 255, 206, 0))

        # T-connect intersection
        self.init_new_code_data([True, False, True],
                                [True, False, False],
                                (206, 114, 255, 255))
        self.init_new_code_data([True, False, True],
                                [False, False, True],
                                (206, 206, 255, 206))
        self.init_new_code_data([True, False, True],
                                [True, False, True],
                                (206, 0, 255, 0))


class Scanner:

    def __init__(self):
        # init the database
        self.database = CodeDataPack()
        self.database.hardcoded_data_init()

    def complete_process(self, image):
        """
        Execute the complete process in the given image.
        :param image: A cv2 image.
        :return: Return a Code() object. Return None if the algorithm couldn't
        perform because of an incomplete image.
        """
        # scan the given image
        code_value = scanner(image)

        # find the associated intersection
        if code_value is not None:

            code_tuple = to_tuple(code_value)

            code_class = Code(self.database.codes)
            code_class.scan_code(code_tuple)

            return code_class


def init_capture_from_load(img_path):
    """
    Load an image and call the init_image() function on it.
    :param img_path: string, path of the image.
    :return: cv2 image, the modified one.
    """
    img = cv2.imread(img_path, 0)
    return init_image(img)


def init_image(img):
    """
    Return the resized image.
    :param img: A cv2 image.
    :return: cv2 image modified.
    """
    img = cv2.resize(img, (500, 500))
    img = img[:, 100:]

    h, w = img.shape

    top_lim = False
    bot_lim = False
    for i in range(w):
        ind = w - i - 1
        if img[0, ind] < 10:
            top_lim = True
        if top_lim and img[0, ind] > 240:
            img = img[:, :ind]
            break
        if img[h - 1, ind] < 10:
            bot_lim = True
        if bot_lim and img[h - 1, ind] > 240:
            img = img[:, :ind]
            break

    return img


def scanner(img):
    """
    Scan a given image and return the associated code.
    :param img: A cv2 image.
    :return: Return the code associated to the image. Return None if the code is
    incomplete.
    """

    code = [None, None, None, None]

    h, w = img.shape

    split = True
    code_index = 0
    histogram = np.zeros(256)

    for y in range(h):
        color = None
        index = np.argmax(img[y, :] < 10)
        if index != 0:
            color = img[y, index + 50]

        if color is not None:
            histogram[color] += 1
            split = False

        elif not split:
            split = True
            code[code_index] = np.argmax(histogram)
            histogram[:] = 0
            code_index += 1

    if None in code:
        return None

    code.reverse()  # reverse to have the same order than the Code class
    return code


def to_tuple(array):
    """
    Convert an array of 4 elements into a tuple.
    :param array: Array of dimension 4.
    :return: A tuple of dimension 4.
    """
    return array[0], array[1], array[2], array[3]


if __name__ == "__main__":

    scan_object = Scanner()
    # load the image (optional if you can give your cv2 image as parameter)
    # if you do, use init_image(your_cv2_image) instead
    image_loaded = \
        init_capture_from_load("test_images/line_code.png")
    print(scan_object.complete_process(image_loaded))







