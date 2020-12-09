class Hedging(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 3, 23)  # Set Start Date 23
        self.SetEndDate(2020, 4, 17) #17
        self.SetCash(1000000)  # Set Strategy Cash
        spy = self.AddEquity("SPY", Resolution.Minute)
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
        self.spy = spy.Symbol
        self.contract = None
        self.spy_per = 0.99
        self.spy_option_per = 1 - self.spy_per

    def OnData(self, data):
       
        if not self.Portfolio[self.spy].Invested:
            self.SetHoldings(self.spy, self.spy_per)
           
        # DO HEDGE
        if self.contract is None:
            self.contract = self.GetContract()
            return
       
        if (self.contract.ID.Date - self.Time).days < 30 :#was 30
            self.Liquidate(self.contract)
            self.RemoveSecurity(self.contract)
            self.contract = None
            return
       
        if not self.Portfolio[self.contract].Invested:
            self.SetHoldings(self.contract, self.spy_option_per)
       
    def GetContract(self):
       
        targetStrike = (self.Securities[self.spy].Price * 0.6)
        contracts = self.OptionChainProvider.GetOptionContractList(self.spy, self.Time)
        puts = [x for x in contracts if x.ID.OptionRight == OptionRight.Put]
        puts = sorted( sorted(puts, key = lambda x: x.ID.Date, reverse = True),
                       key = lambda x: x.ID.StrikePrice)
        puts = [x for x in puts if (abs(x.ID.StrikePrice - targetStrike)/targetStrike)<0.01]#check if this strike exists (make it a range)
        #puts = [x for x in puts if x.ID.StrikePrice == targetStrike]#check if this strike exists (make it a range)
        puts = [x for x in puts if 30 < (x.ID.Date - self.Time).days <= 60] #-> keep it between 30 and 60 maybe
        #make sure the put is always in the portfolio
        if len(puts) == 0:
            return None
        self.AddOptionContract(puts[0], Resolution.Minute)
        return puts[0]
# During the period of March 23rd to April 17th, while the market was up about 28%, our portfolio made 25% profit
# During the period of March 1st to April 1st, while the market lost a substantial percentage, our portfolio made about 5% profit.
