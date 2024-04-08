import os
import logging
import typer
from typing import List, Dict, Callable

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = typer.Typer()

class FlowController:
    def __init__(self, run_directory: str, engines_order: List[str]):
        self.engines = {'EngineA': self.engine_a, 'EngineB': self.engine_b, 'EngineC': self.engine_c}
        self.config = {'run_directory': run_directory, 'engines_order': engines_order}
        self.validate_input()
        self.configure_environment()
        self.create_run_directory()

    def validate_input(self):
        """Validate the input configuration."""
        required_keys = ['run_directory', 'engines_order']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration: {key}")

    def configure_environment(self):
        """Configure the necessary environment settings."""
        logging.info("Configuring environment...")

    def create_run_directory(self):
        """Create the directory for execution results/logs."""
        run_dir = self.config['run_directory']
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
            logging.info(f"Created run directory: {run_dir}")
        else:
            logging.info(f"Run directory already exists: {run_dir}")

    def run_engines(self):
        """Run the engines based on the configured order."""
        engines_order = self.config['engines_order']
        for engine_name in engines_order:
            if engine_name in self.engines:
                logging.info(f"Starting engine: {engine_name}")
                self.engines[engine_name]()
                logging.info(f"Finished engine: {engine_name}")
            else:
                logging.warning(f"Engine not found: {engine_name}")

    # Example engine functions
    def engine_a(self):
        logging.info("Running Engine A")

    def engine_b(self):
        logging.info("Running Engine B")

    def engine_c(self):
        logging.info("Running Engine C")

@app.command()
def run_flow(run_directory: str = typer.Option(..., help="The directory to store run logs"),
             engines_order: List[str] = typer.Option(..., "--engine", help="The order of engines to run")):
    """
    Runs the specified engines in order and manages the flow including input validation, environment configuration, and logging.
    """
    flow = FlowController(run_directory, engines_order)
    flow.run_engines()

if __name__ == "__main__":
    app()
