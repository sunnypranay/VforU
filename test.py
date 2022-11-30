# This is a testing file to test the API endpoint /register/listener

# Path: test.py

import requests


def registerTest(data, expected, testNumber):
    
    # This is the API endpoint
    url = "http://127.0.0.1:5000/register/listener"

    # This is the request we will send to the API endpoint
    response = requests.post(url, json=data)

    # check if the response is same as expected or not
    result = response.json()
    # print(result)
    if result["message"] == expected:
        print("Test passed {}".format(testNumber))
    else:
        print("Test failed {}".format(testNumber))
        print("Expected: {}".format(expected))
        print("Got: {}".format(result["message"]))

if __name__ == "__main__":
    # This is the data we will send to the API endpoint
    data = {
    "name": "Pranay",
    "email": "mpranay2017@gmail.com",
    "password": "Pranaysunny",
    "confirm_password": "Pranaysunny",
    "category": "None",
    "role": "user"
    }

    # This is the expected response we will get from the API endpoint
    expected = "Password should have atleast one digit"

    # This is the test number
    testNumber = 1

    print("Testing /register/listener API endpoint")

    # This is the function to test the API endpoint
    registerTest(data, expected, testNumber)

    data["password"] = "Pranay"
    expected = "Passwords do not match"
    testNumber = 2
    registerTest(data, expected, testNumber)

    data["password"] = "pranay"
    data["confirm_password"] = "pranay"
    expected = "Password should be atleast 8 characters"
    testNumber = 3
    registerTest(data, expected, testNumber)

    data["password"] = "PRANAYSUNNY"
    data["confirm_password"] = "PRANAYSUNNY"
    expected = "Password should have atleast one lowercase character"
    testNumber = 4
    registerTest(data, expected, testNumber)

    data["password"] = "pranaysunny"
    data["confirm_password"] = "pranaysunny"
    expected = "Password should have atleast one uppercase character"
    testNumber = 5
    registerTest(data, expected, testNumber)

    data["password"] = "PranaySunny1"
    data["confirm_password"] = "PranaySunny1"
    expected = "Password should have atleast one special character"
    testNumber = 6
    registerTest(data, expected, testNumber)