import numpy as np
import cv2


# HoughLinesP return array-liked lines with format
# [[[x1, y1, x2, y2]],
# ...
# [[x1, y1, x2, y2]]]


#  def process_image_for_ocr(file_path):
#      # Implement using opencv
#      temp_filename = set_image_dpi(file_path)
#      im_new = remove_noise_and_smooth(temp_filename)
#      return im_new


#  def set_image_dpi(file_path):
#      im = Image.open(file_path)
#      length_x, width_y = im.size
#      factor = max(1, int(IMAGE_SIZE / length_x))
#      size = factor * length_x, factor * width_y
#      # size = (1800, 1800)
#      im_resized = im.resize(size, Image.ANTIALIAS)
#      temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
#      temp_filename = temp_file.name
#      im_resized.save(temp_filename, dpi=(300, 300))
#      return temp_filename


def image_smoothening(img):
    _, th1 = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
    _, th2 = cv2.threshold(
        th1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    blur = cv2.GaussianBlur(th2, (1, 1), 0)
    _, th3 = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th3


def remove_noise_and_smooth(img):
    filtered = cv2.adaptiveThreshold(img.astype(
        np.uint8), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    kernel = np.ones((1, 1), np.uint8)
    opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    img = image_smoothening(img)
    or_image = cv2.bitwise_or(img, closing)
    return or_image


def get_grayscale_img(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def get_canny_img(img):
    return cv2.Canny(img, 50, 100, None, 3)


def get_eroded_img(img, kernel_size=1):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    return img


def get_resized_img(img, s_percent):
    scale_percent = s_percent  # Percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    # Scale image to specified percent
    img = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)
    return img


def detect_lines(img, rho=1, threshold=50, min_line_height=180, max_line_gap=4):
    horizontal_lines = []
    lines_p = cv2.HoughLinesP(
        img,
        rho,
        np.pi / 180,
        threshold,
        None,
        min_line_height,
        max_line_gap
    )

    if lines_p is not None:
        for line in enumerate(lines_p):
            coordinate = line[1][0]
            if is_horizontal(coordinate):
                horizontal_lines.append(coordinate)

    return filter_overlap_lines(horizontal_lines, 1)


def filter_overlap_lines(lines, sorting_index):
    filtered_lines = []

    lines = sorted(lines, key=lambda sorted_lines: sorted_lines[sorting_index])

    for line in enumerate(lines):
        index, cur_line = line
        if index > 0:
            prev_line = lines[index - 1]
            if (cur_line[sorting_index] - prev_line[sorting_index]) > 5:
                filtered_lines.append(cur_line)
        else:
            filtered_lines.append(cur_line)

    return filtered_lines


def is_horizontal(line):
    # Equivalent to y1 == y2, so line is horizontal line
    return line[1] == line[3]


def get_roi_selection(img, horizontal_lines, top_line_index, bottom_line_index, offset=4):
    st_y = 0
    nd_y = 0

    if len(horizontal_lines) > 0:
        # 1 and 3 is the index of y1 and y2 in an array
        # (an array([x1, y1, x2, y2]) indicates a horizontal line),
        # with horizontal lines, value of array at index 1 and 3 is the same
        st_y = horizontal_lines[top_line_index][3] + \
            offset  # Get value of above line
        nd_y = horizontal_lines[bottom_line_index][3] - \
            offset  # Get value of bottom line

    # Use value of y1 and y2 to cut image to many parts (each part is an item in order table)
    cropped_img = get_cropped_img(img, st_y, nd_y)

    return cropped_img


def get_cropped_img(img, st_y, nd_y):
    # img has format
    # [[[255, 255, ..., 255, 255]],
    # ...
    # [[255, 255, ..., 255, 255]]]
    # y1 is the top horizontal axis and y2 is the bottom horizontal axis
    cropped_img = img[st_y:nd_y]
    return cropped_img
