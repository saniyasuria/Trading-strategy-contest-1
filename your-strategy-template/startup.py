from base_bot_template import runner
from your_strategy import create_strategy
import json, os

if __name__ == '__main__':
    cfg_path = os.environ.get('STRATEGY_CONFIG', 'strategy_config.json')
    config = {}
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            config = json.load(f)
    strategy = create_strategy(config)
    runner.run_strategy(strategy, config)
