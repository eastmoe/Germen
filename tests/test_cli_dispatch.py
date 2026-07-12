import sys
import types
import unittest
from unittest.mock import Mock, patch

from germen import cli


class CliDispatchTests(unittest.TestCase):
    def test_no_subcommand_opens_desktop_wizard(self):
        gui_main = Mock()
        fake_gui = types.SimpleNamespace(main=gui_main)
        with patch.dict(sys.modules, {"germen.gui": fake_gui}):
            cli.main([])
        gui_main.assert_called_once_with()

    def test_cli_subcommand_runs_command_line_workflow(self):
        command_main = Mock()
        fake_main_program = types.SimpleNamespace(main=command_main)
        with patch.dict(sys.modules, {"germen.main_program": fake_main_program}):
            cli.main(["cli"])
        command_main.assert_called_once_with()

    def test_ui_alias_still_opens_desktop_wizard(self):
        gui_main = Mock()
        fake_gui = types.SimpleNamespace(main=gui_main)
        with patch.dict(sys.modules, {"germen.gui": fake_gui}):
            cli.main(["ui"])
        gui_main.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
