try:
    from .EditorWindow import *
    from .ModelGeant4 import *
    from .VtkWidget import *
except ImportError:
    print("Need PyQt5")

# from .MainWindow import *
# from .QVTKRenderWindowInteractor import *
# from .GeometryModel import *
