import openai
import requests
import time
from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        
        user_question = request.form['user_question']
        
      
        

        # Set your OpenAI API key here
        api_key = 'myApiKey'
        openai.api_key = api_key
        
        
        # Step 1: send the conversation and available functions to GPT
        messages = [{"role": "user", "content": user_question}]
        functions = [
            {
                "name": "get_gnosis_ethtransfer",
                "description": "Get the amount of ETH transfered for a given address of a user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The address of a user",
                        },
                    },
                    "required": ["address"],
                },
            },
            {
                "name": "get_gnosis_txcount",
                "description": "Get the total amount of transactions by a given address of a user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The address of a user",
                        },
                    },
                    "required": ["address"],
                },
            }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=functions,
            function_call="auto",  # auto is default, but we'll be explicit
        )
        response_message = response["choices"][0]["message"]
        content = response_message.get("content")
        #print(response_message)
        
        # Step 2: check if GPT wanted to call a function
        if response_message.get("function_call"):
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "get_gnosis_ethtransfer": get_gnosis_ethtransfer,
                "get_gnosis_txcount": get_gnosis_txcount,
            }  # only one function in this example, but you can have multiple
            function_name = response_message["function_call"]["name"]
            fuction_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = fuction_to_call(
                address=function_args.get("address"),
            )
            
            # Step 4: send the info on the function call and function response to GPT
            messages.append(response_message)  # extend conversation with assistant's reply
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages,
            )  # get a new response from GPT where it can see the function response
            content = result["choices"][0]["message"]["content"]
            return render_template('index.html', result=content, user_question=user_question)
        else:
            return render_template('index.html', result=content, user_question=user_question)
                
    return render_template('index.html')
    
    
    
def get_gnosis_ethtransfer(address):
    # Set your GnosisScan API key here
    gnosisscan_api_key = 'myApiKey'
    api_url = f"https://api.gnosisscan.io/api?module=account&action=txlistinternal&address={address}&startblock=0&endblock=99999999&page=1&offset=10&sort=asc&apikey={gnosisscan_api_key}"
    response = requests.get(api_url)

    # Check if the API call was successful
    if response.status_code != 200:
        return render_template('index.html', error="Failed to retrieve transaction data.", address=address)

    jsonResponse = response.json()

    # Extract transaction data
    tx_data = jsonResponse.get('result', [])
    
    
    
    ethtransfer_amount = 0
    ethtransfer_amount_eth = 0
    if tx_data:
        for transaction in tx_data:
            amount = str(transaction["value"])
            if amount is not None:
                ethtransfer_amount += int(amount)
                ethtransfer_amount_eth = ethtransfer_amount / 10**18
        
    return str(ethtransfer_amount_eth)

def get_gnosis_txcount(address):
    # Set your GnosisScan API key here
    gnosisscan_api_key = 'YCD4EK9VCSUDHCYSJ8921TUX4VPPZ8ZRSU'
    api_url = f"https://api.gnosisscan.io/api?module=account&action=txlistinternal&address={address}&startblock=0&endblock=99999999&page=1&offset=10&sort=asc&apikey={gnosisscan_api_key}"
    response = requests.get(api_url)

    # Check if the API call was successful
    if response.status_code != 200:
        return render_template('index.html', error="Failed to retrieve transaction data.", address=address)

    jsonResponse = response.json()

    # Extract transaction data
    tx_data = jsonResponse.get('result', [])
        
    tx_count = len(tx_data)
    return str(tx_count)



if __name__ == '__main__':
    app.run()
