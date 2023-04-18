import requests
import numpy as np
import pyomo.environ as pyomo  # Used for modelling the IP
import readAndWriteJson as rwJson  # Used to read data from Json file
import csv # Used to retrieve data from csv file

def readData(filename: str) -> dict:
    data = rwJson.readJsonFileToDictionary(filename)
    return data

# defining the getDistance function, which takes the name, lat and lon for both the start and end position
def getDistance(name1 : str, name2 : str, lat1: str, lon1: str, lat2: str, lon2: str):
    # API Key is how google maps knows who makes the call. This is how we gain access to google maps API
    API_KEY = "!INSERT GOOGLE MAPS API KEY HERE!"


    # The url of the google maps distancematrix endpoint. It takes the lat and lon of the two positions and returns the value in meters
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={lat1},{lon1}&destinations={lat2},{lon2}&key={API_KEY}"
    # we save the result in the variable response. requests.get means that we make a GET-request to googles endpoint.

    if (lat1 == 0 and lat2 == 0):
        return 0
    if (lat1 == 0 and lat2 != 0):
        return name2
    if (lat1 != 0 and lat2 == 0):
        return name1

    response = requests.get(url)

    # save the response from google as a json
    data = response.json()

    # Extract the distance and convert to kilometers

    distance = data["rows"][0]["elements"][0]["distance"]["value"] / 1000

    # print the distance into the console. The value could also be saved somewhere for later evaluation
    # print(f"The distance between {name1} and {name2} is {distance:.2f} kilometers.")
    return str(distance)


def getDistanceMatrix(warehouses: list, customers: list):
    # iterate over every warehouse and every customer, to get the actual value between the two position.
    distances = np.zeros((len(warehouses), len(customers)))
    for i, warehouse in enumerate(warehouses):
        for j, customer in enumerate(customers):
            # getDistance(warehouse.name, warehouse.lat, warehouse.lon, customer.name, customer.lat, customer.lon)
            distances[i, j] = getDistance(warehouse[0], customer[0], warehouse[1], warehouse[2], customer[1], customer[2])

    return distances

def getCustomers():
    # Open the CSV file and read its contents
    with open('coordinates.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)

        # Create an empty list to store the arrays
        customers = []

        # Loop through each row in the CSV file
        for row in reader:
            # Create a new array with the two column values and append it to the array of arrays
            new_customer = [row[0], row[1], row[2]]
            customers.append(new_customer)

    return customers;

def getWarehouses():
    # Open the CSV file and read its contents
    with open('coordinateswarehouses.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)

        # Create an empty list to store the arrays
        warehouses = []

        # Loop through each row in the CSV file
        for row in reader:
            # Create a new array with the two column values and append it to the array of arrays
            new_warehouse = [row[0], row[1], row[2]]
            warehouses.append(new_warehouse)


    return warehouses;

def buildModel(data: dict) -> pyomo.ConcreteModel():
    warehouses = getWarehouses()
    customers = getCustomers()

    warehouses = [[0, 0, 0]] + warehouses
    customers = [[0, 0, 0]] + customers

    distanceMatrix = getDistanceMatrix(warehouses, customers);
    np.savetxt("endeelig_distance_matrix.csv", distanceMatrix, delimiter=",")

def main(instance_file_name):
    data = readData(instance_file_name)
    model = buildModel(data)

if __name__ == '__main__':
    instance_file_name = 'Maps_data'
    main(instance_file_name)
