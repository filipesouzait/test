import os
import yaml
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class ConfigValidator:
    config_paths: List[str]
    meta_config_path: str
    config: Dict[str, Any] = field(init=False)
    meta_config: Dict[str, Any] = field(init=False)

    def __post_init__(self):
        self.config = self.merge_configs(self.config_paths)
        self.meta_config = self.load_yaml(self.meta_config_path)
        
        logging.info("Starting validation process")
        self.validate()

    def load_yaml(self, path: str) -> dict:
        """Load a YAML file."""
        try:
            with open(path, 'r') as file:
                logging.info(f"Loading configuration from {path}")
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Failed to load YAML file: {path}, Error: {e}")
            raise ValueError(f"Failed to load YAML file: {path}, Error: {e}")
    
    def merge_configs(self, paths: List[str]) -> Dict[str, Any]:
        """Merge multiple configuration files, giving precedence to the last."""
        merged_config = {}
        for path in paths:
            config = self.load_yaml(path)
            merged_config.update(config)  # Later configs will override earlier ones
        return merged_config

    # The rest of the class remains the same as the previous version...
    # Implement validate, check_data_type, check_data_range, check_path_exists methods here

# Example usage with a list of configuration paths
config_validator = ConfigValidator(
    ['config_base.yaml', 'config_override.yaml'], 
    'config_metadata.yaml'
)
