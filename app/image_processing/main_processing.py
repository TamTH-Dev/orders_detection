import cv2
import pandas as pd
from .text_detecting import detect_text_data, analyze_text_data
from .image_preprocessing import get_grayscale_img, get_canny_img, detect_lines, \
    get_roi_selection, get_eroded_img, get_resized_img, remove_noise_and_smooth


def wait_and_close_window(window_name):
    wait_time = 1000
    while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
        key_code = cv2.waitKey(wait_time)
        if (key_code & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break


def process(img):
    # Get grayscale image
    grayscale_img = get_grayscale_img(img)

    # Get canny image
    canny_img = get_canny_img(grayscale_img)

    # Get detected horizontal lines to determine items in order
    horizontal_lines = detect_lines(canny_img)

    # Get smooth contrast image
    contrast_img = remove_noise_and_smooth(grayscale_img)

    #  cv2.imshow('contract', contrast_img)
    #  wait_and_close_window('contrast')

    # Get eroded image
    processed_img = get_eroded_img(contrast_img)

    #  cv2.imshow('processed', processed_img)
    #  self.wait_and_close_window('processed')

    order = []
    item_properties = [
        'itemName',
        'quantity',
        'price',
        'total',
        'annotation',
    ]

    for index in range(len(horizontal_lines) - 1):
        # Get items' image which are separated by detected horizontal lines
        cropped_img = get_roi_selection(
            processed_img, horizontal_lines, index, index + 1)

        resized_img = get_resized_img(cropped_img, 200)

        #  cv2.imshow('resized', resized_img)
        #  wait_and_close_window('resized')

        # Get detected data and transfer it to data frame
        text_data = detect_text_data(resized_img)
        data_frame = pd.DataFrame(text_data)

        # Analyze text from received data frame
        analyzed_data = analyze_text_data(data_frame)

        item = {}
        if len(analyzed_data) > 0:
            gap_index = 0 if not analyzed_data[0].isnumeric() else 1
            for data in enumerate(analyzed_data):
                index, detail = data
                if (index == 0 and detail.isnumeric()) or index < gap_index or index - gap_index >= len(item_properties):
                    continue
                item[item_properties[index - gap_index]] = detail

        order.append(item)

    return {'order-details': order}
