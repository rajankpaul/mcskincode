# Minecraft Skin Rendering

This code generates a 3D model of a Minecraft player skin and saves it as a PNG file. The skin is loaded from the Mojang API and rendered using the `pyrender` library.

## Requirements
- Python 3.x
- requests
- Pillow (PIL)
- numpy
- trimesh
- pyrender

## Usage
The code can be used by calling the `render_skin` function and passing in a Minecraft username. The output image will be saved as `{username}.png`.

## Example

    render_skin('rajankpaul')

## Note
The code currently has some limitations and may not display the skins correctly in all cases. Further improvements and bug fixes are welcome.