# Simple bot 2

    def Initialize(self):

        # Timeframes for our backtesting and set starting cash balance
        self.SetStartDate(2023, 1, 1)
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100000)


        # We are buying QQQ, which tracks the performance of the NASDAQ 100 
        self.qqq = self.AddEquity("QQQ", Resolution.Hour).Symbol
        
        # 
        self.entryTicket = None
        self.stopMarketTicket = None
        
        # Buy and sell time, to make sure we wait the full month before trading again
        self.entryTime = datetime.min
        self.stopMarketOrderFillTime = datetime.min

        # The highest price QQQ attained in our posession
        self.highestPrice = 0




    def OnData(self, data):
        
        # wait 30 days after last exit
        if (self.Time - self.stopMarketOrderFillTime).days < 30:
            return
        
        # Get the current price of QQQ
        price = self.Securities[self.qqq].Price
        
        
        # send entry limit order
        # If there are no current investments, and there are no open orders for QQQ
        if not self.Portfolio.Invested and not self.Transactions.GetOpenOrders(self.qqq):
           
            # We want 90% of our buying power to go towards QQQ
            quantity = self.CalculateOrderQuantity(self.qqq, 0.9)
            
            # Limit orders allow you to specify a price you want your order to be filled at. They are not guarenteed, becuase you are the one specifying the price, but if it works, you get a better deal than regular market orders
            # We're still going to keep it simple, so buy QQQ, 90% of our capital at the current market price, 
            self.entryTicket = self.LimitOrder(self.qqq, quantity, price, "Entry Order")
            self.Log("purchased at = " + str(price))
            
            # Update the time of purcahse
            self.entryTime = self.Time
        

        # move limit price if not filled after 1 day
        # If 1 day has passed and the order has not been filled
        if (self.Time - self.entryTime).days > 1 and self.entryTicket.Status != OrderStatus.Filled:
            
            # Update our clock to the current time
            self.entryTime = self.Time

            # To update our entry ticket
            updateFields = UpdateOrderFields()
            
            # Update limit price to current price
            updateFields.LimitPrice = price
            
            # Update the fields in the entry ticket object
            self.entryTicket.Update(updateFields)
        

        # If we are currently invested
        if self.stopMarketTicket is not None and self.Portfolio.Invested:
            
            # If the current price is more than the highest attained price
            if price > self.highestPrice:
                
                # Update the highest recorded price to reflect that
                self.highestPrice = price
                
                # To update our exit ticker
                updateFields = UpdateOrderFields()
                
                # Set our stop loss to 5% less than the highest attained price
                updateFields.StopPrice = price * 0.95
                self.Log("Expected sell Price = " + str(updateFields.StopPrice))
                
                # Update the fields in our exit ticket object
                self.stopMarketTicket.Update(updateFields)


    # When an order event occurs (e.g., order filled, cancelled, etc.)
    def OnOrderEvent(self, orderEvent):
        
         # If the order has not been filled, ignore and return
        if orderEvent.Status != OrderStatus.Filled:
            return
        

        # Check if the order event corresponds to the entry ticket 
        if self.entryTicket is not None and self.entryTicket.OrderId == orderEvent.OrderId:
            
            # Create a stop market order for the same quantity as the entry, with a stop price set to 5% below the highest price)
            self.stopMarketTicket = self.StopMarketOrder(self.qqq, -self.entryTicket.Quantity, 0.95 * self.highestPrice)
            self.Log("Expected sell Price = " + str(self.stopMarketTicket))
            

        # Check if the order event corresponds to the stop market ticket 
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId:
            
            # Record the time when the stop market order is filled
            self.stopMarketOrderFillTime = self.Time
            
            # Reset the highest price to zero since the position has been closed
            self.highestPrice = 0