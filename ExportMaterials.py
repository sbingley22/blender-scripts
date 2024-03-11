import bpy
import re

diffuse_textures = [r"_D", r"_d", r"_diffuse"]
roughness_textures = [r"_SR", r"_R", r"_roughness", r"_r"]
normal_textures = [r"_Normal", r"_N", r"_n"]



def find_texture_node(texture_names, node_tree):
    for texture_name in texture_names:
        for node in node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                if re.search(texture_name, node.image.name):
                    return node
    return None

def copy_principled_settings(source_node, target_node):
    target_node.inputs["Base Color"].default_value = source_node.inputs["Base Color"].default_value
    target_node.inputs["Subsurface"].default_value = source_node.inputs["Subsurface"].default_value
    target_node.inputs["Subsurface Radius"].default_value = source_node.inputs["Subsurface Radius"].default_value
    target_node.inputs["Subsurface Color"].default_value = source_node.inputs["Subsurface Color"].default_value
    target_node.inputs["Metallic"].default_value = source_node.inputs["Metallic"].default_value
    target_node.inputs["Specular"].default_value = source_node.inputs["Specular"].default_value
    target_node.inputs["Specular Tint"].default_value = source_node.inputs["Specular Tint"].default_value
    target_node.inputs["Roughness"].default_value = source_node.inputs["Roughness"].default_value
    target_node.inputs["Anisotropic"].default_value = source_node.inputs["Anisotropic"].default_value
    target_node.inputs["Anisotropic Rotation"].default_value = source_node.inputs["Anisotropic Rotation"].default_value
    target_node.inputs["Sheen"].default_value = source_node.inputs["Sheen"].default_value
    target_node.inputs["Sheen Tint"].default_value = source_node.inputs["Sheen Tint"].default_value
    target_node.inputs["Clearcoat"].default_value = source_node.inputs["Clearcoat"].default_value
    target_node.inputs["Clearcoat Roughness"].default_value = source_node.inputs["Clearcoat Roughness"].default_value
    target_node.inputs["IOR"].default_value = source_node.inputs["IOR"].default_value
    target_node.inputs["Transmission"].default_value = source_node.inputs["Transmission"].default_value
    target_node.inputs["Transmission Roughness"].default_value = source_node.inputs["Transmission Roughness"].default_value
    target_node.inputs["Emission"].default_value = source_node.inputs["Emission"].default_value

def convert(material):
    if not material.use_nodes:
        material.use_nodes = True  # Enable node editing

    node_tree = material.node_tree

    # Check if an output node already exists and disconnect it
    for node in node_tree.nodes:
        if node.type == "OUTPUT_MATERIAL":
            for link in node.inputs['Surface'].links:
                node_tree.links.remove(link)
            node_tree.nodes.remove(node)

    # Add EEVEE output node
    shader_output = node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    shader_output.location = (500, 0)

    # Check if a Principled BSDF node already exists
    principled_shader = None
    for node in node_tree.nodes:
        if node.type == "ShaderNodeBsdfPrincipled":
            principled_shader = node
            break

    # Create a Principled BSDF node if it doesn't exist
    if principled_shader is None:
        principled_shader = node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
        principled_shader.location = (300, 0)
    else:
        # Copy settings from existing Principled BSDF node
        existing_principled_node = principled_shader
        principled_shader = node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
        principled_shader.location = existing_principled_node.location
        copy_principled_settings(existing_principled_node, principled_shader)

    # Connect Principled BSDF to EEVEE output
    node_tree.links.new(principled_shader.outputs["BSDF"], shader_output.inputs["Surface"])

    # Find and connect diffuse texture
    diffuse_node = find_texture_node(diffuse_textures, node_tree)
    if diffuse_node:
        diffuse_input = principled_shader.inputs["Base Color"]
        node_tree.links.new(diffuse_node.outputs["Color"], diffuse_input)

    # Find and connect roughness texture
    roughness_node = find_texture_node(roughness_textures, node_tree)
    if roughness_node:
        roughness_input = principled_shader.inputs["Roughness"]
        node_tree.links.new(roughness_node.outputs["Color"], roughness_input)

    # Find and connect normal texture
    normal_node = find_texture_node(normal_textures, node_tree)
    if normal_node:
        # Create Normal Map node
        normal_map_node = node_tree.nodes.new(type="ShaderNodeNormalMap")
        normal_map_node.location = (-200, 300)
        node_tree.links.new(normal_node.outputs["Color"], normal_map_node.inputs["Color"])

        # Connect Normal Map node to Principled BSDF
        node_tree.links.new(normal_map_node.outputs["Normal"], principled_shader.inputs["Normal"])

# Iterate through all materials and apply the function
for material in bpy.data.materials:
    convert(material)

print("Converted all materials.")
