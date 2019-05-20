import bpy
import bmesh
import svgwrite



class OT_Export(bpy.types.Operator):
    bl_idname = "uv.export_svg"
    bl_label = "Export UVs to SVG"
    bl_description = "Export UV outlines to SVG"

    def execute(self, context):
        # Get the active mesh
        active_obj = context.object.data
        # bm = bmesh.new()
        bm = bmesh.from_edit_mesh(active_obj)

        uv_layer = bm.loops.layers.uv.active

        # TODO: use dedicated API: bpy_extras.mesh_utils.mesh_linked_uv_islands
        # (I discovered it only after implementing it myself)
        boundary = []
        seams = []

        for edge in bm.edges:
            loops = edge.link_loops
            if len(loops) == 1:
                boundary.append(loops[0])
            else:
                l1, l2 = loops
                if l1.link_loop_next[uv_layer].uv != l2[uv_layer].uv:
                    seams.append(l1)
                    seams.append(l2)
                    
        ring_verts = {v.vert for v in boundary + seams}

        assocs = {}
        for l in boundary + seams:
            assocs[l], = [x for x 
                in l.link_loop_next.vert.link_loops 
                if  x[uv_layer].uv == l.link_loop_next[uv_layer].uv 
                and x.link_loop_next.vert in ring_verts]

        rings = []
        while len(assocs):
            seed, nxt = next(iter(assocs.items()))
            ring = [seed[uv_layer].uv]
            while nxt != seed:
                ring.append(nxt[uv_layer].uv)
                nxt_new = assocs[nxt]
                del assocs[nxt]
                nxt = nxt_new
            del assocs[seed]
            rings.append(ring)
                
        scale = self.uv_scale(bm) / 1000 # 1 unit == 1 mm
        drawing = svgwrite.Drawing('/home/pavel/shm/test.svg', size=(1/scale, 1/scale), profile='full')
        for ring in rings:
            drawing.add(drawing.polygon([(u / scale, v / scale) for (u, v) in ring],
                    stroke=svgwrite.rgb(10, 10, 16, '%'),
                    stroke_width=3,
                    fill="none"
                    ))

        drawing.save()
        return  {'FINISHED'}


    def uv_scale(self, bm):
        uv_layer = bm.loops.layers.uv.active

        # Calculate UV area
        uv_bm = bmesh.new()
        uv_area = 0.0
        for face in bm.faces:
            vs = []
            for l in face.loops: 
                vs.append(uv_bm.verts.new(list(l[uv_layer].uv) + [0.0]))
            face = uv_bm.faces.new(vs)
            uv_area += face.calc_area()
            
        uv_bm.free()

        # Calculate mesh area
        mesh_area = sum([face.calc_area() for face in bm.faces])

        return uv_area / mesh_area