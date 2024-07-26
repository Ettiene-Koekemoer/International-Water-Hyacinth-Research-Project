from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import pickle
from numpy import ndarray
from pandas import DataFrame
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor


class Weather(BaseModel):  # Model for input data
    windspeed: float
    winddir: float


class Location(BaseModel):  # Model for output data
    center_x: float
    center_y: float
    x_axis_length: float
    y_axis_length: float
    angle: float


origins: list[str] = ["http://localhost:5173", "http://0.0.0.0:5173", "http://127.0.0.1:5173"]

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

# Loading in the models from the preprocessing
all_values_model: RandomForestRegressor = pickle.load(open("./models/all_values_forest.pkl", "rb"))
center_x_model: KNeighborsRegressor = pickle.load(open("./models/center_x_kneighbors.pkl", "rb"))
center_y_model: KNeighborsRegressor = pickle.load(open("./models/center_y_kneighbors.pkl", "rb"))
x_axis_length_model: KNeighborsRegressor = pickle.load(open("./models/x_axis_length_kneighbors.pkl", "rb"))
y_axis_length_model: KNeighborsRegressor = pickle.load(open("./models/y_axis_length_kneighbors.pkl", "rb"))
angle_model: KNeighborsRegressor = pickle.load(open("./models/angle_kneighbors.pkl", "rb"))


@app.post("/predict/all", response_model=list[Location], status_code=status.HTTP_200_OK)
def get_prediction_for_all_ellipses_from_single_model(input_weather: Weather) -> list[Location]:
    # Loading the input data into a dataframe with the correct labels for the columns
    input_df: DataFrame = DataFrame(columns=["windspeed", "winddir"])
    input_df.loc[len(input_df.index)] = [input_weather.windspeed, input_weather.winddir]

    # Calculating a prediction using the model
    prediction: ndarray = all_values_model.predict(input_df)

    # Converting the data into the response model
    result_locations: list[Location] = []
    new_location: Location
    for i in range(0, len(prediction[0]), 5):
        new_location = Location(center_x=prediction[0][i],
                                center_y=prediction[0][i+1],
                                x_axis_length=prediction[0][i+2],
                                y_axis_length=prediction[0][i+3],
                                angle=prediction[0][i+4])
        result_locations.append(new_location)

    return result_locations


@app.post("/predict/single", response_model=list[Location], status_code=status.HTTP_200_OK)
def get_prediction_for_single_ellipse_from_seperate_models(input_weather: Weather) -> list[Location]:
    # Loading the input data into a dataframe with the correct labels for the columns
    input_df: DataFrame = DataFrame(columns=["windspeed", "winddir"])
    input_df.loc[len(input_df.index)] = [input_weather.windspeed, input_weather.winddir]

    # Calculating a prediction using the model
    prediction_center_x: ndarray = center_x_model.predict(input_df)
    prediction_center_y: ndarray = center_y_model.predict(input_df)
    prediction_x_axis_length: ndarray = x_axis_length_model.predict(input_df)
    prediction_y_axis_length: ndarray = y_axis_length_model.predict(input_df)
    prediction_angle: ndarray = angle_model.predict(input_df)

    # Converting the data into the response model
    result_locations: list[Location] = [Location(center_x=prediction_center_x[0],
                                                 center_y=prediction_center_y[0],
                                                 x_axis_length=prediction_x_axis_length[0],
                                                 y_axis_length=prediction_y_axis_length[0],
                                                 angle=prediction_angle[0])]

    return result_locations
