"""Pod spec unit tests."""
import sys
from unittest.mock import MagicMock

sys.path.append("src")
oci_image = MagicMock()
sys.modules["oci_image"] = oci_image
