from pytesseract import pytesseract, Output


TESSDATA_CONFIG: str = r'-l vie --tessdata-dir "./app/image_processing/tessdata"'


def detect_text_data(cropped_img):
    text_data = pytesseract.image_to_data(
        cropped_img,
        config=TESSDATA_CONFIG,
        output_type=Output.DICT
    )

    return text_data


def analyze_text_data(data_frame):
    prev_left, prev_width, cur_line, cur_par = 0, 0, 0, 0
    text = ''
    analyzed_data = []

    filtered_df = data_frame[(data_frame.conf != '-1') &
                             (data_frame.text != ' ') & (data_frame.text != '')]

    for index, line in filtered_df.iterrows():
        if cur_par != line['par_num']:
            cur_par = line['par_num']
            cur_line = line['line_num']
            prev_left = 0
        elif cur_line != line['line_num']:
            cur_line = line['line_num']
            prev_left = 0

        if line['left'] - prev_width - prev_left > 20 and text != '':
            analyzed_data.append(text.strip())
            text = ''

        text += line['text'] + ' '

        prev_left = line['left']
        prev_width = line['width']

        if index == filtered_df.index[-1]:
            analyzed_data.append(text.strip())

    return analyzed_data
