# Remember to pack the textures first!

import bpy

reduceBy = 4

# Get all image textures in the blend file
textures = [img for img in bpy.data.images if img.packed_file]

# Reduce the size of each texture by half
for texture in textures:
    old_size = texture.size[:]
    new_size = (old_size[0] // reduceBy, old_size[1] // reduceBy)
    
    # Resize the texture
    texture.scale(new_size[0], new_size[1])

print("Texture sizes reduced for all packed textures.")