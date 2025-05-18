import ccxt
import pandas as pd
import requests
import time
from datetime import datetime

# Connexion à l'API Kucoin
kucoin = ccxt.kucoin({
    "apiKey": "682169bc4985e300012f732c",
    "secret": "9df93c57-3e14-4bb9-b2b7-a8447406876e",
    "password": "Klakite23699k?"
})

# Fonction pour obtenir le prix actuel
def getCurrentPrice(perpSymbol):
    try:
        ticker = kucoin.fetchTicker(perpSymbol)
        return float(ticker["ask"])
    except BaseException as err:
        print("An error occurred", err)
        return None

# Fonction pour obtenir le solde USDT
def getSolde():
    try:
        for coin in kucoin.fetchBalance()['info']['data']:
            if coin['currency'] == 'USDT':
                return float(coin['balance'])
    except Exception as err:
        raise err

# Test de connexion
try:
    test = getSolde()
    del test
except Exception as err:
    print(f"Problème de connexion à l'API : {err}")
    exit()

print(f"{str(datetime.now()).split('.')[0]} | Connexion à l'API Kucoin réussie.")
kucoin.load_markets()

nbDePairesExecutionsPrecedentes = 0
print(f"{str(datetime.now()).split('.')[0]} | Bot de sniping lancé avec {getSolde()} USDT, en attente de nouvelles paires...")

while True:
    try:
        liste_pairs = requests.get('https://openapi-v2.kucoin.com/api/v1/symbols').json()
        dataResponse = liste_pairs['data']
        df = pd.DataFrame(dataResponse, columns=['symbol', 'enableTrading'])
        df = df[df.symbol.str.contains("-USDT")]

        perpListBase = [row['symbol'] for index, row in df.iterrows()]

        if len(perpListBase) > nbDePairesExecutionsPrecedentes and nbDePairesExecutionsPrecedentes != 0:
            print(f"{str(datetime.now()).split('.')[0]} | Nouvelle paire disponible !!!")
            kucoin.load_markets()
            symbol = ''
            for pair in perpListBase:
                if pair not in perpListEx:
                    symbol = pair
            if symbol != '':
                print(f"{str(datetime.now()).split('.')[0]} | Tentative de snipping sur {symbol} avec 50 USDT")
                amount = 50 / getCurrentPrice(symbol)
                formatted_amount = kucoin.amount_to_precision(symbol, amount)

                try:
                    kucoin.reload_markets()
                    kucoin.createOrder(symbol, 'market', 'buy', formatted_amount)
                    print(f"{str(datetime.now()).split('.')[0]} | ✅ Buy Order success!")

                    time.sleep(2)  # Optional delay after buy

                    buy_price = getCurrentPrice(symbol)
                    print(f"{str(datetime.now()).split('.')[0]} | Buy at {buy_price:.6f}, monitoring price for profit/loss...")

                    while True:
                        current_price = getCurrentPrice(symbol)
                        profit_ratio = current_price / buy_price

                        if profit_ratio >= 1.10:
                            print(f"{str(datetime.now()).split('.')[0]} | 📈 Profit target hit! Selling at {current_price:.6f}")
                            kucoin.createOrder(symbol, 'market', 'sell', formatted_amount)
                            print(f"{str(datetime.now()).split('.')[0]} | ✅ Sold with profit.")
                            print(f"{str(datetime.now()).split('.')[0]} | Balance: {getSolde()} USDT")
                            break
                        elif profit_ratio <= 0.90:
                            print(f"{str(datetime.now()).split('.')[0]} | ⚠️ Stop-loss triggered. Selling at {current_price:.6f}")
                            kucoin.createOrder(symbol, 'market', 'sell', formatted_amount)
                            print(f"{str(datetime.now()).split('.')[0]} | ❌ Sold with loss.")
                            print(f"{str(datetime.now()).split('.')[0]} | Balance: {getSolde()} USDT")
                            break
                        else:
                            print(f"{str(datetime.now()).split('.')[0]} | Monitoring... Current: {current_price:.6f} | Target: {buy_price * 1.10:.6f} | Stop: {buy_price * 0.90:.6f}")
                            time.sleep(1)

                    print(f"{str(datetime.now()).split('.')[0]} | Sniping réalisé sur {symbol}")

                except Exception as err:
                    print(f"❌ Error during snipe: {err}")
            else:
                print(f"{str(datetime.now()).split('.')[0]} | Aucune paire n'est différente entre cette execution et l'execution précédente")

            nbDePairesExecutionsPrecedentes = len(perpListBase)
            perpListEx = perpListBase
        else:
            nbDePairesExecutionsPrecedentes = len(perpListBase)
            perpListEx = perpListBase

    except Exception as err:
        print(err)
        time.sleep(20)
        pass