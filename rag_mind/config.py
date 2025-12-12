import json
import os
from typing import List, Dict


class ConfigManager:
    """
    Manages configuration settings for the RAG application.
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (str): Path to the configuration file
        """
        self.config_file = config_file
        self.default_config = {
            "document_paths": ["./docs"],
            "collection_name": "rag_collection",
            "n_results": 5,
            "use_augmentation": True,
            "chunk_size": 1000,
            "chunk_overlap": 100,
            "tokens_per_chunk": 256
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """
        Load configuration from file, or create default if not exists.
        
        Returns:
            dict: Configuration dictionary
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.default_config, **config}
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.default_config.copy()
        else:
            # Create default config file
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config: Dict = None):
        """
        Save configuration to file.
        
        Args:
            config (dict): Configuration dictionary to save. If None, saves current config.
        """
        if config is not None:
            self.config = config
        
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"✓ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_document_paths(self) -> List[str]:
        """
        Get list of document paths.
        
        Returns:
            list: List of document directory paths
        """
        return self.config.get("document_paths", ["./docs"])
    
    def add_document_path(self, path: str):
        """
        Add a new document path to the configuration.
        
        Args:
            path (str): Path to add
        """
        document_paths = self.config.get("document_paths", [])
        if path not in document_paths:
            document_paths.append(path)
            self.config["document_paths"] = document_paths
            self.save_config()
            return True
        return False
    
    def remove_document_path(self, path: str):
        """
        Remove a document path from the configuration.
        
        Args:
            path (str): Path to remove
        """
        document_paths = self.config.get("document_paths", [])
        if path in document_paths:
            document_paths.remove(path)
            self.config["document_paths"] = document_paths
            self.save_config()
            return True
        return False
    
    def update_setting(self, key: str, value):
        """
        Update a specific setting.
        
        Args:
            key (str): Setting key
            value: New value for the setting
        """
        self.config[key] = value
        self.save_config()
    
    def get_setting(self, key: str, default=None):
        """
        Get a specific setting value.
        
        Args:
            key (str): Setting key
            default: Default value if key doesn't exist
            
        Returns:
            Setting value or default
        """
        return self.config.get(key, default)
    
    def get_all_settings(self) -> Dict:
        """
        Get all configuration settings.
        
        Returns:
            dict: All configuration settings
        """
        return self.config.copy()
    
    def reset_to_defaults(self):
        """
        Reset configuration to default values.
        """
        self.config = self.default_config.copy()
        self.save_config()
        print("✓ Configuration reset to defaults")
