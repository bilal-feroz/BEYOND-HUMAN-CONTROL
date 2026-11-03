import bpy

print("VERSION", bpy.app.version_string)
sc = bpy.context.scene
print("ENGINES", [e.identifier for e in sc.render.bl_rna.properties['engine'].enum_items])
print("EEVEE", [p.identifier for p in sc.eevee.bl_rna.properties if not p.identifier.startswith('rna')])
print("RENDER mb", hasattr(sc.render, "use_motion_blur"))
print("VIEW", [i.identifier for i in sc.view_settings.bl_rna.properties['view_transform'].enum_items])
try:
    sc.view_settings.view_transform = 'AgX'
    print("LOOKS", [i.identifier for i in sc.view_settings.bl_rna.properties['look'].enum_items])
except Exception as e:
    print("LOOKS ERR", e)
ob = bpy.data.objects.new("x", bpy.data.meshes.new("x"))
sc.collection.objects.link(ob)
m = ob.modifiers.new("Ocean", "OCEAN")
print("OCEAN", [p.identifier for p in m.bl_rna.properties])
ng = bpy.data.node_groups.new("t", "GeometryNodeTree")
rv = ng.nodes.new("FunctionNodeRandomValue")
rv.data_type = 'FLOAT'
print("RV in", [(s.name, s.identifier, getattr(s, 'enabled', None), getattr(s, 'is_unavailable', None)) for s in rv.inputs])
print("RV out", [(s.name, s.identifier, getattr(s, 'enabled', None)) for s in rv.outputs])
print("SOCKET props", [p.identifier for p in rv.inputs[0].bl_rna.properties])
mat = bpy.data.materials.new("m")
print("MAT", [p.identifier for p in mat.bl_rna.properties])
cng = bpy.data.node_groups.new("c", "CompositorNodeTree")
g = cng.nodes.new("CompositorNodeGlare")
print("GLARE in", [(s.name, s.identifier) for s in g.inputs])
print("GLARE props", [p.identifier for p in g.bl_rna.properties if not p.identifier.startswith('bl_')])
print("SCENE comp", hasattr(sc, "compositing_node_group"))
l = bpy.data.lights.new("l", "SPOT")
print("LIGHT", [p.identifier for p in l.bl_rna.properties])
cam = bpy.data.cameras.new("c")
print("DOF", [p.identifier for p in cam.dof.bl_rna.properties])
for n in ["GeometryNodeInputSceneTime", "GeometryNodePoints", "GeometryNodeExtrudeMesh",
          "GeometryNodeInputMeshEdgeNeighbors", "GeometryNodeMeshIcoSphere", "GeometryNodeInstanceOnPoints",
          "ShaderNodeMath", "ShaderNodeVectorMath", "FunctionNodeCompare", "GeometryNodeStoreNamedAttribute",
          "GeometryNodeSetMaterial", "GeometryNodeJoinGeometry", "GeometryNodeFlipFaces", "GeometryNodeMeshGrid",
          "GeometryNodeSetShadeSmooth", "GeometryNodeTransform", "GeometryNodeRealizeInstances",
          "ShaderNodeMapRange", "GeometryNodeRaycast", "GeometryNodeSetPosition", "GeometryNodeInputPosition",
          "ShaderNodeCombineXYZ", "ShaderNodeSeparateXYZ", "GeometryNodeInputIndex", "GeometryNodeMeshCube",
          "GeometryNodeMeshUVSphere", "GeometryNodeObjectInfo", "GeometryNodeDeleteGeometry", "ShaderNodeTexNoise",
          "GeometryNodeSampleNearestSurface", "FunctionNodeBooleanMath", "GeometryNodeScaleElements",
          "GeometryNodeTranslateInstances", "GeometryNodeScaleInstances", "GeometryNodeRotateInstances"]:
    try:
        x = ng.nodes.new(n)
        print("NODE OK", n, "IN", [(s.name, s.identifier) for s in x.inputs][:14], "OUT", [(s.name, s.identifier) for s in x.outputs][:8])
    except Exception as e:
        print("NODE FAIL", n, e)
ext = [n for n in ng.nodes if n.bl_idname == "GeometryNodeExtrudeMesh"][0]
print("EXTRUDE modes", [i.identifier for i in ext.bl_rna.properties['mode'].enum_items] if 'mode' in ext.bl_rna.properties else "mode is socket")
print("EXTRUDE props", [p.identifier for p in ext.bl_rna.properties if not p.identifier.startswith('bl_')])
ma = [n for n in ng.nodes if n.bl_idname == "ShaderNodeMath"][0]
print("MATH props", [p.identifier for p in ma.bl_rna.properties if not p.identifier.startswith('bl_')])
sm = bpy.data.materials.new("s")
nt = sm.node_tree
print("MAT nodes", [n.bl_idname for n in nt.nodes] if nt else "no node tree")
pv = nt.nodes.new("ShaderNodeVolumePrincipled")
print("PVOL", [s.name for s in pv.inputs])
pb = [n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"][0]
print("PBSDF", [s.name for s in pb.inputs])
mod = ob.modifiers.new("GN", "NODES")
mod.node_group = ng
print("GNMOD props", [p.identifier for p in mod.bl_rna.properties])
print("RESULT probe ok")
