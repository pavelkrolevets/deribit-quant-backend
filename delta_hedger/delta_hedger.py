#!/usr/bin/env python

from math import log, sqrt, exp
import time

def hedgeDelta(deribitClient, index, interval_min, interval_max, currency, instrument):
    print("Index values", index)
    # print("Hist vola", hist_vola.iloc[-1])

    ## Get account equity

    try:
        account = deribitClient.account(currency, True)
        print("Account equity", account['equity'], "Currency", currency)
    except Exception:
        print("Error getting account...")
        pass

    # ## check for open positions
    # positions = deribitClient.positions()
    # print("Open positions", positions)

    ## Get global delta
    try:
        globalDelta = deribitClient.account(currency, True)["deltaTotal"]
        print("deltaTotal", globalDelta, "Instrument", currency)

        ## Make delta 0 if its out of range

        while (globalDelta >= interval_max) or (globalDelta <= interval_min):
            ## futures contract
            # fut = currency+"-" + str("27DEC19")

            ## get futures positions
            orderBook = deribitClient.getorderbook(instrument)
            # print(orderBook)

            ## Placing orders
            if globalDelta > 0: # sell futures on bid
                bestBidPrice = orderBook["bids"][0]["price"]
                bestBidAmount = orderBook["bids"][0]["amount"]
                print("Best bid price", bestBidPrice, "Best bid amount", bestBidAmount)
                if bestBidAmount > sqrt(globalDelta**2)*index:
                    ## place the order
                    try:
                        trade = deribitClient.sell(instrument, sqrt(globalDelta**2)*index/10, bestBidPrice, type="limit", time_in_force= "fill_or_kill", postOnly=None, label=None)
                        print(trade)
                    except Exception:
                        print("Error placing the trade.")
                else:
                    ## place the order
                    trade = deribitClient.sell(instrument, bestBidAmount / 10, bestBidPrice, type="limit",
                                               time_in_force="fill_or_kill", postOnly=None, label=None)
                    print(trade)

            if globalDelta < 0: # buy futures on ask
                bestAskPrice = orderBook["asks"][0]["price"]
                bestAskAmount = orderBook["asks"][0]["amount"]
                print("Best ask price", bestAskPrice, "Best ask amount", bestAskAmount)
                if bestAskAmount > sqrt(globalDelta**2)*index:
                    ## place the order
                    trade = deribitClient.buy(instrument, sqrt(globalDelta**2)*index/10, bestAskPrice, type="limit", time_in_force= "fill_or_kill", postOnly=None, label=None)
                    print(trade)
                else:
                    ## place the order
                    trade = deribitClient.buy(instrument, bestAskAmount/10, bestAskPrice, type="limit",
                                              time_in_force="fill_or_kill", postOnly=None, label=None)
                    print(trade)

            globalDelta = deribitClient.account(currency, True)["deltaTotal"]
            print("deltaTotal", globalDelta, "Currency", currency)
            time.sleep(5)

    except Exception:
        print("Error connecting to API.")
        pass
