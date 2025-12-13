"""
YAML configuration management for SLSsteam
"""

import yaml
import os
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Any


class ConfigManager:
    """Manages SLSsteam YAML configuration"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize config manager
        
        Args:
            config_path: Path to SLSsteam config.yaml (default: ~/.config/SLSsteam/config.yaml)
        """
        if config_path is None:
            config_path = os.path.expanduser("~/.config/SLSsteam/config.yaml")
        
        self.config_path = config_path
        self.config_dir = os.path.dirname(config_path)
        self.backup_dir = os.path.join(self.config_dir, "backup")
    
    def ensure_config_dir(self):
        """Ensure configuration directory exists"""
        os.makedirs(self.config_dir, exist_ok=True)
    
    def config_exists(self) -> bool:
        """Check if config file exists"""
        return os.path.exists(self.config_path)
    
    def read_section(self, section_key: str, default_value: Any = None) -> Any:
        """
        Read a specific top-level section from the YAML config
        
        Args:
            section_key: Key of the section to read
            default_value: Value to return if section doesn't exist
        
        Returns:
            Section data or default_value
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                if config and section_key in config and config[section_key] is not None:
                    return config[section_key]
        except FileNotFoundError:
            return default_value
        except (yaml.YAMLError, Exception) as e:
            print(f"Error reading YAML file: {e}")
            return None
        
        return default_value
    
    def write_section(self, section_key: str, new_data: Any) -> bool:
        """
        Write data to a specific section of the config file, preserving comments
        
        Args:
            section_key: Section to write to
            new_data: Data to write (list or dict)
        
        Returns:
            True if successful
        """
        try:
            # Read existing lines
            try:
                with open(self.config_path, 'r') as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []
            
            if not lines:
                lines = [f"{section_key}:\n"]
            
            # Find section start
            start_index = -1
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{section_key}:"):
                    start_index = i
                    break
            
            # Add section if it doesn't exist
            if start_index == -1:
                if lines and not lines[-1].endswith('\n'):
                    lines.append('\n')
                lines.extend([f"\n{section_key}:\n"])
                start_index = len(lines) - 2
            
            # Get indentation level
            indent_level = lines[start_index].find(section_key)
            
            # Format new data
            new_data_lines = []
            if isinstance(new_data, list):
                for item in sorted(list(set(new_data))):
                    new_data_lines.append(f"{' ' * (indent_level + 2)}- {item}\n")
            elif isinstance(new_data, dict):
                for key, value in sorted(new_data.items()):
                    new_data_lines.append(f"{' ' * (indent_level + 2)}{key}: {value}\n")
            
            # Find section end
            end_index = start_index + 1
            while end_index < len(lines):
                line = lines[end_index]
                is_section_item = (line.strip() and 
                                 (len(line) - len(line.lstrip(' '))) > indent_level)
                if not is_section_item:
                    break
                end_index += 1
            
            # Combine lines
            final_lines = lines[:start_index + 1] + new_data_lines + lines[end_index:]
            
            # Write back
            self.ensure_config_dir()
            with open(self.config_path, 'w') as f:
                f.writelines(final_lines)
            
            return True
        
        except Exception as e:
            print(f"Error writing to config file: {e}")
            return False
    
    def backup_config(self) -> bool:
        """
        Create a timestamped backup of the config file
        
        Returns:
            True if successful
        """
        if not self.config_exists():
            return True
        
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"config.{timestamp}.yaml")
            shutil.copy(self.config_path, backup_file)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def list_backups(self) -> List[str]:
        """
        List available config backups
        
        Returns:
            List of backup filenames
        """
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = [f for f in os.listdir(self.backup_dir) 
                  if f.startswith('config.') and f.endswith('.yaml')]
        return sorted(backups, reverse=True)  # Most recent first
    
    def restore_backup(self, backup_filename: str) -> bool:
        """
        Restore a config backup
        
        Args:
            backup_filename: Name of backup file to restore
        
        Returns:
            True if successful
        """
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            print(f"Backup file not found: {backup_filename}")
            return False
        
        try:
            # Backup current config before restoring
            if self.config_exists():
                self.backup_config()
            
            shutil.copy(backup_path, self.config_path)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def get_additional_apps(self) -> List[int]:
        """Get list of additional app IDs"""
        return self.read_section('AdditionalApps', [])
    
    def set_additional_apps(self, app_ids: List[int]) -> bool:
        """Set list of additional app IDs"""
        return self.write_section('AdditionalApps', app_ids)
    
    def add_additional_app(self, app_id: int) -> bool:
        """Add a single app to additional apps"""
        apps = set(self.get_additional_apps())
        apps.add(app_id)
        return self.set_additional_apps(list(apps))
    
    def remove_additional_app(self, app_id: int) -> bool:
        """Remove a single app from additional apps"""
        apps = set(self.get_additional_apps())
        apps.discard(app_id)
        return self.set_additional_apps(list(apps))
    
    def get_fake_app_ids(self) -> Dict[int, int]:
        """Get FakeAppIds mapping (online fix)"""
        return self.read_section('FakeAppIds', {})
    
    def set_fake_app_ids(self, mapping: Dict[int, int]) -> bool:
        """Set FakeAppIds mapping"""
        return self.write_section('FakeAppIds', mapping)
    
    def add_fake_app_id(self, real_id: int, fake_id: int = 480) -> bool:
        """Add an online fix mapping"""
        mapping = self.get_fake_app_ids()
        mapping[real_id] = fake_id
        return self.set_fake_app_ids(mapping)
    
    def remove_fake_app_id(self, real_id: int) -> bool:
        """Remove an online fix mapping"""
        mapping = self.get_fake_app_ids()
        mapping.pop(real_id, None)
        return self.set_fake_app_ids(mapping)
