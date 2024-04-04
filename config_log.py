import os
import yaml
import logging
from dataclasses import dataclass, field
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class ConfigValidator:
    config_path: str
    meta_config_path: str
    config: Dict[str, Any] = field(init=False)
    meta_config: Dict[str, Any] = field(init=False)

    def __post_init__(self):
        logging.info(f"Loading configuration from {self.config_path}")
        self.config = self.load_yaml(self.config_path)
        
        logging.info(f"Loading metadata configuration from {self.meta_config_path}")
        self.meta_config = self.load_yaml(self.meta_config_path)
        
        logging.info("Starting validation process")
        self.validate()

    def load_yaml(self, path: str) -> dict:
        """Load a YAML file."""
        try:
            with open(path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Failed to load YAML file: {path}, Error: {e}")
            raise ValueError(f"Failed to load YAML file: {path}, Error: {e}")
    
    def validate(self) -> None:
        """Run all validations based on the metadata configuration."""
        for field, specs in self.meta_config.items():
            if specs.get("required", False) and field not in self.config:
                logging.error(f"Missing required field: {field}")
                raise ValueError(f"Missing required field: {field}")
            if field in self.config:
                self.check_data_type(field, specs.get("type"))
                if "range" in specs:
                    self.check_data_range(field, *specs["range"])
                if specs.get("type") == "path":
                    self.check_path_exists(field)
        logging.info("Validation completed successfully")

    def check_data_type(self, field: str, expected_type: str) -> None:
        """Check if a field's value matches the expected data type."""
        value = self.config[field]
        if expected_type == "str" and not isinstance(value, str) or \
           expected_type == "int" and not isinstance(value, int) or \
           expected_type == "path" and not isinstance(value, str):
            logging.error(f"Field '{field}' should be of type {expected_type}")
            raise ValueError(f"Field '{field}' should be of type {expected_type}")

    def check_data_range(self, field: str, min_val: int, max_val: int) -> None:
        """Check if a numerical field's value falls within a specified range."""
        value = self.config[field]
        if not (min_val <= value <= max_val):
            logging.error(f"Field '{field}' must be between {min_val} and {max_val}")
            raise ValueError(f"Field '{field}' must be between {min_val} and {max_val}")

    def check_path_exists(self, field: str) -> None:
        """Check if a file or directory exists."""
        path = self.config[field]
        if not os.path.exists(path):
            logging.error(f"Specified path for '{field}' does not exist: {path}")
            raise ValueError(f"Specified path for '{field}' does not exist: {path}")

# Example usage
config_validator = ConfigValidator('config.yaml', 'config_metadata.yaml')
