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


bl_info = {
    "name": "Ultra Coder",
    "author": "Daniel Monteiro Basso",
    "version": (1, 1, 0),
    "blender": (2, 78, 0),
    "location": "Sequencer",
    "description": "Helper for marking events in the timeline",
    "warning": "",
    "wiki_url": "",
    "category": "Sequencer",
}


import bpy  # noqa - bl_info must come before top-level imports
from bpy_extras.io_utils import ExportHelper, ImportHelper  # noqa


try:
    import os
    import json
    with open(os.path.expanduser("~/.ultra-coder.json")) as cfg_file:
        labels = json.load(cfg_file)
except Exception:
    labels = [
        ("TRIA_LEFT", "vL", "NUMPAD_4"),
        ("FULLSCREEN_EXIT", "C", "NUMPAD_5"),
        ("BORDERMOVE", "QR", "NUMPAD_1"),
        ("SOUND", "DTMF", "NUMPAD_2"),
        ("FREEZE", "A", "NUMPAD_8"),
        ("TRIA_RIGHT", "vR", "NUMPAD_6"),
    ]


class ExportMarkers(bpy.types.Operator, ExportHelper):
    """Export markers as a .csv file"""
    bl_idname = "sequence_editor.export_markers"
    bl_label = "Export Markers"
    filename_ext = ".csv"

    filter_glob = bpy.props.StringProperty(
        default="*.csv", options={'HIDDEN'}, maxlen=255,
    )
    sel_only = bpy.props.BoolProperty(
        name="Selected Only", default=False,
    )

    def execute(self, context):
        with open(self.filepath, 'w', encoding='utf-8') as out:
            out.write("\n".join(
                "{0.frame},{0.name}".format(m)
                for m in context.scene.timeline_markers
                if not self.sel_only or m.select
            ))
        return {'FINISHED'}


class ImportMarkers(bpy.types.Operator, ImportHelper):
    """Import markers from a .csv file"""
    bl_idname = "sequence_editor.import_markers"
    bl_label = "Import Markers"
    filename_ext = ".csv"

    filter_glob = bpy.props.StringProperty(
        default="*.csv", options={'HIDDEN'}, maxlen=255,
    )

    def execute(self, context):
        with open(self.filepath, encoding='utf-8') as src:
            rows = (l.strip().split(",", 2) for l in src if l.strip())
            for frame, label in rows:
                context.scene.timeline_markers.new(label).frame = int(frame)
        return {'FINISHED'}


class SeqMarkerOperator(bpy.types.Operator):
    """Add an event marker"""
    bl_idname = "sequence_editor.add_marker"
    bl_label = "Add Event Marker"

    m_label = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        s = context.scene
        s.timeline_markers.new(self.m_label).frame = s.frame_current
        s.frame_set(s.frame_current + 1)
        return {'FINISHED'}


def seq_header_buttons(self, context):
    st = context.space_data
    if st.view_type != 'SEQUENCER':
        return
    row = self.layout.row(align=True)
    for icon, label, sc in labels:
        if not icon:
            continue
        row.operator(
            "sequence_editor.add_marker", text="", icon=icon
        ).m_label = label
    row = self.layout.row(align=True)
    row.operator("sequence_editor.import_markers", text="", icon="IMPORT")
    row.operator("sequence_editor.export_markers", text="", icon="EXPORT")


def register():
    bpy.utils.register_class(ImportMarkers)
    bpy.utils.register_class(ExportMarkers)
    bpy.types.SEQUENCER_HT_header.append(seq_header_buttons)
    bpy.utils.register_class(SeqMarkerOperator)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new("Sequencer", space_type="SEQUENCE_EDITOR")
        for icon, label, sc in labels:
            if not sc:
                continue
            kmi = km.keymap_items.new(
                "sequence_editor.add_marker", sc, 'PRESS'
            )
            kmi.properties.m_label = label


def unregister():
    bpy.utils.unregister_class(ImportMarkers)
    bpy.utils.unregister_class(ExportMarkers)
    bpy.types.SEQUENCER_HT_header.remove(seq_header_buttons)
    bpy.utils.unregister_class(SeqMarkerOperator)
