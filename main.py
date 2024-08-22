# region imports
from AlgorithmImports import *
from LinRegIndicators import SlopeIndicator
# endregion

class RSIBacktesting(QCAlgorithm):

    def initialize(self):
        self.parameters = self.get_parameters()
        self.rsi_ticker = self.parameters["rsi_ticker"]  # Use self.parameters instead of os.getenv
        self.rsi_period = int(self.parameters["rsi_period"])  # Use self.parameters
        self.rsi_threshold = float(self.parameters["rsi_threshold"])  # Use self.parameters
        self.trading_ticker = self.parameters["trading_ticker"]  # Use self.parameters
        
        self.lin_reg_period = int(self.parameters["lin_reg_period"])  # Use self.parameters
        self.slope_period = int(self.parameters["slope_period"])  # Use self.parameters
        self.long_thresh = float(self.parameters["long_thresh"])  # Use self.parameters
        self.short_thresh = float(self.parameters["short_thresh"])  # Use self.parameters

        self.set_start_date(2013, 10, 7)
        self.set_end_date(2023, 10, 11)
        self.set_cash(100000)

        self.rsi_symbol = self.add_equity(self.rsi_ticker, Resolution.DAILY).symbol
        self.trading_symbol = self.add_equity(self.trading_ticker, Resolution.DAILY).symbol
        self.rsi_ind: RelativeStrengthIndex = self.rsi(self.rsi_ticker, self.rsi_period, MovingAverageType.SIMPLE, Resolution.DAILY)
        self.atr_ind: AverageTrueRange = self.atr(self.trading_ticker, 14, MovingAverageType.SIMPLE, Resolution.DAILY)
        
        self.boolean_exit_system: SlopeIndicator = SlopeIndicator(self.lin_reg_period, self.slope_period, self.long_thresh, self.short_thresh)
        self.use_advanced_exit = True
        self.turned_green_yet = False
        self.register_indicator(self.rsi_symbol, self.boolean_exit_system, Resolution.DAILY)
        self.warm_up_indicator(self.rsi_symbol, self.boolean_exit_system, Resolution.DAILY)

        self.crash = False
        self.set_warm_up(self.rsi_period)
        self.stop_order = None

    def on_data(self, slice: Slice):
        if self.is_warming_up:
            return

        rsi_value = self.rsi_ind.current.value
        
        if not self.portfolio.invested: # make a trade
            if rsi_value < self.rsi_threshold and not self.crash:
                self.set_holdings(self.trading_symbol, 1.0, tag="Entry")
                self.debug(f"Long trade opened. RSI: {rsi_value}")
        else: # exit trade
            if self.use_advanced_exit:
                if self.boolean_exit_system.Value == 1 and not self.turned_green_yet:
                    self.turned_green_yet = True
                elif self.boolean_exit_system.Value != 1 and self.turned_green_yet:
                    self.liquidate(self.trading_symbol)
                    self.turned_green_yet = False # reset for the next trade
                    self.debug(f"Trade closed. RSI: {rsi_value}")
            elif rsi_value > self.rsi_threshold:
                self.liquidate(self.trading_symbol)
                self.debug(f"Trade closed. RSI: {rsi_value}")

        if self.crash and rsi_value > self.rsi_threshold: # switch crash back to safe state after a crash
            self.crash = False
            self.debug("Crash flag reset")

    def on_order_event(self, order_event: OrderEvent):
        if order_event.status == OrderStatus.FILLED:
            if self.stop_order and order_event.order_id == self.stop_order.order_id:
                self.crash = True
                self.turned_green_yet = False # reset for the next trade
                self.debug("Stop loss triggered. Crash flag set.")
            if "Entry" in order_event.ticket.tag: # set stop loss
                current_price = self.securities[self.trading_symbol].price
                stop_price = current_price - 2 * self.atr_ind.current.value
                self.stop_order: OrderTicket = self.stop_market_order(self.trading_symbol, -self.portfolio[self.trading_symbol].quantity, stop_price)
                self.debug(f"Stop loss set. Price: {stop_price}")


                