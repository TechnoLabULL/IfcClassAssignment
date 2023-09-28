# IFC Class Assignment Add-on
# Copyright (c) 2023 Ana Pérez-García
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

bl_info = {
    "name": "IFC Class Assignment Add-on",
    "description": "Automatically assigns IFC classes to the elements of a building model created with the Archipack add-on, using the BlenderBIM add-on",
    "author": "aperezga",
    "version": (1, 0),
    "blender": (3, 50, 0),
    "location": "",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Add Mesh",
}

import bpy, time
from bpy.types import Operator

"""Lists and dictionaries to store data"""
heights = []
parents_doors = []
parents_windows = []
init_levels = []
ifc_levels = []

data = {}
data2 = {}

walls = []
autobooleans = []
automerges = []
holes = []

clean_holes = []
clean_walls = []

def createIFCSchema4():
    bpy.context.scene.BIMProjectProperties.export_schema = 'IFC4'
    bpy.ops.bim.create_project()
    return {'FINISHED'}

def createBuildingStoreys():
    """Extracts the Z-value from the existing level references in the file"""
    for obj in bpy.data.collections['Levels'].all_objects:
        if 'Reference' in obj.name:
            loc = obj.location
            heights.append(round(loc.z, 2))

    """Changes the default name of the first BuildingStorey collection in the IFC schema"""
    # Changes the name to the default reference level in the default BuildingStorey collection
    init_ref = bpy.data.objects.get('IfcBuildingStorey/My Storey')
    if init_ref:
        init_ref.name = 'IfcBuildingStorey/Level ' + str(int(heights[0]))
        init_ref.location[2] = heights[0]

    # Changes the name to the default BuildingStorey collection in the IFC Schema
    init_stor = bpy.data.collections.get('IfcBuildingStorey/My Storey')
    if init_stor:
        init_stor.name = 'IfcBuildingStorey/Level ' + str(int(heights[0]))

    """Creates as many BuildingStorey collections as there are references in the file and assigns it the correspondent Z-value from the list"""
    collect = bpy.data.collections['IfcBuilding/My Building']
    ind = 1
    while ind < len(heights):
        empty = bpy.data.objects.new('Level ' + str(ind), None)
        collect.objects.link(empty)
        empty.select_set(True)
        bpy.ops.bim.assign_class(ifc_class="IfcBuildingStorey", predefined_type="NOTDEFINED", userdefined_type="")
        empty.empty_display_type = 'PLAIN_AXES'
        empty.location[2] = heights[ind]
        ind += 1
    bpy.ops.object.select_all(action='DESELECT')
    return {'FINISHED'}
    
def listsOfLevels():
    """Stores the number of building levels in lists"""
    for init_subcoll in bpy.data.collections['Levels'].children:
        init_levels.append(init_subcoll)
    for ifc_subcoll in bpy.data.collections['IfcBuilding/My Building'].children:
        ifc_levels.append(ifc_subcoll)
    return {'FINISHED'}

def joinDoors():
    """Links hierarchy of doors"""
    obj = bpy.data.objects['Door']
    parents_doors.append(obj) 
    for obj in bpy.data.collections["Openings"].all_objects:
        if 'Door.' in obj.name and len(obj.children) > 0:
            parents_doors.append(obj)
    for p in parents_doors:
        bpy.context.view_layer.objects.active = p
        obj = bpy.context.view_layer.objects.active
        bpy.ops.object.select_grouped(type="CHILDREN_RECURSIVE")
        obj.select_set(True)
        for hol in bpy.data.objects:
            if 'hole' in hol.name:    
                hol.select_set(False)
        bpy.ops.object.join()
    bpy.ops.object.select_all(action='DESELECT')
    return {'FINISHED'}

def joinWindows():
    """Link the hierarchy of windows"""
    obj = bpy.data.objects['Window']
    parents_windows.append(obj) 
    for obj in bpy.data.collections["Openings"].all_objects:
        if 'Window.' in obj.name and len(obj.children) > 0:
            parents_windows.append(obj)
    for p in parents_windows:
        bpy.context.view_layer.objects.active = p
        obj = bpy.context.view_layer.objects.active
        bpy.ops.object.select_grouped(type="CHILDREN_RECURSIVE")
        obj.select_set(True)
        for hol in bpy.data.objects:
            if 'hole' in hol.name:    
                hol.select_set(False)
        bpy.ops.object.join()
    bpy.ops.object.select_all(action='DESELECT')
    return {'FINISHED'}

def deduplicateObjectsData():
    """De-duplicates holes data from copied storeys in case they are linked to the base one"""
    bpy.ops.object.select_all(action='DESELECT')
    for hol in bpy.data.collections['Holes'].all_objects:
        if 'hole' in hol.name:
            hol.select_set(True)
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
    bpy.ops.object.select_all(action='DESELECT')
    return {'FINISHED'}

def makeHolesSelectable():
    """Activates the Selectable Restriction Toggle"""
    outliner_area = next(a for a in bpy.context.screen.areas if a.type == "OUTLINER")
    space = outliner_area.spaces[0]
    space.show_restrict_column_select = True
    space.show_restrict_column_hide = True
    """Makes all holes selectable"""
    for obj in bpy.data.collections['Holes'].all_objects:
        if 'hole' in obj.name:
            obj.hide_select = False
            obj.hide_render = False
    time.sleep(2)
    for obj in bpy.data.collections['Holes'].all_objects:
        if 'hole' in obj.name:
            obj.hide_set(False)
    return {'FINISHED'}
 
def createOpeningVoids():
    """Links door and window holes to the walls in which they are located"""
    mod_name = "AutoMixedBoolean"
    for obj in bpy.data.objects:
        if 'Wall' in obj.name and mod_name in obj.modifiers:
            a = bpy.data.objects[obj.name].modifiers['AutoMixedBoolean'].object.name
            data[obj.name] = bpy.data.objects[a].modifiers.keys()
            data2[a] = bpy.data.objects[a].modifiers.keys()
    for key, list in data.items():
        for value in list:
            walls.append(key)
            automerges.append(value)
    for key, list in data2.items():
        for value in list:
            autobooleans.append(key)
    for autoboolean, automerge in zip(autobooleans, automerges):
        holes.append(bpy.data.objects[autoboolean].modifiers[automerge].object)
    i = j = 0
    while i < len(holes):
        if holes[i] != None:
            clean_holes.append(holes[i].name)
            clean_walls.append(walls[j])
        i += 1
        j += 1
    m = n = 0
    while m < len(clean_holes):
        bpy.data.objects[clean_holes[m]].select_set(True)
        bpy.data.objects[clean_walls[n]].select_set(True)
        bpy.ops.bim.add_opening()
        bpy.ops.object.select_all(action='DESELECT')
        m += 1
        n += 1   
    return {'FINISHED'}

def assignClassToWalls():
    """Assigns IFC class to walls and places them in the correct place of the IFC tree"""
    lev = 0
    while lev < len(init_levels):
        for obj in init_levels[lev].all_objects:
            if 'Wall' in obj.name:
                obj.select_set(True)
        bpy.ops.bim.assign_class(ifc_class="IfcWall", predefined_type="STANDARD", userdefined_type="")
        # Adds walls with IFC class to the IFC schema
        objs = bpy.context.selected_objects
        coll_target = ifc_levels[lev]
        for obj in objs:
            for coll in obj.users_collection:
                # Unlinks objects from original collections
                coll.objects.unlink(obj)
            # Links objects to target collection
            coll_target.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        lev += 1
    return {'FINISHED'}

def assignClassToSlabs():
    """Assigns IFC class to slabs and places them in the correct place of the IFC tree"""
    lev = 0
    while lev < len(init_levels):
        for obj in init_levels[lev].all_objects:
            if 'Slab' in obj.name:
                obj.select_set(True)
        bpy.ops.bim.assign_class(ifc_class="IfcSlab", predefined_type="FLOOR", userdefined_type="")
        # Adds slabs with IFC class to the IFC schema
        objs = bpy.context.selected_objects
        coll_target = ifc_levels[lev]
        for obj in objs:
            for coll in obj.users_collection:
                # Unlinks objects from original collections
                coll.objects.unlink(obj)
            # Links objects to target collection
            coll_target.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        lev += 1
    return {'FINISHED'}

def assignClassToDoors():
    """Assigns IFC class to doors and places them in the correct place of the IFC tree"""
    lev = 0
    while lev < len(init_levels):
        for obj in init_levels[lev].all_objects:
            if 'Door' in obj.name:
                obj.select_set(True)
        bpy.ops.bim.assign_class(ifc_class="IfcDoor", predefined_type="DOOR", userdefined_type="")
        # Adds doors with IFC class to the IFC schema
        objs = bpy.context.selected_objects
        coll_target = ifc_levels[lev]
        for obj in objs:
            for coll in obj.users_collection:
                # Unlinks objects from original collections
                coll.objects.unlink(obj)
            # Links objects to target collection
            coll_target.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        lev += 1
    return {'FINISHED'}

def assignClassToWindows():
    """Assigns IFC class to windows and places them in the correct place of the IFC tree"""
    lev = 0
    while lev < len(init_levels):
        for obj in init_levels[lev].all_objects:
            if 'Window' in obj.name:
                obj.select_set(True)
        bpy.ops.bim.assign_class(ifc_class="IfcWindow", predefined_type="WINDOW", userdefined_type="")
        # Adds windows with IFC class to the IFC schema
        objs = bpy.context.selected_objects
        coll_target = ifc_levels[lev]
        for obj in objs:
            for coll in obj.users_collection:
                # Unlinks objects from original collections
                coll.objects.unlink(obj)
            # Links objects to target collection
            coll_target.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        lev += 1
    return {'FINISHED'}

def assignClassToStairs():
    """Assigns IFC class to stairs and places them in the correct place of the IFC tree"""
    lev = 0
    while lev < len(init_levels):
        for obj in init_levels[lev].all_objects:
            if 'Stair' in obj.name:
                obj.select_set(True)
        bpy.ops.bim.assign_class(ifc_class="IfcStair", predefined_type="USERDEFINED", userdefined_type="STAIR")
        # Adds stairs with IFC class to the IFC schema
        objs = bpy.context.selected_objects
        coll_target = ifc_levels[lev]
        for obj in objs:
            for coll in obj.users_collection:
                # Unlinks objects from original collections
                coll.objects.unlink(obj)
            # Links objects to target collection
            coll_target.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        lev += 1
    return {'FINISHED'}

def assignClassToRoofs():
    """Assigns IFC class to roofs and places them in the correct place of the IFC tree"""
    lev = len(init_levels)-1 #Se da por hecho que los tejados van a estar siempre en el último nivel
    while lev < len(init_levels):
        for obj in init_levels[lev].all_objects:
            if 'Roof' in obj.name:
                obj.select_set(True)
        bpy.ops.bim.assign_class(ifc_class="IfcRoof", predefined_type="USERDEFINED", userdefined_type="ROOF")
        # Adds roofs with IFC class to the IFC schema
        objs = bpy.context.selected_objects
        coll_target = ifc_levels[lev]
        for obj in objs:
            for coll in obj.users_collection:
                # Unlinks objects from original collections
                coll.objects.unlink(obj)
            # Links objects to target collection
            coll_target.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        lev += 1
    return {'FINISHED'}

def assignClassToColumns():
    """Assigns IFC class to columns and places them in the correct place of the IFC tree"""
    lev = 0
    while lev < len(init_levels):
        for obj in init_levels[lev].all_objects:
            if 'Beam' in obj.name or 'Column' in obj.name:
                obj.select_set(True)
        bpy.ops.bim.assign_class(ifc_class="IfcColumn", predefined_type="COLUMN", userdefined_type="")
        # Adds stairs with IFC class to the IFC schema
        objs = bpy.context.selected_objects
        coll_target = ifc_levels[lev]
        for obj in objs:
            for coll in obj.users_collection:
                # Unlinks objects from original collections
                coll.objects.unlink(obj)
            # Links objects to target collection
            coll_target.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        lev += 1
    return {'FINISHED'}

def assignClassToRailings():
    """Assigns IFC class to fences and places them in the correct place of the IFC tree"""
    lev = 0
    while lev < len(init_levels):
        for obj in init_levels[lev].all_objects:
            if 'Fence' in obj.name or 'Railing' in obj.name:
                obj.select_set(True)
        bpy.ops.bim.assign_class(ifc_class="IfcRailing", predefined_type="GUARDRAIL", userdefined_type="")
        # Adds stairs with IFC class to the IFC schema
        objs = bpy.context.selected_objects
        coll_target = ifc_levels[lev]
        for obj in objs:
            for coll in obj.users_collection:
                # Unlinks objects from original collections
                coll.objects.unlink(obj)
            # Links objects to target collection
            coll_target.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        lev += 1
    return {'FINISHED'}

def saveIFCProject():
    bpy.ops.export_ifc.bim('INVOKE_AREA')
    return {'FINISHED'}

class WM_OT_IfcSchema4(Operator):

    bl_idname = "wm.ifc_schema_4"
    bl_label = "ifc_schema_4"
    bl_description = "Create an IFC4 tree in the Blender file"

    def execute(self, context):
        createIFCSchema4()
        return {'FINISHED'}

class WM_OT_ExportIfcProject(Operator):

    bl_idname = "wm.export_ifc_project"
    bl_label = "export_ifc_project"
    bl_description = "Export the IFC project"

    def execute(self, context):
        saveIFCProject()
        return {'FINISHED'}

class WM_OT_LevelsIfcSchema(Operator):
    
    bl_idname = "wm.levels_ifc_schema"
    bl_label = "levels_ifc_schema"
    bl_description = "Creates the necessary levels in the IFC schema"

    def execute(self, context):
        createBuildingStoreys()
        listsOfLevels()        
        return {'FINISHED'}

class WM_OT_IfcClassWalls(Operator):

    bl_idname = "wm.ifc_class_walls"
    bl_label = "ifc_class_walls"
    bl_description = "Assign IFC class to existing walls in the model"

    def execute(self, context):
        makeHolesSelectable()
        deduplicateObjectsData()
        assignClassToWalls()
        createOpeningVoids()
        return {'FINISHED'}

class WM_OT_IfcClassSlabs(Operator):

    bl_idname = "wm.ifc_class_slabs"
    bl_label = "ifc_class_slabs"
    bl_description = "Assign IFC class to existing slabs in the model"

    def execute(self, context):
        assignClassToSlabs()
        return {'FINISHED'}

class WM_OT_IfcClassDoors(Operator):

    bl_idname = "wm.ifc_class_doors"
    bl_label = "ifc_class_doors"
    bl_description = "Assign IFC class to existing doors in the model"

    def execute(self, context):
        parents_doors.clear()
        joinDoors()
        assignClassToDoors()
        return {'FINISHED'}

class WM_OT_IfcClassWindows(Operator):

    bl_idname = "wm.ifc_class_windows"
    bl_label = "ifc_class_windows"
    bl_description = "Assign IFC class to existing windows in the model"

    def execute(self, context):
        parents_windows.clear()
        joinWindows()
        assignClassToWindows()
        return {'FINISHED'}

class WM_OT_IfcClassStairs(Operator):

    bl_idname = "wm.ifc_class_stairs"
    bl_label = "ifc_class_stairs"
    bl_description = "Assign IFC class to existing stairs in the model"

    def execute(self, context):
        assignClassToStairs()
        return {'FINISHED'}

class WM_OT_IfcClassRoofs(Operator):

    bl_idname = "wm.ifc_class_roofs"
    bl_label = "ifc_class_roofs"
    bl_description = "Assign IFC class to existing roofs in the model"

    def execute(self, context):
        assignClassToRoofs()
        return {'FINISHED'}

class WM_OT_IfcClassColumns(Operator):

    bl_idname = "wm.ifc_class_columns"
    bl_label = "ifc_class_columns"
    bl_description = "Assign IFC class to existing columns in the model"

    def execute(self, context):
        assignClassToColumns()
        return {'FINISHED'}

class WM_OT_IfcClassRailings(Operator):

    bl_idname = "wm.ifc_class_railings"
    bl_label = "ifc_class_railings"
    bl_description = "Assign IFC class to existing railings in the model"

    def execute(self, context):
        assignClassToRailings()
        return {'FINISHED'}

classes = [
    WM_OT_IfcSchema4,
    WM_OT_ExportIfcProject,
    WM_OT_LevelsIfcSchema,
    WM_OT_IfcClassWalls,
    WM_OT_IfcClassSlabs,
    WM_OT_IfcClassDoors,
    WM_OT_IfcClassWindows,
    WM_OT_IfcClassStairs,
    WM_OT_IfcClassRoofs,
    WM_OT_IfcClassColumns,
    WM_OT_IfcClassRailings,
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