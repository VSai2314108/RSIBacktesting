from executor import execute_strategy

def run_all_strategies(names: list[str]):
    for name in names:
        parts = name.split("_")
        execute_strategy(parts[0], parts[1], int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]), int(parts[6]))

if __name__ == "__main__":
    # test on SPY, TQQQ, NVDA, TSLA with slope per of 10 lin per of 10 thresh of 10 
    # structure is RSITicker_TradingTicker_RSI_Period_RSI_Threshold_LinReg_Period_Slope_Period_Long_Threshold
    tests = ["SPY_SPY_10_20_14_14_0", "TQQQ_TQQQ_10_20_14_14_0", "NVDA_NVDA_10_20_14_14_0", "TSLA_TSLA_10_20_14_14_0"]
    run_all_strategies(tests)