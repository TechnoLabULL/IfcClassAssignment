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
    "category": "Development",
}

import bpy

from . import operators
from . import panel

def register():
    operators.register()
    panel.register()

def unregister():
    operators.unregister()
    panel.unregister()