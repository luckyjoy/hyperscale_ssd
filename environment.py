# features/environment.py
import os
import json
import logging
from datetime import datetime

# Set directories
PWD = os.getcwd()
DATA_DIR = os.path.join(PWD, "data")
LOG_DIR = os.path.join(PWD, "logs")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
log_file = os.path.join(LOG_DIR, f"behave_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ---------------------------
# Hooks
# ---------------------------
def before_scenario(context, scenario):
    context.scenario_data = {}
    logging.info(f"Starting scenario: {scenario.name}")

def after_step(context, step):
    # Record step status
    step_info = {
        "name": step.name,
        "status": step.status.name
    }
    context.scenario_data.setdefault("steps", []).append(step_info)

def after_scenario(context, scenario):
    logging.info(f"Finished scenario: {scenario.name} - Status: {scenario.status.name}")

    # Write scenario data JSON
    json_file = os.path.join(DATA_DIR, f"{scenario.name.replace(' ', '_')}.json")
    with open(json_file, "w") as f:
        json.dump(context.scenario_data, f, indent=2)

    logging.info(f"Scenario JSON data saved: {json_file}")
