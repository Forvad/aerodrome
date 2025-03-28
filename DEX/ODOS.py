import time

import requests
import json

from web3 import Web3

from Log.Loging import log
from Utils.EVMutils import EVM
from config import private_key


def swap(input_tokens, output_tokens, amount):
    try:
        web3 = EVM.web3('base')
        wallet = web3.eth.account.from_key(private_key).address
        url = 'https://api.odos.xyz/sor/quote/v2'

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        data = {
            "chainId": 8453,
            "compact": True,
            "gasPrice": 200000,
            "inputTokens":
                [
                    {
                        "amount": str(amount),
                        "tokenAddress": input_tokens
                    }],
            "outputTokens":
                [
                    {
                        "proportion": 1,
                        "tokenAddress": output_tokens
                    }
                ],
            "referralCode": 0,
            "slippageLimitPercent": 1,
            "sourceBlacklist":  [],
            "sourceWhitelist": [],
            "userAddr": wallet
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        log().info(response.json())

        pathId = response.json()['pathId']
        json_data = {
            "pathId": pathId,
            "simulate": False,
            "userAddr": wallet
        }
        response_1 = requests.post('https://api.odos.xyz/sor/assemble', headers=headers, json=json_data)
        data_tx = response_1.json()['transaction']
        EVM.approve(amount, private_key, 'base', input_tokens, data_tx['to'])
        tx = {
            'data': data_tx['data'],
            'from': Web3.to_checksum_address(data_tx['from']),
            'to': Web3.to_checksum_address(data_tx['to']),
            'chainId': web3.eth.chain_id,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(Web3.to_checksum_address(data_tx['from'])),
            # 'gas': 0
        }
        module_str = f'Swap Token'
        tx_bool = EVM.sending_tx(web3, tx, 'base', private_key, 1, module_str)
        if not tx_bool:
            log().error('The transaction failed')
            time.sleep(15)
            return swap(input_tokens, output_tokens, amount)
        else:
            return True
    except BaseException as error:
        log().error(error)
        time.sleep(10)
        return swap(input_tokens, output_tokens, amount)


