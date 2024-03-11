import bpy

# Iterate through all materials in the scene
for material in bpy.data.materials:
    # Set the viewport display metallic to zero
    material.metallic = 0
    
    # Check if material has nodes
    if material.use_nodes:
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Delete all existing output nodes
        output_nodes = [node for node in nodes if node.type == 'OUTPUT_MATERIAL']
        for output_node in output_nodes:
            nodes.remove(output_node)
        
        # Create a new output node
        output_node = nodes.new('ShaderNodeOutputMaterial')
        
        # Set the new output node as active
        material.node_tree.nodes.active = output_node
        
        # Mapping of input names to Principled BSDF shader inputs
        input_mapping = {
            "Diffuse Color: Texture": "Base Color",
            "Cutout Opacity: Texture": "Alpha",
            "Dual Lobe Specular Reflectivity: Texture": "Specular IOR Level",
            "Glossy Roughness: Texture": "Roughness",
            "Metallic Weight Texture": "Metallic"
        }
        
        input_value_mapping = {
            "Diffuse Color: Value": "Base Color",
            "Glossy Roughness: Value": "Roughness",
            "Cutout Opacity: Value": "Alpha",
            "Metallic Weight: Value": "Metallic"
        }
        
        # Iterate through nodes in the material
        for node in nodes:
            if node.type == 'GROUP':
                # First handle nodes that require special treatment
                for input in node.inputs:
                    for input_name, shader_input_name in input_value_mapping.items():
                        if input_name in [input.name for input in node.inputs]:
                            input_node = next((input for input in node.inputs if input.name == input_name), None)
                            if input_node:
                                principled_node = nodes.get('Principled BSDF') or nodes.new('ShaderNodeBsdfPrincipled')
                                principled_node.inputs[shader_input_name].default_value = input_node.default_value
                            
                    if input.name == "Bump Strength: Texture" and bool(input.links):
                        # Create Bump node and set its strength to 0.1
                        bump_node = nodes.new('ShaderNodeBump')
                        bump_node.inputs['Strength'].default_value = 0.05
                        
                        # Create Principled BSDF shader node if not already created
                        principled_node = nodes.get('Principled BSDF') or nodes.new('ShaderNodeBsdfPrincipled')
                        
                        # Connect Bump node's Normal output to Principled BSDF's Normal input
                        links.new(bump_node.outputs['Normal'], principled_node.inputs['Normal'])
                        
                        # Connect Bump Strength to Bump Height input
                        for link in links:
                            if link.to_node == node and link.to_socket.name == "Bump Strength: Texture":
                                links.new(link.from_node.outputs[0], bump_node.inputs['Height'])
                                links.remove(link)
                                
                    elif input.name == "Normal Map: Texture" and bool(input.links):
                        # Create Bump node and set its strength to 0.1
                        normal_node = nodes.new('ShaderNodeNormalMap')
                        
                        # Create Principled BSDF shader node if not already created
                        principled_node = nodes.get('Principled BSDF') or nodes.new('ShaderNodeBsdfPrincipled')
                        
                        # Connect Normal node's Normal output to Principled BSDF's Normal input
                        links.new(normal_node.outputs['Normal'], principled_node.inputs['Normal'])
                        
                        # Connect Bump Strength to Bump Height input
                        for link in links:
                            if link.to_node == node and link.to_socket.name == "Normal Map: Texture":
                                links.new(link.from_node.outputs[0], normal_node.inputs['Color'])
                                links.remove(link)
                                
                # Now handle nodes from input mapping
                for input_name, shader_input_name in input_mapping.items():
                    if input_name in [input.name for input in node.inputs]:
                        # Create Principled BSDF shader node if not already created
                        principled_node = nodes.get('Principled BSDF') or nodes.new('ShaderNodeBsdfPrincipled')
                        
                        # Disconnect existing connections and reconnect to Principled BSDF inputs
                        for link in links:
                            if link.to_node == node and link.to_socket.name == input_name:
                                links.new(link.from_node.outputs[0], principled_node.inputs[shader_input_name])
                                links.remove(link)
        
        # Connect Principled BSDF shader node to the new output node
        principled_node = nodes.get('Principled BSDF') or nodes.new('ShaderNodeBsdfPrincipled')
                        
        links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
        
        # Perform Custom Actions on special materials
        if material.name.endswith("_EyeMoisture"):
            for node in material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    node.inputs['Alpha'].default_value = 0
                    
        elif material.name.endswith("_EyeMoisture_1"):
            for node in material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    node.inputs['Alpha'].default_value = 0
                    
        elif material.name.endswith("_Cornea"):
            for node in material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    node.inputs['Alpha'].default_value = 0
                    
        elif material.name.endswith("_Pupils"):
            for node in material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    node.inputs['Base Color'].default_value = (0, 0, 0, 1)
                