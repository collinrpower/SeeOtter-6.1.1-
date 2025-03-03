from unittest import TestCase

from Config.otter_checker_config import OtterCheckerConfig
from unit_test_helpers import *


class Test(TestCase):

    def test_otter_checker_config_save(self):
        file_path = join(testing_output_dir, "otter_checker_config_save_test.json")
        config = OtterCheckerConfig()
        config.save(file_path)

    def test_otter_checker_config_load(self):
        file_path = join(testing_output_dir, "otter_checker_config_load_test.json")
        create_config = OtterCheckerConfig()
        create_config.VALIDATOR_MODE = True
        create_config.save(file_path)
        config = OtterCheckerConfig().load(file_path)
        self.assertEqual(True, config.VALIDATOR_MODE)
        create_config.VALIDATOR_MODE = False
        create_config.save(file_path)
        config = OtterCheckerConfig().load(file_path)
        self.assertEqual(False, config.VALIDATOR_MODE)
