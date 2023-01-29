# femfat-matGroups
Automatically assign FEMFAT material files according to matching group names.

This repository includes two scripts to help make material assignments
in the [FEMFAT](https://femfat.magna.com) CAE fatigue analysis software.
The scripts may be used together or independently.

1. An Abaqus python script to define FEMFAT element groups for each material found in
  the .odb results.
2. A FEMFAT script to automatically assign materials to Groups which share the name
  of each material file (.ffd) in the working directory.

When used together you should copy .ffd material files into the working directory
and either rename them to match with the appropriate Abaqus material names in the
model or use the .ffd names for materials inside Abaqus.

## Download

Get the [latest release](https://github.com/costerwi/femfat-matGroups/releases/latest)

## 1. Python script to create FEMFAT groups based on Abaqus .odb materials

In a large assembly of several components it can sometimes be more efficient to
assign fatigue material properties according to the material names used in the original
FEA rather than working with separate assignments for each component.
This can also help avoid mistakes during fatigue material assignments.

The Abaqus python script `matGroups.py` creates FEMFAT element group definitions with
names equal to the material names used in Abaqus.
The group definitions are stored in Hypermesh .bdf format files which may be
imported in the FEMFAT GUI **Groups** page or using the .ffj command:

```tcl
setValue {} {} GUI_Group:Import "Job-1_material_PART-1-1.bdf"
```

The element material groups for each Abaqus instance will be stored in
separate .bdf files since FEMFAT can only work with one instance at a time.

Note that node characteristics, such as materials, must be assigned to *nodes*
in FEMFAT.
Nodes may be added to element groups using the FEMFAT
"Nodes related to elements in Group" feature.

### Command line execution

    abaqus python matGroups.py Job-1.odb [Job-2.odb ...]

### Automatic execution

Copy the `onJobCompletion()` method into your local `abaqus_v6.env` file for
automatic execution whenever an Abaqus job completes. Make sure `matGroups.py`
is in the working directory or the
[PYTHONPATH](https://docs.python.org/release/2.7.15/using/cmdline.html?highlight=pythonpath#envvar-PYTHONPATH).

## 2. FEMFAT script to assign .ffd materials to groups of the same name

The user should first import **FE Entities** to FEMFAT and define or rename
**Groups** as needed, potentially reading element material Groups defined with the script above.
For each .ffd material file in the working directory,
the script will look for all matching group names in the current model.
If a match is found then the material will be loaded.
The script will add nodes related to each matching group and then
assign the material to the **Node Characteristics** of that group.

### FEMFAT GUI execution

Use the menu item `File->Append...` to run `assignMaterials.ffj` in the interactive GUI.
Alternatively, that script may be copied to the FEMFAT templates directory and
will alway be available from the menu `Templates->assignMaterials`.

### FEMFAT Job (.ffj) execution

The script may be referenced from an existing .ffj file using the syntax:

```tcl
source "assignMaterials.ffj"
```

## Support and Contributions

Any problems or suggestions for improvement may be directed to
[Issues](https://github.com/costerwi/femfat-matGroups/issues).
Similarly, you may propose enhancements with a
[Pull request](https://github.com/costerwi/femfat-matGroups/pulls).
