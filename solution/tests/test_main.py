import sys
from unittest import TestCase, mock

import src.main


class TestMain(TestCase):

    def test_main_calls_parseargs(self):
        args = ["--arg1", "argval1"]
        prev_argv = sys.argv.copy()
        sys.argv.extend(args)
        with mock.patch("src.main.parse_argv", mock.MagicMock(
                return_value=("1", "2", "3"))) as parse_argv_mock:
            src.main.main()

        sys.argv = prev_argv
        parse_argv_mock.assert_called_with(args)
