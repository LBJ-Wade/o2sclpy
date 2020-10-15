#  -------------------------------------------------------------------
#  
#  Copyright (C) 2006-2020, Andrew W. Steiner
#  
#  This file is part of O2sclpy.
#  
#  O2sclpy is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  O2sclpy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with O2sclpy. If not, see <http://www.gnu.org/licenses/>.
#  
#  -------------------------------------------------------------------
#
# O2sclpy is a library of classes and functions which integrates
# O2scl, python, and matplotlib. The principal purpose of the library
# is to provide a script named 'o2graph', which allows fast analysis
# and plotting of HDF5 files (especially those generated by O2scl).
#

version='0.925a1'
"""
The version number string
"""

from o2sclpy.doc_data import cmaps, new_cmaps, base_list
from o2sclpy.doc_data import extra_types, extra_list, param_list
from o2sclpy.doc_data import yt_param_list
from o2sclpy.slack import slack_notify
from o2sclpy.cloud_file import cloud_file
from o2sclpy.hdf5 import hdf5_reader
from o2sclpy.link_o2scl import build_o2scl, link_o2scl, link_o2scl_part
from o2sclpy.utils import force_bytes, default_plot, get_str_array
from o2sclpy.utils import parse_arguments, string_to_dict, terminal
from o2sclpy.plot_base import plot_base
from o2sclpy.plotter import plotter
from o2sclpy.o2graph_plotter import o2graph_plotter
from o2sclpy.plot_info import marker_list, markers_plot, colors_near
from o2sclpy.plot_info import cmap_list_func, cmaps_plot, xkcd_colors_list
from o2sclpy.plot_info import colors_plot
from o2sclpy.part import init_part_pointers

class todo_list:
    """

    Todo list:

    .. todo:: Allow the user to name and list axes to ensure less
       confusion when adding, e.g. insets to subplots
    .. todo:: an example of a cube plot like Raph(?) showed, where
       three density plots are shown on the xy xz and yz planes
       in combination with a volume rendering.
    .. todo:: an example of more complicated yt annotations
    .. todo:: finish the 'moveauto' path in yt_render()
    .. todo:: create a vector field command in yt
    .. todo:: allow the creation of colormaps on the fly? 
    .. todo:: add map to colormap option for yt tf's
    .. todo:: Create a system of protected variables and functions using
       underscores and also create a __repr__() object
    .. todo:: Create a plot_base_yt class in between plot_base
       and o2graph_plotter?
    .. todo:: Ensure yt uses self.font for text objects?
    .. todo:: Finish den-plot-anim for a tensor_grid objects
    .. todo:: plot-set for a table3d object to create 
       a sequence of curves for each column or row, or maybe 
       do this as a 'mult-vector-spec'?
    .. todo:: Simplify some of the larger functions like 
       o2graph_plotter::plot(), possibly by creating a separate
       function for each type?
    .. todo:: Ensure the 'clf' command clears the yt objects?
    .. todo:: More yt-path options
    .. todo:: Anti-alias text objects in yt (also anti-alias line 
       sources?)
    
    """

    def empty_class():
        print(' ')


