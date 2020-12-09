class Hedging(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020,3, 1)
        self.SetEndDate(2020, 4,1)
        self.SetCash(1000000)
        equity = self.AddEquity("SPY", Resolution.Minute)
        option = self.AddOption("SPY", Resolution.Minute)
        self.symbol = option.Symbol
        # set our strike/expiry filter for this option chain
        option.SetFilter(-70,0, timedelta(0), timedelta(30))
        # use the underlying equity as the benchmark
        self.SetBenchmark(equity.Symbol)
       
    def BuyPut(self,optionchain):
        for i in optionchain:
            if i.Key != self.symbol: continue
            chain = i.Value
            # choose the furthest expiration date within 30 days from now on
            expiry = sorted(chain, key = lambda x: x.Expiry)[-1]
            # filter the put options contracts
            put = [x for x in chain if x.Right == 1 and x.Expiry == expiry]
            if put ==[]:
                continue
            OTM = [x for x in put if (x.Strike - put.UnderlyingLastPrice) < 0][0]
            #ATM = contracts = sorted(optionchain, key = lambda x: abs(optionchain.Underlying.Price - x.Strike))[0]
            self.otm_put = sorted(OTM, key = lambda x: x.Strike)
            #if (self.otm_put is None): continue
            self.Buy(self.otm_put.Symbol, 1) # buy the OTM put
            self.log(OTM)
            self.log(self.otm_put)
           
           
    def OnData(self,slice):
        optionchain = slice.OptionChains
        for i in slice.OptionChains:
            if i.Key != self.symbol: continue
            chains = i.Value
            contract_list = [x for x in chains]
            if (slice.OptionChains.Count == 0) or (len(contract_list) == 0): return
            # if you don't hold options and stocks, buy the stocks and trade the options
            if not self.Portfolio.Invested:
                self.Buy("SPY",300)     # buy 100 shares of the underlying stock
                self.BuyPut(optionchain)   # sell OTM call and buy OTM put

# Over the time span of March to April, where there was a major market downturn, we only lost 1.5% compared to the 30% market drop. In a time period of market uptrend, March 17 to April 23, our portfolio exprei
