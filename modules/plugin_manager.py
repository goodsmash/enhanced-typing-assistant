import importlib
import os
import logging
from typing import List, ModuleType

class PluginManager:
    """
    Manages plugins that extend the application's functionalities.
    """
    
    def __init__(self, plugins_directory='plugins'):
        """
        Initialize the PluginManager.
        
        :param plugins_directory: str - Path to the plugins directory.
        """
        self.plugins_directory = plugins_directory
        self.plugins: List[ModuleType] = []
        logging.info(f"PluginManager initialized with plugins directory: {plugins_directory}")
    
    def load_plugins(self) -> None:
        """
        Load all plugins from the plugins directory.
        """
        if not os.path.exists(self.plugins_directory):
            logging.warning(f"Plugins directory '{self.plugins_directory}' does not exist.")
            return
        
        for filename in os.listdir(self.plugins_directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"{self.plugins_directory}.{module_name}")
                    self.plugins.append(module)
                    logging.info(f"Loaded plugin: {module_name}")
                except Exception as e:
                    logging.error(f"Failed to load plugin '{module_name}': {e}")
    
    def activate_plugins(self) -> None:
        """
        Activate all loaded plugins.
        """
        for plugin in self.plugins:
            if hasattr(plugin, 'activate'):
                try:
                    plugin.activate()
                    logging.info(f"Activated plugin: {plugin.__name__}")
                except Exception as e:
                    logging.error(f"Failed to activate plugin '{plugin.__name__}': {e}")
