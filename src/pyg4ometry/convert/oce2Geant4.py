import pyg4ometry as _pyg4
import pyg4ometry.pyoce as _oce

def oceShape_Geant4_PhysicalVolume(name, logicalVolume, pos, rot, greg):
    pass

def oceShpae_Geant4_LogicalVolume(name,solid,material,greg):
    try :
        return greg.logicalVolumeDict[name]
    except :
        pass

    return _pyg4.geant4.LogicalVolume(solid,material,name,greg)

def oceShape_Geant4_Assembly(name, shape, greg) :
    try :
        return greg.logicalVolumeDict[name]
    except :
        pass

    return _pyg4.geant4.AssemblyVolume(name, greg, True)

def oceShape_Geant4_Tessellated(name, shape, greg) :

    ##############################################
    # Check if already in registry
    ##############################################
    try :
        return greg.solidDict[name]
    except KeyError :
        pass

    ##############################################
    # G4 tessellated solid
    ##############################################
    g4t = _pyg4.geant4.solid.TessellatedSolid(name,None,greg)

    nbVerties   = 0
    nbTriangles = 0

    ##############################################
    # create triangulation
    ##############################################
    aMesher = _oce.BRepMesh.BRepMesh_IncrementalMesh(shape, 0.5, False, 0.5, True);

    ##############################################
    # Count total number of nodes and triangles
    ##############################################
    mergedNbNodes = 0
    mergedNbTriangles = 0

    topoExp  = _oce.TopExp.TopExp_Explorer(shape, _oce.TopAbs.TopAbs_FACE, _oce.TopAbs.TopAbs_VERTEX)
    location = _oce.TopLoc.TopLoc_Location()

    while(topoExp.More()) :
        triangulation = _oce.BRep.BRep_Tool.Triangulation(_oce.TopoDS.TopoDSClass.Face(topoExp.Current()),
                                                          location,
                                                          _oce.Poly.Poly_MeshPurpose_NONE)
        topoExp.Next()

        mergedNbNodes += triangulation.NbNodes()
        mergedNbTriangles += triangulation.NbTriangles()

    # print('total : nodes, triangles',mergedNbNodes,mergedNbTriangles)

    ##############################################
    # Empty tesselation
    ##############################################
    if mergedNbNodes == 0 or mergedNbTriangles == 0 :
        return None

    ##############################################
    # Merge triangles from faces
    ##############################################
    mergedMesh = _oce.Poly.Poly_Triangulation(mergedNbNodes, mergedNbTriangles, False,False)

    topoExp.Init(shape, _oce.TopAbs.TopAbs_FACE, _oce.TopAbs.TopAbs_VERTEX)

    nodeCounter = 0
    triangleCounter = 0

    while(topoExp.More()) :

        triangulation = _oce.BRep.BRep_Tool.Triangulation(_oce.TopoDS.TopoDSClass.Face(topoExp.Current()),
                                                          location,
                                                          _oce.Poly.Poly_MeshPurpose_NONE)

        aTrsf = location.Transformation()
        for i in range(1,triangulation.NbNodes()+1,1) :
            aPnt = triangulation.Node(i)
            aPnt.Transform(aTrsf)
            mergedMesh.SetNode(i+nodeCounter, aPnt)
            g4t.addVertex([aPnt.X(), aPnt.Y(), aPnt.Z()])

        orientation = topoExp.Current().Orientation();
        for i in range(1,triangulation.NbTriangles()+1,1) :
            aTri = triangulation.Triangle(i);
            i1, i2, i3 = aTri.Get()

            i1 += nodeCounter
            i2 += nodeCounter
            i3 += nodeCounter

            if orientation == _oce.TopAbs.TopAbs_Orientation.TopAbs_REVERSED :
                aTri.Set(i2,i1,i3)
                g4t.addTriangle([i2 - 1, i1 - 1, i3 - 1])
            else :
                aTri.Set(i1,i2,i3)
                g4t.addTriangle([i1 - 1, i2 - 1, i3 - 1])

            mergedMesh.SetTriangle(i+triangleCounter, aTri)

        nodeCounter += triangulation.NbNodes()
        triangleCounter += triangulation.NbTriangles()

        topoExp.Next()

    g4t.removeDuplicateVertices()

    return g4t

def _oce2Geant4_traverse(shapeTool,label,greg, addBoundingSolids = False) :
    name  = _oce.pythonHelpers.get_TDataStd_Name_From_Label(label)
    node = _pyg4.pyoce.TCollection.TCollection_AsciiString()
    _oce.TDF.TDF_Tool.Entry(label,node)
    if name is None :
        name = node.ToCString()
    loc   = _oce.pythonHelpers.get_XCAFDoc_Location_From_Label(label)

    shape = shapeTool.GetShape(label)
    locShape = shape.Location()
    # locShape.ShallowDump()

    if shapeTool.IsAssembly(label) :
        # print(name,"assembly",label.NbChildren())

        # make assembly
        try :
            return greg.logicalVolumeDict[name]
        except :
            assembly = oceShape_Geant4_Assembly(name,shape,greg)

        # Loop over children
        for i in range(1, label.NbChildren() + 1, 1):
            b, child = label.FindChild(i, False)
            component = _oce2Geant4_traverse(shapeTool, child, greg)

            # need to do this after to keep recursion clean (TODO consider move with extra parameter)
            if component :
                component.motherVolume = assembly
                assembly.add(component)

        return assembly

    elif shapeTool.IsComponent(label) :
        rlabel = _oce.TDF.TDF_Label()
        shapeTool.GetReferredShape(label, rlabel)

        #print(name,"component",label.NbChildren(),rlabel)

        # Create solid
        logicalVolume = _oce2Geant4_traverse(shapeTool, rlabel, greg)

        if not logicalVolume :
            return

        ax = _pyg4.pyoce.gp.gp_XYZ()
        an = 0

        trsf = locShape.Transformation()

        scale = trsf.ScaleFactor()
        trans = trsf.TranslationPart()
        b, ax, an = trsf.GetRotation(ax,an)

        trans = _oce.pythonHelpers.gp_XYZ_numpy(trans)
        ax    = _oce.pythonHelpers.gp_XYZ_numpy(ax)
        rot = _pyg4.transformation.axisangle2tbxyz(ax,an)

        # make physical volume
        physicalVolume = _pyg4.geant4.PhysicalVolume(list(rot),list(trans),logicalVolume,name,None,greg)

        return physicalVolume

    elif shapeTool.IsShape(label) :
        # print(name, "shape",label.NbChildren())

        # make solid
        solid =  oceShape_Geant4_Tessellated(name, shape, greg)

        if not solid :
            return None

        # make logicalVolume
        logicalVolume = oceShpae_Geant4_LogicalVolume(name,solid,"G4_Fe",greg)

        return logicalVolume


def oce2Geant4(shapeTool, shapeName) :
    greg = _pyg4.geant4.Registry()

    label = _oce.pythonHelpers.findOCCShapeByName(shapeTool, shapeName)
    if label is None :
        print("Cannot find shape, exiting")
        return

    # find name of shape
    name = _oce.pythonHelpers.get_TDataStd_Name_From_Label(label)

    # traverse cad and make geant4 geometry
    _oce2Geant4_traverse(shapeTool, label, greg)

    return greg
