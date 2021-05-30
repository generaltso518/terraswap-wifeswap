import http.client
import requests
import urllib3.exceptions
from terra_sdk.client.lcd import LCDClient
from terra_sdk.exceptions import LCDResponseError
from terra_sdk.key.mnemonic import MnemonicKey
from terra_sdk.core.auth import StdFee
from terra_sdk.core.bank import MsgSend
from terra_sdk.core.wasm import MsgExecuteContract

from time import sleep
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()
import os
SEED = os.environ.get("SEED")

class TerraSwap:

    def __init__(self, terra, wallet=None) -> None:
        self.terra = terra
        self.wallet = wallet

    def get_exchange_rate(self, amount):
        contract = "terra1jxazgm67et0ce260kvrpfv50acuushpjsz2y0p"
        result = self.terra.wasm.contract_query(
            contract,
            {
                "simulation": {
                    "offer_asset": {
                        "amount": str(amount * 1000000),
                        "info": {
                            "native_token": {
                                "denom": "uluna"
                            }
                        }
                    }
                }
            }
        )
        return result

    def swap(self, amount):
        contract = "terra1jxazgm67et0ce260kvrpfv50acuushpjsz2y0p"

        execute = MsgExecuteContract(
            self.wallet.key.acc_address,
            contract,
            {
                "increase_allowance": {
                    "amount": str(amount * 1000000),
                    "spender": self.wallet.key.acc_address
                }
            },
            {"uluna": amount * 1000000},
        )

        execute_tx = self.wallet.create_and_sign_tx(msgs=[execute])
        result = self.terra.tx.broadcast(execute_tx)
    


    

bot_token = 'xxxxxxxxx'

terra = LCDClient(chain_id="columbus-4", url="https://lcd.terra.dev")
mk = MnemonicKey(mnemonic=SEED)
wallet = terra.wallet(mk)
swap = TerraSwap(terra, wallet)

swap_amount = 10
percent = 5

# terra.tx.search()
while True:
  rate = swap.get_exchange_rate(swap_amount)
  rate['zProfit'] = int(rate['return_amount']) / 1000000 - swap_amount
  rate['zzPR'] = '{:.2%}'.format(rate['zProfit'] / swap_amount)
  rate['zzzAPR'] = '{:.2%}'.format(rate['zProfit'] / swap_amount / 21 * 365)
  rate['zzzzAPY'] = '{:.2%}'.format((1 + (rate['zProfit'] / swap_amount )) ** 17)
  pprint(rate)
  sleep(5)

