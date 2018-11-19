# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# This script was developed with financial support from the
# Foundation for Science and Technology of Portugal (FCT),
# under the grant PTDC/MHC-PCN/1530/2014.

bl_info = {
    "name": "Point-Light Display Creator",
    "author": "Daniel Monteiro Basso",
    "version": (1, 0, 0),
    "blender": (2, 78, 0),
    "location": "3D View",
    "description": "Creates spheres and attaches them to bones",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
}


import bpy  # noqa - bl_info must come before top-level imports
from mathutils import Vector  # noqa


class CreatePLD(bpy.types.Operator):
    """Creates spheres and attaches them to bones"""
    bl_idname = "view3d.create_pld"
    bl_label = "Create PLD"

    def execute(self, context):
        # a armature deve estar selecionada e em modo de pose
        arma = bpy.context.active_object
        assert arma.type == 'ARMATURE' and bpy.context.mode == 'POSE'
        spheres = []
        for bone in arma.pose.bones:
            loc = (arma.matrix_world * bone.matrix).translation
            bpy.ops.mesh.primitive_uv_sphere_add(
                view_align=False, enter_editmode=False,
                location=loc,
                size=.025
            )
            sphere = bpy.context.active_object
            spheres.append(sphere)
            sphere.name = bone.name
            bpy.ops.object.shade_smooth()
            bpy.context.scene.objects.active = arma
            arma.data.bones.active = bone.bone
            bpy.ops.object.parent_set(type='BONE', keep_transform=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=False)
        if "pure white" in bpy.data.materials:
            mat = bpy.data.materials["pure white"]
        else:
            bpy.ops.material.new()
            mat = bpy.data.materials[-1]
            mat.name = "pure white"
            mat.diffuse_color = (1, 1, 1)
            mat.use_shadeless = True
        bpy.context.object.active_material = mat
        bpy.ops.object.make_links_data(type='MATERIAL')
        return {'FINISHED'}


def view3d_header_buttons(self, context):
    if bpy.context.mode != 'POSE':
        return
    row = self.layout.row(align=True)
    row.operator("view3d.create_pld", text="PLD", icon="OUTLINER_DATA_POSE")


def register():
    bpy.utils.register_class(CreatePLD)
    bpy.types.VIEW3D_HT_header.append(view3d_header_buttons)


def unregister():
    bpy.utils.unregister_class(CreatePLD)
    bpy.types.VIEW3D_HT_header.remove(view3d_header_buttons)
