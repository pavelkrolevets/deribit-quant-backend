#!/usr/bin/env python

from math import log, sqrt, exp
import time

def hedgeDelta(deribitClient, index, delta, currency, instrument):
    print("Index values", index)
    # print("Hist vola", hist_vola.iloc[-1])

    ## Get account equity

    try:
        account = deribitClient.account(currency, True)
        print("Account equity", account['equity'], "Currency", currency)
    except Exception:
        print("Error getting account...")

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
                delta_diff = (globalDelta - delta)/globalDelta
                print("Sell amount ",delta_diff,delta_diff*index)
                trade = deribitClient.sell(instrument, delta_diff*index, bestBidPrice, type="limit", time_in_force= "immediate_or_cancel", postOnly=None, label=None)
                print(trade)
                # if bestBidAmount >= delta_diff*index:
                #     ## place the order
                #     try:
                #         print("Sell amount ",delta_diff*index)
                #         trade = deribitClient.sell(instrument, delta_diff*index, bestBidPrice, type="limit", time_in_force= "fill_or_kill", postOnly=None, label=None)
                #         print(trade)
                #     except:
                #         print("Error placing the trade.")
                # elif bestBidAmount < delta_diff*index:
                #     ## place the order
                #     try:
                #         trade = deribitClient.sell(instrument, bestBidAmount, bestBidPrice, type="limit",
                #                                 time_in_force="fill_or_kill", postOnly=None, label=None)
                #         print("Sell amount ", bestBidAmount)
                #         print(trade)
                #     except:
                #         print("Error placing the trade.")
            if globalDelta < delta: # buy futures on ask
                bestAskPrice = orderBook["asks"][0]["price"]
                bestAskAmount = orderBook["asks"][0]["amount"]
                print("Best ask price", bestAskPrice, "Best ask amount", bestAskAmount)
                delta_diff = (delta - globalDelta)/delta
                print("Buy amount ", delta_diff, delta_diff ,delta_diff*index)
                trade = deribitClient.buy(instrument, delta_diff*index, bestAskPrice, type="limit", time_in_force= "immediate_or_cancel", postOnly=None, label=None)
                print(trade)
                # if bestAskAmount >= delta_diff*index:
                #      ## place the order
                #     try:
                #         print("Buy amount ", delta_diff ,delta_diff*index)
                #         trade = deribitClient.buy(instrument, delta_diff*index, bestAskPrice, type="limit", time_in_force= "fill_or_kill", postOnly=None, label=None)
                #         print(trade)
                #     except:
                #         print("Error placing the trade.")
                # elif bestAskAmount < delta_diff*index:
                #     ## place the order
                #     try:
                #         trade = deribitClient.buy(instrument, bestAskAmount, bestAskPrice, type="limit",
                #                                 time_in_force="fill_or_kill", postOnly=None, label=None)
                #         print("Buy amount ", bestAskAmount)
                #         print(trade)
                #     except:
                #         print("Error placing the trade.")
            globalDelta = deribitClient.account(currency, True)["deltaTotal"]
            print("deltaTotal", globalDelta, "Instrument", instrument, "Target Delta", delta)
            time.sleep(0.1)

    except Exception:
        print("Error placing orders.")
