import bpy

mapsToKeep = ["Alpha", "Roughness"]

# Function to check if a texture node is a non-color texture
def is_non_color_texture(node):
    return node.type == 'TEX_IMAGE' and node.image.colorspace_settings.name == 'Non-Color'

# Iterate through all materials in the scene
for material in bpy.data.materials:
    # Check if the material has a node tree
    if material.node_tree:
        # Create a list to store texture nodes to remove
        nodes_to_remove = []
        
        # Iterate through all nodes in the material's node tree
        for node in material.node_tree.nodes:
            # Check if the node is a non-color texture
            if is_non_color_texture(node):
                # Check where the Color output of the texture node is connected
                for link in material.node_tree.links:
                    if link.from_node == node and link.from_socket.name == 'Color':
                        if link.to_node.type != 'BSDF_PRINCIPLED':
                            nodes_to_remove.append(node)
                            break
                        
                        saveNode = False
                        for map in mapsToKeep:
                            if link.to_socket.name == map:
                                saveNode = True
                                break
                        if not saveNode:
                            nodes_to_remove.append(node)
        
        # Remove the identified non-color texture nodes that are not connected to Roughness input
        for node in nodes_to_remove:
            material.node_tree.nodes.remove(node)