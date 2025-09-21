"""
Tests for ConfigManager utility
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager"""

    def test_init_creates_manager(self):
        """Test that ConfigManager can be instantiated"""
        manager = ConfigManager()
        assert manager is not None
        assert hasattr(manager, 'config')

    def test_config_is_dict(self):
        """Test that config is a dictionary"""
        manager = ConfigManager()
        assert isinstance(manager.config, dict)

    def test_get_method_exists(self):
        """Test that get method exists and works"""
        manager = ConfigManager()
        # Should not raise an exception
        result = manager.get('general.source_directory', default='.')
        assert result is not None

    def test_set_method_exists(self):
        """Test that set method exists"""
        manager = ConfigManager()
        # Should not raise an exception
        manager.set('test.key', 'test_value')

    def test_default_config_structure(self):
        """Test that default config has expected structure"""
        manager = ConfigManager()
        config = manager.config

        # Check for main sections
        expected_sections = ['general', 'file_types', 'organization', 'naming']
        for section in expected_sections:
            assert section in config, f"Expected section '{section}' not found in config"

    def test_general_config_defaults(self):
        """Test general configuration defaults"""
        manager = ConfigManager()
        general = manager.config.get('general', {})

        assert 'source_directory' in general
        assert 'destination_directory' in general
        assert 'preserve_originals' in general

    def test_file_types_config(self):
        """Test file types configuration"""
        manager = ConfigManager()
        file_types = manager.config.get('file_types', {})

        assert 'images' in file_types
        assert 'raw' in file_types
        assert 'videos' in file_types

        # Check that they are lists
        assert isinstance(file_types.get('images'), list)
        assert isinstance(file_types.get('raw'), list)
        assert isinstance(file_types.get('videos'), list)

    def test_update_from_args_source(self):
        """Test updating config from args - source directory"""
        manager = ConfigManager()
        args = {'source': '/test/source'}

        manager.update_from_args(args)
        assert manager.get('general.source_directory') == '/test/source'

    def test_update_from_args_destination(self):
        """Test updating config from args - destination directory"""
        manager = ConfigManager()
        args = {'destination': '/test/dest'}

        manager.update_from_args(args)
        assert manager.get('general.destination_directory') == '/test/dest'

    def test_update_from_args_dry_run(self):
        """Test updating config from args - dry run"""
        manager = ConfigManager()
        args = {'dry_run': True}

        manager.update_from_args(args)
        assert manager.get('general.dry_run') is True

    def test_update_from_args_verbose(self):
        """Test updating config from args - verbose"""
        manager = ConfigManager()
        args = {'verbose': False}

        manager.update_from_args(args)
        assert manager.get('general.verbose') is False

    def test_get_with_default(self):
        """Test get method with default value"""
        manager = ConfigManager()
        result = manager.get('nonexistent.key', 'default_value')
        assert result == 'default_value'

    def test_get_nested_key(self):
        """Test getting nested configuration keys"""
        manager = ConfigManager()
        # This should work for existing nested keys
        result = manager.get('general.source_directory')
        assert result is not None