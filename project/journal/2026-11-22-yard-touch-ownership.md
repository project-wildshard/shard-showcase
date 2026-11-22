# 2026-11-22: independent touch look

The camera now retains its initiating pointer until release, cancel, capture
loss, or window blur. An extra touch cannot jump the camera or cancel a drag.
Movement and combat buttons keep their existing independent input. Added
regression tests for interleaved fingers, capture loss and blur.
