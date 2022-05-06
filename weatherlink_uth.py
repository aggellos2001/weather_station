from nis import cat
from signal import signal
import time
import inspect
from turtle import st
from unittest.mock import DEFAULT
import requests
from matplotlib.font_manager import json_dump
from signature_calculator import SignatureCalculator
import configparser


def get_stations():

    sig_calc = SignatureCalculator()
    signature = sig_calc.calculate_stations_signature(
        parameters["api-key"], parameters["api-secret"], parameters["t"]
    )
    try:
        request = requests.get(
            f"https://api.weatherlink.com/v2/stations",
            params={
                "api-key": parameters["api-key"],
                "api-signature": signature,
                "t": str(parameters["t"]),
            },
        )
    except Exception as e:
        print("Something went wrong!: ", e)

    print(
        f"https://api.weatherlink.com/v2/stations?api-key={parameters['api-key']}&api-signature={signature}&t={parameters['t']}"
    )

    data = request.json()
    json_dump(data, "response.json")
    print("API response was written to response.json")
    return data


def get_current_data():

    if not parameters["station-id"].isnumeric():
        print(
            "Station ID must be a number!\n"
            "Please check your configuration file (config.ini).\n"
            "Run option 1 to find your station id!"
        )
        exit()

    signature_calculator = SignatureCalculator()
    signature = signature_calculator.calculate_current_signature(
        parameters["api-key"],
        parameters["api-secret"],
        parameters["t"],
        parameters["station-id"],
    )
    print(
        f"https://api.weatherlink.com/v2/current/{parameters['station-id']}?api-key={parameters['api-key']}&api-signature={signature}&t={parameters['t']}"
    )

    station_id = parameters.pop("station-id")
    try:
        request = requests.get(
            f"https://api.weatherlink.com/v2/current/{station_id}",
            params={
                "api-key": parameters["api-key"],
                "api-signature": signature,
                "t": str(parameters["t"]),
            },
        )
    except Exception as e:
        print("Something went wrong!: ", e)
    data = request.json()
    json_dump(data, "response.json")
    print("API response was written to response.json")
    return data


if __name__ == "__main__":

    global parameters
    parameters = {}

    config = configparser.ConfigParser()
    config.read("config.ini")
    if config.sections() == []:
        print("No configuration file was found!")
        print("Creating a new config.ini...")
        config["username(change to your own)"] = {
            "api-key": "xxxxxxxxxxxxx",
            "secret-key": "xxxxxxxxxxxxx",
            "station-id": "run option 1 to find your station id",
        }
        with open("config.ini", "w") as configfile:
            config.write(configfile)
        print("Configuration file created. Please edit it and run the program again.")
        exit()
    else:
        print("Found configuration file!")
        available_users = dict(enumerate(config.sections(), start=1))
        selection = int(input(f"Select user from the config: {available_users}: "))
        while selection not in list(available_users.keys()):
            selection = int(input(f"Select user from the config: {available_users}: "))
        username = available_users[selection]

    print(f"Loading API keys for username {username}!")
    parameters["username"] = username
    parameters["api-key"] = config.get(username, "api-key")
    parameters["api-secret"] = config.get(username, "secret-key")
    parameters["station-id"] = config.get(username, "station-id")
    parameters["t"] = int(time.time())

    print("----------------------------------------")
    sel_text = """
        Type the number of the action you want to perform:
        1 to get all stations in your API Key
        2 to get the current data for selected station
        0 to exit 
        Select an option: """
    response = -1
    while response < 0 or response > 2:
        choice = input(inspect.cleandoc(sel_text))
        try:
            response = int(choice)
        except ValueError:
            print("Please enter a valid number!")
            continue
    print("----------------------------------------")
    if response == 0:
        exit()
    if response == 1:
        get_stations()
    elif response == 2:
        get_current_data()
