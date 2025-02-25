# type: ignore
import unittest.mock

from absl.testing import absltest
from absl.testing import parameterized

from lxm3.xm_cluster import config as config_lib

_SAMPLE_CONFIG = """
project = ""
[local]
[local.storage]
staging = ".lxm"

[[clusters]]
name = "cs"
server = "beaker.cs.ucl.ac.uk"
user = "foo"

[clusters.storage]
staging = "/home/foo/lxm3-staging"

[[clusters]]
name = "myriad"
server = "myriad.rc.ucl.ac.uk"
user = "ucaby36"

[clusters.storage]
staging = "/home/bar/Scratch/lxm3-staging"

"""


def _test_config():
    return config_lib.Config.from_string(_SAMPLE_CONFIG)


class ConfigTest(parameterized.TestCase):
    def test_config(self):
        config = _test_config()
        self.assertTrue(isinstance(config["clusters"], list))
        self.assertEqual(config["clusters"][0]["name"], "cs")

    def test_local_config(self):
        config = _test_config()
        self.assertEqual(config.local_config()["storage"], {"staging": ".lxm"})

    def test_default_cluster(self):
        config = _test_config()
        self.assertEqual(config.default_cluster(), "cs")
        with unittest.mock.patch.dict("os.environ", {"LXM_CLUSTER": "myriad"}):
            self.assertEqual(config.default_cluster(), "myriad")

    def test_cluster_config(self):
        config = _test_config()
        self.assertEqual(config.cluster_config()["name"], "cs")
        self.assertEqual(config.cluster_config("myriad")["name"], "myriad")
        with self.assertRaisesRegex(ValueError, "Unknown cluster"):
            config.cluster_config("foo")

    def test_config_project(self):
        config = config_lib.Config()
        self.assertEqual(config.project(), None)
        with unittest.mock.patch.dict("os.environ", {"LXM_PROJECT": "test"}):
            self.assertEqual(config.project(), "test")


if __name__ == "__main__":
    absltest.main()
