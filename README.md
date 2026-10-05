This project implements some filters studied in the Image Processing subject.

Most of the filters implemented for the images were coded trying to avoid using cv2's functions to learn how they work.

For the video, the filters manually implemented were too slow, so cv2 was used.

### Requirements

- Python 3
- Python packages: `opencv-python`, `numpy`, `matplotlib`, and `websockets`
- A modern browser with WebSocket and ES module support
- Camera access is optional and is only needed for the camera workflow

### How to run

From the project directory, start the existing WebSocket processor:

```bash
python3 main.py
```

The processor listens on `localhost:8080`. While it is running, open
`index.html` in a browser. The page connects to the processor automatically.

### Using the interface

Use **Load image** to choose an image, or **Start camera** to process the camera
stream after granting browser permission. Choose a filter from the grouped
filter panel on the right and provide any requested parameters. The current
image and processing status remain visible in the viewer.

Active filters are managed in the lower **Applied filters** rail. Filters stay
in the order in which they were applied, and the filter count shows how many
are active. Select the filter body to edit its parameters. Each active filter
also has a visible **X** button; activate that button with a mouse or keyboard
to remove only that filter. Removing the last active filter restores the
original image.
