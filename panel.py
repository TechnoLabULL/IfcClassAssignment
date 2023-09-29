# IFC Class Assignment Add-on
# Copyright (c) 2023 Ana Pérez-García <aperezga@ull.edu.es>, Norena Martín-Dorta, José Ángel Aranda
#
# This file is part of Ifc Class Assignment Add-on.
#
# IFC Class Assignment Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IFC Class Assignment Add-on. If not, see <http://www.gnu.org/licenses/>.

import bpy

class PT_IfcClassUtilPanel(bpy.types.Panel):
    """Creates a Sub-Panel in the Property Area of the 3D View"""
    bl_label = "IFC Class Assignment"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "IFC Class Assignment"

    def draw(self, context):
        
        layout = self.layout
        
        layout.label(text="IFC project")
        row = layout.row()
        row.operator("wm.ifc_schema_4", text= "Create", icon= 'FILE_NEW')
        row.operator("wm.export_ifc_project", text= "Export", icon= 'EXPORT')    
        row = layout.row()
        row.operator("wm.levels_ifc_schema", text= "Generate building storeys", icon= 'COLLECTION_NEW')        
        row = layout.row()        
        
        layout.label(text="Assignment of IFC classes to model elements")
        row = layout.row()
        row.operator("wm.ifc_class_walls", text= "Walls", icon= 'AXIS_FRONT')
        row.operator("wm.ifc_class_doors", text= "Doors", icon= 'HOME')
        row = layout.row()
        row.operator("wm.ifc_class_slabs", text= "Slabs", icon= 'AXIS_TOP')
        row.operator("wm.ifc_class_windows", text= "Windows", icon= 'MOD_LATTICE')
        row = layout.row()        
        row.operator("wm.ifc_class_stairs", text= "Stairs", icon= 'IPO_CONSTANT')
        row.operator("wm.ifc_class_columns", text= "Columns", icon= 'MESH_CYLINDER')        
        row = layout.row()
        row.operator("wm.ifc_class_roofs", text= "Roofs", icon= 'LINCURVE')
        row.operator("wm.ifc_class_railings", text= "Railings", icon= 'SNAP_EDGE')        
        layout.row()

classes = [
    PT_IfcClassUtilPanel,
]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
