# the main method here will function as a bash script and update data before invoke the main.py script
import os
import json
from DataUpdater import update_data

def execute_strategy(rsi_tricker, trading_ticker, rsi_per, rsi_threshold, lin_reg_period, slope_period, long_thresh):
    # UPDATE DATA
    data_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    # data_folder = "/Users/vsai23/Workspace/RSIBacktester/data"
    update_data([rsi_tricker, trading_ticker], data_folder)
    
        
    backtest_name = f"{rsi_tricker}_{trading_ticker}_{rsi_per}_{rsi_threshold}"
    
    # RUN BACKTEST
    # read in the local config.json and add parameters to it
    with open("config.json", "r") as f:
        docker_config = json.load(f)
        docker_config["parameters"]  = {
            "rsi_ticker": rsi_tricker,
            "rsi_period": rsi_per,
            "rsi_threshold": rsi_threshold,
            "trading_ticker": trading_ticker,
            "lin_reg_period": lin_reg_period,
            "slope_period": slope_period,
            "long_thresh": long_thresh,
            "short_thresh": -long_thresh
        }  
    
    # write the updated config.json
    with open("config.json", "w") as f:
        json.dump(docker_config, f)
        
    # run the following command in a shell
    commands = [
        "source .venv/bin/activate",
        f"lean backtest . --output ./backtests/{backtest_name} --backtest-name '{backtest_name}'",
    ]
    
    os.system(" && ".join(commands)) 
    
    # for windows - not sure if it works
    # powershell_command = f'''
    # powershell -Command "& {{
    #     .\.venv\Scripts\Activate.ps1;
    #     lean backtest . --output .\backtests\{backtest_name} --backtest-name '{backtest_name}'
    # }}"
    # '''

    # os.system(powershell_command)