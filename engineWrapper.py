import asyncio
import logging
from typing import Any, Callable, List

import typer
from rich.progress import Progress

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = typer.Typer()

# Mock Database API
async def fetch_initial_input() -> dict:
    """Mock function to fetch initial input from the database."""
    logging.info("Fetching initial input from the database.")
    return {"data": "initial data"}  # Example initial data

# Mock Database API to send delta
async def send_delta_to_database(delta: dict):
    """Mock function to send delta changes to the database."""
    logging.info(f"Sending delta to the database: {delta}")

class EngineWrapper:
    def __init__(self, engines: List[Callable[[Any], Any]]):
        self.engines = engines

    async def run_engines(self):
        input_obj = await fetch_initial_input()
        with Progress() as progress:
            task = progress.add_task("[green]Running engines...", total=len(self.engines))
            for engine in self.engines:
                try:
                    logging.info(f"Running engine: {engine.__name__}")
                    output_obj = await engine(input_obj)
                    delta = self.extract_delta(input_obj, output_obj)
                    await send_delta_to_database(delta)
                    input_obj = output_obj  # Pass output as input to the next engine
                    progress.advance(task)
                except Exception as e:
                    logging.error(f"Error running engine {engine.__name__}: {e}")
                    break  # Stop execution on error

    @staticmethod
    def extract_delta(input_obj: dict, output_obj: dict) -> dict:
        """Extract delta changes between input and output objects."""
        delta = {key: output_obj[key] for key in output_obj if key not in input_obj or output_obj[key] != input_obj[key]}
        return delta

# Mock Engine functions
async def engine1(input_obj: dict) -> dict:
    input_obj["engine1"] = "processed"
    return input_obj

async def engine2(input_obj: dict) -> dict:
    input_obj["engine2"] = "processed"
    return input_obj

@app.command()
def run_wrapper():
    """Runs the engine wrapper with a CLI command."""
    wrapper = EngineWrapper([engine1, engine2])
    asyncio.run(wrapper.run_engines())

if __name__ == "__main__":
    app()
