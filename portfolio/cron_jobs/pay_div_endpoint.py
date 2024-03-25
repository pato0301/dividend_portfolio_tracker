import requests
import os

def main():
    # Define the endpoint URL
    try:
        URL = os.environ["ENPOINT_DIV"]
    except KeyError:
        URL = "URL not available!"

    # Send a POST request to the endpoint
    response = requests.get(URL)

    # Check if the response status code is 200 (OK)
    if response.status_code == 200:
        # Check if the response message is 'Dividend payments processing started successfully'
        if response.json().get('message') == 'Dividend payments processing started successfully':
            print('Successfully finished')
        else:
            print('Failed: Unexpected response message')
    else:
        print(f'Failed: HTTP Error {response.status_code}')

if __name__ == '__main__':
    main()