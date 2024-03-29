from web3 import Web3
from web3.exceptions import TransactionNotFound, ABIFunctionNotFound
import json
import requests
import os
import re

infura_key = os.environ.get('INFURA_KEY') 
etherscan_key = os.environ.get('ETHERSCAN_KEY') 

web3 = Web3(Web3.WebsocketProvider(f'wss://mainnet.infura.io/ws/v3/{infura_key}'))

address_list = [
   web3.toChecksumAddress('0xb8551f8577e93172d1f95cbb967c1042147b3a4d'),
   web3.toChecksumAddress('0xe7ee96303a82d383b678bc6ee8bc5d19c4abe852'),
   web3.toChecksumAddress('0x18c57894c5ccbb86a175c3576e4696df9c0a2d63'),
   web3.toChecksumAddress('0x4b3cd022df95c4fc7a2427ab5efaeba87dcdf436'),
   web3.toChecksumAddress('0xfbedefe3bf9640dfdd4fbc38085c9cca2df09ec2'),
   web3.toChecksumAddress('0x7a250d5630b4cf539739df2c5dacb4c659f2488d'),
   web3.toChecksumAddress('0x8ff5ceb90fab0e98fdfb3b9eacdf162dffaafeb4'),
   web3.toChecksumAddress('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'),
   web3.toChecksumAddress('0x30f66bebd0bce108101cc03238ae143e84b6eba3'),
   web3.toChecksumAddress('0xe6a733e58b6f69ea7dd4361a5630a5e172391e51'),
   web3.toChecksumAddress('0x2e90eab144506e3662f2ee222e1d311516513b80'),
   web3.toChecksumAddress('0xf6e6c3a86166d0db2dd03417d041792e3463cbc0'),
   web3.toChecksumAddress('0xb3395ca596ef326e31fc98fd23f1c6c431b96874'),
   web3.toChecksumAddress('0x592d7a278234308f146b9425ddc3adeaae34e2d6'),
   web3.toChecksumAddress('0x8187bc8bb50499952d22a290074171aee2c5057c'),
   web3.toChecksumAddress('0xB35AC81B0AAA58E05C024CF8F8CE3DEC7C44213A'),
   web3.toChecksumAddress('0x9B80DF270E17C30C343DAC70E7347ADF02C9447D'),
   web3.toChecksumAddress('0x19013B9BEC01C02B5F51A1AE1162F77057A7A6FF'),
   web3.toChecksumAddress('0xC5A1B96BEE388BD77FC1CA9D92CF61BEA9F4FF2D'),
   web3.toChecksumAddress('0xEAFEB70900374A2FF7F67DB1C85B9914541223FD'),
   web3.toChecksumAddress('0x135997B08B8503C5B6B4660017DEC5460B3AB3EF'),
   web3.toChecksumAddress('0x4D91838268F6D6D4E590E8FD2A001CD91C32E7A4'),
   web3.toChecksumAddress('0xD3C47E1B483D1446AFD412D810414818BAAE7169'),
   web3.toChecksumAddress('0x04670D5B71DDB30F84675DC1D6AE165A0A3A0481'),
   web3.toChecksumAddress('0x2C8536221C6C27F051F70531A1C5F33F8FA3CC5C'),
   web3.toChecksumAddress('0xAF7132486663A9902EE352EBF94171886AC2C3C8'),
   web3.toChecksumAddress('0x16B8C239F1AABF0DCBAA5618F0BCA0334732BF10'),
   web3.toChecksumAddress('0xF3A2B7D7F24C32A893011CC849E96B7BBBB7D607'),
   web3.toChecksumAddress('0xF9E9783EC1DE26D2ECAB797E367E8A768BF801A7'),
   web3.toChecksumAddress('0x35C7BCFE1E7FE513F39E72E9E0B12855D901E263')
   ]

def get_price(contract_address):

    gecko_url = f'https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={contract_address}&vs_currencies=usd'
    try:
        gecko_result = json.loads(requests.get(gecko_url).text)
    except:
        import ipdb; ipdb.set_trace()
    if gecko_result:
        token_price = json.loads(requests.get(gecko_url).text).get(contract_address.lower())['usd']
    else:
        token_price = 0
    return token_price

def get_abi(contract_address):

    url = f'https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={etherscan_key}'
    result = json.loads(requests.get(url).text)['result']

    if '"name":"name"' in result:
        contract = web3.eth.contract(address=web3.toChecksumAddress(contract_address), abi=result)
        token_name = contract.functions.name().call()
        token_symbol = contract.functions.symbol().call()
        token_decimals = contract.functions.decimals().call()
        token_price = get_price(contract_address)

        return (contract, token_name, token_symbol, token_decimals, token_price)

    if '"inputs"' in result or 'not verified' in result: 
        url = f'https://etherscan.io/token/{contract_address}'
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        }

        request = requests.get(url, headers=headers)

        pattern = re.compile('(?<="Description" content=")([^\(]*)\(([^\)]*)')
        decimal_pattern = re.compile("(?<=\\'decimals\\': \\')\d+")
        token_name, token_symbol = pattern.findall(request.text)[0][0], pattern.findall(request.text)[0][1]
        token_decimals = decimal_pattern.findall(request.text)[0][0]
        token_price = get_price(contract_address)

        return (token_name, token_symbol, token_decimals, token_price)

def transfer(hex_data, method=''):
    to_contract_address = web3.eth.getTransaction(tx).to
    token_info = get_abi(to_contract_address)
    to_address,value = hex_data[0], int(hex_data[1], 16) / int('1' + '0'*int(token_info[-2]))   

    print(f"Pending transfer from sending address: https://etherscan.io/address/{from_address}")
    print(f"Receiving address: https://etherscan.io/address/{to_address}")
    print(f"tx: https://etherscan.io/tx/{tx}")
    print(f"Token transferred: {token_info[-4]}")
    print(f"Amount transferred: {value} {token_info[-3]}\n")

    # return {
    #     'to_contract_address': to_contract_address,
    #     'token_name': token_info[-3],
    #     'token_symbol': token_info[-2],
    #     'value': value
    # }

def uniswap_transaction(hex_data, method_id):

    mapping = {'2': -2, '3': -3, '4': -4, '5': -5, '6': -6, }

    amount_mapping = [
        {"0x38ed1739": {'from_address': hex_data[3], 'in': int(hex_data[0], 16), 'out': int(hex_data[1], 16)}},
        {"0x8803dbee": {'from_address': hex_data[3], 'in': int(hex_data[1], 16), 'out': int(hex_data[0], 16)}},
        {"0x7ff36ab5": {'from_address': hex_data[2], 'in': web3.eth.getTransaction(tx).value, 'out': int(hex_data[0], 16)}},
        {"0x4a25d94a": {'from_address': hex_data[3], 'in': int(hex_data[1], 16), 'out': int(hex_data[0], 16)}},
        {"0x18cbafe5": {'from_address': hex_data[3], 'in': int(hex_data[0], 16), 'out': int(hex_data[1], 16)}},
        {"0xfb3bdb41": {'from_address': hex_data[3], 'in': web3.eth.getTransaction(tx).value, 'out': int(hex_data[0], 16)}},
        {"0x5c11d795": {'from_address': hex_data[3], 'in': int(hex_data[0], 16), 'out': int(hex_data[1], 16)}},
        {"0xb6f9de95": {'from_address': hex_data[3], 'in': web3.eth.getTransaction(tx).value, 'out': int(hex_data[0], 16)}},
        {"0x791ac947": {'from_address': hex_data[3], 'in': int(hex_data[0], 16), 'out': int(hex_data[1], 16)}}
    ]
    
    for number in mapping:
        for element in hex_data:
            if number == element:
                while not len(hex_data[-1]) == 40:
                    hex_data[-1] = '0' + hex_data[-1]
                to_contract_address  = '0x' + hex_data[-1]
                token_bought = get_abi(to_contract_address)

                while not len(hex_data[-int(number)]) == 40:
                    hex_data[-int(number)] = '0' + hex_data[-int(number)]    
                token_sold = get_abi('0x' + hex_data[-int(number)])

                for element in amount_mapping:
                    if method_id in element:
                        try:
                            amount_bought = element[method_id]['out'] / int('1' + '0'*int(token_bought[-2]))
                            amount_sold = element[method_id]['in'] / int('1' + '0'*int(token_sold[-2]))
                        except TypeError:
                            import ipdb; ipdb.set_trace()
                        print(f"Pending transaction from address: https://etherscan.io/address/{element[method_id]['from_address']}")
                        print(f"tx: https://etherscan.io/tx/{tx}")
                        print(f"Token sold: {token_sold[-3]} - ${round(token_sold[-1], 2)}")
                        print(f"Amount sold: {amount_sold} {token_sold[-3]} (${round(token_sold[-1] * amount_sold, 2)})")
                        print(f"Token bought: {token_bought[-4]} - ${round(token_bought[-1], 2)}")
                        print(f"Amount received (estimated): {amount_bought} {token_bought[-3]} (${round(token_bought[-1] * amount_bought, 2)})\n")

def decode_data_input(input_data):
    
    method_id = input_data[:10]

    methods = [
        #  {"0xa9059cbb": 'transfer', 'function': transfer},
        #  {"0x1a695230": 'transfer(address addr)', 'function': transfer}
         {"0x38ed1739": 'swapExactTokensForTokens', 'function': uniswap_transaction},
         {"0x8803dbee": 'swapTokensForExactTokens', 'function': uniswap_transaction},
         {"0x7ff36ab5": 'swapExactETHForTokens', 'function': uniswap_transaction},
         {"0x4a25d94a": 'swapTokensForExactETH', 'function': uniswap_transaction},
         {"0x18cbafe5": 'swapExactTokensForETH', 'function': uniswap_transaction},
         {"0xfb3bdb41": 'swapETHForExactTokens', 'function': uniswap_transaction},
         {"0x5c11d795": 'swapExactTokensForTokensSupportingFeeOnTransferTokens', 'function': uniswap_transaction},
         {"0xb6f9de95": 'swapExactETHForTokensSupportingFeeOnTransferTokens', 'function': uniswap_transaction},
         {"0x791ac947": 'swapExactTokensForETHSupportingFeeOnTransferTokens', 'function': uniswap_transaction}
        #  {"0x095ea7b3": 'approve', 'function': uniswap_transaction}
        ]
	
    for method in methods:
        if method_id in method:
            data = '0' * 10 + input_data
            data = [ data[i:i+64] for i in range(20, len(data), 64) ]
            hex_data = []
            for i in data:
                while i[0] == "0" and len(i) > 1:
                    i = i[1:]
                hex_data.append(i)
            method['function'](hex_data, method_id)

while True:
    try:
        tx_list = [tx.hex() for tx in web3.eth.getBlock('pending')['transactions']]
        for tx in tx_list:
            from_address = web3.eth.getTransaction(tx)['from']
            if from_address not in address_list:
                data_input = decode_data_input(web3.eth.getTransaction(tx).input)

    except TransactionNotFound:
        print("transaction not found\n")
        continue
    except KeyError:
        print("key error\n")
        continue
