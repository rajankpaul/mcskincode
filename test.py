import requests
from PIL import Image
import pyrender
from io import BytesIO

# Define the Mojang API endpoint and the skin URL format
API_ENDPOINT = 'https://api.mojang.com/users/profiles/minecraft/{username}'
SKIN_URL_FORMAT = 'http://textures.minecraft.net/texture/{texture_hash}'

# Define the size of the output image
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512

# Define the camera and lighting setup for rendering the model
camera = pyrender.PerspectiveCamera(yfov=45.0, aspectRatio=1.0)
light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=10.0)

# Define a function to get the skin file URL and texture hash from the Mojang API
def get_skin_url(username):
    response = requests.get(API_ENDPOINT.format(username=username))
    json = response.json()
    if 'textures' in json:
        texture_hash = json['textures']['SKIN']['url'].split('/')[-1]
        return SKIN_URL_FORMAT.format(texture_hash=texture_hash), texture_hash
    else:
        return None, None

# Define a function to render the skin as a 3D model and save it as a PNG file
def render_skin(username):
    # Get the skin URL and texture hash from the Mojang API
    skin_url, texture_hash = get_skin_url(username)

    # Download the skin file and open it with Pillow
    response = requests.get(skin_url)
    skin_image = Image.open(BytesIO(response.content))

    # Create a pyrender mesh that matches the dimensions of the skin
    mesh = pyrender.Mesh.from_points(pyrender.Mesh.Cube().vertices * [skin_image.width/IMAGE_WIDTH, skin_image.height/IMAGE_HEIGHT, 1])

    # Map the skin texture onto the mesh
    texture = pyrender.Texture.from_image(skin_image)
    material = pyrender.MetallicRoughnessMaterial(
        baseColorTexture=texture,
        alphaMode='MASK',
        alphaCutoff=0.5,
    )
    mesh.primitives[0].material = material

    # Create a pyrender scene with the mesh, camera, and lighting
    scene = pyrender.Scene()
    scene.add(mesh)
    scene.add(camera)
    scene.add(light, pose=camera.get_pose())

    # Render the scene as a PNG image
    renderer = pyrender.OffscreenRenderer(IMAGE_WIDTH, IMAGE_HEIGHT)
    image, depth = renderer.render(scene)

    # Save the image as a PNG file
    image.save(f'{username}.png')

# Example usage:
render_skin('Notch')