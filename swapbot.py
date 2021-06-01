import http.client
import requests
import urllib3.exceptions
from terra_sdk.client.lcd import LCDClient
from terra_sdk.exceptions import LCDResponseError
from terra_sdk.key.mnemonic import MnemonicKey
from terra_sdk.core.auth import StdFee
from terra_sdk.core.bank import MsgSend
from terra_sdk.core.wasm import MsgExecuteContract
from terra_sdk.core.coins import Coins

from time import sleep
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()
import os
SEED = os.environ.get("SEED")

class TerraSwap:
    terraSwapContract = "terra1jxazgm67et0ce260kvrpfv50acuushpjsz2y0p"
    bLunaContract = 'terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp'

    def __init__(self, terra, wallet=None) -> None:
        self.terra = terra
        self.wallet = wallet

    def get_exchange_rate(self, amount):
        result = self.terra.wasm.contract_query(
            self.terraSwapContract,
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

    def swap(self, amount, return_amount):
        

        increase_allowance = MsgExecuteContract(
            self.wallet.key.acc_address,
            self.bLunaContract,
            {
                "increase_allowance": {
                    "amount": str(return_amount),
                    "spender": self.terraSwapContract
                }
            }
        )

        swap_bluna = MsgExecuteContract(
            self.wallet.key.acc_address,
            self.terraSwapContract,
            {
                "swap": {
                    "offer_asset": {
                        "amount": str(amount * 1000000),
                        "info": {
                            "native_token": {
                                "denom": "uluna"
                            }
                        }
                    }
                }
            },
            {"uluna": amount * 1000000},
        )

        tx = self.wallet.create_and_sign_tx(msgs=[increase_allowance, swap_bluna], gas_prices="0.15uusd", gas_adjustment=1.5)
        # fee = self.terra.tx.estimate_fee(tx)
        result = self.terra.tx.broadcast(tx)
        return [tx, result]
        # return result
    


    

bot_token = 'xxxxxxxxx'

terra = LCDClient(chain_id="columbus-4", url="https://lcd.terra.dev")
mk = MnemonicKey(mnemonic=SEED)
wallet = terra.wallet(mk)
swap = TerraSwap(terra, wallet)

swap_amount = 1
percent = 5

# terra.tx.search()
while True:
    rate = swap.get_exchange_rate(swap_amount)
    rate['zProfit'] = int(rate['return_amount']) / 1000000 - swap_amount
    rate['zzPR'] = '{:.2%}'.format(rate['zProfit'] / swap_amount)
    rate['zzzAPR'] = '{:.2%}'.format(rate['zProfit'] / swap_amount / 21 * 365)
    rate['zzzzAPY'] = '{:.2%}'.format((1 + rate['zProfit'] / swap_amount) ** 17 - 1)
    pprint(rate)

    swap_result = swap.swap(swap_amount, rate['return_amount'])
    pprint(swap_result)


    break
    sleep(5)

