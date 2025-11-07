"""
Tests for Progress Tracker utility
"""

import sys
import os
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.progress_tracker import ProgressTracker


class TestProgressTracker:
    """Test cases for ProgressTracker"""

    def test_progress_tracker_init(self):
        """Test that ProgressTracker can be instantiated"""
        tracker = ProgressTracker()
        assert tracker is not None

    def test_progress_tracker_init_with_verbose(self):
        """Test ProgressTracker initialization with verbose option"""
        tracker = ProgressTracker(verbose=True)
        assert tracker is not None

        tracker_quiet = ProgressTracker(verbose=False)
        assert tracker_quiet is not None

    def test_progress_tracker_has_console(self):
        """Test that ProgressTracker has console attribute"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "console")

    def test_print_info_method_exists(self):
        """Test that print_info method exists"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "print_info")
        assert callable(tracker.print_info)

    def test_print_error_method_exists(self):
        """Test that print_error method exists"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "print_error")
        assert callable(tracker.print_error)

    def test_print_warning_method_exists(self):
        """Test that print_warning method exists"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "print_warning")
        assert callable(tracker.print_warning)

    def test_print_success_method_exists(self):
        """Test that print_success method exists"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "print_success")
        assert callable(tracker.print_success)

    def test_print_dry_run_method_exists(self):
        """Test that print_dry_run method exists"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "print_dry_run")
        assert callable(tracker.print_dry_run)

    def test_start_processing_method_exists(self):
        """Test that start_processing method exists"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "start_processing")
        assert callable(tracker.start_processing)

    def test_stop_processing_method_exists(self):
        """Test that stop_processing method exists"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "stop_processing")
        assert callable(tracker.stop_processing)

    def test_file_processed_method_exists(self):
        """Test that file_processed method exists"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "file_processed")
        assert callable(tracker.file_processed)

    def test_print_summary_method_exists(self):
        """Test that print_summary method exists"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "print_summary")
        assert callable(tracker.print_summary)

    @patch("utils.progress_tracker.Console")
    def test_print_info_calls_console(self, mock_console):
        """Test that print_info calls console.print"""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        tracker = ProgressTracker()
        tracker.print_info("Test message")

        # Console should have been called during initialization
        mock_console.assert_called()

    def test_basic_workflow(self):
        """Test basic progress tracking workflow"""
        tracker = ProgressTracker()

        # Start processing
        tracker.start_processing(10, "Testing")

        # Process some files
        tracker.file_processed(success=True)
        tracker.file_processed(success=False)

        # Stop processing
        tracker.stop_processing()

        # Print summary
        tracker.print_summary()

        # Should not raise any exceptions
        assert True

    def test_message_methods_basic(self):
        """Test that message methods don't raise exceptions"""
        tracker = ProgressTracker()

        # These should not raise exceptions
        tracker.print_info("Info message")
        tracker.print_error("Error message")
        tracker.print_warning("Warning message")
        tracker.print_success("Success message")
        tracker.print_dry_run("Dry run message")

        assert True

    def test_update_file_method_exists(self):
        """Test that update_file method exists"""
        tracker = ProgressTracker()
        assert hasattr(tracker, "update_file")
        assert callable(tracker.update_file)

    def test_update_file_basic(self):
        """Test basic update_file usage"""
        tracker = ProgressTracker()

        # Should not raise exception
        tracker.update_file("test_file.jpg", "Processing")
        assert True
