============
Installation
============


Requirements
------------

pyg4ometry is developed exclusively for Python 3 (Python2 is deprecated). It is developed on Python 3.9 and 3.10.


 * `VTK (Visualisation toolkit) <https://vtk.org>`_ (including Python bindings)
 * `antlr4 <https://www.antlr.org>`_
 * `cython <https://cython.org>`_
 * `CGAL <https://www.cgal.org>`_
 * `pybind11 <https://pybind11.readthedocs.io/en/stable/>`_
 * `OpenCASCADE <https://dev.opencascade.org>`_

Packages that are required but will be found through PIP automatically:

 * matplotlib
 * GitPython
 * vtk
 * pandas
 * pypandoc
 * networkx
 * numpy
 * sympy
 * pygltflib
 * testtools
 * importlib-resources
 * antlr4
 * configparser

**Optional**

 * `ROOT  <https://root.cern.ch>`_ for ROOT geometry loading

.. note:: A full list can be found in :code:`pyg4ometry/setup.py`.

.. note:: if you are choosing a python version, it is worth choosing according to which
	  version VTK provides a python build of through PIP if you use that. See
	  https://pypi.org/project/vtk/#files  For example, there are limited builds
	  for M1 Mac (ARM64).


Installation
------------

To install pyg4ometry, simply run::

  pip install pyg4ometry

To install from source::

  git clone https://github.com/g4edge/pyg4ometry.git
  cd pyg4ometry
  pip install .

If an editable version needs to be installed (i.e if you are a developer)::

  git clone https://github.com/g4edge/pyg4ometry.git
  cd pyg4ometry
  pip install --editable .

Docker image
------------
1. Download and install `Docker desktop <https://www.docker.com/products/docker-desktop>`_
2. open a terminal (linux) or cmd (windows)
3. (windows) Start `Xming <https://sourceforge.net/projects/xming/>`_ or `Vxsrv <https://sourceforge.net/projects/vcxsrv/>`_

An image can be obtained from docker::

  docker pull pyg4ometry:latest

Another possibility is to download the `pyg4ometry docker file <https://bitbucket.org/jairhul/pyg4ometry/raw/82373218033874607f682a77be33e03d5b6706aa/docker/Dockerfile-ubuntu-pyg4ometry>`_ and build the image::

  docker build -t ubuntu-pyg4ometry -f Dockerfile-ubuntu-pyg4ometry .

If you need to update increment the variable ``ARG PYG4OMETRY_VER=1``

To start the container

#. open a terminal (linux/mac) or cmd (windows)
#. get your IP address ``ifconfig`` (linux/mac) or ``ipconfig /all`` (windows)
#. Start XQuartz (mac) or Xming/Vxsrv (windows). For Xming/Vxsrv (might need to play with the settings when launching)
#. ``docker run -ti -v /tmp/.X11-unix:/tmp/.X11-unix -v YOURWORKDIR:/tmp/Physics -e DISPLAY=YOUR_IP ubuntu-pyg4ometry`` (the ``-v /tmp/.X11-unix:/tmp/.X11-unix`` is only required for mac/linux)

Test the installation::

  docker> cd pyg4ometry/pyg4ometry/test/pythonGeant4/
  docker> ipython
  python> import pyg4ometry
  python> import T001_Box
  python> T001_Box.Test(True,True)

There is the possibility of problems with X windows. An alternative is to install X windows to VNC so
the x windows are forwarded to a VNC connection.
