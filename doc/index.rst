.. _o2sclpy:

O\ :sub:`2`\ sclpy: v0.926.a1
=============================

O\ :sub:`2`\ sclpy principally consists of a python interface to the
C++ library :ref:`O2scl <o2scl>` and a high-level plotting script,
``o2graph``, for quick `matplotlib <https://matplotlib.org>`_ or `yt
<https://yt-project.org/>`_ plots from the command-line.

.. warning:: This python library is experimental and still under
	     development.

Installation and Requirements
-----------------------------

O\ :sub:`2`\ sclpy requires an installation of the development version
of O\ :sub:`2`\ scl. The release version, O\ :sub:`2`\ sclpy 0.925,
requires the O\ :sub:`2`\ scl v0.925 release from
<https://github.com/awsteiner/o2scl/releases/tag/v0.925> and the
development version, O\ :sub:`2`\ sclpy 0.926a1, requires that the
most recent version of O\ :sub:`2`\ scl from the master branch on
github is installed on your machine.

The python associated with O\ :sub:`2`\ sclpy can be installed with
e.g. ``pip3 install o2sclpy``. If you want to install the development
version (v0.926a1), you can clone the git repository, change directory
to the O\ :sub:`2`\ sclpy directory, and then use e.g. ``pip3 install
.`` if you want to use the pip package manager or ``python3 setup.py
install`` to do a direct installation. O\ :sub:`2`\ sclpy requires
python3 packages `requests <https://pypi.org/project/requests/>`_,
`h5py <https://www.h5py.org/>`_, `numpy <https://www.numpy.org>`_, and
`matplotlib <https://matplotlib.org>`_. O\ :sub:`2`\ sclpy also
assumes LaTeX is installed on your system.

O\ :sub:`2`\ sclpy dynamically loads the O\ :sub:`2`\ scl libraries
using the :class:`o2sclpy.linker` python class. This class may require
some additional information about your system in order to perform the
dynamic loading properly. See :ref:`link` for more details.

Contents
--------

.. toctree::
   :maxdepth: 2

   licensing
   link
   cpp
   base
   part
   nuclei
   eos
   o2graph
   yt
   plot_ref
   class_plotter
   class_hdf5_reader
   class_cloud_file
   class_plot_base
   class_yt_plot_base
   class_o2graph_plotter
   other
   todos

--------------------------------------------------------------

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

