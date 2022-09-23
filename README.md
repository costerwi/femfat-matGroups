# femfat-matGroups
Define FEMFAT element groups for each material found in an Abaqus .odb file.

## Execution

    abaqus python matGroups.py Job-1.odb [Job-2.odb ...]

## Optional automatic execution

Copy the `onJobCompletion()` method into your local abaqus_v6.env file for
automatic execution whenever an Abaqus job completes. Make sure this
script is in the working directory or the PYTHONPATH

## Description

In a large assembly of several components it can sometimes be more efficient to
assign fatigue material properties according to the material names used in the original
FEA rather than working with separate assignments for each component. This can
also help avoid mistakes during fatigue material assignments.

This script creates FEMFAT element group definitions with names equal to the
material names used in Abaqus. The groups for each instance will be stored in
separate .bdf files since FEMFAT can only work with one instance at a time.

The group definitions are stored in Hypermesh .bdf format files which may be
imported in the FEMFAT Groups page or using the .ffj command:

```tcl
setValue {} {} GUI_Group:Import "Job-1_material_PART-1-1.bdf"
```

To assign node characteristics like material in FEMFAT you will need to add
nodes to these groups using the "Nodes related to elements in Group" feature.
