import requests
from PIL import Image
from io import BytesIO
import base64
import json
import pyrender
import numpy as np
import trimesh


# Define the Mojang API endpoint and the skin URL format
API_ENDPOINT = 'https://api.mojang.com/users/profiles/minecraft/{username}'
SESSION_SERVER_ENDPOINT = 'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}'
SKIN_URL_FORMAT = 'https://textures.minecraft.net/texture/{texture_hash}'

# Define the size of the output image
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512

# Define the camera and lighting setup for rendering the model
camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
light = pyrender.SpotLight(color=np.ones(3), intensity=2.0,
                           innerConeAngle=np.pi/16.0,
                           outerConeAngle=np.pi/6.0)


# Define a function to get the skin file URL and texture hash from the Mojang API
def get_skin_url(username):
    try:
        response = requests.get(API_ENDPOINT.format(username=username))
        if response.status_code == 204:
            print(f"No player found for username {username}.")
            return None, None

        uuid = response.json()['id']
        response = requests.get(SESSION_SERVER_ENDPOINT.format(uuid=uuid))
        if response.status_code == 204:
            print(f"No skin texture found for UUID {uuid}.")
            return None, None

        texture_data = response.json()['properties'][0]['value']
        decoded_data = base64.b64decode(texture_data).decode()
        texture_json = json.loads(decoded_data)

        if 'textures' in texture_json:
            skin_url = texture_json['textures']['SKIN']['url']
            texture_hash = skin_url.split('/')[-1]

            # Load the Minecraft skin texture from the URL and save it as a PNG file
            texture_data = requests.get(SKIN_URL_FORMAT.format(texture_hash=texture_hash)).content
            texture_image = Image.open(BytesIO(texture_data)).convert('RGB')
            texture_image.save(f"{username}_skin.png")

            return skin_url, texture_hash

        print(f"No skin texture found for UUID {uuid}.")
        return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving skin texture for username {username}: {e}")
        return None, None

# Define a function to render the skin as a 3D model and save it as a PNG file
def render_skin(username):
    # Get the skin file URL and texture hash from the Mojang API
    skin_url, texture_hash = get_skin_url(username)
    if skin_url is None:
        return None

    # Load the Minecraft skin texture from the URL
    texture_data = requests.get(SKIN_URL_FORMAT.format(texture_hash=texture_hash)).content
    texture_image = Image.open(BytesIO(texture_data)).convert('RGB')
    texture_array = np.array(texture_image)

    # Define the faces for the Minecraft player model
    head_faces = np.array([
        [0, 1, 3],
        [0, 3, 2],
        [4, 7, 5],
        [4, 6, 7],
        [0, 4, 5],
        [0, 5, 1],
        [2, 3, 7],
        [2, 7, 6],
        [0, 2, 6],
        [0, 6, 4],
        [1, 3, 7],
        [1, 7, 5],
    ])
    body_faces = np.array([
        [0, 1, 2],
        [1, 3, 2],
        [4, 7, 5],
        [4, 6, 7],
        [0, 4, 5],
        [0, 5, 1],
        [2, 3, 7],
        [2, 7, 6],
        [0, 2, 6],
        [0, 6, 4],
        [1, 3, 7],
        [1, 7, 5],
    ])
    arm_faces = np.array([
        [0, 1, 2],
        [1, 3, 2],
        [4, 7, 5],
        [4, 6, 7],
        [0, 2, 4],
        [2, 6, 4],
        [1, 3, 5],
        [3, 7, 5],
        [0, 4, 1],
        [4, 5, 1],
        [2, 3, 6],
        [3, 7, 6],
    ])
    leg_faces = np.array([
        [0, 1, 2],
        [1, 3, 2],
        [4, 7, 5],
        [4, 6, 7],
        [0, 2, 4],
        [2, 6, 4],
        [1, 3, 5],
        [3, 7, 5],
        [0, 4, 1],
        [4, 5, 1],
        [2, 3, 6],
        [3, 7, 6],
    ])

    # Create a 3D model of the player with the skin texture applied
    # Define the vertices for the Minecraft player model
    head_vertices = np.array([
        [-0.25, 0.5, -0.25],
        [-0.25, 0.5, 0.25],
        [0.25, 0.5, -0.25],
        [0.25, 0.5, 0.25],
        [-0.25, 1.0, -0.25],
        [-0.25, 1.0, 0.25],
        [0.25, 1.0, -0.25],
        [0.25, 1.0, 0.25],
    ])
    body_vertices = np.array([
        [-0.375, 0.0, -0.1875],
        [-0.375, 0.0, 0.1875],
        [0.375, 0.0, -0.1875],
        [0.375, 0.0, 0.1875],
        [-0.375, 1.0, -0.1875],
        [-0.375, 1.0, 0.1875],
        [0.375, 1.0, -0.1875],
        [0.375, 1.0, 0.1875],
    ])
    arm_vertices = np.array([
        [0.0, 0.0, -0.125],
        [0.0, 0.0, 0.125],
        [0.125, 0.0, -0.125],
        [0.125, 0.0, 0.125],
        [0.0, 1.0, -0.125],
        [0.0, 1.0, 0.125],
        [0.125, 1.0, -0.125],
        [0.125, 1.0, 0.125],
    ])
    leg_vertices = np.array([
        [-0.125, 0.0, -0.125],
        [-0.125, 0.0, 0.125],
        [0.125, 0.0, -0.125],
        [0.125, 0.0, 0.125],
        [-0.125, 1.0, -0.125],
        [-0.125, 1.0, 0.125],
        [0.125, 1.0, -0.125],
        [0.125, 1.0, 0.125],
    ])

    # Create a 3D model of the head with the skin texture applied
    head_mesh = pyrender.Mesh.from_trimesh(trimesh.Trimesh(vertices=head_vertices + [0, 1.5, 0], faces=head_faces,
                                                           vertex_colors=np.tile(texture_array, (8, 1, 1))))

    # Create a 3D model of the body with the skin texture applied
    body_mesh = pyrender.Mesh.from_trimesh(trimesh.Trimesh(vertices=body_vertices, faces=body_faces,
                                    vertex_colors=np.tile(texture_array, (8, 1, 1))))

    # Create a 3D model of the arms with the skin texture applied
    left_arm_mesh = pyrender.Mesh.from_trimesh(trimesh.Trimesh(vertices=arm_vertices + [-0.375, 1.0, -0.0625], faces=arm_faces,
                                    vertex_colors=np.tile(texture_array, (8, 1, 1))))
    right_arm_mesh = pyrender.Mesh.from_trimesh(trimesh.Trimesh(vertices=arm_vertices + [0.375, 1.0, -0.0625], faces=arm_faces,
                                    vertex_colors=np.tile(texture_array, (8, 1, 1))))

    # Create a 3D model of the legs with the skin texture applied
    left_leg_mesh = pyrender.Mesh.from_trimesh(trimesh.Trimesh(vertices=leg_vertices + [-0.1875, 0.0, 0.0], faces=leg_faces,
                                    vertex_colors=np.tile(texture_array, (8, 1, 1))))
    right_leg_mesh = pyrender.Mesh.from_trimesh(trimesh.Trimesh(vertices=leg_vertices + [0.1875, 0.0, 0.0], faces=leg_faces,
                                    vertex_colors=np.tile(texture_array, (8, 1, 1))))

    # Create a pyrender scene and add the 3D model of the player to it
    scene = pyrender.Scene()
    scene.add(head_mesh)
    scene.add(body_mesh)
    scene.add(left_arm_mesh)
    scene.add(right_arm_mesh)
    scene.add(left_leg_mesh)
    scene.add(right_leg_mesh)

    # Define the camera and lighting setup for rendering the model
    camera = pyrender.PerspectiveCamera(yfov=45.0, aspectRatio=1.0)
    camera_pose = np.array([[1.0, 0.0 , 0.0, 0.0],
                            [0.0, 1.0, 0.0, 0.0],
                            [0.0, 0.0, -1.0, -5.0],
                            [0.0, 0.0, 0.0, 1.0]])
    light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=1.0)

    # Add the camera and lighting to the scene
    scene.add(camera, pose=camera_pose)
    scene.add(light)

    # Render the scene and save the output image as a PNG file
    r = pyrender.OffscreenRenderer(IMAGE_WIDTH, IMAGE_HEIGHT)
    color, depth = r.render(scene)
    image = Image.fromarray(color)
    image.save(f"{username}_render.png")

    return image

# Example usage:
render_skin('rajankpaul')