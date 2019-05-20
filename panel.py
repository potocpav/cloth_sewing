import bpy

class PT_Panel(bpy.types.Panel):
    bl_idname = "PT_Panel"
    bl_label = "Cloth Sewing"
    bl_category = "Cloth Sewing"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('view3d.cursor_center', text="Center 3D cursor")
        row.operator('uv.export_svg', text="Export UV Outlines")
        row = layout.row()
        row.operator('uv.export_svg', text="Export UV Outlines")
        