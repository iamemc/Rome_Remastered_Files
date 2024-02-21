import bpy
import os

bl_info = {
    "name": "LOD Generator",
    "description": "Blender addon wrapper of Swagger's LOD Generator.",
    "author": "Swagger, Lorenzo-Feral",
    "version": (1, 0, 2),
    "blender": (4, 0, 0),
    "category": "3D View"
}

# FUNCTIONS (Swagger Tool Functions)


def add_decimate_modifier(context, decimate_ratio):
    try:
        selected_objects = [
            obj for obj in context.selected_objects if obj.type == 'MESH']
        for obj in selected_objects:
            mod = obj.modifiers.get("DECIMATE")
            if mod is None:
                decimate_modifier = obj.modifiers.new("DECIMATE", 'DECIMATE')
                decimate_modifier.ratio = decimate_ratio / 100.0
                print(f"Added DECIMATE modifier to object '{obj.name}'")
            else:
                print(
                    f"DECIMATE modifier already exists on object '{obj.name}'")
        if not selected_objects:
            print("No mesh objects selected.")
    except bpy.exceptions.MissingOperatorException:
        print("An operator is missing. Make sure you are in Object mode.")
    except Exception as e:
        print(f"An error occurred: {e}")


def apply_decimate_modifier(context):
    try:
        selected_objects = [
            obj for obj in context.selected_objects if obj.type == 'MESH']
        for obj in selected_objects:
            context.view_layer.objects.active = obj
            decimate_modifier_applied = False
            for modifier in obj.modifiers:
                if modifier.type == 'DECIMATE':
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                    print(f"Applied DECIMATE modifier on object '{obj.name}'")
                    decimate_modifier_applied = True
                    break
            if not decimate_modifier_applied:
                print(f"No DECIMATE modifier found on object '{obj.name}'")
        if not selected_objects:
            print("No mesh objects selected.")
    except bpy.exceptions.MissingOperatorException:
        print("An operator is missing. Make sure you are in Object mode.")
    except Exception as e:
        print(f"An error occurred: {e}")


def rename_uv_maps(context, file_name):
    try:
        selected_objects = [
            obj for obj in context.selected_objects if obj.type == 'MESH']
        for obj in selected_objects:
            if obj.data.uv_layers:
                for uv_map in obj.data.uv_layers:
                    uv_map.name = file_name[:-4]
                print(
                    f"UV map names for object '{obj.name}' have been renamed.")
            else:
                print(f"No UV maps found for object '{obj.name}'")
        if not selected_objects:
            print("No mesh objects selected.")
    except Exception as e:
        print(f"An error occurred: {e}")


def purge_objects():
    try:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False, confirm=False)
        bpy.ops.outliner.orphans_purge(
            num_deleted=0, do_local_ids=True, do_linked_ids=True, do_recursive=True)
        print("Objects purged successfully.")
    except bpy.exceptions.MissingOperatorException:
        print("One or more operators are missing. Make sure you are in Object mode.")
    except Exception as e:
        print(f"An error occurred: {e}")


def join_child_objects(context):
    try:
        bpy.ops.object.select_all(action='DESELECT')
        objects_to_join = []
        for obj in context.scene.objects:
            if obj.type == 'MESH' and obj.name.lower() not in ("armature", "primary_weapon", "primary__weapon",
                                                               "secondary_weapon", "secondary__weapon"):
                try:
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)
                    if "upper pteryges" in obj.name.lower() or "wide lower pteryges" in obj.name.lower() or \
                            "wide_lower_pteryges" in obj.name.lower():
                        bpy.ops.object.editmode_toggle()
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.mesh.flip_normals()
                        bpy.ops.object.mode_set()
                    objects_to_join.append(obj)
                except Exception as e:
                    print(
                        f"An error occurred while processing object {obj.name}: {e}")
                    continue
        if objects_to_join:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objects_to_join:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = objects_to_join[0]
            bpy.ops.object.join()
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set()
            print("Objects joined successfully.")
    except bpy.exceptions.MissingOperatorException:
        print("One or more operators are missing. Make sure you are in Object mode.")
    except Exception as e:
        print(f"An error occurred: {e}")


def limitBoneWeighting(context):
    try:
        bpy.ops.object.select_all(action='DESELECT')
        armature_exists = False
        for obj in context.scene.objects:
            if obj.name.lower() in ("armature", "primary_weapon", "primary__weapon",
                                    "secondary_weapon", "secondary__weapon"):
                armature_exists = True
        if armature_exists:
            for obj in context.scene.objects:
                if obj.name.lower() not in ("armature", "primary_weapon", "primary__weapon",
                                            "secondary_weapon", "secondary__weapon"):
                    print("Limiting Bone Weights Now")
                    bpy.ops.paint.weight_paint_toggle()
                    bpy.context.object.data.use_paint_mask_vertex = True
                    bpy.ops.paint.vert_select_all(action='SELECT')
                    bpy.ops.object.vertex_group_limit_total(limit=1)
                    bpy.ops.paint.weight_paint_toggle()
    except Exception as e:
        print(f"An error occurred: {e}")


def checkIfDirectoryExists(file_name_string):
    try:
        directory_name = file_name_string[:-4]
        if not os.path.isdir(directory_name):
            os.mkdir(directory_name)
            print(f"Directory '{directory_name}' created successfully.")
        else:
            print(f"Directory '{directory_name}' already exists.")
    except Exception as e:
        print(
            f"An error occurred while creating directory '{directory_name}': {e}")


def generate_lods(context, input_dir, output_dir, decimate_ratio):
    try:
        purge_objects()
        for filename in os.listdir(input_dir):
            file = os.path.join(input_dir, filename)
            if os.path.isfile(file) and file.endswith("dae"):
                file_name = os.path.basename(file)
                LOD_level = context.scene.lod_level
                print("FILENAME: ", file_name)
                bpy.ops.wm.collada_import(filepath=file)
                rename_uv_maps(context=context, file_name=file_name)
                join_child_objects(context=context)
                if decimate_ratio != 1.0:
                    add_decimate_modifier(
                        context=context, decimate_ratio=decimate_ratio)
                    apply_decimate_modifier(context=context)
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.context.active_object.data.vertices.foreach_set(
                        'select', [False] * len(bpy.context.active_object.data.vertices))
                    bpy.context.active_object.data.edges.foreach_set(
                        'select', [False] * len(bpy.context.active_object.data.edges))
                    bpy.context.active_object.data.polygons.foreach_set(
                        'select', [False] * len(bpy.context.active_object.data.polygons))
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.remove_doubles(
                        threshold=0.000001, use_unselected=True)
                    bpy.ops.mesh.delete_loose()
                    bpy.ops.object.mode_set(mode='OBJECT')
                file_name = file_name.replace("_lod0", "")
                output_file_name = f"{file_name[:-4]}_{LOD_level}.dae"
                limitBoneWeighting(context)
                bpy.ops.wm.collada_export(
                    filepath=os.path.join(output_dir, output_file_name))
                purge_objects()
    except OSError as e:
        print(f"Error accessing file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# PANEL
class FERAL_PT_Decimation_Tool(bpy.types.Panel):
    bl_label = "DAE Decimation Tool"
    bl_idname = "FERAL_PT_Decimation_Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Mod - Rome Remastered'

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout

        # Add tutorial text container
        box = layout.box()
        box.label(text="Tutorial:", icon='INFO')
        box.label(
            text="1. Set the input directory where your DAE files are located.")
        box.label(
            text="2. Set the output directory where the decimated DAE files will be exported.")
        box.label(text="3. Adjust the decimation amount. Or choose a Preset")
        box.label(text="4. Click 'Generate LODs' to begin the decimation process.")

        col = layout.column(align=False)

        row = col.row(align=True)
        row.prop(context.scene, "decimation_input_basedir")

        row = col.row(align=True)
        row.prop(context.scene, "decimation_output_basedir")

        row = col.row(align=True)
        row.prop(context.scene, "decimation_amount")

        row = col.row(align=True)
        row.label(text="LOD Presets:")
        row.prop(context.scene, "lod_level", expand=True)

        col.separator(factor=1.0)

        op = col.operator("feral_dae_decimation.decimate_folder",
                          text=r"Generate LODs", emboss=True, depress=False, icon_value=0)


# END PANEL

# OPERATORS

class FERAL_OT_Decimate_DAE(bpy.types.Operator):
    bl_idname = "feral_dae_decimation.decimate_folder"
    bl_label = "Decimate DAE Folder"
    bl_description = "Decimate all dae files in a folder."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.decimation_input_basedir != ""

    def execute(self, context):
        try:
            input_dir = context.scene.decimation_input_basedir
            output_dir = context.scene.decimation_output_basedir if context.scene.decimation_output_basedir else input_dir
            decimate_ratio = context.scene.decimation_amount
            generate_lods(context=context, input_dir=input_dir,
                          output_dir=output_dir, decimate_ratio=decimate_ratio)
        except Exception as exc:
            print(f"An error occurred: {exc}")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


# END OPERATORS

# REGISTER PROPERTIES


def register_properties():
    bpy.types.Scene.decimation_input_basedir = bpy.props.StringProperty(
        name="Input directory",
        default="",
        description="Directory with dae files to decimate.",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.decimation_output_basedir = bpy.props.StringProperty(
        name="Output directory",
        default="",
        description="Directory to export decimated dae models to.",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.decimation_amount = bpy.props.FloatProperty(
        name='Decimation Ratio',
        description='Ratio of decimation',
        default=75,
        min=1,
        max=100
    )

    bpy.types.Scene.lod_level = bpy.props.EnumProperty(
        name="LOD Level",
        description="Level of LOD (1, 2, or 3)",
        items=[
            ('lod1', 'LOD 1 | -25%', 'Level of Detail 1'),
            ('lod2', 'LOD 2 | -50%', 'Level of Detail 2'),
            ('lod3', 'LOD 3 | -75%', 'Level of Detail 3')
        ],
        default='lod1',
        update=update_decimation_amount
    )


def unregister_properties():
    del bpy.types.Scene.decimation_input_basedir
    del bpy.types.Scene.decimation_output_basedir
    del bpy.types.Scene.decimation_amount
    del bpy.types.Scene.lod_level


# REGISTER ADDON

def update_decimation_amount(self, context):
    if self.lod_level == 'lod1':
        context.scene.decimation_amount = 75
    elif self.lod_level == 'lod2':
        context.scene.decimation_amount = 50
    elif self.lod_level == 'lod3':
        context.scene.decimation_amount = 25


def register():
    register_properties()
    bpy.utils.register_class(FERAL_PT_Decimation_Tool)
    bpy.utils.register_class(FERAL_OT_Decimate_DAE)


# UNREGISTER ADDON

def unregister():
    unregister_properties()
    bpy.utils.unregister_class(FERAL_OT_Decimate_DAE)
    bpy.utils.unregister_class(FERAL_PT_Decimation_Tool)


if __name__ == "__main__":
    register()
