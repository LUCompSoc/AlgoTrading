# Simple Bot

    def Initialize(self):
        self.SetStartDate(2023, 1, 1)  # Set Start Date
        self.SetEndDate(2024, 1, 1) # Set End Date
        self.SetCash(100000)  # Set Strategy Cash (THIS AMOUNT OF CASH IS NOT REAL!!!)
        
        # Add asset to use
        spy = self.AddEquity("SPY", Resolution.Daily)
        
        # We want the data raw
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
        # This is to make sure we get the right symbol
        self.spy = spy.Symbol
        
        # Setting the benchmark we want to compare our results to
        self.SetBenchmark("SPY")

        # This considers fees if we were to do this through another brokerage
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Cash)
        
        self.entryPrice = 0 # This will track the entry price of our position
        self.period = timedelta(31)
        self.nextEntryTime = self.Time # Set to "current time" so we can start trading straight away


    def OnData(self, data):
        # If there is no, or insufficient data, quit
        if not self.spy in data:
            return
        
        # Get the current price of SPY
        price = self.Securities[self.spy].Close
        
        # If SPY is not currently in our portfolio
        if not self.Portfolio.Invested:

            # Unless we are currently in our time out cash period
            if self.nextEntryTime <= self.Time:
                # We want 100% of our portfolio to be in SPY
                self.SetHoldings(self.spy, 1)

                # This does the same thing
                # self.MarketOrder(self.spy, int(self.Portfolio.Cash / price) )
                
                # Let me know you bought it and set the entry price to the current price
                self.Log("BUY SPY @" + str(price))
                self.entryPrice = price
        
        # If SPY is currently in our portfolio
        # If SPY price we paid has changed 10% up or down
        elif self.entryPrice * 1.1 < price or self.entryPrice * 0.90 > price:
            # Sell it all, let me know, then set the nextEntryTime to 1 month from now. We will be in cash for this period.
            self.Liquidate()
            self.Log("SELL SPY @" + str(price))
            self.nextEntryTime = self.Time + self.period