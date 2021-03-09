# See https://docs.blender.org/api/blender_python_api_2_78_0/info_tutorial_addon.html for more info

bl_info = {
    "name": "Defold Mesh Export",
    "author": "",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Export > Defold Mesh (.mesh)",
    "description": "Export to Defold .mesh format",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy
from bpy_extras.io_utils import ExportHelper, orientation_helper
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
)

import json
from collections import OrderedDict

def make_stream(name, component_count, data, typ="float32"):
    return OrderedDict([('name', name),
                        ('type', typ),
                        ('count', component_count),
                        ('data', data)
                        ])

def export_mesh(mesh):
    mesh.calc_loop_triangles()
    mesh.calc_normals_split()
    mesh.calc_tangents()
    mesh_materials = mesh.materials
    mesh_loops = mesh.loops
    mesh_vertices = mesh.vertices
    mesh_uv_layers = mesh.uv_layers
    mesh_color_layers = mesh.vertex_colors

    position_values = []
    normal_values = []
    tangent_values = []
    bitangent_values = []
    bitangent_sign_values = []
    uv_values_by_layer = [[]] * len(mesh_uv_layers)
    color_values_by_layer = [[]] * len(mesh_color_layers)

    # https://docs.blender.org/api/current/bpy.types.MeshLoopTriangle.html#bpy.types.MeshLoopTriangle
    for triangle in mesh.loop_triangles:
        material_index = triangle.material_index
        use_smooth = triangle.use_smooth

        for triangle_vertex_index, mesh_vertex_index in enumerate(triangle.vertices):
            mesh_loop = mesh_loops[triangle.loops[triangle_vertex_index]]
            mesh_vertex = mesh_vertices[mesh_vertex_index]

            position = mesh_vertex.co.to_tuple()
            normal = (mesh_vertex.normal if use_smooth else triangle.normal).to_tuple()
            tangent = mesh_loop.tangent.to_tuple()
            bitangent = mesh_loop.bitangent.to_tuple()
            bitangent_sign = mesh_loop.bitangent_sign

            position_values.extend(position)
            normal_values.extend(normal)
            tangent_values.extend(tangent)
            bitangent_values.extend(bitangent)
            bitangent_sign_values.append(bitangent_sign)

        for loop_index in triangle.loops:

            for mesh_uv_layer_index, mesh_uv_layer in enumerate(mesh_uv_layers):
                uv = mesh_uv_layer.data[loop_index].uv
                uv_values_by_layer[mesh_uv_layer_index].extend(uv)

            for mesh_color_layer_index, mesh_color_layer in enumerate(mesh_color_layers):
                color = mesh_color_layer.data[loop_index].color
                color_values_by_layer[mesh_color_layer_index].extend(color)

    streams = [
        make_stream("position", 3, position_values),
        make_stream("normal", 3, normal_values)
    ]

    streams.extend(map(lambda mesh_uv_layer, uv_values: make_stream(mesh_uv_layer.name, 2, uv_values), mesh_uv_layers, uv_values_by_layer))
    streams.extend(map(lambda mesh_color_layer, color_values: make_stream(mesh_color_layer.name, 4, color_values), mesh_color_layers, color_values_by_layer))

    return streams

def export_to_file(f, indent=0):
    obj = bpy.context.active_object

    # if we don't exit edit mode, the (uv) layers will be empty!
    is_editmode = (obj.mode == 'EDIT')
    if is_editmode:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    mesh = obj.data

    streams = export_mesh(mesh)

    s = json.dumps(streams, separators=(',', ':'), indent=indent if indent > 0 else None)
    print(s)
    f.write(bytearray(s, 'utf-8'))


# The main exporter class.
@orientation_helper(axis_forward='-Z', axis_up='Y')
class DefoldExporter(bpy.types.Operator, ExportHelper):
    bl_idname       = "export_mesh.defold_exporter"
    bl_label        = "Export"
    bl_description  = "Export Defold mesh data"

    filename_ext    = ".buffer"
    filter_glob: StringProperty(default="*.buffer", options={'HIDDEN'})

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )

    indent: IntProperty(
        name="Indent",
        min=0, max=8,
        default=0,
    )

    def execute(self, context):
        with open(self.filepath, 'wb') as f:
            export_to_file(f, indent=self.indent)
        return {'FINISHED'}

    def draw(self, context):
        pass


def menu_export(self, context):
    self.layout.operator(DefoldExporter.bl_idname, text="Defold Mesh (.buffer)")

def register():
    bpy.utils.register_class(DefoldExporter)
    bpy.types.TOPBAR_MT_file_export.append(menu_export)

def unregister():
    bpy.utils.unregister_class(DefoldExporter)
    bpy.types.TOPBAR_MT_file_export.remove(menu_export)


if (__name__ == "__main__"):
    register()

    try:
        with open("test.buffer", "wb") as f:
            export_to_file(f)
    finally:
        unregister()
