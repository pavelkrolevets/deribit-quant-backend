#!/usr/bin/env python

from math import log, sqrt, exp
import time

def hedgeDelta(deribitClient, index, delta, currency, instrument):
    print("Index values", index)
    # print("Hist vola", hist_vola.iloc[-1])

    ## Get global delta
    try:
        globalDelta = deribitClient.account(currency, True)["deltaTotal"]

        while (round(globalDelta,2) != round(delta,2)):
            ## get futures positions
            orderBook = deribitClient.getorderbook(instrument)

            ## Placing orders
            if globalDelta > delta: # sel futures at bid
                bestBidPrice = orderBook["bids"][0]["price"]
                bestBidAmount = orderBook["bids"][0]["amount"]
                print("Best bid price", bestBidPrice, "Best bid amount", bestBidAmount)
                delta_diff = globalDelta - delta
                print("Sell amount ",delta_diff,delta_diff*index)
                trade = deribitClient.sell(instrument, round(delta_diff*index/10, 0), bestBidPrice, type="limit", time_in_force= "immediate_or_cancel", postOnly=None, label=None)
                print(trade)
               
            if globalDelta < delta: # buy futures on ask
                bestAskPrice = orderBook["asks"][0]["price"]
                bestAskAmount = orderBook["asks"][0]["amount"]
                print("Best ask price", bestAskPrice, "Best ask amount", bestAskAmount)
                delta_diff = delta - globalDelta
                print("Buy amount ", delta_diff, delta_diff ,delta_diff*index)
                trade = deribitClient.buy(instrument, round(delta_diff*index/10, 0), bestAskPrice, type="limit", time_in_force= "immediate_or_cancel", postOnly=None, label=None)
                print(trade)
              
            globalDelta = deribitClient.account(currency, True)["deltaTotal"]
            print("deltaTotal", globalDelta, "Instrument", instrument, "Target Delta", delta)
            time.sleep(1)

    except Exception:
        print("Error starting hedger.")
        traceback.print_exc(file=sys.stdout)
        sys.exit(0)
