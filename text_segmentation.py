import cv2
import numpy as np
from PIL import Image
import os


def resize_image_with_aspect_ratio(image_path, new_width=None, new_height=None):
    image = Image.open(image_path)
    width, height = image.size
    aspect_ratio = width / height

    if new_width and new_height:
        # Изменяем размер изображения с сохранением соотношения сторон
        if aspect_ratio > 1:
            new_height = int(new_width / aspect_ratio)
            image = image.resize((new_width, new_height))
        else:
            new_width = int(new_height * aspect_ratio)
            image = image.resize((new_width, new_height))
    elif new_width:
        # Изменяем ширину с сохранением соотношения сторон
        new_height = int(new_width / aspect_ratio)
        image = image.resize((new_width, new_height))
    elif new_height:
        # Изменяем высоту с сохранением соотношения сторон
        new_width = int(new_height * aspect_ratio)
        image = image.resize((new_width, new_height))
    else:
        # Если не указаны новые размеры, возвращаем исходное изображение
        return image

    return image


def extract_text_words(image_path):
    # Изменяем размер изображения с сохранением соотношения сторон
    resized_image = resize_image_with_aspect_ratio(image_path, new_width=3200)

    image = cv2.cvtColor(np.array(resized_image), cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel = np.ones((5, 45), np.uint8)
    img_dilation = cv2.dilate(threshold, kernel, iterations=2)

    contours, _ = cv2.findContours(img_dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    words = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        word_image = image[y:y + h, x:x + w]

        if w > 90 and h > 20 and w * h < (x * y - 16000):
            words.append(word_image)

    return words


def process_images_in_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_files = os.listdir(input_folder)
    j = 0
    for image_file in image_files:
        j += 1
        image_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(output_folder, image_file)
        words = extract_text_words(image_path)

        for i, word in enumerate(words):
            word_path = f"{output_path.split('.jpg')[0]}_{i}.jpg"
            cv2.imwrite(word_path, word)


input_folder = 'place_docs_here/processing/rotated_pngs'
output_folder = 'place_docs_here/processing/segmented_pngs'

process_images_in_folder(input_folder, output_folder)
