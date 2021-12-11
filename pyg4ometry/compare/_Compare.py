from collections import defaultdict as _defaultdict
from copy import deepcopy as _deepcopy
import enum as _enum

from pyg4ometry.gdml.Defines import evaluateToFloat as _evaluateToFloat
from pyg4ometry.geant4 import Material as _Material
from pyg4ometry.geant4 import Element as _Element

class Tests:
    """
    Set of options of which tests to perform and potentially with what tolerance.
    """
    def __init__(self):
        self.names             = True
        self.nDaughters        = True
        self.solidExact        = True
        self.shapeExtent       = True
        self.shapeVolume       = True
        self.placement         = True # i.e. position and rotation
        self.materialClassType = True
        self.materialCompositionType = True # i.e. N atoms or mass fraction
        self.testDaughtersByName = True # if true, match up daughters by name, otherwise just iterate over in sequence

        self.toleranceSolidParameterFraction  = 1e-3
        self.toleranceSolidExtentFraction     = 1e-6
        self.toleranceVolumeFraction          = 1e-2
        self.toleranceTranslationFraction     = 1e-6
        self.toleranceScaleFraction           = 1e-3
        self.toleranceRotationFraction        = 1e-6
        self.toleranceMaterialDensityFraction = 1e-4
        self.toleranceMaterialMassFraction    = 1e-4

class TestResult(_enum.Enum):
    """
    A test result can be either pass, fail or not conducted.
    
    Use 0,1 so we can also implicitly construct this with a Boolean.

    Use the bitwise or operator | and not the keyword 'or'. This bitwise or
    operator returns Failed if either have failed. Only returns
    NotTested if both are not tested. Cannot use bitwise |= as we cannot
    update an Enum internally.

    Use TestResult.All() for a list of all possible results - useful as an argument for printing.
    """
    Failed    = 0
    Passed    = 1
    NotTested = 2

    def __or__(self, other):
        if self == TestResult.NotTested and other == TestResult.NotTested:
            return TestResult.NotTested
        # bool(2) = True here
        return TestResult(bool(self.value) and bool(other.value))

    def __ior__(self, other):
        raise IOError("not implement")

    @staticmethod
    def All():
        """
        Utility function to get a list of all test types in one.
        """
        return [TestResult.Failed, TestResult.Passed, TestResult.NotTested]

class TestResultNamed:
    def __init__(self, nameIn, testResultIn=TestResult.Failed, detailsIn=""):
        self.testResult = testResultIn
        self.name = nameIn
        self.details = detailsIn

    def __str__(self):
        return ": ".join([self.name, str(self.testResult), self.details])

class ComparisonResult:
    """
    Holder for a test result. Roughly a dict[testname] = list(TestResultNamed)

    Use + and += to append to this object. Uses a default dictionary so no
    need to initialise any key names. Should always append a list even if only
    1 item.

    >>> cr = ComparisonResult()
    >>> cr['nDaughtersTest'] += [TestResultNamed('volume_1', TestResult.Failed, 'different number')]
    >>> cr.print()

    print() can take a list of test result outcomes to print. e.g. TestResult.All()
    """
    def __init__(self):
        self.test = _defaultdict(list)
        self.result = TestResult.NotTested
        
    def __getitem__(self,key):
        return self.test[key]

    def __setitem__(self,key,value):
        self.test[key] = value
        for testResNamed in value:
            self.result = self.result | testResNamed.testResult  # or equals operator

    def __add__(self, other):
        result = _deepcopy(self)
        for testName,results in other.test:
            result.test[testName].extend(results)
            for v in results:
                result.result = result.result | v.testResult
        return result

    def __iadd__(self, other):
        self.result = self.result | other.result # this should already be a product of all subtests
        for testName, results in other.test.items():
            self.test[testName].extend(results)
        return self

    def __len__(self):
        return len(self.test)

    def testNames(self):
        return list(self.test.keys())

    def print(self, testName=None, testResultsToPrint=[TestResult.Failed], allTests=False):
        """
        :param testName: (optional) name of specific single test to print - see testNames()
        :type  testName: str
        :param testResultsToPrint: (optional) list of result outcomes to print
        :type  testResultsToPrint: list(TestResult)
        :poram allTests: (optional) print all tests irrespective of the result
        :type  allTests: bool

        Print all types of tests (by default) or a specific one type.
        Control level of print out with optional argument of list of test outcomes to print.

        >>> cr.print()
        >>> cr.print('solidName')
        >>> cr.print(testResultsToPrint=TestResult.All())
        >>> cr.print(allTests=True)
        """
        print("Overall result> ", self.result)
        if allTests:
            testResultsToPrint = TestResult.All()
        if testName is None:
            for tn, results in self.test.items():
                print('Test> ', tn)
                for result in results:
                    # only print if required
                    if result.testResult in testResultsToPrint:
                        print(result)
                print(" ")
        else:
            print('Test> ', testName)
            for result in self.test[testName]:
                print(result)
            print(" ") # for a new line
                    

def gdmlFiles(referenceFile, otherFile, tests=Tests(), includeAllTestResults=True):
    import pyg4ometry.gdml as gd
    referenceReader  = gd.Reader(referenceFile)
    referenceReg     = referenceReader.getRegistry()
    referenceWorldLV = referenceReg.getWorldVolume()
    otherReader      = gd.Reader(otherFile)
    otherReg         = otherReader.getRegistry()
    otherWorldLV     = otherReg.getWorldVolume()
    return geometry(referenceWorldLV, otherWorldLV, tests, includeAllTestResults)

def geometry(referenceLV, otherLV, tests=Tests(), includeAllTestResults=True):
    result = logicalVolumes(referenceLV, otherLV, tests, True, includeAllTestResults)
    return result

def logicalVolumes(referenceLV, otherLV, tests, recursive=False, includeAllTestResults=False, testsAlreadyDone=[]):
    result = ComparisonResult()

    rlv = referenceLV  # shortcuts
    olv = otherLV

    testName = ": ".join(["(lv)", rlv.name])

    if tests.names:
        result += _names("logicalVolumeName", rlv.name, olv.name, testName, includeAllTestResults)
    result += solids(rlv.solid, olv.solid, tests,testName, includeAllTestResults)
    if ("mat_test_"+rlv.material.name, "mat_test_"+olv.material.name) not in testsAlreadyDone:
        result += materials(rlv.material, olv.material, tests, testName, includeAllTestResults)
        testsAlreadyDone.append( ("mat_test_"+rlv.material.name, "mat_test_"+olv.material.name) )

    if len(olv.daughterVolumes) != len(rlv.daughterVolumes):
        details =  "# daughters: ('"+rlv.name+"') : "+str(len(rlv.daughterVolumes))
        details += ", ('"+olv.name+"') : "+str(len(olv.daughterVolumes))
        result['nDaughters'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['nDaughters'] += [TestResultNamed(testName, TestResult.Passed)]

    result += _meshes(testName, rlv.mesh, olv.mesh, tests)

    # if not recursive return now and don't loop over daughter physical volumes
    if not recursive:
        testsAlreadyDone.append( ("lv_test_"+referenceLV.name, "lv_test_"+otherLV.name) )
        return result

    # test daughters are the same - could even be same number but different
    # we rely here on unique names in pyg4ometry as that's true in GDML
    rNameToObject = {d.name : d for d in rlv.daughterVolumes}
    oNameToObject = {d.name : d for d in olv.daughterVolumes}
    rSet = set([d.name for d in rlv.daughterVolumes])
    oSet = set([d.name for d in olv.daughterVolumes])

    # iterate over daughters
    # if we assume there's some mismatch, we use the intersection set of names - ie the ones
    # that exist in both.
    if tests.testDaughtersByName:
        # work out names that exist in both sets of daughter names
        overlapSet = rSet.intersection(oSet)
        for daugtherName in overlapSet:
            i_rDaughter = rNameToObject[daugtherName]
            i_oDaughter = oNameToObject[daugtherName]
            if ("daughter_test_"+i_rDaughter.name, "daughter_test_"+i_oDaughter.name) in testsAlreadyDone:
                continue  # already done this test

            result = _checkPVLikeDaughters(i_rDaughter, i_oDaughter, tests, rlv.name, testName,
                                           result, recursive, includeAllTestResults, testsAlreadyDone)
    else:
        for i in range(min(len(rlv.daughterVolumes), len(olv.daughterVolumes))):
            i_rDaughter = rlv.daughterVolumes[i]
            i_oDaughter = olv.daughterVolumes[i]
            if ("daughter_test_"+i_rDaughter.name, "daughter_test_"+i_oDaughter.name) in testsAlreadyDone:
                continue  # already done this test

            result = _checkPVLikeDaughters(i_rDaughter, i_oDaughter, tests, rlv.name, testName,
                                           result, recursive, includeAllTestResults, testsAlreadyDone)

    result = _testDaughterNameSets(rSet, oSet, result, testName, includeAllTestResults)

    testsAlreadyDone.append( ("lv_test_"+referenceLV.name, "lv_test_"+otherLV.name) )
    return result

def physicalVolumes(referencePV, otherPV, tests, recursive=False, lvName="", includeAllTestResults=False, testsAlreadyDone=[]):
    """
    lvName is an optional parent object name to help in print out details decode where the placement is.
    """
    result = ComparisonResult()

    rpv = referencePV # shortcuts
    opv = otherPV

    testName = ": ".join(list(filter(None, [lvName, "(pv)", rpv.name])))

    if tests.names:
        result += _names("placementName", rpv.name, opv.name, testName, includeAllTestResults)
    if tests.placement:
        result += _vector("rotation", rpv.rotation, opv.rotation, tests, testName, includeAllTestResults)
        result += _vector("position", rpv.position, opv.position, tests, testName, includeAllTestResults)

    if rpv.scale and opv.scale: # may be None
        result += _vector("scale", rpv.scale, opv.scale, tests, testName, includeAllTestResults)
    elif rpv.scale or opv.scale:
        rpvScale = str(rpv.scale) if rpv.scale else "None"
        opvScale = str(opv.scale) if opv.scale else "None"
        details = "pv scale inconsistent: (reference): " + rpvScale + ", (other): " + opvScale
        result['pvScale'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['pvScale'] += [TestResultNamed(testName, TestResult.NotTested)]

    result += _copyNumber(testName, rpv.copyNumber, opv.copyNumber, tests, includeAllTestResults)
    if ("lv_test_"+rpv.logicalVolume.name, "lv_test_"+opv.logicalVolume.name) not in testsAlreadyDone:
        result += logicalVolumes(rpv.logicalVolume, opv.logicalVolume, tests, recursive, includeAllTestResults, testsAlreadyDone)
        testsAlreadyDone.append( ("lv_test_"+rpv.logicalVolume.name, "lv_test_"+opv.logicalVolume.name) )

    testsAlreadyDone.append( ("pv_test_"+referencePV.name, "pv_test_"+otherPV.name) )
    return result

def assemblyVolumes(referenceAV, otherAV, tests, recursive=False, includeAllTestResults=False, testsAlreadyDone=[]):
    result = ComparisonResult()

    rav = referenceAV
    oav = otherAV

    testName = ": ".join(["(av)", rav.name])

    if tests.names:
        result += _names("assemblyName", rav.name, oav.name, rav.name, includeAllTestResults)

    # compare placements inside assembly
    rDaughters = rav.daughterVolumes
    oDaughters = oav.daughterVolumes

    # test daughters are the same - could even be same number but different
    # we rely here on unique names in pyg4ometry as that's true in GDML
    rNameToObject = {d.name : d for d in rDaughters}
    oNameToObject = {d.name : d for d in oDaughters}
    rSet = set([d.name for d in rDaughters])
    oSet = set([d.name for d in oDaughters])

    result = _testDaughterNameSets(rSet, oSet, result, testName, includeAllTestResults)

    # iterate over daughters
    # if we assume there's some mismatch, we use the intersection set of names - ie the ones
    # that exist in both.
    if tests.testDaughtersByName:
        # work out names that exist in both sets of daughter names
        overlapSet = rSet.intersection(oSet)
        for daugtherName in overlapSet:
            i_rDaughter = rNameToObject[daugtherName]
            i_oDaughter = oNameToObject[daugtherName]
            if ("daughter_test_"+i_rDaughter.name, "daughter_test_"+i_oDaughter.name) in testsAlreadyDone:
                continue  # already done this test

            result = _checkPVLikeDaughters(i_rDaughter, i_oDaughter, tests, rav.name, testName,
                                           result, recursive, includeAllTestResults, testsAlreadyDone)
    else:
        for i in range(min(len(rDaughters), len(oDaughters))):
            i_rDaughter = rDaughters[i]
            i_oDaughter = oDaughters[i]
            if ("daughter_test_"+i_rDaughter.name, "daughter_test_"+i_oDaughter.name) in testsAlreadyDone:
                continue  # already done this test

            result = _checkPVLikeDaughters(i_rDaughter, i_oDaughter, tests, rav.name, testName,
                                           result, recursive, includeAllTestResults, testsAlreadyDone)

    testsAlreadyDone.append( ("av_test_"+referenceAV.name, "av_test_"+otherAV.name) )
    return result

def _checkPVLikeDaughters(referencePVLikeObject, otherPVLikeObject, tests, parentName, testName, result,
                          recursive=True, includeAllTestResults=True, testsAlreadyDone=[]):
    rDaughter = referencePVLikeObject
    oDaughter = otherPVLikeObject
    r = recursive
    iatr = includeAllTestResults

    # check types
    expectedType = rDaughter.type
    if expectedType != oDaughter.type:
        details = "daughter types in '" + parentName + "': (ref): " + str(expectedType)
        details += ", (other): " + str(oDaughter.type)
        result['daughterType'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['daughterType'] += [TestResultNamed(testName, TestResult.Passed)]

    # do custom type check
    if expectedType == "placement":
        result += physicalVolumes(rDaughter, oDaughter, tests, r, testName, iatr, testsAlreadyDone)
    elif expectedType == "assembly":
        result += assemblyVolumes(rDaughter, oDaughter, tests, r, iatr, testsAlreadyDone)
    elif expectedType == "replica":
        result += replicaVolumes(rDaughter, oDaughter, tests, iatr, testsAlreadyDone)
    elif expectedType == "division":
        result += divisionVolumes(rDaughter, oDaughter, tests, iatr, testsAlreadyDone)
    elif expectedType == "parameterised":
        result += parameterisedVolumes(rDaughter, oDaughter, tests, iatr, testsAlreadyDone)
    else:
        # LN: don't know what to SkinSurface, BorderSurface and Loop
        pass
    testsAlreadyDone.append(("daughter_test_" + rDaughter.name, "daughter_test_" + oDaughter.name))

    return result

def _testDaughterNameSets(referenceDaughterNameSet, otherDaughterNameSet, result, testName, includeAllTestResults):
    rSet = referenceDaughterNameSet
    oSet = otherDaughterNameSet
    # test the number and identity of the daughters matches
    # we rely here on unique names in pyg4ometry as that's true in GDML
    extraNames = oSet - rSet  # ones in oSet but not in rSet
    if len(extraNames) > 0:
        details = "extra daughter"
        if len(extraNames) > 1:
            details += "s "
        details += "[" + ", ".join(extraNames) + "]"
        result['extraDaughter'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['extraDaughter'] += [TestResultNamed(testName, TestResult.Passed)]

    missingNames = rSet - oSet  # ones in rSet but not in oSet
    if len(missingNames) > 0:
        details = "missing daughter"
        if len(missingNames) > 1:
            details += "s "
        details += "[" + ", ".join(missingNames) + "]"
        result['missingDaughter'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['missingDaughter'] += [TestResultNamed(testName, TestResult.Passed)]

    return result

def replicaVolumes(referenceRV, otherRV, tests, recursive=True, includeAllTestResults=False, testsAlreadyDone=[]):
    result = ComparisonResult()

    rrv = referenceRV
    orv = otherRV

    testName = ": ".join(["(rv)", rrv.name])

    if tests.names:
        result += _names("replicaVolumeName", rrv.name, orv.name, testName, includeAllTestResults)

    # check type
    if rrv.type != orv.type:
        details = "replica types in '" + rrv.name + "': (ref): " + str(rrv.type)
        details += ", (other): " + str(orv.type)
        result['replicaType'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['replicaType'] += [TestResultNamed(testName, TestResult.Passed)]

    # replica's logical volume
    result += logicalVolumes(rrv.logicalVolume, orv.logicalVolume, tests, recursive, includeAllTestResults, testsAlreadyDone)

    # axis of replication
    if rrv.axis != orv.axis:
        details = "replica axis in '" + rrv.name + "': (ref): " + str(rrv.GetAxisName())
        details += ", (other): " + str(orv.GetAxisName())
        result['replicaAxis'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['replicaAxis'] += [TestResultNamed(testName, TestResult.Passed)]

    # n replicas
    if rrv.nreplicas != orv.nreplicas:
        details = "replica N replicas in '" + rrv.name + "': (ref): " + str(rrv.nreplicas)
        details += ", (other): " + str(orv.nreplicas)
        result['replicaNReplicas'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['replicaNReplicas'] += [TestResultNamed(testName, TestResult.Passed)]

    # width
    if rrv.width != orv.width:
        details = "replica width in '" + rrv.name + "': (ref): " + str(rrv.width)
        details += ", (other): " + str(orv.width)
        result['replicaWidth'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['replicaWidth'] += [TestResultNamed(testName, TestResult.Passed)]

    # offset
    if rrv.offset != orv.offset:
        details = "replica offset in '" + rrv.name + "': (ref): " + str(rrv.offset)
        details += ", (other): " + str(orv.offset)
        result['replicaOffset'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['replicaOffset'] += [TestResultNamed(testName, TestResult.Passed)]

    # w unit
    if rrv.wunit != orv.wunit:
        details = "replicaWUnit in '" + rrv.name + "': (ref): " + str(rrv.wunit)
        details += ", (other): " + str(orv.wunit)
        result['replicaWUnit'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['replicaWUnit'] += [TestResultNamed(testName, TestResult.Passed)]

    # o unit
    if rrv.ounit != orv.ounit:
        details = "replicaOUnit '" + rrv.name + "': (ref): " + str(rrv.ounit)
        details += ", (other): " + str(orv.ounit)
        result['replicaOUnit'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['replicaOunit'] += [TestResultNamed(testName, TestResult.Passed)]

    testsAlreadyDone.append( ("rv_test_"+rrv.name, "rv_test_"+orv.name) )
        
    return result

def divisionVolumes(referenceRV, otherRV, tests, includeAllTestResults=False, testsAlreadyDone=[]):
    result = ComparisonResult()
    return result

def parameterisedVolumes(referenceRV, otherRV, tests, includeAllTestResults=False, testsAlreadyDone=[]):
    result = ComparisonResult()
    return result

def materials(referenceMaterial, otherMaterial, tests, lvName="", includeAllTestResults=False, testsAlreadyDone=[]):
    """
    This tests assumes both referenceMaterial and otherMaterial are derived from the 
    type pyg4ometry.geant4._Material.Material.

    Compares, name, classname, density, n components
    """
    result = ComparisonResult()

    rm = referenceMaterial
    om = otherMaterial

    testName = ": ".join(list(filter(None, [lvName, "(material)", rm.name])))

    if tests.names:
        result += _names("materialName", rm.name, om.name, testName, includeAllTestResults)

    if tests.materialClassType:
        if type(om) != type(rm):
            details = "material type: (reference): "+str(type(rm))+", (other): "+str(type(om))
            result['materialType'] += [TestResultNamed(testName, TestResult.Failed, details)]
        elif includeAllTestResults:
            result['materialType'] += [TestResultNamed(testName, TestResult.Passed)]

    if rm.type == "nist" or om.type == "nist":
        if includeAllTestResults:
            result['materialDensity'] += [TestResultNamed(testName, TestResult.NotTested)]
            result['materialNComponents'] += [TestResultNamed(testName, TestResult.NotTested)]
            result['materialComponentType'] += [TestResultNamed(testName, TestResult.NotTested)]
            result['materialComponentMassFraction'] += [TestResultNamed(testName, TestResult.NotTested)]
        result.result = result.result | TestResult.Passed
        return result

    # density
    dDensity = om.density - rm.density
    if dDensity != 0: # avoid zero division
        if abs(dDensity / rm.density) > tests.toleranceMaterialDensityFraction:
            details = "density: (reference): "+str(rm.density)+", (other): "+str(om.density)
            result['materialDensity'] += [TestResultNamed(testName, TestResult.Failed, details)]
        elif includeAllTestResults:
            result['materialDensity'] += [TestResultNamed(testName, TestResult.Passed)]
            
    # n components of material
    if om.number_of_components != rm.number_of_components:
        details = "# components: (reference): "+str(rm.number_of_components)
        details += ", (other): "+str(om.number_of_components)
        result['materialNComponents'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['materialNComponents'] += [TestResultNamed(testName, TestResult.Passed)]
            
    # components and fractions
    if om.number_of_components == rm.number_of_components:
        for i in range(rm.number_of_components):
            rc, oc = rm.components[i], om.components[i]
            # we expect these each to be a tuple of (object, number, "type of fraction"

            # we don't test component names as this doesn't matter if they're functionally
            # the same as judged by other parameters.

            # component type
            rComponentType, oComponentType = rc[2], oc[2]
            if rComponentType != oComponentType:
                if tests.materialCompositionType:
                    details =  "material component type: (reference): "+str(rComponentType)
                    details += ", (other): "+str(oComponentType)
                    result['materialComponentType'] += [TestResultNamed(testName, TestResult.Failed, details)]
                break # we can't possibly make a more detailed comparison now
            elif includeAllTestResults:
                result['materialComponentType'] += [TestResultNamed(testName, TestResult.Passed)]
                
            # component fraction
            rFrac, oFrac = rc[1], oc[1]
            if rComponentType == "natoms":
                # integer comparison
                if rFrac != oFrac:
                    details =  "natoms: component (i): "+str(i)+", named: "+str(rc[0].name)
                    details += ": (reference): "+str(rFrac)+", (other): "+str(oFrac)
                    result['materialComponentNAtoms'] += [TestResultNamed(testName, TestResult.Failed, details)]
                elif includeAllTestResults:
                    result['materialComponentNAtoms'] += [TestResultNamed(testName, TestResult.Passed)]
            else:
                # fractional float comparison
                dFrac = oFrac - rFrac
                if dFrac != 0: # avoid zero division
                    if abs(dFrac / rFrac) > tests.toleranceMaterialMassFraction:
                        details =  "mass fraction: component (i): "+str(i)+", named: "+str(rc[0].name)
                        details += ": (reference): "+str(rFrac)+", (other): "+str(oFrac)
                        result['materialComponentMassFraction'] += [TestResultNamed(testName, TestResult.Failed, details)]
                elif includeAllTestResults:
                    result['materialComponentMassFraction'] += [TestResultNamed(testName, TestResult.Passed)]

            # components themselves
            if type(rc[0]) is _Material:
                result += materials(rc[0], oc[0], tests, lvName, includeAllTestResults)
            elif type(rc[0]) is _Element:
                result += _elements(rc[0], oc[0], tests, lvName, includeAllTestResults)
            else:
                print(type(rc))

    result.result = result.result | TestResult.Passed
    return result

def _elements(referenceElement, otherElement, tests, lvName="", includeAllTestResults=False):
    result = ComparisonResult()

    re = referenceElement
    oe = otherElement

    testName = ": ".join(list(filter(None, [lvName, re.name])))
    
    if tests.names:
        result += _names("elementName", re.name, oe.name, lvName, includeAllTestResults)

    if re.type != oe.type:
        details = "element type: (reference): "+str(re.type)+", (other): "+str(oe.type)
        result['elementType'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['elementType'] += [TestResultNamed(testName, TestResult.Passed)]

    if re.type == oe.type:
        # can only do comparison if they're the same type
        if re.type == "simple":
            # compare A
            if re.A != re.A:
                details = "element A: (reference): "+str(re.A)+", (other): "+str(oe.A)
                result['elementA'] += [TestResultNamed(testName, TestResult.Failed, details)]
            elif includeAllTestResults:
                result['elementA'] += [TestResultNamed(testName, TestResult.Passed)]
            # compare Z
            if re.Z != re.Z:
                details = "element Z: (reference): "+str(re.Z)+", (other): "+str(oe.Z)
                result['elementZ'] += [TestResultNamed(testName, TestResult.Failed, details)]
            elif includeAllTestResults:
                result['elementZ'] += [TestResultNamed(testName, TestResult.Passed)]

        elif re.type == "composite":
            if re.n_comp != re.n_comp:
                details = "element n_comp: (reference): "+str(re.n_comp)+", (other): "+str(oe.n_comp)
                result['elementNComp'] += [TestResultNamed(testName, TestResult.Failed, details)]
            elif includeAllTestResults:
                result['elementNComp'] += [TestResultNamed(testName, TestResult.Passed)]

        else:
            pass
    result.result = result.result | TestResult.Passed
    return result

def solids(referenceSolid, otherSolid, tests, lvName="", includeAllTestResults=False):
    """
    """
    result = ComparisonResult()

    rso = referenceSolid
    oso = otherSolid

    testName = ": ".join(list(filter(None, [lvName, rso.name])))
    
    if tests.names:
        result += _names("solidName", rso.name, oso.name, lvName, includeAllTestResults)
        
    if tests.solidExact:
        # solid type
        if rso.type != oso.type:
            details = "solid type: (reference): "+str(rso.type)
            result['solidExactType'] += [TestResultNamed(testName, TestResult.Failed, details)]
        elif includeAllTestResults:
            result['solidExactType'] += [TestResultNamed(testName, TestResult.Passed)]

        if rso.type == oso.type:
            # can only compare variables if they're the same type
            for var in _excludeUnits(rso.varNames):
                rv = _evaluateToFloat(rso.registry, getattr(rso, var))
                ov = _evaluateToFloat(oso.registry, getattr(oso, var))
                problem = False

                def CheckDiff(v1,v2):
                    """Compare two floats."""
                    dv = v2 - v1
                    nonlocal problem
                    aDifference = dv != 0
                    if aDifference:
                        problem = problem or ((dv / v1) > tests.toleranceSolidParameterFraction)

                def ProblemLength(v1,v2):
                    """Report if length of iterable list or tuple is different."""
                    nonlocal problem
                    nonlocal result
                    if len(v1) != len(v2):
                        problem = True
                        details = "solid parameter '" + var + "': (reference): " + str(rv) + ", (other): " + str(ov)
                        result['solidExactParameter'] += [TestResultNamed(testName, TestResult.Failed, details)]
                        return True
                    else:
                        return False

                def CheckVar(br,bo):
                    """Recursively check values in list structures."""
                    if type(br) in (float, int):
                        CheckDiff(br, bo)
                    elif type(br) in (list, tuple):
                        if ProblemLength(rv, ov):
                            return
                        for bri, boi in zip(br, bo):
                            CheckVar(bri, boi)
                # do the check
                CheckVar(rv, ov)

                if problem:
                    details = "solid parameter '"+var+"': (reference): "+str(rv)+", (other): "+str(ov)
                    result['solidExactParameter'] += [TestResultNamed(testName, TestResult.Failed, details)]
                elif includeAllTestResults:
                    result['solidExactParameter'] += [TestResultNamed(testName, TestResult.Passed)]
    elif includeAllTestResults:
        result['solidExactType'] += [TestResultNamed(testName, TestResult.NotTested)]

    result.result = result.result | TestResult.Passed
    return result

def _excludeUnits(varNamesList):
    toExclude = ("lunit", "aunit")
    result = [v for v in varNamesList if v not in toExclude]
    return result

def _names(testName, str1, str2, parentName="", includeAllTestResults=False):
    result = ComparisonResult()

    nameTest = str1 == str2
    if not nameTest:
        details = "'"+str1+"' != '"+str2+"'"
        result[testName] = [TestResultNamed(": ".join(list(filter(None, [parentName, str1]))), TestResult.Failed, details)]
    elif includeAllTestResults:
        result[testName] = [TestResultNamed(": ".join(list(filter(None, [parentName, str1]))), TestResult.Passed)]

    result.result = result.result | TestResult.Passed
    return result

def _vector(vectortype, r1, r2, tests, parentName="", includeAllTestResults=False):
    result = ComparisonResult()

    tols = {'rotation' : tests.toleranceRotationFraction,
            'position' : tests.toleranceTranslationFraction,
            'scale'    : tests.toleranceScaleFraction}
    tolerance = tols[vectortype]
    
    for v in ['x','y','z']:
        rc, oc = float(getattr(r1,v)), float(getattr(r2,v))
        drc = oc - rc
        if drc != 0:
            if abs((drc / rc)) > tolerance:
                details = v+": (reference): "+str(rc)+", (other): "+str(oc)
                result[vectortype] += [TestResultNamed(": ".join(list(filter(None, [parentName, r1.name]))), TestResult.Failed, details)]
            elif includeAllTestResults:
                result[vectortype] += [TestResultNamed(": ".join(list(filter(None, [parentName, r1.name]))), TestResult.Passed)]
    
    return result

def _copyNumber(pvname, c1, c2, tests, includeAllTestResults=False):
    result = ComparisonResult()

    if c1 != c2:
        details = "copy number: (reference): "+str(c1)+", (other): "+str(c2)
        result['copyNumber'] += [TestResultNamed(pvname, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['copyNumber'] += [TestResultNamed(pvname, TestResult.Passed)]
    
    return result

def _meshes(lvname, referenceMesh, otherMesh, tests):
    result = ComparisonResult()

    rm = referenceMesh
    om = otherMesh
    
    if tests.shapeExtent:
        if rm and om:
            # can only compare if meshes exist
            [rmMin, rmMax] = rm.getBoundingBox()
            [omMin, omMax] = om.getBoundingBox()
            for i in range(3):
                dMin = omMin[i] - rmMin[i]
                if dMin != 0:
                    if abs(dMin / rmMin[i]) > tests.toleranceSolidExtentFraction:
                        details =  "axis-aligned bounding box lower edge: component i: "+str(i)
                        details += ", (reference): "+str(omMin[i])+", (other): "+str(omMin[i])
                        result['shapeExtentBoundingBoxMin'] += [TestResultNamed(lvname, TestResult.Failed, details)]
                dMax = omMax[i] - rmMax[i]
                if dMax != 0:
                    if abs(dMax / rmMax[i]) > tests.toleranceSolidExtentFraction:
                        details =  "axis-aligned bounding box upper edge: component i: "+str(i)
                        details += ", (reference): "+str(omMax[i])+", (other): "+str(omMax[i])
                        result['shapeExtentBoundingBoxMax'] += [TestResultNamed(lvname, TestResult.Failed, details)]
            # no include all tests here as just too many
            result.result = result.result | TestResult.Passed
        else:
            # explicitly flag as we were meant to test but can't
            result['shapeExtent'] += [TestResultNamed(lvname, TestResult.NotTested, "no meshes")]

    if tests.shapeVolume:
        if rm and om:
            # can only compare if meshes exist
            # TODO can't see any method on meshes to calculate this
            #result.result = result.result | TestResult.Passed
            pass
        else:
            # explicitly flag as we were meant to test but can't
            result['shapeVolume'] += [TestResultNamed(lvname, TestResult.NotTested, "no meshes")]

    return result

def registries(reference, other):
    print("not implemented yet")
    pass