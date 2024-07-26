import cv2
import glob
import datetime
import numpy as np
import pandas as pd

from cv2.typing import MatLike
from typing import Sequence

DEBUG: bool = False
KERNEL_SIZE: int = 3
EROSION_DILATION_ITR: int = 1
LARGEST_BLOBS_TRACKED: int = 3


def get_all_images_in_folder(folder_path: str, filter_bad_out: bool) -> list[str]:
    # Get all image paths from the folder
    images: list[str] = glob.glob(f"{folder_path}/*.png")
    # Sort them, which sorts them by date due to the naming
    images.sort()

    if filter_bad_out:
        # Filter all images that have the letter 'X'
        # This marking shows that they have clouds and thus are unusable
        good_images: list[str] = []
        for image in images:
            if image.find('X') == -1:
                good_images.append(image)
        return good_images
    else:
        return images


def convert_image_to_dataframe_row(image_path: str) -> pd.DataFrame:
    # Read the image from the file
    image: MatLike = cv2.imread(image_path)

    if DEBUG:  # Display the image
        cv2.imshow(f"{image_path} - Full Res", image)
        cv2.waitKey(0)

    # Blurring the image to try reduce noise
    smoothed_image: MatLike = cv2.GaussianBlur(image, (KERNEL_SIZE, KERNEL_SIZE), 0)

    if DEBUG:
        cv2.imshow(f"{image_path} - Smoothed", smoothed_image)
        cv2.waitKey(0)

    # Detecting and green of the lake
    # Perfect green and blue have a hue of 120 and 240 respectively
    # OpenCV HSV maximum hue value is 360/2, so perfects are 60 and 120 respectively
    # https://docs.opencv.org/4.x/da/d97/tutorial_threshold_inRange.html
    hsv_image: MatLike = cv2.cvtColor(smoothed_image, cv2.COLOR_BGR2HSV)

    # Threshold values were obtained emperically
    # These thresholds are ideal for the Sentinel2 optical image
    lower_green: np.ndarray = np.array([55, 50, 112])  # Value is set to around 50%, because the BGR value of the green surface is 0, 128, 0
    upper_green: np.ndarray = np.array([65, 255, 144])  # With a max value of 256, 128 is exactly this 50%

    # These thresholds are ideal for the Sentinel1 radar image
    # lower_green: np.ndarray = np.array([55, 50, 50])  # Value is set to be within 20% and 100%
    # upper_green: np.ndarray = np.array([65, 255, 255])

    # These thresholds are a middle ground to have a decent enough detection with both satellites
    # lower_green: np.ndarray = np.array([55, 50, 100])  # Value is set to be within 40% and 80%
    # upper_green: np.ndarray = np.array([65, 255, 200])

    mask_green: MatLike = cv2.inRange(hsv_image, lower_green, upper_green)

    if DEBUG:
        cv2.imshow(f"{image_path} - Green Mask", mask_green)
        cv2.waitKey(0)

    # Eroding and dilating the image to clear noise
    kernel: np.ndarray = np.ones((KERNEL_SIZE, KERNEL_SIZE), np.uint8)
    noise_cleared_image: MatLike = cv2.dilate(
        cv2.erode(
            mask_green,
            kernel,
            iterations=EROSION_DILATION_ITR),
        kernel,
        iterations=EROSION_DILATION_ITR)

    if DEBUG:
        cv2.imshow(f"{image_path} - Erosion & Dilation ({EROSION_DILATION_ITR} times, Kernel size: {KERNEL_SIZE})", noise_cleared_image)
        cv2.waitKey(0)

    # Dilating and eroding to fill gaps
    kernel: np.ndarray = np.ones((KERNEL_SIZE, KERNEL_SIZE), np.uint8)
    gap_filled_image: MatLike = cv2.erode(
        cv2.dilate(
            noise_cleared_image,
            kernel,
            iterations=EROSION_DILATION_ITR),
        kernel,
        iterations=EROSION_DILATION_ITR)

    if DEBUG:
        cv2.imshow(f"{image_path} - Dilation & Erosion ({EROSION_DILATION_ITR} times, Kernel size: {KERNEL_SIZE})", gap_filled_image)
        cv2.waitKey(0)

    # Detecting the contours of the shapes in the image
    # https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html
    contours_return: tuple[Sequence[MatLike], MatLike] = cv2.findContours(gap_filled_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours: list[MatLike] = list(contours_return[0])
    contours.sort(key=lambda item: cv2.contourArea(item), reverse=True)

    # Draw the x amount largest contours, these are the ones we are going to keep track of
    i: int = 0
    selected_shapes: int = 0
    resulting_ellipses: pd.DataFrame = pd.DataFrame(columns=["center_x", "center_y", "x_axis_length", "y_axis_length", "angle"])
    while selected_shapes < LARGEST_BLOBS_TRACKED:
        # Finding center point of the shape
        M: dict[str, float] = cv2.moments(contours[i])
        if M['m00'] != 0:
            x = int(M['m10']/M['m00'])
            y = int(M['m01']/M['m00'])

            # Check if the contours is surrounding an area of plant mass or not (if plant mass pixel value will be 255)
            if gap_filled_image[y, x] != 0:
                cv2.drawContours(image, [contours[i]], 0, (0, 0, 255), 2)
                cv2.putText(image, f"Contour_center ({x},{y})", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                # Fitting an ellipse to the contour of the plant masses, this returns the rotated rectangle in which the ellipse is inscribed
                ellipse: tuple[Sequence[float], Sequence[int], float] = cv2.fitEllipse(contours[i])
                cv2.ellipse(image, ellipse, (0, 255, 0), 2)
                cv2.putText(image, f"Ellipse_center ({int(ellipse[0][0])},{int(ellipse[0][1])})",
                            (int(ellipse[0][0]), int(ellipse[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # Adding a new row to the dataframe with the center coordinates, axes lengths and angle of the ellipse
                resulting_ellipses.loc[len(resulting_ellipses.index)] = [ellipse[0][0], ellipse[0][1], ellipse[1][0], ellipse[1][1], ellipse[2]]
                selected_shapes += 1
        i += 1

    if DEBUG:
        cv2.imshow(f"{image_path} Original Image - {LARGEST_BLOBS_TRACKED} Largest Contours Drawn", image)
        cv2.waitKey(0)

    # Creating a new dataframe where all ellipses are in a single record
    single_row_df: pd.DataFrame = pd.DataFrame()

    # Separating the date-time from the image name
    date_string: str = image_path.split('/')[3].split('_')[0]
    date_object: datetime.date = datetime.datetime.strptime(date_string, "%Y%m%d").date()
    single_row_df.insert(0, "datetime", [str(date_object)], True)

    # This should be done better, preferably during the assignment of the ellipse to the resulting_ellipses dataframe
    # so this can be avoided and we don't iterate over stuff too often
    # Slice the dataframe up and fit it into a single row for each day
    record_index: int = 1
    column_index: int
    new_column_index: int = 1
    for record in resulting_ellipses.to_numpy():
        column_index = 0
        for column in record:
            single_row_df.insert(new_column_index, f"{resulting_ellipses.columns[column_index]}_{record_index}", [column], True)
            column_index += 1
            new_column_index += 1
        record_index += 1

    return single_row_df
