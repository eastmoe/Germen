import io
import unittest
from contextlib import redirect_stdout

from germen.main_program import print_banner


class MainProgramTests(unittest.TestCase):
    def test_cli_banner_contains_leaf_and_name(self):
        output = io.StringIO()
        with redirect_stdout(output):
            print_banner()
        banner = output.getvalue()
        self.assertIn("/\\", banner)
        self.assertIn("||", banner)
        self.assertIn("G  E  R  M  E  N", banner)


if __name__ == "__main__":
    unittest.main()
