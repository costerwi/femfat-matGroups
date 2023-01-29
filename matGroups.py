#!/usr/bin/env -S abaqus python
"""Define FEMFAT element groups for each material found in an Abaqus .odb file.

Execution:

    abaqus python matGroups.py Job-1.odb [Job-2.odb ...]

Optional automatic execution:

    Copy the onJobCompletion() method into your local abaqus_v6.env file for
    automatic execution whenever an Abaqus job completes. Make sure this
    script is in the working directory or the PYTHONPATH

Description:

In a large assembly of several components it can sometimes be more efficient to
assign fatigue material properties according to the material names used in the
original FEA rather than working with separate assignments for each component.
This can also help avoid mistakes during fatigue material assignments.

This script creates FEMFAT element group definitions with names equal to the
material names used in Abaqus. The groups for each instance will be stored in
separate .bdf files since FEMFAT can only work with one instance at a time.

The group definitions are stored in Hypermesh .bdf format files which may be
imported in the FEMFAT Groups page or using the .ffj command:

    setValue {} {} GUI_Group:Import "Job-1_material_PART-1-1.bdf"

To assign node characteristics like material in FEMFAT you will need to add
nodes to these groups using the "Nodes related to elements in Group" feature.


Latest: https://github.com/costerwi/femfat-matGroups
Carl Osterwisch, August 2021
"""

from __future__ import print_function, with_statement
__version__ = "1.1.0"


def onJobCompletion():
    """Copy this method into abaqus_v6.env for automatic execution"""
    import os, matGroups
    matGroups.fromOdb(os.path.join(savedir, id + '.odb'), instanceName='')


def ranges(intList):
    """Yield ranges of continuous sequences within list of integers

    >>> list(ranges([10,11,12,1,2,3,4,17,18,20]))
    [(1, 4), (10, 12), (17, 18), (20, 20)]
    """

    sortedInts = sorted(intList)
    lower = 0 # lower index
    while lower < len(sortedInts):
        upper = lower # begin binary search to find upper index
        boundary = len(sortedInts) # index of too high
        while boundary > upper + 1:
            mid = (upper + boundary)//2 # middle index
            while sortedInts[mid] - sortedInts[upper] > mid - upper:
                boundary = mid
                mid = (upper + boundary)//2
            upper = mid
        yield sortedInts[lower], sortedInts[upper]
        lower = upper + 1


def hmRanges(intList):
    """Yield ranges of intList in bdf set format

    >>> list(hmRanges([10,11,12,1,2,3,4,17,18,20]))
    ['1 THRU 4', '10 THRU 12', 17, 18, 20]
    """

    for lower, upper in ranges(intList):
        if lower == upper:
            yield lower
        elif lower + 1 == upper:
            # adjacent numbers listed separately
            yield lower
            yield upper
        else:
            yield '%d THRU %d'%(lower, upper)


def bdfExport(bdf, setDict, setType=2):
    """Store sets from setDict to Hypermesh .bdf formatted file

    setType = 1 for node sets, 2 for element sets (default)

    >>> bdfExport(sys.stdout, {
    ...   'SET_A': [10,11,12,1,2,3,4,17,18,20],
    ...   'SET_B': [2,4,6,8,10,12,14,16,18,20],
    ...   })
    CEND
    SET    1 = 1 THRU 4,10 THRU 12,17,18,20
    $HMSET        1        2 "SET_A"
    SET    2 = 2,4,6,8,10,12,14,16,
    18,20
    $HMSET        2        2 "SET_B"
    BEGIN BULK
    ENDDATA
    """

    print('CEND', file=bdf)
    for matId, (matName, elems) in enumerate(sorted(setDict.items()), 1):
        print(matName, len(elems), file=sys.stderr)
        print('SET%5d = '%matId, end='', file=bdf)
        hmList = list(hmRanges(elems))
        chunkSize = 8 # entities per line
        i = -chunkSize
        for i in range(0, len(hmList) - chunkSize, chunkSize):
            print(*(hmList[i:i + chunkSize]), sep=',', end=',\n', file=bdf)
        i += chunkSize # index for last line
        print(*(hmList[i:]), sep=',', file=bdf)
        print('$HMSET %8d %8d "%s"'%(matId, setType, matName), file=bdf)
    print('BEGIN BULK', file=bdf)
    print('ENDDATA', file=bdf)


def fromOdb(odbName, instanceName=''):
    """Extract elsets for each material and store in Hypermesh .bdf format

    The sets for each instance will be stored in separate .bdf files since
    FEMFAT can only work with one instance at a time.

    If an instanceName parameter is specified then only materials for that
    instance will be exported.
    """

    import os
    from contextlib import closing
    from odbAccess import openOdb

    with closing(openOdb(odbName, readOnly=True)) as odb:
        for instance in odb.rootAssembly.instances.values():
            if instanceName and instance.name != instanceName:
                print('Skipping %r != %r'%(instance.name, instanceName), file=sys.stderr)
                continue
            print('Reporting material groups from', instance.name, file=sys.stderr)
            materialSets = {}  # material name => list of element labels
            for sectionAssignment in instance.sectionAssignments:
                section = odb.sections[sectionAssignment.sectionName]
                if not hasattr(section, 'material') or not section.material:
                    continue # skip sections without materials
                materialSets.setdefault(section.material, []).extend(
                        e.label for e in sectionAssignment.region.elements)
            if materialSets:
                fname = '%s_material_%s.bdf'%(
                        os.path.splitext(odbName)[0], instance.name)
                with open(fname, 'w') as bdf:
                    bdfExport(bdf, materialSets)
            else:
                print('-No materials-', file=sys.stderr)


import sys
for odbName in sys.argv[1:]:
    """Export material groups for each specified odb name if run from command line"""
    if '--help' == odbName:
        print(__doc__)
    elif '--test' == odbName:
        import doctest
        doctest.testmod(verbose=True)
    else:
        print(odbName, file=sys.stderr)
        fromOdb(odbName)
