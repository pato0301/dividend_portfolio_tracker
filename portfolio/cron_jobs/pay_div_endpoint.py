import requests

def main():
    # Define the endpoint URL
    url = 'https://dividend-portfolio-tracker.vercel.app/pay_div'

    # Send a POST request to the endpoint
    response = requests.get(url)

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