import unittest
from unittest.mock import Mock, patch

from germen import frame_sources


class OpenInputSourceTests(unittest.TestCase):
    def test_network_source_uses_opencv_default_backend(self):
        fake_cv2 = Mock()
        with patch.dict("sys.modules", {"cv2": fake_cv2}):
            frame_sources.open_input_source("http://192.168.1.2:8080/cam.mjpg")
        fake_cv2.VideoCapture.assert_called_once_with("http://192.168.1.2:8080/cam.mjpg")

    def test_windows_camera_id_uses_directshow(self):
        fake_cv2 = Mock(CAP_DSHOW=700)
        with patch.dict("sys.modules", {"cv2": fake_cv2}), patch.object(
            frame_sources.sys, "platform", "win32"
        ):
            frame_sources.open_input_source("2")
        fake_cv2.VideoCapture.assert_called_once_with(2, 700)

    def test_non_windows_camera_id_uses_default_backend(self):
        fake_cv2 = Mock()
        with patch.dict("sys.modules", {"cv2": fake_cv2}), patch.object(
            frame_sources.sys, "platform", "linux"
        ):
            frame_sources.open_input_source("2")
        fake_cv2.VideoCapture.assert_called_once_with(2)


if __name__ == "__main__":
    unittest.main()
