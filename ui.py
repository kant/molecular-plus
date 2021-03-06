import bpy
from .utils import get_object

class MS_PT_MolecularHelperPanel(bpy.types.Panel):
    """Creates a Panel in the Tool properties window"""
    bl_label = "Molecular+"
    bl_idname = "OBJECT_PT_molecular_helper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Molecular+"

    @classmethod
    def poll(cls, context):
        return True #context.object != None and context.object.type == 'MESH'

    def draw(self, context):

        layout = self.layout
        scn = context.scene
        obj = context.object
        #psys = obj.particle_systems.active

        if context.object != None:
            psys = get_object(context, obj).particle_systems.active

        row = layout.row()

        if obj and psys != None:

            box = layout.box()
            row = box.row()
            row.label(text = "Molecular Object : " + obj.name)
            row = box.row()
            row.label(text = "System particles : " + str(scn.mol_parnum))
            row.operator("object.mol_set_subs", text = "", icon = "FILE_REFRESH")

            box = layout.box()
            row = box.row()
            if scn.mol_simrun == False and psys.point_cache.is_baked == False:
                row.enabled = True
                row.operator("object.mol_simulate", icon = 'RADIOBUT_ON',text = "Start Simulation")
                row = box.row()
                row.enabled = False
                row.operator("object.clear_pcache", text="Free All Bakes")


            if psys.point_cache.is_baked == True and scn.mol_simrun == False:
                row.enabled = False
                row.operator("object.mol_simulate",icon = 'RADIOBUT_ON',text = "Simulation baked")
                row = box.row()
                row.enabled = True
                row.operator("object.clear_pcache", text="Free All Bakes")
            if scn.mol_simrun == True:
                row.enabled = False
                row.operator("object.mol_simulate",icon = 'RADIOBUT_ON',text = "Process: " + scn.mol_timeremain + " left")
                row = box.row()
                row.enabled = False
                row.operator("object.clear_pcache", text="Free All Bakes")

            #row.prop(scn,"frame_start",text = "start")
            #row.prop(scn,"frame_end",text = "end")
            #row = layout.row()
            #row.prop(scn,"mol_timescale_active",text = "Activate TimeScaling")
            #row = layout.row()
            #row.enabled = scn.mol_timescale_active
            #row.prop(scn,"timescale",text = "TimeScale")
            #row.label(text = "")
            #row = box.row()

            row = box.row()
            row.prop(scn,"mol_bake",text = "Bake Solve")
            row.prop(scn,"mol_render",text = "Render")
            #row = layout.row()
            col = layout.column()
            row = col.row()
            row.active = not scn.mol_autosubsteps
            row.prop(scn,"mol_substep", text = "Steps")#, enabled = !scn.mol_autosubsteps)
            row.prop(scn,"mol_autosubsteps", text = "auto")
            col.prop(scn,"mol_cpu",text = "CPUs")


        if obj and ('Collision' in obj.modifiers) and not psys:
            box = layout.box()
            row = box.row()
            row.label(text = "Collision: " + obj.name)
            row = box.row()
            row.prop(obj.collision, "damping_factor", text = "Damping")
            row = box.row()
            row.prop(obj.collision, "friction_factor", text = "Friction")
            row = box.row()
            row.prop(obj.collision, "stickiness", text = "Stickiness", slider=True)

        if obj and obj.type == 'MESH' and not ('Collision' in obj.modifiers):
            box = layout.box()
            row = box.row()
            row.label(text = "Create :")
            row = box.row()
            row.prop(scn,"mol_voxel_size",text = "Voxel Size")
            row.alignment=('RIGHT')
            row.prop(scn,"mol_hexgrid", text = "hexa")


            #box=layout.box()

            row = box.row()
            row.operator("molecular_operators.molecular_makeemitter", icon = 'MOD_PARTICLE_INSTANCE',text = "Emitter")
            row = box.row()
            row.operator("molecular_operators.molecular_makegrid2d", icon = 'GRID',text = "2D Grid")
            row = box.row()
            row.operator("molecular_operators.molecular_makegrid3d", icon = 'MOD_REMESH',text = "3D Grid")
            row = box.row()
            row.operator("molecular_operators.molecular_makecollider", icon = 'MOD_PHYSICS', text = "Collider")
                #row = box.row
        else:
            if obj and not ('Collision' in obj.modifiers):
                row = layout.row()
                row.label(text = "No Mesh selected !")

class MS_PT_MolecularPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Molecular"
    bl_idname = "OBJECT_PT_molecular"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_category = "Molecular"

    @classmethod
    def poll(cls, context):
        if context.object.particle_systems.active and context.object.particle_systems.active.settings.mol_active == True:
            return True

    def draw(self, context):

        layout = self.layout
        scn = context.scene
        obj = context.object
        #obj = bpy.context.view_layer.depsgraph.objects.get(obj.name, None)

        psys = obj.particle_systems.active
        if psys is None:
            return

        #for the data
        psys_eval = get_object(context, obj).particle_systems.active

        if psys.settings.mol_active == False:
            return
        layout.enabled = psys.settings.mol_active
        #row = layout.row()

        ###   Density by Mass   ###
        box = layout.box()
        box.prop(psys.settings,"mol_density_active", icon = "PLUS",text = "Calculate particles weight by density")

        if psys.settings.mol_density_active:

            subbox = box.box()
            row = subbox.row()

            row.prop(psys.settings,"mol_matter",text = "Preset:")
            row = subbox.row()
            if psys.settings.mol_matter != "-1":
                pmass = (psys.settings.particle_size**3) * float(psys.settings.mol_matter)
                density = float(psys.settings.mol_matter)
                row.label(icon = "INFO",text = "Kg per CubeMeter:" + str(round(density,5))+ " kg")
            else:
                row.prop(psys.settings,"mol_density", text = "Kg per CubeMeter:")
                row = subbox.row()

                pmass = (psys.settings.particle_size**3) * psys.settings.mol_density

            row = subbox.row()
            row.label(icon = "INFO",text = "Mass per Particle: " + str(round(pmass,5)) + " kg")
            row = subbox.row()
            row.label(icon = "INFO",text = "Total system approx weight: " + str(round(len(psys_eval.particles) * pmass,4)) + " kg")


        #row = layout.separator()
        row = layout.row()

        ###   Collision   ###
        row.label(text = "Collisions :")
        box = layout.box()
        row = box.row()
        row.prop(psys.settings,"mol_selfcollision_active", icon = 'PHYSICS', text = "Self Collision")
        row.prop(psys.settings,"mol_othercollision_active", icon = 'PHYSICS', text = "Collision with Others")
        if psys.settings.mol_othercollision_active:
            box.prop(psys.settings,"mol_collision_group",text = "only with:")
        if psys.settings.mol_selfcollision_active or psys.settings.mol_othercollision_active:
            box.prop(psys.settings,"mol_friction",text = " Friction:")
            box.prop(psys.settings,"mol_collision_damp",text = " Damping:")

        row = layout.separator()
        row = layout.row()

        ###   Links at Birth   ###
        row.label(text = "Linking :")
        box = layout.box()
        row = box.row()
        row.prop(psys.settings,"mol_links_active", icon = 'CONSTRAINT', text = "Link at Birth")
        row.prop(psys.settings,"mol_other_link_active", icon = 'CONSTRAINT', text = "Link with Others at Birth")

        if psys.settings.mol_links_active :
            row = box.row()
            row.prop(psys.settings,"mol_link_length",text = "Search Distance")
            row.prop(psys.settings,"mol_link_rellength",text = "Relative")

            row = box.row()
            row.prop(psys.settings,"mol_link_max",text = "Max links")
            row = box.row()
            row.prop(psys.settings,"mol_link_friction",text = "Link friction")
            row = box.row()
            row.prop(psys.settings,"mol_link_tension",text = "Tension")
            row.prop(psys.settings,"mol_link_tensionrand",text = "Rand Tension")
            row = box.row()
            row.prop(psys.settings,"mol_link_stiff",text = "Stiff")
            row.prop(psys.settings,"mol_link_stiffrand",text = "Rand Stiff")
            #row = subbox.row()
            #row.prop(psys.settings,"mol_link_stiffexp",text = "Exponent")
            #row.label(text = "")
            row = box.row()
            row.prop(psys.settings,"mol_link_damp",text = "Damping")
            row.prop(psys.settings,"mol_link_damprand",text = "Rand Damping")
            row = box.row()
            row.prop(psys.settings,"mol_link_broken",text = "broken")
            row.prop(psys.settings,"mol_link_brokenrand",text = "Rand Broken")
            row = box.row()
            row = box.row()
            row.prop(psys.settings,"mol_link_samevalue", text = "Same values for compression/expansion")
            row = box.row()

            if not psys.settings.mol_link_samevalue:
                row.prop(psys.settings,"mol_link_estiff",text = "E Stiff")
                row.prop(psys.settings,"mol_link_estiffrand",text = "Rand E Stiff")
                row = box.row()
                #row.enabled  = not psys.settings.mol_link_samevalue
                #row.prop(psys.settings,"mol_link_estiffexp",text = "E Exponent")
                #row.label(text = "")
                row = box.row()
                row.prop(psys.settings,"mol_link_edamp",text = "E Damping")
                row.prop(psys.settings,"mol_link_edamprand",text = "Rand E Damping")
                row = box.row()
                row.prop(psys.settings,"mol_link_ebroken",text = "E broken")
                row.prop(psys.settings,"mol_link_ebrokenrand",text = "Rand E Broken")

        ###   Relinking   ###

        box = layout.box()
        row = box.row()
        row.prop(psys.settings,"mol_selfrelink_active", icon = 'CONSTRAINT', text = "Self Relink")
        row.prop(psys.settings,"mol_other_link_active", icon = 'CONSTRAINT', text = "Relink with Others")

        if psys.settings.mol_other_link_active:
            row = box.row()
            row.prop(psys.settings,"mol_relink_group",text = "Only with:")

        if psys.settings.mol_other_link_active:#psys:#.settings.mol_selfrelink_active or psys.settings.mol_otherrelink_active:
            row = box.row()
            row.prop(psys.settings,"mol_relink_chance",text = "% linking")
            row.prop(psys.settings,"mol_relink_chancerand",text = "Rand % linking")

            row = box.row()
            row.prop(psys.settings,"mol_relink_max",text = "Max links")
            row = box.row()
            row.prop(psys.settings,"mol_relink_tension",text = "Tension")
            row.prop(psys.settings,"mol_relink_tensionrand",text = "Rand Tension")
            row = box.row()
            row.prop(psys.settings,"mol_relink_stiff",text = "Stiff")
            row.prop(psys.settings,"mol_relink_stiffrand",text = "Rand Stiff")
            #row = subbox.row()
            #row.prop(psys.settings,"mol_relink_stiffexp",text = "Exp")
            #row.label(text = "")
            row = box.row()
            row.prop(psys.settings,"mol_relink_damp",text = "Damping")
            row.prop(psys.settings,"mol_relink_damprand",text = "Rand Damping")
            row = box.row()
            row.prop(psys.settings,"mol_relink_broken",text = "broken")
            row.prop(psys.settings,"mol_relink_brokenrand",text = "Rand broken")
            row = box.row()
            row.prop(psys.settings,"mol_relink_samevalue", text = "Same values for compression/expansion")
            row = box.row()

        if not psys.settings.mol_relink_samevalue:
            row.prop(psys.settings,"mol_relink_estiff",text = "E Stiff")
            row.prop(psys.settings,"mol_relink_estiffrand",text = "Rand E Stiff")
            row = box.row()
            row.prop(psys.settings,"mol_relink_edamp",text = "E Damping")
            row.prop(psys.settings,"mol_relink_edamprand",text = "Rand E Damping")
            row = box.row()
            row.prop(psys.settings,"mol_relink_ebroken",text = "E broken")
            row.prop(psys.settings,"mol_relink_ebrokenrand",text = "Rand E broken")

        box = layout.box()
        row = box.row()
        if obj.data.uv_layers.active != None:
            row.active = True
            row.prop(psys.settings,"mol_bakeuv",text = "Bake UV (current: " + str(obj.data.uv_layers.active.name) + ")" )
        else:
            row.active = False
            if row.active == False:
                row.prop(psys.settings,"mol_bakeuv",text = "Bake UV (current: None)" )
        row = box.row()
        row.active = psys.settings.mol_bakeuv
        row.prop(psys.settings,"mol_bakeuv_global",text = "Global")

        row = layout.separator()

        """
        box = layout.box()
        row = box.row()
        box.active = False
        box.alert = False
        row.alignment = 'CENTER'
        row.label(text = "THANKS TO ALL DONATORS !")
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text = "If you want donate to support my work")
        row = box.row()
        row.alignment = 'CENTER'
        row.operator("wm.url_open", text=" click here to Donate ", icon='URL').url = "www.pyroevil.com/donate/"
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text = "or visit: ")
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text = "www.pyroevil.com/donate/")
        """

class MolecularAdd(bpy.types.Operator):
    bl_idname = "molecular_operators.molecular_add"
    bl_label = "Add Molecular object"
    bl_description = "Add active object as Molecular"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.object.particle_systems.active

    def execute(self, context):
        obj = context.object
        psys = obj.particle_systems.active
        #for the data
        psys_eval = get_object(context, obj).particle_systems.active

        psys.settings.mol_active = True

        return {'FINISHED'}

class MolecularRemove(bpy.types.Operator):
    bl_idname = "molecular_operators.molecular_remove"
    bl_label = "Remove Molecular object"
    bl_description = "Remove Molecular settings from Object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object

        psys = obj.particle_systems.active
        #for the data
        psys_eval = get_object(context, obj).particle_systems.active

        psys.settings.mol_active = False
        return {'FINISHED'}


def append_to_PHYSICS_PT_add_panel(self, context):
    obj = context.object

    if not obj.type == 'MESH':
        return

    psys = obj.particle_systems.active
    if not psys:
        return
    column = self.layout.column(align=True)
    #split = column.split(factor=1.0)
    #column_left = split.column()
    #column_right = split.column()
    col = column

    #for the data
    psys_eval = get_object(context, obj).particle_systems.active

    if psys.settings.mol_active:

        col.operator(
                "molecular_operators.molecular_remove",
                 text="Molecular",
                 icon='X'
                )
    else:

        col.operator(
                "molecular_operators.molecular_add",
                text="Molecular",
                icon='MOD_PARTICLES'
                )


panel_classes = (MS_PT_MolecularPanel,MolecularAdd, MolecularRemove, MS_PT_MolecularHelperPanel)
