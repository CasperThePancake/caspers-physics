# caspers-physics

A simple physics simulation in Python, rendered with PyGame.

# Requires

Python, numpy, PyGame

# Features

A ball that acts to interact with an environment made up of rectangles. These rectangles have positions, widths, heights, angles, colors, and coefficients of restitution.

To exert forces on the ball, use ZQSD (sorry to my inferior QWERTY users).

The project is pre-loaded with a test map. To edit the map, use the following keys:
- SPACE: Toggle editor mode
- Arrow keys: Modify width and height of rectangle
- RSHIFT: Rotate the rectangle
- Left-click: Place the rectangle
- R: Remove the last-placed rectangle
- G: Toggle gravity
- F: Freeze the ball (set all velocity to zero)
- TAB: Get stage save code (printed to terminal)

To load a level using a correct save code, paste it in the saveCode part of the code (replace the current default level code). The level will automatically be loaded when rebooting the simulation.

# Notes

Features that I had planned, but are not yet included:
- Optimization for disabling rendering of rectangles that are off-screen (I fail to think of how to do the maths on this)
- Air resistance and friction (technically this should not be that hard to implement)
- Slope fixes (the ball acts strange on slopes with certain CORs and especially on corners)
