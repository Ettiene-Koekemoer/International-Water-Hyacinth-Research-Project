import preprocessing_weather as preproc_wthr
import preprocessing_image as preproc_img

import argparse
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor

PATH_TO_IMAGES: str = "./training_data/Sentinel2"
PATH_TO_PROCESSED_DATA: str = "./training_data/processed_data"

PREPROCESS: bool = True


def gather_data_and_preprocess() -> tuple[pd.DataFrame, pd.DataFrame]:
    # First we drop all unneeded columns from the weather data
    weather_df: pd.DataFrame = preproc_wthr.drop_unneeded_columns()
    # Write it to a csv file for safekeeping and easy viewing
    weather_df.to_csv(f"{PATH_TO_PROCESSED_DATA}/preprocessed_weather_hartbeespoort.csv", index=False)

    # Get a list of all the images in the folder
    images: list[str] = preproc_img.get_all_images_in_folder(PATH_TO_IMAGES, True)

    # Create a new dataframe with the structure fo the first image
    images_df: pd.DataFrame = preproc_img.convert_image_to_dataframe_row(images[0])
    for i in range(1, len(images)):
        images_df = pd.concat([images_df, preproc_img.convert_image_to_dataframe_row(images[i])])
    # Write it to a csv file for safekeeping and easy viewing
    images_df.to_csv(f"{PATH_TO_PROCESSED_DATA}/preprocessed_image_hartbeespoort.csv", index=False)

    # Dropping rows in the weather data that are before the first and after the last image
    weather_df.drop(weather_df[weather_df["datetime"] < images_df["datetime"].min()].index, inplace=True)
    weather_df.drop(weather_df[weather_df["datetime"] > images_df["datetime"].max()].index, inplace=True)

    # Remove rows in the weather data where we have no image data for
    # Since according to the researchers the hyacinth moves across the lake in a couple of hours,
    # it doesn't really matter what happen in between the days of the images
    filtered_weather_df: pd.DataFrame = pd.DataFrame(columns=weather_df.columns)
    for item in weather_df.values:
        if item[0] in images_df["datetime"].values:
            filtered_weather_df.loc[len(filtered_weather_df.index)] = item

    # Set the date of the row as the index
    filtered_weather_df.set_index(["datetime"], inplace=True)
    images_df.set_index(["datetime"], inplace=True)

    filtered_weather_df.to_feather(f"{PATH_TO_PROCESSED_DATA}/preprocessed_weather_hartbeespoort.feather")
    images_df.to_feather(f"{PATH_TO_PROCESSED_DATA}/preprocessed_image_hartbeespoort.feather")

    return filtered_weather_df, images_df


def main() -> None:
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description="Preprocess and predict location of Water Hyacinth on Hartbeespoort dam.")
    parser.add_argument("-p", "--preprocess", action="store_true")

    args: argparse.Namespace = parser.parse_args()
    PREPROCESS: bool = args.preprocess

    weather_df: pd.DataFrame
    images_df: pd.DataFrame

    if PREPROCESS:
        result_data: tuple[pd.DataFrame, pd.DataFrame] = gather_data_and_preprocess()
        weather_df = result_data[0]
        images_df = result_data[1]
    else:
        weather_df = pd.read_feather(f"{PATH_TO_PROCESSED_DATA}/preprocessed_weather_hartbeespoort.feather")
        images_df = pd.read_feather(f"{PATH_TO_PROCESSED_DATA}/preprocessed_image_test.feather")

    # Fitting a regression model to predict all values
    all_values_model = RandomForestRegressor()
    all_values_model.fit(weather_df, images_df)
    # Exporting the model
    pickle.dump(all_values_model, open("./models/all_values_forest.pkl", "wb"))

    # Prepare data for multiple models, but only once ellipse
    shrunk_images_df: pd.DataFrame = pd.DataFrame(columns=["center_x", "center_y", "x_axis_length", "y_axis_length", "angle"])
    for row in images_df.values:
        shrunk_images_df.loc[len(shrunk_images_df.index)] = [row[0], row[1], row[2], row[3], row[4]]
    shrunk_images_df.index = images_df.index
    # Splitting into dataframes per feature
    center_x_image_df: pd.DataFrame = shrunk_images_df.drop(columns=["center_y", "x_axis_length", "y_axis_length", "angle"])
    center_y_image_df: pd.DataFrame = shrunk_images_df.drop(columns=["center_x", "x_axis_length", "y_axis_length", "angle"])
    x_axis_length_image_df: pd.DataFrame = shrunk_images_df.drop(columns=["center_x", "center_y", "y_axis_length", "angle"])
    y_axis_length_image_df: pd.DataFrame = shrunk_images_df.drop(columns=["center_x", "center_y", "x_axis_length", "angle"])
    angle_image_df: pd.DataFrame = shrunk_images_df.drop(columns=["center_x", "center_y", "x_axis_length", "y_axis_length"])
    # Fitting Kneigbors models to predict all values seperately
    center_x_model = KNeighborsRegressor(n_neighbors=50, p=5, weights="distance")
    center_y_model = KNeighborsRegressor(n_neighbors=25, p=1)
    x_axis_length_model = KNeighborsRegressor(n_neighbors=100, p=5)
    y_axis_length_model = KNeighborsRegressor(n_neighbors=100, leaf_size=5, p=1)
    angle_model = KNeighborsRegressor(n_neighbors=100, leaf_size=100, p=1)
    center_x_model.fit(weather_df, center_x_image_df)
    center_y_model.fit(weather_df, center_y_image_df)
    x_axis_length_model.fit(weather_df, x_axis_length_image_df)
    y_axis_length_model.fit(weather_df, y_axis_length_image_df)
    angle_model.fit(weather_df, angle_image_df)
    # Exporting all models
    pickle.dump(center_x_model, open("./models/center_x_kneighbors.pkl", "wb"))
    pickle.dump(center_y_model, open("./models/center_y_kneighbors.pkl", "wb"))
    pickle.dump(x_axis_length_model, open("./models/x_axis_length_kneighbors.pkl", "wb"))
    pickle.dump(y_axis_length_model, open("./models/y_axis_length_kneighbors.pkl", "wb"))
    pickle.dump(angle_model, open("./models/angle_kneighbors.pkl", "wb"))


if __name__ == "__main__":
    main()
