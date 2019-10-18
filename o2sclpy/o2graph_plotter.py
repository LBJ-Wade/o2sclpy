#  -------------------------------------------------------------------
#  
#  Copyright (C) 2006-2019, Andrew W. Steiner
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

import math
import os
import sys
import ctypes
import numpy

import matplotlib.pyplot as plot

# For system type detection
import platform

# For wrapping help text
import textwrap

# For code.interact() in 'python' command
import code 

# For rectangles
import matplotlib.patches as patches

from o2sclpy.doc_data import cmaps, new_cmaps, base_list
from o2sclpy.doc_data import extra_types, extra_list, param_list
from o2sclpy.doc_data import yt_param_list
from o2sclpy.utils import parse_arguments, string_to_dict
from o2sclpy.utils import force_bytes, default_plot, get_str_array
from o2sclpy.plot_base import plot_base

class o2graph_plotter(plot_base):
    """
    A plotting class for the o2graph script. This class is a child of the
    :py:class:`o2sclpy.plot_base` class.

    This class is not necessarily intended to be instantiated by the 
    end user. 

    Todo list:
     
    .. todo:: Move code out of parse_string_list() to separate functions
    .. todo:: Simplify some of the larger functions like plot()
    .. todo:: Simplify this class somehow to make the source file smaller,
       possibly by separating out the yt part or moving the o2scl
       integration somewhere else
    .. todo:: Create a default volume in yt-scatter if one hasn't already
       been specified
    .. todo:: Allow the user to modify sigma_clip
    .. todo:: Fix colors and sizes for yt-scatter
    .. todo:: Finish setting up -set yt_resolution so it parses the
       two numerical values
    .. todo:: Move yt-axis to a command so that we can place the
       axis at an arbitrary location in either coordinate system.
       This would also allow removing all the yt_axis parameters.
    .. todo:: Ensure the 'clf' command clears the yt objects
    .. todo:: Create a list of yt objects so that we can manipulate them
       in the middle of an animation
    .. todo:: Figure out how to place 2d plot elements on top of the render
    .. todo:: Figure out how to allow user to specify focus and position in
       both coordinate systems
    .. todo:: Create yt-box command for BoxSource
    .. todo:: More yt-path options
    .. todo:: Create yt-surface
    .. todo:: Anti-aliasing the axis would be nice
    
    """

    yt_scene=0
    """ 
    The yt scene object
    """
    yt_created_scene=False
    """
    If true, then the yt scene object has been created
    """
    yt_camera=0
    """ 
    The yt camera object
    """
    yt_created_camera=False
    """
    If true, then the yt camera object has been created
    """

    def yt_create_scene(self):
        """
        Create the yt scene object and set yt_created_scene to True
        """
        from yt.visualization.volume_rendering.api import Scene
        print('o2graph_plotter:yt_create_scene(): Creating scene.')
        self.yt_scene=Scene()
        self.yt_created_scene=True
        
    def yt_create_camera(self,ds):
        """
        Create the yt camera object using the class variables
        ``yt_resolution``, ``yt_position``, and ``yt_focus``, with a
        camera width based on the domain width of ``ds``.
        """
        print('o2graph_plotter:yt_create_camera(): Creating camera.')
        self.yt_camera=self.yt_scene.add_camera()
        self.yt_camera.resolution=self.yt_resolution
        self.yt_camera.width=1.5*ds.domain_width[0]
        self.yt_camera.position=self.yt_position
        self.yt_camera.focus=self.yt_focus
        self.yt_camera.north_vector=[0.0,0.0,1.0]
        self.yt_camera.switch_orientation()
        self.yt_created_camera=True
    
    def yt_text_to_points(self,veco,vecx,vecy,text,alpha=0.5,font=20,
                          show=False):
        """
        Take three 3D vectors 'veco' (origin), 'vecx' (x direction) and
        'vecy' (y direction), and a string of text ('text'), and
        return a numpy array of shape (6,npoints) which has entries
        (x,y,z,r,g,b). The values r, g, and b are between 0 and 1.

        """
        fig, axes = plot.subplots()
        plot.rc('text',usetex=True)
        axes.text(0.5,0.5,text,fontsize=font,ha='center',va='center')
        plot.axis('off')
        fig.canvas.draw()
        if show:
            plot.show()
        X=numpy.array(fig.canvas.renderer._renderer)
        Y=[]
        Y2=[]
        for i in range(0,480):
            for j in range(0,640):
                if X[i,j,0]!=255 or X[i,j,1]!=255 or X[i,j,2]!=255:
                    xold=(i-240)/240.0
                    yold=(j-320)/320.0
                    vecnew=[veco[0]-vecy[0]*xold+vecx[0]*yold,
                            veco[1]-vecy[1]*xold+vecx[1]*yold,
                            veco[2]-vecy[2]*xold+vecx[2]*yold]
                    Y.append([vecnew[0],vecnew[1],vecnew[2]])
                    Y2.append([1.0-X[i,j,0]/255.0,1.0-X[i,j,1]/255.0,
                               1.0-X[i,j,2]/255.0,alpha])
        return(numpy.array(Y),numpy.array(Y2))

    def yt_text_to_scene(self,loc,text,scale=0.6,
                         keyname='o2graph_text'):
        """
        At location 'loc' put text 'text' into the scene using
        specified scale parameter and keyname.
        """
        
        # Imports
        from yt.visualization.volume_rendering.api \
            import PointSource
        
        # Construct orientation vectors
        view_y=self.yt_camera.north_vector
        view_x=-numpy.cross(view_y,self.yt_camera.focus-
                         self.yt_camera.position)
        # Normalize view_x and view_y
        view_x=view_x/numpy.sqrt(view_x[0]**2+view_x[1]**2+view_x[2]**2)
        view_y=view_y/numpy.sqrt(view_y[0]**2+view_y[1]**2+view_y[2]**2)
    
        # Choose scale
        view_x=view_x*scale
        view_y=view_y*scale
        
        # Convert text to points
        (Y,Y2)=self.yt_text_to_points(loc,view_x,view_y,text)
    
        # Add the point source
        points_xalabels=PointSource(Y,colors=Y2)
        self.yt_scene.add_source(points_xalabels,keyname=keyname)

    def yt_plot_axis(self,origin=[0.0,0.0,0.0],color=[1.0,1.0,1.0,0.5],
                     ihat=[1.0,0.0,0.0],jhat=[0.0,1.0,0.0],
                     khat=[0.0,0.0,1.0]):

        print('o2graph_plotter:yt_plot_axis(): Adding axis.')
        
        # Imports
        from yt.visualization.volume_rendering.api \
            import PointSource, LineSource
        
        # Point at origin
        vertex_origin=numpy.array([origin])
        color_origin=numpy.array([color])
        points=PointSource(vertex_origin,colors=color_origin,radii=3)
        self.yt_scene.add_source(points,keyname='o2graph_origin')
    
        # Axis lines
        vertices_axis=numpy.array([[origin,ihat],
                                   [origin,jhat],
                                   [origin,khat]])
        colors_axis=numpy.array([color,color,color])
        axis=LineSource(vertices_axis,colors_axis)
        self.yt_scene.add_source(axis,keyname='o2graph_axis_lines')
        
        # Arrow heads
        list2=[]
        clist2=[]
        for theta in range(0,20):
            for z in range(0,10):
                xloc=1.0-z/200.0
                r=z/800.0
                yloc=r*math.cos(theta/10.0*math.pi)
                zloc=r*math.sin(theta/10.0*math.pi)
                list2.append([[1,0,0],[xloc,yloc,zloc]])
                yloc=1.0-z/200.0
                r=z/800.0
                xloc=r*math.cos(theta/10.0*math.pi)
                zloc=r*math.sin(theta/10.0*math.pi)
                list2.append([[0,1,0],[xloc,yloc,zloc]])
                zloc=1.0-z/200.0
                r=z/800.0
                xloc=r*math.cos(theta/10.0*math.pi)
                yloc=r*math.sin(theta/10.0*math.pi)
                list2.append([[0,0,1],[xloc,yloc,zloc]])
                clist2.append(color)
                clist2.append(color)
                clist2.append(color)
        points_aheads2=LineSource(numpy.array(list2),numpy.array(clist2))
        self.yt_scene.add_source(points_aheads2,keyname='o2graph_axis_arrows')
        
    def yt_check_backend(self):
        """
        For yt, check that we're using the Agg backend.
        """
        import matplotlib
        if (matplotlib.get_backend()!='Agg' and 
            matplotlib.get_backend()!='agg'):
            print('yt integration only works with Agg.')
            print('Current backend is',matplotlib.get_backend())
            return
    
    def set_wrapper(self,o2scl_hdf,amp,args):
        """
        Wrapper for :py:func:`o2sclpy.plot_base.set` which sets
        plot-related parameters and sends other parameters to
        ``acol_manager``
        """

        match=False
        for line in param_list:
            if args[0]==line[0]:
                match=True
                
        for line in yt_param_list:
            if args[0]==line[0]:
                match=True
                
        if match==True:
            self.set(args[0],args[1])

        # If we're modifying the verbose parameter, then make
        # sure both the o2graph and the acol version match. Otherwise,
        # if it's only an o2graph parameter, then just return.
        if (match==True and 
            force_bytes(args[0])!=b'verbose'):
            return
        
        str_args='-set'
        size_type=ctypes.c_int * (len(args)+1)
        sizes=size_type()
        sizes[0]=len('set')+1
            
        for i in range(0,len(args)):
            str_args=str_args+args[i]
            sizes[i+1]=len(args[i])
        ccp=ctypes.c_char_p(force_bytes(str_args))
    
        parse_fn=o2scl_hdf.o2scl_acol_parse
        parse_fn.argtypes=[ctypes.c_void_p,ctypes.c_int,
                           size_type,ctypes.c_char_p]
            
        parse_fn(amp,len(args)+1,sizes,ccp)

    def get_wrapper(self,o2scl_hdf,amp,args):
        """
        Wrapper for :py:func:`o2sclpy.plot_base.get` which
        gets plot-related parameters and gets other parameters
        from ``acol_manager``
        """
        match=False
        for line in param_list:
            if args[0]==line[0]:
                match=True

        for line in yt_param_list:
            if args[0]==line[0]:
                match=True
                
        if match==True:
            
            self.get(args[0])
                            
        else:
                        
            str_args='-get'
            size_type=ctypes.c_int * (len(args)+1)
            sizes=size_type()
            sizes[0]=len('get')+1
        
            for i in range(0,len(args)):
                str_args=str_args+args[i]
                sizes[i+1]=len(args[i])
            ccp=ctypes.c_char_p(force_bytes(str_args))
        
            parse_fn=o2scl_hdf.o2scl_acol_parse
            parse_fn.argtypes=[ctypes.c_void_p,ctypes.c_int,
                              size_type,ctypes.c_char_p]
        
            parse_fn(amp,len(args)+1,sizes,ccp)

    def gen_acol(self,o2scl_hdf,amp,cmd_name,args):
        """
        Run a general ``acol`` command named ``cmd_name`` with arguments
        stored in ``args``.
        """

        str_args='-'+cmd_name
        size_type=ctypes.c_int * (len(args)+1)
        sizes=size_type()
        sizes[0]=len(cmd_name)+1
        
        for i in range(0,len(args)):
            str_args=str_args+args[i]
            sizes[i+1]=len(args[i])
        ccp=ctypes.c_char_p(force_bytes(str_args))

        parse_fn=o2scl_hdf.o2scl_acol_parse
        parse_fn.argtypes=[ctypes.c_void_p,ctypes.c_int,
                           size_type,ctypes.c_char_p]
        
        parse_fn(amp,len(args)+1,sizes,ccp)

    def get_type(self,o2scl_hdf,amp):
        """
        Get the current O\ :sub:`2`\ scl object type
        """
        
        int_ptr=ctypes.POINTER(ctypes.c_int)
        char_ptr=ctypes.POINTER(ctypes.c_char)
        char_ptr_ptr=ctypes.POINTER(char_ptr)
        
        # Set up wrapper for type function
        type_fn=o2scl_hdf.o2scl_acol_get_type
        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]
        
        # Get current type
        it=ctypes.c_int(0)
        type_ptr=char_ptr()
        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
        curr_type=b''
        for i in range(0,it.value):
            curr_type=curr_type+type_ptr[i]
                        
        return curr_type
        
    def den_plot(self,o2scl_hdf,amp,args):
        """
        Density plot from a ``table3d``, ``hist_2d`` ``tensor_grid``,
        ``tensor``, ``tensor<int>`` or ``tensor<size_t>`` object
        """

        int_ptr=ctypes.POINTER(ctypes.c_int)
        double_ptr=ctypes.POINTER(ctypes.c_double)
        char_ptr=ctypes.POINTER(ctypes.c_char)
        double_ptr_ptr=ctypes.POINTER(double_ptr)
        char_ptr_ptr=ctypes.POINTER(char_ptr)

        # Set up wrapper for type function
        type_fn=o2scl_hdf.o2scl_acol_get_type
        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]

        # Get current type
        it=ctypes.c_int(0)
        type_ptr=char_ptr()
        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
        kwstring=''
                
        curr_type=b''
        for i in range(0,it.value):
            curr_type=curr_type+type_ptr[i]

        # Handle tensor and table3d types
        if (curr_type==b'tensor' or curr_type==b'tensor<size_t>' or
            curr_type==b'tensor_grid' or curr_type==b'tensor<int>' or
            curr_type==b'table3d'):

            # If the object is a tensor, convert to a table3d
            # object before plotting
            if curr_type!=b'table3d':
                index1=0
                index2=1
                if len(args)==1:
                    kwstring=args[0]
                if len(args)>=2:
                    index1=int(args[0])
                    index2=int(args[1])
                if len(args)>=3:
                    kwstring=args[2]
                if index1+index2!=1 and index1*index2!=0:
                    print('Indices must be "0 1" or "1 0" in',
                          'in den-plot.')
                    return
                    
                conv_fn=o2scl_hdf.o2scl_acol_tensor_to_table3d
                conv_fn.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
                conv_fn.restype=ctypes.c_int
                
                conv_ret=conv_fn(amp,index1,index2)
                if conv_ret!=0:
                    print('Automatic conversion to table3d failed.')
                    return
                slice_name="tensor"
            else:
                slice_name=args[0]
                if len(args)>=2:
                    kwstring=args[1]

            # Now that we are guaranteed to have a table3d
            # object to use, use that to create the density
            # plot
            get_fn=o2scl_hdf.o2scl_acol_get_slice
            get_fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                             int_ptr,double_ptr_ptr,
                             int_ptr,double_ptr_ptr,double_ptr_ptr]

            slice=ctypes.c_char_p(force_bytes(slice_name))
            nx=ctypes.c_int(0)
            ptrx=double_ptr()
            ny=ctypes.c_int(0)
            ptry=double_ptr()
            ptrs=double_ptr()
            get_fn(amp,slice,ctypes.byref(nx),ctypes.byref(ptrx),
                   ctypes.byref(ny),ctypes.byref(ptry),
                   ctypes.byref(ptrs))

            xgrid=[ptrx[i] for i in range(0,nx.value)]
            ygrid=[ptry[i] for i in range(0,ny.value)]
            stemp=[ptrs[i] for i in range(0,nx.value*ny.value)]
            stemp2=numpy.array(stemp)
            sl=stemp2.reshape(nx.value,ny.value)
            sl=sl.transpose()

            # If logz was specified, then manually apply the
            # log to the data. Alternatively, we should consider
            # using 'LogNorm' here, as suggested in
            
            #https://stackoverflow.com/questions/2546475/
            #how-can-i-draw-a-log-normalized-imshow-plot-
            #with-a-colorbar-representing-the-raw
            
            if self.logz==True:
                fail_found=False
                for i in range(0,ny.value):
                    for j in range(0,nx.value):
                        if sl[i][j]>0.0:
                            sl[i][j]=math.log10(sl[i][j])
                        else:
                            if fail_found==False:
                                print('Failed to take log of',sl[i][j],
                                      'at (i,j)=(',j,',',i,') or (',
                                      xgrid[j],',',ygrid[i],
                                      '). Setting point to zero and',
                                      'suppressing future warnings.')
                            fail_found=True
                            sl[i][j]=0.0
                                
            if self.logx==True:
                xgrid=[math.log(ptrx[i],10) for i in
                       range(0,nx.value)]
            if self.logy==True:
                ygrid=[math.log(ptry[i],10) for i in
                       range(0,ny.value)]

            # If the z range was specified, truncate all values
            # outside that range (this truncation is done after
            # the application of the log above)
            if self.zset==True:
                for i in range(0,ny.value):
                    for j in range(0,nx.value):
                        if sl[i][j]>self.zhi:
                            sl[i][j]=self.zhi
                        elif sl[i][j]<self.zlo:
                            sl[i][j]=self.zlo

            if self.canvas_flag==False:
                self.canvas()

            diffs_x=[xgrid[i+1]-xgrid[i] for i in range(0,len(xgrid)-1)]
            mean_x=numpy.mean(diffs_x)
            std_x=numpy.std(diffs_x)
            diffs_y=[ygrid[i+1]-ygrid[i] for i in range(0,len(ygrid)-1)]
            mean_y=numpy.mean(diffs_y)
            std_y=numpy.std(diffs_y)
            
            if std_x/mean_x>1.0e-4 or std_x/mean_x>1.0e-4:
                print('Warning in o2graph::o2graph_plotter::den_plot():')
                print('  Nonlinearity of x or y grid is greater than '+
                      '10^{-4}.')
                print('  Value of std(diff_x)/mean(diff_x): %7.6e .' %
                      (std_x/mean_x))
                print('  Value of std(diff_y)/mean(diff_y): %7.6e .' %
                      (std_y/mean_y))
                print('  The density plot may not be properly scaled.')
                
            extent1=xgrid[0]-(xgrid[1]-xgrid[0])/2
            extent2=xgrid[nx.value-1]+(xgrid[nx.value-1]-
                                       xgrid[nx.value-2])/2
            extent3=ygrid[0]-(ygrid[1]-ygrid[0])/2
            extent4=ygrid[ny.value-1]+(ygrid[ny.value-1]-
                                       ygrid[ny.value-2])/2
                        
            if len(kwstring)==0:
                self.last_image=self.axes.imshow(sl,interpolation='nearest',
                                    origin='lower',extent=[extent1,extent2,
                                                           extent3,extent4],
                                    aspect='auto')
            else:
                self.last_image=self.axes.imshow(sl,interpolation='nearest',
                                    origin='lower',extent=[extent1,extent2,
                                                           extent3,extent4],
                                    aspect='auto',**string_to_dict(kwstring))

            # The color bar is added later below...

            # End of section for tensor types and table3d
        elif curr_type==b'hist_2d':

            get_fn=o2scl_hdf.o2scl_acol_get_hist_2d
            get_fn.argtypes=[ctypes.c_void_p,int_ptr,double_ptr_ptr,
                             int_ptr,double_ptr_ptr,double_ptr_ptr]

            nx=ctypes.c_int(0)
            ptrx=double_ptr()
            ny=ctypes.c_int(0)
            ptry=double_ptr()
            ptrs=double_ptr()
            get_fn(amp,ctypes.byref(nx),ctypes.byref(ptrx),
                   ctypes.byref(ny),ctypes.byref(ptry),
                   ctypes.byref(ptrs))

            xgrid=[ptrx[i] for i in range(0,nx.value)]
            ygrid=[ptry[i] for i in range(0,ny.value)]
            stemp=[ptrs[i] for i in range(0,nx.value*ny.value)]
            stemp2=numpy.array(stemp)
            sl=stemp2.reshape(nx.value,ny.value)
            sl=sl.transpose()

            if self.logx==True:
                xgrid=[math.log(ptrx[i],10) for i in
                       range(0,nx.value)]
            if self.logy==True:
                ygrid=[math.log(ptry[i],10) for i in
                       range(0,ny.value)]

            if self.zset==True:
                for i in range(0,ny.value):
                    for j in range(0,nx.value):
                        if sl[i][j]>self.zhi:
                            sl[i][j]=self.zhi
                        elif sl[i][j]<self.zlo:
                            sl[i][j]=self.zlo
                            
            if self.logz==True:
                for i in range(0,ny.value):
                    for j in range(0,nx.value):
                        sl[i][j]=math.log10(sl[i][j])
                        
            if self.canvas_flag==False:
                self.canvas()

            extent1=xgrid[0]-(xgrid[1]-xgrid[0])/2
            extent2=xgrid[nx.value-1]+(xgrid[nx.value-1]-
                                       xgrid[nx.value-2])/2
            extent3=ygrid[0]-(ygrid[1]-ygrid[0])/2
            extent4=ygrid[ny.value-1]+(ygrid[ny.value-1]-
                                       ygrid[ny.value-2])/2
                        
            if len(args)<1:
                self.last_image=self.axes.imshow(sl,interpolation='nearest',
                            origin='lower',extent=[extent1,extent2,
                                                   extent3,extent4],
                            aspect='auto')
            else:
                self.last_image=self.axes.imshow(sl,interpolation='nearest',
                            origin='lower',extent=[extent1,extent2,
                                                   extent3,extent4],
                            aspect='auto',**string_to_dict(args[0]))

            # The color bar is added later below...

            # End of section for type hist_2d
        else:
            print("Command 'den-plot' not supported for type",
                  curr_type,".")
            return

        if self.colbar==True:
            cbar=self.fig.colorbar(self.last_image,ax=self.axes)
            cbar.ax.tick_params(labelsize=self.font*0.8)

    def plot(self,o2scl_hdf,amp,args):
        """
        Plot a two-dimensional set of data
        """

        # Useful pointer types
        double_ptr=ctypes.POINTER(ctypes.c_double)
        char_ptr=ctypes.POINTER(ctypes.c_char)
        double_ptr_ptr=ctypes.POINTER(double_ptr)
        char_ptr_ptr=ctypes.POINTER(char_ptr)
        int_ptr=ctypes.POINTER(ctypes.c_int)
        
        # Set up wrapper for type function
        type_fn=o2scl_hdf.o2scl_acol_get_type
        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]

        # Get current type
        it=ctypes.c_int(0)
        type_ptr=char_ptr()
        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
        curr_type=b''
        for i in range(0,it.value):
            curr_type=curr_type+type_ptr[i]
                        
        if curr_type==b'table':
                            
            failed=False

            get_fn=o2scl_hdf.o2scl_acol_get_column
            get_fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                             int_ptr,double_ptr_ptr]
            get_fn.restype=ctypes.c_int

            colx=ctypes.c_char_p(force_bytes(args[0]))
            idx=ctypes.c_int(0)
            ptrx=double_ptr()
            get_ret=get_fn(amp,colx,ctypes.byref(idx),ctypes.byref(ptrx))
            if get_ret!=0:
                print('Failed to get column named "'+args[0]+'".')
                failed=True

            coly=ctypes.c_char_p(force_bytes(args[1]))
            idy=ctypes.c_int(0)
            ptry=double_ptr()
            get_ret=get_fn(amp,coly,ctypes.byref(idy),ctypes.byref(ptry))
            if get_ret!=0:
                print('Failed to get column named "'+args[1]+'".')
                failed=True

            if failed==False:
                xv=[ptrx[i] for i in range(0,idx.value)]
                yv=[ptry[i] for i in range(0,idy.value)]
        
                if self.canvas_flag==False:
                    self.canvas()
                if self.logx==True:
                    if self.logy==True:
                        if len(args)<3:
                            self.axes.loglog(xv,yv)
                        else:
                            self.axes.loglog(xv,yv,**string_to_dict(args[2]))
                    else:
                        if len(args)<3:
                            self.axes.semilogx(xv,yv)
                        else:
                            self.axes.semilogx(xv,yv,**string_to_dict(args[2]))
                else:
                    if self.logy==True:
                        if len(args)<3:
                            self.axes.semilogy(xv,yv)
                        else:
                            self.axes.semilogy(xv,yv,**string_to_dict(args[2]))
                    else:
                        if len(args)<3:
                            self.axes.plot(xv,yv)
                        else:
                            self.axes.plot(xv,yv,**string_to_dict(args[2]))

            # End of section for 'table' type
        elif curr_type==b'hist':

            get_reps_fn=o2scl_hdf.o2scl_acol_get_hist_reps
            get_reps_fn.argtypes=[ctypes.c_void_p,
                             int_ptr,double_ptr_ptr]
                            
            get_wgts_fn=o2scl_hdf.o2scl_acol_get_hist_wgts
            get_wgts_fn.argtypes=[ctypes.c_void_p,
                             int_ptr,double_ptr_ptr]
                            
            idx=ctypes.c_int(0)
            ptrx=double_ptr()
            get_reps_fn(amp,ctypes.byref(idx),
                        ctypes.byref(ptrx))

            idy=ctypes.c_int(0)
            ptry=double_ptr()
            get_wgts_fn(amp,ctypes.byref(idy),
                        ctypes.byref(ptry))

            xv=[ptrx[i] for i in range(0,idx.value)]
            yv=[ptry[i] for i in range(0,idy.value)]
    
            if self.canvas_flag==False:
                self.canvas()
            if self.logx==True:
                if self.logy==True:
                    if len(args)<1:
                        self.axes.loglog(xv,yv)
                    else:
                        self.axes.loglog(xv,yv,**string_to_dict(args[0]))
                else:
                    if len(args)<1:
                        self.axes.semilogx(xv,yv)
                    else:
                        self.axes.semilogx(xv,yv,**string_to_dict(args[0]))
            else:
                if self.logy==True:
                    if len(args)<1:
                        self.axes.semilogy(xv,yv)
                    else:
                        self.axes.semilogy(xv,yv,**string_to_dict(args[0]))
                else:
                    if len(args)<1:
                        self.axes.plot(xv,yv)
                    else:
                        self.axes.plot(xv,yv,**string_to_dict(args[0]))
                            
            # End of section for 'hist' type
        elif curr_type==b'prob_dens_mdim_amr':

            get_base_fn=o2scl_hdf.o2scl_acol_pdma_get_base
            get_base_fn.argtypes=[ctypes.c_void_p,int_ptr,
                                  int_ptr,double_ptr_ptr,double_ptr_ptr]
                            
            get_cube_fn=o2scl_hdf.o2scl_acol_pdma_get_cube
            get_cube_fn.argtypes=[ctypes.c_void_p,ctypes.c_int,
                                  double_ptr_ptr,double_ptr_ptr,
                                  double_ptr,double_ptr]
                            
            ndimx=ctypes.c_int(0)
            nx=ctypes.c_int(0)
            lowx=double_ptr()
            highx=double_ptr()
            get_base_fn(amp,ctypes.byref(ndimx),ctypes.byref(nx),
                        ctypes.byref(lowx),ctypes.byref(highx))

            dimx=int(args[0])
            dimy=int(args[1])

            self.xlo=lowx[dimx]
            self.ylo=lowx[dimy]
            self.xset=True
            self.xhi=highx[dimx]
            self.yhi=highx[dimy]
            self.yset=True

            if self.canvas_flag==False:
                self.canvas()

            # Need to figure out here how to convert fill function
            # to a value, keeping in mind it can depend on
            # fvy.value (fractional volume) or wy.value (weight)
                
            fill_fn='None'
            if len(args)>=3:
                fill_fn=args[2]
                
            print('Fill function',fill_fn)
                
            for i in range(0,nx.value):

                iy=ctypes.c_int(i)
                lowy=double_ptr()
                highy=double_ptr()
                fvy=ctypes.c_double(0.0)
                wy=ctypes.c_double(0.0)
                get_cube_fn(amp,iy,ctypes.byref(lowy),
                            ctypes.byref(highy),
                            ctypes.byref(fvy),
                            ctypes.byref(wy))
                
                left=lowy[dimx]
                lower=lowy[dimy]
                right=highy[dimx]
                upper=highy[dimy]
                w=right-left
                h=upper-lower

                if len(args)<4:
                    r=patches.Rectangle((left,lower),w,h,0.0,
                                        alpha=fvy.value)
                    self.axes.add_patch(r)
                else:
                    strtemp='alpha='+str(fvy.value)+','+args[3]
                    r=patches.Rectangle((left,lower),w,h,0.0,
                                        **string_to_dict(strtemp))
                    self.axes.add_patch(r)
                            
            # End of section for 'prob_dens_mdim_amr' type
        elif curr_type==b'vector<contour_line>':

            # Get the total number of contour lines
            cont_n_fn=o2scl_hdf.o2scl_acol_contours_n
            cont_n_fn.argtypes=[ctypes.c_void_p]
            cont_n_fn.restype=ctypes.c_int
            nconts=cont_n_fn(amp)

            # Define types for extracting each contour line
            cont_line_fn=o2scl_hdf.o2scl_acol_contours_line
            cont_line_fn.argtypes=[ctypes.c_void_p,ctypes.c_int,
                                   int_ptr,double_ptr_ptr,
                                   double_ptr_ptr]
            cont_line_fn.restype=ctypes.c_double

            if self.canvas_flag==False:
                self.canvas()

            # Loop over all contour lines
            for k in range(0,nconts):
                idx=ctypes.c_int(0)
                ptrx=double_ptr()
                ptry=double_ptr()
                lev=cont_line_fn(amp,k,ctypes.byref(idx),
                                 ctypes.byref(ptrx),ctypes.byref(ptry))
                xv=[ptrx[i] for i in range(0,idx.value)]
                yv=[ptry[i] for i in range(0,idx.value)]
                
                if self.logx==True:
                    if self.logy==True:
                        if len(args)<1:
                            self.axes.loglog(xv,yv)
                        else:
                            self.axes.loglog(xv,yv,**string_to_dict(args[0]))
                    else:
                        if len(args)<1:
                            self.axes.semilogx(xv,yv)
                        else:
                            self.axes.semilogx(xv,yv,**string_to_dict(args[0]))
                else:
                    if self.logy==True:
                        if len(args)<1:
                            self.axes.semilogy(xv,yv)
                        else:
                            self.axes.semilogy(xv,yv,**string_to_dict(args[0]))
                    else:
                        if len(args)<1:
                            self.axes.plot(xv,yv)
                        else:
                            self.axes.plot(xv,yv,**string_to_dict(args[0]))
            # End of section for 'vector<contour_line>' type
        else:
            print("Command 'plot' not supported for type",
                  curr_type,".")
            return
        
        if self.xset==True:
            self.axes.set_xlim(self.xlo,self.xhi)
        if self.yset==True:
            self.axes.set_ylim(self.ylo,self.yhi)
                                 
        # End of 'plot' function
                                 
    def rplot(self,o2scl_hdf,amp,args):
        """
        Plot a region inside a curve or in between two curves
        """

        # Useful pointer types
        double_ptr=ctypes.POINTER(ctypes.c_double)
        char_ptr=ctypes.POINTER(ctypes.c_char)
        double_ptr_ptr=ctypes.POINTER(double_ptr)
        char_ptr_ptr=ctypes.POINTER(char_ptr)
        int_ptr=ctypes.POINTER(ctypes.c_int)
        
        # Set up wrapper for type function
        type_fn=o2scl_hdf.o2scl_acol_get_type
        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]

        # Get current type
        it=ctypes.c_int(0)
        type_ptr=char_ptr()
        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
        curr_type=b''
        for i in range(0,it.value):
            curr_type=curr_type+type_ptr[i]
                        
        if curr_type==b'table':
                            
            failed=False

            get_fn=o2scl_hdf.o2scl_acol_get_column
            get_fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                             int_ptr,double_ptr_ptr]
            get_fn.restype=ctypes.c_int

            colx1=ctypes.c_char_p(force_bytes(args[0]))
            idx1=ctypes.c_int(0)
            ptrx1=double_ptr()
            get_ret=get_fn(amp,colx1,ctypes.byref(idx1),ctypes.byref(ptrx1))
            if get_ret!=0:
                print('Failed to get column named "'+args[0]+'".')
                failed=True

            coly1=ctypes.c_char_p(force_bytes(args[1]))
            idy1=ctypes.c_int(0)
            ptry1=double_ptr()
            get_ret=get_fn(amp,coly1,ctypes.byref(idy1),ctypes.byref(ptry1))
            if get_ret!=0:
                print('Failed to get column named "'+args[1]+'".')
                failed=True

            if failed==False:
                xv=[ptrx1[i] for i in range(0,idx1.value)]
                yv=[ptry1[i] for i in range(0,idy1.value)]
                
            if len(args)>3:
                colx2=ctypes.c_char_p(force_bytes(args[2]))
                idx2=ctypes.c_int(0)
                ptrx2=double_ptr()
                get_ret=get_fn(amp,colx2,ctypes.byref(idx2),ctypes.byref(ptrx2))
                if get_ret!=0:
                    print('Failed to get column named "'+args[2]+'".')
                    failed=True

                coly2=ctypes.c_char_p(force_bytes(args[3]))
                idy2=ctypes.c_int(0)
                ptry2=double_ptr()
                get_ret=get_fn(amp,coly2,ctypes.byref(idy2),ctypes.byref(ptry2))
                if get_ret!=0:
                    print('Failed to get column named "'+args[3]+'".')
                    failed=True

                if failed==False:
                    for i in range(0,idx2.value):
                        xv.append(ptrx2[idx2.value-1-i])
                        yv.append(ptry2[idy2.value-1-i])

            if failed==False:
                # Make sure the loop is closed
                xv.append(ptrx1[0])
                yv.append(ptry1[0])
        
                if self.canvas_flag==False:
                    self.canvas()
                if len(args)==3:
                    self.axes.fill(xv,yv,**string_to_dict(args[2]))
                elif len(args)==5:
                    self.axes.fill(xv,yv,**string_to_dict(args[4]))
                else:
                    self.axes.fill(xv,yv)

                if self.logx==True:
                    self.axes.set_xscale('log')
                if self.logy==True:
                    self.axes.set_yscale('log')
                    
                if self.xset==True:
                    self.axes.set_xlim(self.xlo,self.xhi)
                if self.yset==True:
                    self.axes.set_ylim(self.ylo,self.yhi)
                                 
            # End of section for 'table' type
        else:
            print("Command 'rplot' not supported for type",
                  curr_type,".")
            return
        
        # End of 'rplot' function
                                 
    def scatter(self,o2scl_hdf,amp,args):
        """
        Generate a scatter plot.
        """

        # Useful pointer types
        double_ptr=ctypes.POINTER(ctypes.c_double)
        char_ptr=ctypes.POINTER(ctypes.c_char)
        double_ptr_ptr=ctypes.POINTER(double_ptr)
        char_ptr_ptr=ctypes.POINTER(char_ptr)
        int_ptr=ctypes.POINTER(ctypes.c_int)
        
        # Set up wrapper for type function
        type_fn=o2scl_hdf.o2scl_acol_get_type
        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]

        # Get current type
        it=ctypes.c_int(0)
        type_ptr=char_ptr()
        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
        curr_type=b''
        for i in range(0,it.value):
            curr_type=curr_type+type_ptr[i]
                        
        if curr_type==b'table':
                            
            failed=False

            get_fn=o2scl_hdf.o2scl_acol_get_column
            get_fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                             int_ptr,double_ptr_ptr]
            get_fn.restype=ctypes.c_int

            colx=ctypes.c_char_p(force_bytes(args[0]))
            idx=ctypes.c_int(0)
            ptrx=double_ptr()
            get_ret=get_fn(amp,colx,ctypes.byref(idx),ctypes.byref(ptrx))
            if get_ret!=0:
                print('Failed to get column named "'+args[0]+'".')
                failed=True

            coly=ctypes.c_char_p(force_bytes(args[1]))
            idy=ctypes.c_int(0)
            ptry=double_ptr()
            get_ret=get_fn(amp,coly,ctypes.byref(idy),ctypes.byref(ptry))
            if get_ret!=0:
                print('Failed to get column named "'+args[1]+'".')
                failed=True

            if failed==False:
                xv=[ptrx[i] for i in range(0,idx.value)]
                yv=[ptry[i] for i in range(0,idy.value)]

            sv=[]
            cv=[]

            if (len(args)>2 and force_bytes(args[2])!=b'None' and
                force_bytes(args[2])!=b'none'):
                cols=ctypes.c_char_p(force_bytes(args[2]))
                ids=ctypes.c_int(0)
                ptrs=double_ptr()
                get_ret=get_fn(amp,cols,ctypes.byref(ids),ctypes.byref(ptrs))
                if get_ret!=0:
                    print('Failed to get column named "'+args[2]+'".')
                    failed=True
                else:
                    sv=[ptrs[i] for i in range(0,ids.value)]

            if (len(args)>3 and force_bytes(args[3])!=b'None' and
                force_bytes(args[3])!=b'none'):
                colc=ctypes.c_char_p(force_bytes(args[3]))
                idc=ctypes.c_int(0)
                ptrc=double_ptr()
                get_ret=get_fn(amp,colc,ctypes.byref(idc),ctypes.byref(ptrc))
                if get_ret!=0:
                    print('Failed to get column named "'+args[3]+'".')
                    failed=True
                else:
                    cv=[ptrc[i] for i in range(0,idc.value)]

            if failed==False:
                
                if self.canvas_flag==False:
                    self.canvas()
                if len(sv)>0:
                    if len(cv)>0:
                        if len(args)>4:
                            self.axes.scatter(xv,yv,s=sv,c=cv,
                                         **string_to_dict(args[4]))
                        else:
                            self.axes.scatter(xv,yv,s=sv,c=cv)
                    else:
                        if len(args)>4:
                            self.axes.scatter(xv,yv,s=sv,
                                         **string_to_dict(args[4]))
                        else:
                            self.axes.scatter(xv,yv,s=sv)
                else:
                    if len(cv)>0:
                        if len(args)>4:
                            self.axes.scatter(xv,yv,c=cv,
                                         **string_to_dict(args[4]))
                        else:
                            self.axes.scatter(xv,yv,c=cv)
                    else:
                        if len(args)>4:
                            self.axes.scatter(xv,yv,**string_to_dict(args[4]))
                        else:
                            self.axes.scatter(xv,yv)

                if self.logx==True:
                    self.axes.set_xscale('log')
                if self.logy==True:
                    self.axes.set_yscale('log')
                    
                if self.xset==True:
                    self.axes.set_xlim(self.xlo,self.xhi)
                if self.yset==True:
                    self.axes.set_ylim(self.ylo,self.yhi)
                if self.colbar==True and len(cv)>0:
                    cbar=plot.colorbar(ax=self.axes)
                    cbar.ax.tick_params(labelsize=self.font*0.8)
                    
            # End of section for 'table' type
        else:
            print("Command 'scatter' not supported for type",
                  curr_type,".")
            return
        
        if self.xset==True:
            self.axes.set_xlim(self.xlo,self.xhi)
        if self.yset==True:
            self.axes.set_ylim(self.ylo,self.yhi)
                                 
        # End of 'scatter' function
                                 
    def histplot(self,o2scl_hdf,amp,args):
        """
        Plot a histogram
        """

        # Useful pointer types
        double_ptr=ctypes.POINTER(ctypes.c_double)
        char_ptr=ctypes.POINTER(ctypes.c_char)
        double_ptr_ptr=ctypes.POINTER(double_ptr)
        char_ptr_ptr=ctypes.POINTER(char_ptr)
        int_ptr=ctypes.POINTER(ctypes.c_int)
        
        # Set up wrapper for type function
        type_fn=o2scl_hdf.o2scl_acol_get_type
        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]

        # Get current type
        it=ctypes.c_int(0)
        type_ptr=char_ptr()
        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
        curr_type=b''
        for i in range(0,it.value):
            curr_type=curr_type+type_ptr[i]
                        
        if curr_type==b'table':
                            
            get_fn=o2scl_hdf.o2scl_acol_get_column
            get_fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                             int_ptr,double_ptr_ptr]
            get_fn.restype=ctypes.c_int

            colx=ctypes.c_char_p(force_bytes(args[0]))
            idx=ctypes.c_int(0)
            ptrx=double_ptr()
            get_ret=get_fn(amp,colx,ctypes.byref(idx),ctypes.byref(ptrx))
            failed=False
            if get_ret!=0:
                print('Failed to get column named "'+args[0]+'".')
                failed=True

            if failed==False:
                xv=[ptrx[i] for i in range(0,idx.value)]
        
                if self.canvas_flag==False:
                    self.canvas()
                if len(args)<2:
                    self.axes.hist(xv)
                else:
                    self.axes.hist(xv,**string_to_dict(args[1]))
                
            # End of section for 'table' type
        else:
            print("Command 'histplot' not supported for type",
                  curr_type,".")
            return
        
        if self.xset==True:
            self.axes.set_xlim(self.xlo,self.xhi)
        if self.yset==True:
            self.axes.set_ylim(self.ylo,self.yhi)
                                 
        # End of 'histplot' function
                                 
    def hist2dplot(self,o2scl_hdf,amp,args):
        """
        Plot a two-dimensional histogram
        """

        # Useful pointer types
        double_ptr=ctypes.POINTER(ctypes.c_double)
        char_ptr=ctypes.POINTER(ctypes.c_char)
        double_ptr_ptr=ctypes.POINTER(double_ptr)
        char_ptr_ptr=ctypes.POINTER(char_ptr)
        int_ptr=ctypes.POINTER(ctypes.c_int)
        
        # Set up wrapper for type function
        type_fn=o2scl_hdf.o2scl_acol_get_type
        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]

        # Get current type
        it=ctypes.c_int(0)
        type_ptr=char_ptr()
        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
        curr_type=b''
        for i in range(0,it.value):
            curr_type=curr_type+type_ptr[i]
                        
        if curr_type==b'table':
                            
            get_fn=o2scl_hdf.o2scl_acol_get_column
            get_fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                             int_ptr,double_ptr_ptr]
            get_fn.restype=ctypes.c_int

            failed=False

            colx=ctypes.c_char_p(force_bytes(args[0]))
            idx=ctypes.c_int(0)
            ptrx=double_ptr()
            get_ret=get_fn(amp,colx,ctypes.byref(idx),ctypes.byref(ptrx))
            if get_ret!=0:
                print('Failed to get column named "'+args[0]+'".')
                failed=True
            
            coly=ctypes.c_char_p(force_bytes(args[1]))
            idy=ctypes.c_int(0)
            ptry=double_ptr()
            get_ret=get_fn(amp,coly,ctypes.byref(idy),ctypes.byref(ptry))
            if get_ret!=0:
                print('Failed to get column named "'+args[1]+'".')
                failed=True

            if failed==False:
                xv=[ptrx[i] for i in range(0,idx.value)]
                yv=[ptry[i] for i in range(0,idy.value)]
        
                if self.canvas_flag==False:
                    self.canvas()
                if len(args)<3:
                    c,x,y,self.last_image=self.axes.hist2d(xv,yv)
                else:
                    c,x,y,self.last_image=self.axes.hist2d(xv,yv,**string_to_dict(args[2]))
                
                if self.colbar==True:
                    cbar=plot.colorbar(self.last_image,ax=self.axes)
                    cbar.ax.tick_params(labelsize=self.font*0.8)
                    
            # End of section for 'table' type
        else:
            print("Command 'plot' not supported for type",
                  curr_type,".")
            return
        
        if self.xset==True:
            self.axes.set_xlim(self.xlo,self.xhi)
        if self.yset==True:
            self.axes.set_ylim(self.ylo,self.yhi)
                                 
        # End of 'plot' function
                                 
    def errorbar(self,o2scl_hdf,amp,args):
        """
        Create a plot with error bars
        """

        # Useful pointer types
        double_ptr=ctypes.POINTER(ctypes.c_double)
        char_ptr=ctypes.POINTER(ctypes.c_char)
        double_ptr_ptr=ctypes.POINTER(double_ptr)
        char_ptr_ptr=ctypes.POINTER(char_ptr)
        int_ptr=ctypes.POINTER(ctypes.c_int)
        
        # Set up wrapper for type function
        type_fn=o2scl_hdf.o2scl_acol_get_type
        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]

        # Get current type
        it=ctypes.c_int(0)
        type_ptr=char_ptr()
        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
        curr_type=b''
        for i in range(0,it.value):
            curr_type=curr_type+type_ptr[i]
                        
        if curr_type==b'table':
                            
            get_fn=o2scl_hdf.o2scl_acol_get_column
            get_fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                             int_ptr,double_ptr_ptr]

            colx=ctypes.c_char_p(force_bytes(args[0]))
            idx=ctypes.c_int(0)
            ptrx=double_ptr()
            get_fn(amp,colx,ctypes.byref(idx),ctypes.byref(ptrx))
            xv=[ptrx[i] for i in range(0,idx.value)]

            coly=ctypes.c_char_p(force_bytes(args[1]))
            idy=ctypes.c_int(0)
            ptry=double_ptr()
            get_fn(amp,coly,ctypes.byref(idy),ctypes.byref(ptry))
            yv=[ptry[i] for i in range(0,idy.value)]

            if args[2]=='0':
                xerrv=[0.0 for i in range(0,idx.value)]
            else:
                colxerr=ctypes.c_char_p(force_bytes(args[2]))
                idxerr=ctypes.c_int(0)
                ptrxerr=double_ptr()
                get_fn(amp,colxerr,ctypes.byref(idxerr),ctypes.byref(ptrxerr))
                xerrv=[ptrxerr[i] for i in range(0,idxerr.value)]
    
            if args[3]=='0':
                yerrv=[0.0 for i in range(0,idy.value)]
            else:
                colyerr=ctypes.c_char_p(force_bytes(args[3]))
                idyerr=ctypes.c_int(0)
                ptryerr=double_ptr()
                get_fn(amp,colyerr,ctypes.byref(idyerr),ctypes.byref(ptryerr))
                yerrv=[ptryerr[i] for i in range(0,idyerr.value)]

            if self.canvas_flag==False:
                self.canvas()
            if len(args)<5:
                self.axes.errorbar(xv,yv,yerr=yerrv,xerr=xerrv)
            else:
                self.axes.errorbar(xv,yv,yerr=yerrv,xerr=xerrv,
                                   **string_to_dict(args[4]))
                
            # End of section for 'table' type
        else:
            print("Command 'plot' not supported for type",
                  curr_type,".")
            return
        
        if self.xset==True:
            self.axes.set_xlim(self.xlo,self.xhi)
        if self.yset==True:
            self.axes.set_ylim(self.ylo,self.yhi)
                                 
        # End of 'errorbar' function
                                 
    def plot1(self,o2scl_hdf,amp,args):
        """
        Plot data versus an integer x axis
        """

        int_ptr=ctypes.POINTER(ctypes.c_int)
        double_ptr=ctypes.POINTER(ctypes.c_double)
        char_ptr=ctypes.POINTER(ctypes.c_char)
        double_ptr_ptr=ctypes.POINTER(double_ptr)
        char_ptr_ptr=ctypes.POINTER(char_ptr)
        
        # Set up wrapper for type function
        type_fn=o2scl_hdf.o2scl_acol_get_type
        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]

        # Get current type
        it=ctypes.c_int(0)
        type_ptr=char_ptr()
        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
        curr_type=b''
        for i in range(0,it.value):
            curr_type=curr_type+type_ptr[i]
                        
        if curr_type==b'table':
            
            get_fn=o2scl_hdf.o2scl_acol_get_column
            get_fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                             int_ptr,double_ptr_ptr]
            get_fn.restype=ctypes.c_int

            colx=ctypes.c_char_p(force_bytes(args[0]))
            idx=ctypes.c_int(0)
            ptrx=double_ptr()
            get_ret=get_fn(amp,colx,ctypes.byref(idx),ctypes.byref(ptrx))
            failed=False
            if get_ret!=0:
                print('Failed to get column named "'+args[0]+'".')
                failed=True

            if failed==False:
                xv=[i for i in range(0,idx.value)]
                yv=[ptrx[i] for i in range(0,idx.value)]
        
                if self.canvas_flag==False:
                    self.canvas()
                if self.logx==True:
                    if self.logy==True:
                        if len(args)<2:
                            self.axes.loglog(xv,yv)
                        else:
                            self.axes.loglog(xv,yv,**string_to_dict(args[1]))
                    else:
                        if len(args)<2:
                            self.axes.semilogx(xv,yv)
                        else:
                            self.axes.semilogx(xv,yv,**string_to_dict(args[1]))
                else:
                    if self.logy==True:
                        if len(args)<2:
                            self.axes.semilogy(xv,yv)
                        else:
                            self.axes.semilogy(xv,yv,**string_to_dict(args[1]))
                    else:
                        if len(args)<2:
                            self.axes.plot(xv,yv)
                        else:
                            self.axes.plot(xv,yv,**string_to_dict(args[1]))
                                
                if self.xset==True:
                    self.axes.set_xlim(self.xlo,self.xhi)
                if self.yset==True:
                    self.axes.set_ylim(self.ylo,self.yhi)
                    
        elif (curr_type==b'double[]' or curr_type==b'int[]' or
              curr_type==b'size_t[]'):

            get_fn=o2scl_hdf.o2scl_acol_get_double_arr
            get_fn.argtypes=[ctypes.c_void_p,int_ptr,double_ptr_ptr]
                            
            id=ctypes.c_int(0)
            ptr=double_ptr()
            get_fn(amp,ctypes.byref(id),ctypes.byref(ptr))
            
            xv=[i for i in range(0,id.value)]
            yv=[ptr[i] for i in range(0,id.value)]

            if self.canvas_flag==False:
                self.canvas()
            if self.logx==True:
                if self.logy==True:
                    if len(args)<1:
                        self.axes.loglog(xv,yv)
                    else:
                        self.axes.loglog(xv,yv,**string_to_dict(args[0]))
                else:
                    if len(args)<1:
                        self.axes.semilogx(xv,yv)
                    else:
                        self.axes.semilogx(xv,yv,**string_to_dict(args[0]))
            else:
                if self.logy==True:
                    if len(args)<1:
                        self.axes.semilogy(xv,yv)
                    else:
                        self.axes.semilogy(xv,yv,**string_to_dict(args[0]))
                else:
                    if len(args)<1:
                        self.axes.plot(xv,yv)
                    else:
                        self.axes.plot(xv,yv,**string_to_dict(args[0]))
                            
            if self.xset==True:
                self.axes.set_xlim(self.xlo,self.xhi)
            if self.yset==True:
                self.axes.set_ylim(self.ylo,self.yhi)
                    
        # End of 'plot1' function
            
    def plotv(self,o2scl_hdf,amp,args):
        """
        Plot two multiple vector specifications
        """

        char_ptr=ctypes.POINTER(ctypes.c_char)
        char_ptr_ptr=ctypes.POINTER(char_ptr)
        double_ptr=ctypes.POINTER(ctypes.c_double)
        double_ptr_ptr=ctypes.POINTER(double_ptr)
        int_ptr=ctypes.POINTER(ctypes.c_int)
        
        # Set up wrapper for type function
        type_fn=o2scl_hdf.o2scl_acol_get_type
        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]
        
        # Get current type
        it=ctypes.c_int(0)
        type_ptr=char_ptr()
        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
        curr_type=b''
        for i in range(0,it.value):
            curr_type=curr_type+type_ptr[i]

        if curr_type==b'vector<contour_line>':
             print('Store and clear the vector<contour_line> object '+
                   'before using \'plotv\'.')
             return 1
        
        conv_fn=o2scl_hdf.o2scl_acol_mult_vectors_to_conts
        conv_fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                          ctypes.c_char_p]
        conv_fn.restype=ctypes.c_int

        if len(args)>=2:
            if self.verbose>1:
                print('Calling mult_vectors_to_conts() with',
                      args[0],'and',args[1])
            mvs1=ctypes.c_char_p(force_bytes(args[0]))
            mvs2=ctypes.c_char_p(force_bytes(args[1]))
            conv_ret=conv_fn(amp,mvs1,mvs2)
            if conv_ret!=0:
                print('Failed to read "'+args[0]+'" and "'+args[1]+'".')
                return 2
        else:
            if self.verbose>1:
                print('Calling mult_vectors_to_conts() with',
                      args[0])
            mvs1=ctypes.c_char_p(0)
            mvs2=ctypes.c_char_p(force_bytes(args[0]))
            conv_ret=conv_fn(amp,mvs1,mvs2)
            if conv_ret!=0:
                print('Failed to read "'+args[0])
                return 2
        
        
        # Get the total number of contour lines
        cont_n_fn=o2scl_hdf.o2scl_acol_contours_n
        cont_n_fn.argtypes=[ctypes.c_void_p]
        cont_n_fn.restype=ctypes.c_int
        nconts=cont_n_fn(amp)

        # Define types for extracting each contour line
        cont_line_fn=o2scl_hdf.o2scl_acol_contours_line
        cont_line_fn.argtypes=[ctypes.c_void_p,ctypes.c_int,
                               int_ptr,double_ptr_ptr,
                               double_ptr_ptr]
        cont_line_fn.restype=ctypes.c_double

        if self.canvas_flag==False:
            self.canvas()

        # Loop over all contour lines
        for k in range(0,nconts):
            idx=ctypes.c_int(0)
            ptrx=double_ptr()
            ptry=double_ptr()
            lev=cont_line_fn(amp,k,ctypes.byref(idx),
                             ctypes.byref(ptrx),ctypes.byref(ptry))
            xv=[ptrx[i] for i in range(0,idx.value)]
            yv=[ptry[i] for i in range(0,idx.value)]
                
            if self.logx==True:
                if self.logy==True:
                    if len(args)<3:
                        self.axes.loglog(xv,yv)
                    else:
                        self.axes.loglog(xv,yv,**string_to_dict(args[2]))
                else:
                    if len(args)<3:
                        self.axes.semilogx(xv,yv)
                    else:
                        self.axes.semilogx(xv,yv,**string_to_dict(args[2]))
            else:
                if self.logy==True:
                    if len(args)<3:
                        self.axes.semilogy(xv,yv)
                    else:
                        self.axes.semilogy(xv,yv,**string_to_dict(args[2]))
                else:
                    if len(args)<3:
                        self.axes.plot(xv,yv)
                    else:
                        self.axes.plot(xv,yv,**string_to_dict(args[2]))
                        
        # End of 'plotv' function
        
    def print_param_docs(self):
        """
        Print parameter documentation.
        """
        
        # I don't know why this doesn't work right now
        # print(plot_base.logz.__doc__)
        
        print('O2graph parameter list:')
        print(' ')
        for line in param_list:
            if line[0]!='verbose':
                if line[0]=='colbar':
                    print(line[0]+' '+str(self.colbar))
                elif line[0]=='fig-dict':
                    print(line[0]+' '+str(self.fig_dict))
                elif line[0]=='font':
                    print(line[0]+' '+str(self.font))
                elif line[0]=='logx':
                    print(line[0]+' '+str(self.logx))
                elif line[0]=='logy':
                    print(line[0]+' '+str(self.logy))
                elif line[0]=='logz':
                    print(line[0]+' '+str(self.logz))
                elif line[0]=='xhi':
                    print(line[0]+' '+str(self.xhi))
                elif line[0]=='xlo':
                    print(line[0]+' '+str(self.xlo))
                elif line[0]=='xset':
                    print(line[0]+' '+str(self.xset))
                elif line[0]=='yhi':
                    print(line[0]+' '+str(self.yhi))
                elif line[0]=='ylo':
                    print(line[0]+' '+str(self.ylo))
                elif line[0]=='yset':
                    print(line[0]+' '+str(self.yset))
                elif line[0]=='zhi':
                    print(line[0]+' '+str(self.zhi))
                elif line[0]=='zlo':
                    print(line[0]+' '+str(self.zlo))
                elif line[0]=='zset':
                    print(line[0]+' '+str(self.zset))
                else:
                    print(line[0])
                print(' '+line[1])
                print(' ')
        print('yt-related settings:')
        print(' ')
        for line in yt_param_list:
            if line[0]=='yt_focus':
                print(line[0]+' '+str(self.yt_focus))
            if line[0]=='yt_position':
                print(line[0]+' '+str(self.yt_position))
            if line[0]=='yt_path':
                print(line[0]+' '+self.yt_path)
            if line[0]=='yt_resolution':
                print(line[0]+' '+str(self.yt_resolution))
            print(' '+line[1])
            print(' ')

    def parse_argv(self,argv,o2scl_hdf):
        """
        Parse command-line arguments.

        This is the main function used by the :ref:`O2graph script` .
        Once it has created a list of strings from argv, it calls
        parse_string_list() to call the proper functions.
        """

        # Create an acol_manager object and get the pointer
        o2scl_hdf.o2scl_create_acol_manager.restype=ctypes.c_void_p
        amp=o2scl_hdf.o2scl_create_acol_manager()

        names_fn=o2scl_hdf.o2scl_acol_set_names
        names_fn.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_char_p,
                           ctypes.c_int,ctypes.c_char_p,ctypes.c_int,
                           ctypes.c_char_p]

        # Get current type
        cmd_name=b'o2graph'
        cmd_desc=(b'o2graph: A data viewing and '+
                  b'processing program for O2scl.\n')
        env_var=b'O2GRAPH_DEFAULTS'
        names_fn(amp,len(cmd_name),ctypes.c_char_p(cmd_name),
                 len(cmd_desc),ctypes.c_char_p(cmd_desc),
                 len(env_var),ctypes.c_char_p(env_var))

        # Apply aliases before parsing. We convert argv 
        # to a set of integer and character arrays, then
        # pass them to o2scl_acol_apply_aliases()
        if True:

            orig_len=len(argv)
            
            int_ptr=ctypes.POINTER(ctypes.c_int)
            char_ptr=ctypes.POINTER(ctypes.c_char)
            int_ptr_ptr=ctypes.POINTER(int_ptr)
            char_ptr_ptr=ctypes.POINTER(char_ptr)

            # Allocate space for arrays
            tiarr=(ctypes.c_int*len(argv))()
            ttot=0
            for i in range(0,len(argv)):
                ttot+=len(argv[i])
            tcarr=(ctypes.c_char*ttot)()

            # Fill arrays with data
            tcnt=0
            for i in range(0,len(argv)):
                tiarr[i]=len(argv[i])
                #print(i,tiarr[i])
                for j in range(0,len(argv[i])):
                    tcarr[tcnt]=bytes(argv[i][j],'utf8')
                    #print(j,tcarr[tcnt])
                    tcnt=tcnt+1

            # Call the alias_counts() function to find out how big the
            # destination arrays need to be. This two step-process
            # allows python to handle the memory allocation.
            count_fn=o2scl_hdf.o2scl_acol_alias_counts
            count_fn.argtypes=[ctypes.c_void_p,ctypes.c_int,int_ptr,
                               ctypes.c_char_p,int_ptr,int_ptr]
            n_new=ctypes.c_int(0)
            s_new=ctypes.c_int(0)
            count_fn(amp,len(argv),tiarr,tcarr,ctypes.byref(n_new),
                     ctypes.byref(s_new))

            # Allocate the new integer and string arrays
            tiarr2=(ctypes.c_int*n_new.value)()
            tcarr2=(ctypes.c_char*s_new.value)()

            # Setup and call alias function
            alias_fn=o2scl_hdf.o2scl_acol_apply_aliases
            alias_fn.argtypes=[ctypes.c_void_p,ctypes.c_int,int_ptr,
                               ctypes.c_char_p,int_ptr,ctypes.c_char_p]
            alias_fn(amp,len(argv),tiarr,tcarr,tiarr2,tcarr2)

            # Construct the new argv list. We skip alias
            # definitions because they are already taken care of
            argv=[]
            icnt=0
            cnt=0
            iskip=0
            if len(tiarr2)!=orig_len:
                print('After applying alias,',orig_len,'->',len(tiarr2))
            for i in range(0,n_new.value):
                tstr=''
                for j in range(0,tiarr2[i]):
                    tstr=tstr+tcarr2[cnt].decode('utf-8')
                    cnt=cnt+1
                if tstr=='-alias':
                    iskip=2
                elif iskip==0:
                    argv.append(tstr)
                    if len(tiarr2)!=orig_len:
                        print(icnt,argv[icnt])
                    icnt=icnt+1
                else:
                    iskip=iskip-1
            
        if len(argv)<=1:
            done_flag=False
            readline.parse_and_bind('tab: complete')
            readline.parse_and_bind('set editing-mode emacs')
            while done_flag==False:
                line=input('o2graph> ')
                if line[0:4]=='quit' or line[0:4]=='exit':
                    done_flag=True
                else:
                    strlist=line.split(' ')
                    strlist[0]='-'+strlist[0]
                    self.parse_string_list(strlist,o2scl_hdf,amp)
        else:
            strlist=[str(argv[i]) for i in range(1,len(argv))]
            if self.verbose>2:
                print('Number of arguments:',len(strlist),'arguments.')
                print('Argument List:',strlist)
            self.parse_string_list(strlist,o2scl_hdf,amp)

        # End of function parse_argv
        return

    def command_func(self,o2scl_hdf,amp,args):

        self.gen_acol(o2scl_hdf,amp,'commands',args)
                    
        if len(args)>0:
            
            curr_type=args[0]
                        
        else:

            # Get current type
            int_ptr=ctypes.POINTER(ctypes.c_int)
            char_ptr=ctypes.POINTER(ctypes.c_char)
            char_ptr_ptr=ctypes.POINTER(char_ptr)
            
            # Set up wrapper for type function
            type_fn=o2scl_hdf.o2scl_acol_get_type
            type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]
            
            # Get current type
            it=ctypes.c_int(0)
            type_ptr=char_ptr()
            type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
            
            curr_type=b''
            for i in range(0,it.value):
                curr_type=curr_type+type_ptr[i]
                
        print('O2graph commands for type '+
              str(curr_type)+':\n')
        strout=''
        for line in base_list:
            strout+=line[0]+' '
        for line in extra_list:
            if (curr_type==line[0] or
                curr_type==force_bytes(line[0])):
                strout+=line[1]+' '
        str_list=textwrap.wrap(strout,79)
        for i in range (0,len(str_list)):
            print(str_list[i])

        return
    
    def parse_string_list(self,strlist,o2scl_hdf,amp):
        """
        Parse a list of strings

        This function is called by parse_argv().
        """
        if self.verbose>2:
            print('In parse_string_list()',strlist)
        
        ix=0
        while ix<len(strlist):
            
            if self.verbose>2:
                print('Processing index',ix,'with value',strlist[ix],'.')
            # Find first option, at index ix
            initial_ix_done=0
            while initial_ix_done==0:
                if ix==len(strlist):
                    initial_ix_done=1
                elif strlist[ix][0]=='-':
                    initial_ix_done=1
                else:
                    if self.verbose>2:
                         print('Incrementing ix')
                    ix=ix+1
                    
            # If there is an option, then ix is its index
            if ix<len(strlist):
                
                cmd_name=strlist[ix][1:]
                # If there was two dashes, one will be left so
                # remove it
                if cmd_name[0]=='-':
                    cmd_name=cmd_name[1:]
                if self.verbose>2:
                    print('Found option',cmd_name,'at index',ix)
                # Set ix_next to the next option, or to the end if
                # there is no next option
                ix_next=ix+1
                ix_next_done=0
                while ix_next_done==0:
                    if ix_next==len(strlist):
                        ix_next_done=1
                    elif len(strlist[ix_next])>0 and strlist[ix_next][0]=='-':
                        ix_next_done=1
                    else:
                        if self.verbose>2:
                            print('Incrementing ix_next')
                        ix_next=ix_next+1

                # List of 'acol' commands for option processing loop
                acol_list=['a','alias','assign','autocorr','c',
                           'calc','cat','commands','contours','convert-unit',
                           'convert_unit','create','d','D',
                           'delete-col','delete-rows','delete-rows-tol',
                           'delete_col','delete_rows','delete_rows_tol',
                           'deriv','deriv2',
                           'download','entry','f','filelist','find-row',
                           'find_row','fit','function','g','gen3-list',
                           'gen3_list','generic','get-conv','get-row',
                           'get-unit','get_conv','get_row','get_unit',
                           'h','help','i','I','index','insert','insert-full',
                           'insert_full','integ','internal','interp',
                           'interp-type','interp_type','l','license','list',
                           'max','min','N','nlines','o','output','P',
                           'preview','q',
                           'r','read','rename','run',
                           's','S','select','select-rows',
                           'select_rows','select-rows2','select_rows2',
                           'set-data','set_data','set-unit',
                           'set_unit','show-units','show_units','slice',
                           'sort','stats','sum','to-hist','to_hist',
                           'to-hist-2d' 'to_hist_2d',
                           'to_table3d','to-table','to_table','to-table3d',
                           'type','v','warranty']
                
                # Now process the option
                if cmd_name=='set':

                    if self.verbose>2:
                        print('Process set.')
                        
                    if ix_next-ix<3:
                        print('Not enough parameters for set option.')
                    else:
                        self.set_wrapper(o2scl_hdf,amp,strlist[ix+1:ix_next])
                        
                elif cmd_name=='get':
                    
                    if self.verbose>2:
                        print('Process get.')
                        
                    if ix_next-ix<2:
                        self.get('No parameter specified to get.')
                    else:
                        self.get_wrapper(o2scl_hdf,amp,strlist[ix+1:ix_next])

                elif cmd_name=='commands':
                    
                    if self.verbose>2:
                        print('Process commands.')

                    # This doesn't work yet, it segfaults on osx
                    #print('here1')
                    #self.command_func(o2scl_hdf,amp,
                    #                  strlist[ix+1:ix_next])
                    #print('here2')
                    
                    self.gen_acol(o2scl_hdf,amp,cmd_name,
                                  strlist[ix+1:ix_next])
                    
                    if (ix_next-ix)==2:
                        
                        curr_type=strlist[ix+1]
                        
                    else:

                        # Get current type
                        int_ptr=ctypes.POINTER(ctypes.c_int)
                        char_ptr=ctypes.POINTER(ctypes.c_char)
                        char_ptr_ptr=ctypes.POINTER(char_ptr)

                        # Set up wrapper for type function
                        type_fn=o2scl_hdf.o2scl_acol_get_type
                        type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]

                        # Get current type
                        it=ctypes.c_int(0)
                        type_ptr=char_ptr()
                        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
                        curr_type=b''
                        for i in range(0,it.value):
                            curr_type=curr_type+type_ptr[i]

                    print('O2graph commands for type '+
                          str(curr_type)+':\n')
                    strout=''
                    for line in base_list:
                        strout+=line[0]+' '
                    for line in extra_list:
                        if (curr_type==line[0] or
                            curr_type==force_bytes(line[0])):
                            strout+=line[1]+' '
                    str_list=textwrap.wrap(strout,79)
                    for i in range (0,len(str_list)):
                        print(str_list[i])
                            
                elif cmd_name=='yt-add-vol':

                    int_ptr=ctypes.POINTER(ctypes.c_int)
                    char_ptr=ctypes.POINTER(ctypes.c_char)
                    char_ptr_ptr=ctypes.POINTER(char_ptr)
                    double_ptr=ctypes.POINTER(ctypes.c_double)
                    double_ptr_ptr=ctypes.POINTER(double_ptr)
                    
                    # Set up wrapper for type function
                    type_fn=o2scl_hdf.o2scl_acol_get_type
                    type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]
                    
                    # Get current type
                    it=ctypes.c_int(0)
                    type_ptr=char_ptr()
                    type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                    
                    curr_type=b''
                    for i in range(0,it.value):
                        curr_type=curr_type+type_ptr[i]

                    if curr_type==b'tensor_grid':
                        self.yt_check_backend()
                        import yt
                        from yt.visualization.volume_rendering.api \
                            import VolumeSource
                        from yt.visualization.volume_rendering.transfer_function_helper \
    import TransferFunctionHelper

                        # Set up wrapper for get function
                        get_fn=o2scl_hdf.o2scl_acol_get_tensor_grid3
                        get_fn.argtypes=[ctypes.c_void_p,int_ptr,int_ptr,
                                         int_ptr,double_ptr_ptr,
                                         double_ptr_ptr,double_ptr_ptr,
                                         double_ptr_ptr]
                        get_fn.restype=ctypes.c_int

                        # Call get function
                        nx=ctypes.c_int(0)
                        ny=ctypes.c_int(0)
                        nz=ctypes.c_int(0)
                        ret=ctypes.c_int(0)
                        gridx=double_ptr()
                        gridy=double_ptr()
                        gridz=double_ptr()
                        data=double_ptr()
                        ret=get_fn(amp,ctypes.byref(nx),ctypes.byref(ny),
                                   ctypes.byref(nz),ctypes.byref(gridx),
                                   ctypes.byref(gridy),ctypes.byref(gridz),
                                   ctypes.byref(data))

                        nx=nx.value
                        ny=ny.value
                        nz=nz.value
                        total_size=nx*ny*nz
                        #maxval=data[0]
                        #minval=data[0]
                        #for ij in range(0,total_size):
                        #    if data[ij]>maxval:
                        #        maxval=data[ij]
                        #    if data[ij]<minval:
                        #        minval=data[ij]
                        #drange=maxval-minval

                        if self.xset==False:
                            self.xlo=gridx[0]
                            self.xhi=gridx[nx-1]
                        if self.yset==False:
                            self.ylo=gridy[0]
                            self.yhi=gridy[ny-1]
                        if self.zset==False:
                            self.zlo=gridz[0]
                            self.zhi=gridz[nz-1]
                        print('o2graph_plotter:yt-add-vol: axis limits:',
                              self.xlo,self.xhi,
                              self.ylo,self.yhi,self.zlo,self.zhi)
                        
                        arr=numpy.ctypeslib.as_array(data,shape=(nx,ny,nz))
                        bbox=numpy.array([[0.0,1.0],[0.0,1.0],[0.0,1.0]])
                        ds=yt.load_uniform_grid(dict(density=arr),
                                                arr.shape,bbox=bbox)

                        vol=VolumeSource(ds,field='density')
                        vol.log_field=False

                        # Setup the transfer function
                        if True:
                            vol.set_transfer_function(self.yt_tf)
                            print(self.yt_tf)
                            # tf=yt.ColorTransferFunction((minval,maxval),
                            #                             grey_opacity=False)
                            # wid=0.012
                            # tf.add_gaussian(minval+drange*0.9,wid,
                            #                 [1.0,0.0,0.0,1.0])
                            # wid=0.01
                            # tf.add_gaussian(minval+drange*0.5,wid,
                            #                 [0.0,1.0,0.0,1.0])
                            # wid=0.012
                            # tf.add_gaussian(minval+drange*0.1,wid,
                            #                 [0.0,0.0,1.0,1.0])
                            # vol.set_transfer_function(tf)
                            # print(tf)
                        else:
                            tfh=TransferFunctionHelper(ds)
                            tfh.set_field('density')
                            tfh.set_log(False)
                            tfh.set_bounds()
                            tfh.build_transfer_function()
                            tfh.tf.add_layers(3)
                            #tfh.plot('tf.png')
                            vol.set_transfer_function(tfh.tf)
                            print(tfh.tf)
                        
                        if self.yt_created_scene==False:
                            self.yt_create_scene()

                        self.yt_scene.add_source(vol,keyname='vol1')
                            
                        if self.yt_created_camera==False:
                            self.yt_create_camera(ds)

                elif cmd_name=='yt-scatter':

                    int_ptr=ctypes.POINTER(ctypes.c_int)
                    char_ptr=ctypes.POINTER(ctypes.c_char)
                    char_ptr_ptr=ctypes.POINTER(char_ptr)
                    double_ptr=ctypes.POINTER(ctypes.c_double)
                    double_ptr_ptr=ctypes.POINTER(double_ptr)
                    
                    # Set up wrapper for type function
                    type_fn=o2scl_hdf.o2scl_acol_get_type
                    type_fn.argtypes=[ctypes.c_void_p,int_ptr,char_ptr_ptr]
                    
                    # Get current type
                    it=ctypes.c_int(0)
                    type_ptr=char_ptr()
                    type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                    
                    curr_type=b''
                    for i in range(0,it.value):
                        curr_type=curr_type+type_ptr[i]

                    if curr_type==b'table':
                        self.yt_check_backend()
                        import yt
                        from yt.visualization.volume_rendering.api \
                            import PointSource
                        
                        get_fn=o2scl_hdf.o2scl_acol_get_column
                        get_fn.argtypes=[ctypes.c_void_p,ctypes.c_char_p,
                                         int_ptr,double_ptr_ptr]
                        get_fn.restype=ctypes.c_int
                        
                        colx=ctypes.c_char_p(force_bytes(strlist[ix+1]))
                        idx=ctypes.c_int(0)
                        ptrx=double_ptr()
                        get_ret=get_fn(amp,colx,ctypes.byref(idx),
                                       ctypes.byref(ptrx))
                        if get_ret!=0:
                            print('Failed to get column named "'+
                                  strlist[ix+1]+'".')
                            failed=True
                            
                        coly=ctypes.c_char_p(force_bytes(strlist[ix+2]))
                        idy=ctypes.c_int(0)
                        ptry=double_ptr()
                        get_ret=get_fn(amp,coly,ctypes.byref(idy),
                                       ctypes.byref(ptry))
                        if get_ret!=0:
                            print('Failed to get column named "'+
                                  strlist[ix+3]+'".')
                            failed=True

                        colz=ctypes.c_char_p(force_bytes(strlist[ix+2]))
                        idz=ctypes.c_int(0)
                        ptrz=double_ptr()
                        get_ret=get_fn(amp,colz,ctypes.byref(idz),
                                       ctypes.byref(ptrz))
                        if get_ret!=0:
                            print('Failed to get column named "'+
                                  strlist[ix+3]+'".')
                            failed=True

                        if self.xset==False:
                            self.xlo=ptrx[0]
                            self.xhi=ptrx[0]
                            for i in range(0,idx.value):
                                if ptrx[i]<self.xlo:
                                    self.xlo=ptrx[i]
                                if ptrx[i]>self.xhi:
                                    self.xhi=ptrx[i]
                        if self.yset==False:
                            self.ylo=ptry[0]
                            self.yhi=ptry[0]
                            for i in range(0,idy.value):
                                if ptry[i]<self.ylo:
                                    self.ylo=ptry[i]
                                if ptry[i]>self.yhi:
                                    self.yhi=ptry[i]
                        if self.zset==False:
                            self.zlo=ptrz[0]
                            self.zhi=ptrz[0]
                            for i in range(0,idz.value):
                                if ptrz[i]<self.zlo:
                                    self.zlo=ptrz[i]
                                if ptrz[i]>self.zhi:
                                    self.zhi=ptrz[i]
                        x_range=self.xhi-self.xlo
                        y_range=self.yhi-self.ylo
                        z_range=self.zhi-self.zlo

                        pts=[]
                        cols=[]
                        for i in range(0,idx.value):
                            pts.append([(ptrx[i]-self.xlo)/x_range,
                                        (ptry[i]-self.ylo)/y_range,
                                        (ptrz[i]-self.zlo)/z_range])
                            cols.append([1.0,1.0,1.0,1.0])
                        pts2=numpy.array(pts)
                        cols2=numpy.array(cols)

                        ps=PointSource(pts2,colors=cols2,radii=3)

                        if self.yt_created_scene==False:
                            self.yt_create_scene()

                        print('o2graph:yt-scatter: Adding point source.')
                        self.yt_scene.add_source(ps,keyname='o2graph_point')
                        
                        if self.yt_created_camera==False:
                            self.yt_create_camera(ps)
                            
                elif cmd_name=='yt-source-list':

                    icnt=0
                    for key, value in self.yt_scene.sources.items():
                        print('yt-source-list',icnt,key,type(value))
                        icnt=icnt+1
                    
                elif cmd_name=='yt-axis':

                    self.yt_plot_axis()

                elif cmd_name=='yt-render':

                    # AWS 10/14/19 the call to save() below does
                    # the render() so I don't think I need this
                    #self.yt_scene.render()

                    fname=strlist[ix+1]
                    mov_fname=''
                    if ix_next-ix>=3:
                        mov_fname=strlist[ix+2]
                    if self.yt_path=='':
                        print('o2graph:yt-render: Calling yt_scene.save().')
                        self.yt_scene.save(fname,sigma_clip=1.0)
                    else:

                        # Setup destination filename
                        if mov_fname=='':
                            mov_fname='o2graph.mp4'

                        # Parse image file pattern
                        asterisk=fname.find('*')
                        prefix=fname[0:asterisk]
                        suffix=fname[asterisk+1:len(fname)]
                        print('o2graph:yt-render:',
                              'fname,prefix,suffix,mov_fname:',
                              fname,prefix,suffix,mov_fname)
                            
                        # Read yaw arguments
                        path_arr=self.yt_path.split(' ')
                        if path_arr[0]=='yaw':
                            first=True
                            n_frames=int(path_arr[1])
                            angle=float(path_arr[2])*numpy.pi*2.0
                            
                            for i in range(0,n_frames):
                                if i+1<10:
                                    fname2=prefix+'0'+str(i+1)+suffix
                                else:
                                    fname2=prefix+str(i+1)+suffix
                                self.yt_scene.save(fname2,sigma_clip=1.0)
                                if platform.system()!='Darwin':
                                    os.system('cp '+fname2+
                                              ' /tmp/o2graph_temp.png')
                                    if first:
                                        os.system('eog /tmp/o2graph_temp.png &')
                                        first=False
                                else:
                                    os.system('cp '+fname2+
                                              ' /tmp/o2graph_temp.png')
                                    if first:
                                        os.system('open /tmp/o2gr'+
                                                  'aph_temp.png &')
                                        first=False
                                self.yt_camera.yaw(angle)

                        # -r is rate, -f is format, -vcodec is video
                        # codec (apparently 420p works well with
                        # quicktime), -pix_fmt sepcifies the pixel format,
                        # -crf is the quality (15-25 recommended)
                        # -y forces overwrite of the movie file
                        
                        cmd=('ffmpeg -y -r 10 -f image2 -i '+
                                  prefix+'%02d'+suffix+' -vcodec libx264 '+
                                  '-crf 25 -pix_fmt yuv420p '+mov_fname)
                        print('ffmpeg command:',cmd)
                        os.system(cmd)

                elif cmd_name=='yt-tf':

                    if strlist[ix+1]=='new':
                        import yt
                        print('o2graph:yt-tf: New transfer function.')
                        print('o2graph:yt-tf: min:',strlist[ix+2],
                              'max:',strlist[ix+3])
                        self.yt_tf=yt.ColorTransferFunction((float(strlist[ix+2]),
                                                             float(strlist[ix+3])),
                                                            grey_opacity=False)
                    elif strlist[ix+1]=='gauss':
                        print('o2graph:yt-tf: Adding Gaussian to',
                              'transfer function.')
                        print('o2graph:yt-tf: location:',strlist[ix+2],
                              'width:',strlist[ix+3])
                        print('o2graph:yt-tf: r,g,b,a:',
                              strlist[ix+4],strlist[ix+5],
                              strlist[ix+6],strlist[ix+7])
                        self.yt_tf.add_gaussian(float(strlist[ix+2]),
                                                float(strlist[ix+3]),
                                                [float(strlist[ix+4]),
                                                 float(strlist[ix+5]),
                                                 float(strlist[ix+6]),
                                                 float(strlist[ix+7])])

                elif cmd_name=='help' or cmd_name=='h':
                    
                    if self.verbose>2:
                        print('Process help.')

                    curr_type=''
                    cmd=''

                    redirected=False
                    if sys.stdout.isatty()==False:
                        redirected=True
                    
                    str_line=''
                    if redirected:
                        for jj in range(0,78):
                            str_line+='-'
                    else:
                        str_line=str_line+chr(27)+'(0'
                        for jj in range(0,78):
                            str_line+='q'
                        str_line=str_line+chr(27)+'(B'
                        
                    # If only a command is specified
                    if (ix_next-ix)==2:

                        # Get current type
                        int_ptr=ctypes.POINTER(ctypes.c_int)
                        char_ptr=ctypes.POINTER(ctypes.c_char)
                        char_ptr_ptr=ctypes.POINTER(char_ptr)

                        # Set up wrapper for type function
                        type_fn=o2scl_hdf.o2scl_acol_get_type
                        type_fn.argtypes=[ctypes.c_void_p,int_ptr,
                                          char_ptr_ptr]

                        # Get current type
                        it=ctypes.c_int(0)
                        type_ptr=char_ptr()
                        type_fn(amp,ctypes.byref(it),ctypes.byref(type_ptr))
                
                        curr_type=b''
                        for i in range(0,it.value):
                            curr_type=curr_type+type_ptr[i]
                            
                        cmd=strlist[ix+1]

                    elif (ix_next-ix)==3:
                        # If both a type and command are specified
                        
                        curr_type=strlist[ix+1]
                        cmd=strlist[ix+2]

                    # See if we matched an o2graph command
                    match=False
                    
                    # Handle the case of an o2graph command from the
                    # base list
                    for line in base_list:
                        if cmd==line[0]:
                            match=True
                            print('Usage: '+cmd+' '+line[2]+'\n\n'+
                                  line[1]+'\n')
                            tempx_arr=line[3].split('\n')
                            for j in range(0,len(tempx_arr)):
                                #print('here.'+tempx_arr[j]+'.')
                                if len(tempx_arr[j])<79:
                                    print(tempx_arr[j])
                                else:
                                    str_list=textwrap.wrap(tempx_arr[j],79)
                                    for i in range (0,len(str_list)):
                                        print(str_list[i])
                                
                    # Handle the case of an o2graph command from the
                    # extra list
                    for line in extra_list:
                        if ((curr_type==line[0] or
                             curr_type==force_bytes(line[0])) and
                            cmd==line[1]):
                            match=True
                            print('Usage: '+cmd+' '+line[3]+'\n\n'+
                                  line[2]+'\n')
                            str_list=textwrap.wrap(line[4],79)
                            for i in range (0,len(str_list)):
                                print(str_list[i])

                    finished=False
                    if (cmd=='cmaps_list') and (ix_next-ix)==2:
                        print('Matplotlib colormaps:')
                        print(str_line)
                        for category, cmap_list in cmaps:
                            list2=''
                            for name in cmap_list:
                                list2+=name+' '
                            str_list=textwrap.wrap(category+': '+list2,79)
                            for i in range (0,len(str_list)):
                                print(str_list[i])
                            print(' ')
                        print('Remember that colormaps can all be',
                              'reversed by using a "_r" suffix.')
                        finished=True

                    if (cmd=='cmaps' or cmd=='cmap') and (ix_next-ix)==2:

                        if self.new_cmaps_defined==False:
                            self.new_cmaps()

                        print('Generating colormap summary figure.')
                        
                        # An internal implementation of
                        # https://matplotlib.org/3.1.0/gallery/
                        # color/colormap_reference.html
                        
                        self.left_margin=0.01
                        self.right_margin=0.01
                        self.top_margin=0.01
                        self.bottom_margin=0.01
                        gradient=numpy.linspace(0,1,256)
                        gradient=numpy.vstack((gradient,gradient))
                        
                        nrows=0
                        for category, cmap_list in cmaps:
                            for name in cmap_list:
                                nrows=nrows+1
                        for category, cmap_list in new_cmaps:
                            for name in cmap_list:
                                nrows=nrows+1
                        ncols=3
                        while nrows%ncols!=0:
                            nrows=nrows+1
                        nrows=int((nrows)/ncols)

                        # Manually create figure and axes 
                        fig_x=7.0
                        fig_y=0.95*(0.35+0.15+(nrows+(nrows-1)*0.1)*0.22)
                        (self.fig,self.axes)=plot.subplots(nrows=nrows,
                                                           ncols=ncols,
                                                           figsize=(fig_x,
                                                                    fig_y))
                        self.fig.subplots_adjust(top=1.0-0.35/fig_y,
                                                 bottom=0.15/fig_y,
                                                 left=0.01,right=0.99,
                                                 wspace=0.01)
                        plot.rc('text',usetex=True)
                        plot.rc('font',family='serif')

                        for i in range(0,nrows):
                            for j in range(0,ncols):
                                self.axes[i][j].set_axis_off()
                        
                        row_ctr=0
                        col_ctr=0
                        for category, cmap_list in cmaps:
                            for name in cmap_list:
                                name2=name.replace('_','\_')
                                ax=self.axes[row_ctr][col_ctr]
                                ax.imshow(gradient,aspect='auto',
                                                 cmap=plot.get_cmap(name))
                                r=patches.Rectangle((0.32,0.1),0.36,0.8,0,
                                                    fc=(1,1,1,0.7),lw=0,
                                                    fill=True,
                                                    transform=ax.transAxes)
                                ax.add_patch(r)
                                ax.text(0.5,0.45,name2,
                                                    va='center',ha='center',
                                                    fontsize=8,color=(0,0,0),
                                                    transform=ax.transAxes)
                                row_ctr=row_ctr+1
                                if row_ctr>=nrows:
                                    row_ctr=0
                                    col_ctr=col_ctr+1
                        for category, cmap_list in new_cmaps:
                            for name in cmap_list:
                                name2=name.replace('_','\_')
                                ax=self.axes[row_ctr][col_ctr]
                                ax.imshow(gradient,aspect='auto',
                                                 cmap=plot.get_cmap(name))
                                r=patches.Rectangle((0.32,0.1),0.36,0.8,0,
                                                    fc=(1,1,1,0.7),lw=0,
                                                    fill=True,
                                                    transform=ax.transAxes)
                                ax.add_patch(r)
                                ax.text(0.5,0.45,name2,
                                        va='center',ha='center',
                                        fontsize=8,color=(0,0,0),
                                        transform=ax.transAxes)
                                row_ctr=row_ctr+1
                                if row_ctr>=nrows:
                                    row_ctr=0
                                    col_ctr=col_ctr+1

                        ax=self.axes[0][0]
                        ax.text(1.5,1.7,
                                (r'$ \mathrm{O}_2\mathrm{sc'+
                                 'lpy~colormap~reference} $'),
                                ha='center',va='center',fontsize=16,
                                transform=ax.transAxes)
                        plot.savefig('o2graph_cmaps.png')
                        print('Created file o2graph_cmaps.png.')
                        print('Remember that colormaps can all be',
                              'reversed by using a "_r" suffix.')
                        import matplotlib
                        if (matplotlib.get_backend()!='Agg' and 
                            matplotlib.get_backend()!='agg'):
                            plot.show()
                        finished=True

                    if (cmd=='colors') and (ix_next-ix)==2:
                        from matplotlib import colors as mc

                        colors=dict(**mc.CSS4_COLORS)
                        by_hsv=sorted((tuple(mc.rgb_to_hsv(mc.to_rgba(color)[:3])),name)
                                        for name, color in colors.items())
                        sorted_names=[name for hsv, name in by_hsv]
                        n=len(sorted_names)
                        ncols=4
                        nrows=n//ncols
                        plot.rc('text',usetex=True)
                        plot.rc('font',family='serif')
                        self.fig,self.axes=plot.subplots(figsize=(8,6.4))
                        # Get height and width
                        X,Y=self.fig.get_dpi()*self.fig.get_size_inches()
                        h=Y/(nrows+1)
                        w=X/ncols

                        ax=self.axes
                        for i, name in enumerate(sorted_names):
                            row=i%nrows
                            col=i//nrows
                            y=Y-(row*h)-h
                            xi_line=w*(col+0.05)
                            xf_line=w*(col+0.25)
                            xi_text=w*(col+0.3)
                            ax.text(xi_text,y,name,fontsize=(h*0.6),
                                    ha='left',va='center')

                            ax.hlines(y+h*0.1,xi_line,xf_line,
                                      color=colors[name],linewidth=(h*0.8))

                            ax.set_xlim(0,X)
                            ax.set_ylim(0,Y)
                            ax.set_axis_off()
                            
                            self.fig.subplots_adjust(left=0,right=1,
                                                     top=1,bottom=0,
                                                     hspace=0,wspace=0)
                        plot.savefig('o2graph_colors.png')
                        print('Created file o2graph_colors.png.')
                        import matplotlib
                        if (matplotlib.get_backend()!='Agg' and 
                            matplotlib.get_backend()!='agg'):
                            plot.show()
                        finished=True
                        
                    if len(strlist)>ix+1 and strlist[ix+1]=='colors2':
                        from matplotlib import colors as mc

                        colors=dict(**mc.CSS4_COLORS,**mc.XKCD_COLORS)
                        by_hsv=sorted((tuple(mc.rgb_to_hsv(mc.to_rgba(color)[:3])),name)
                                        for name, color in colors.items())
                        sorted_names=[(hsv, name) for hsv, name in by_hsv]
                        selected=[]
                        if (ix_next-ix)==3 and strlist[ix+2]=='greys':
                            for i in range(0,len(sorted_names)):
                                if (sorted_names[i][0][1]<0.2):
                                    selected.append((sorted_names[i][0][0],
                                                     sorted_names[i][0][1],
                                                     sorted_names[i][0][2],
                                                     sorted_names[i][1]))
                        elif (ix_next-ix)==3 and strlist[ix+2]=='reds':
                            for i in range(0,len(sorted_names)):
                                if (sorted_names[i][0][0]>0.0 and
                                    sorted_names[i][0][0]<0.05 and
                                    sorted_names[i][0][1]>0.2):
                                    selected.append((sorted_names[i][0][0],
                                                     sorted_names[i][0][1],
                                                     sorted_names[i][0][2],
                                                     sorted_names[i][1]))
                        elif (ix_next-ix)==3 and strlist[ix+2]=='oranges':
                            for i in range(0,len(sorted_names)):
                                if (sorted_names[i][0][0]>0.05 and
                                    sorted_names[i][0][0]<0.105 and
                                    sorted_names[i][0][1]>0.2):
                                    selected.append((sorted_names[i][0][0],
                                                     sorted_names[i][0][1],
                                                     sorted_names[i][0][2],
                                                     sorted_names[i][1]))
                        elif (ix_next-ix)==3 and strlist[ix+2]=='yellows':
                            for i in range(0,len(sorted_names)):
                                if (sorted_names[i][0][0]>0.105 and
                                    sorted_names[i][0][0]<0.17 and
                                    sorted_names[i][0][1]>0.2):
                                    selected.append((sorted_names[i][0][0],
                                                     sorted_names[i][0][1],
                                                     sorted_names[i][0][2],
                                                     sorted_names[i][1]))
                        elif (ix_next-ix)==3 and strlist[ix+2]=='greens':
                            for i in range(0,len(sorted_names)):
                                if (sorted_names[i][0][0]>0.17 and
                                    sorted_names[i][0][0]<0.25 and
                                    sorted_names[i][0][1]>0.2):
                                    selected.append((sorted_names[i][0][0],
                                                     sorted_names[i][0][1],
                                                     sorted_names[i][0][2],
                                                     sorted_names[i][1]))
                        elif (ix_next-ix)==3 and strlist[ix+2]=='blues':
                            for i in range(0,len(sorted_names)):
                                if (sorted_names[i][0][0]>0.0 and
                                    sorted_names[i][0][0]<0.05 and
                                    sorted_names[i][0][1]>0.2):
                                    selected.append((sorted_names[i][0][0],
                                                     sorted_names[i][0][1],
                                                     sorted_names[i][0][2],
                                                     sorted_names[i][1]))
                        elif (ix_next-ix)==3 and strlist[ix+2]=='purples':
                            for i in range(0,len(sorted_names)):
                                if (sorted_names[i][0][0]>0.0 and
                                    sorted_names[i][0][0]<0.05 and
                                    sorted_names[i][0][1]>0.2):
                                    selected.append((sorted_names[i][0][0],
                                                     sorted_names[i][0][1],
                                                     sorted_names[i][0][2],
                                                     sorted_names[i][1]))
                        elif (ix_next-ix)==3 and strlist[ix+2]=='pinks':
                            for i in range(0,len(sorted_names)):
                                if (sorted_names[i][0][0]>0.0 and
                                    sorted_names[i][0][0]<0.05 and
                                    sorted_names[i][0][1]>0.2):
                                    selected.append((sorted_names[i][0][0],
                                                     sorted_names[i][0][1],
                                                     sorted_names[i][0][2],
                                                     sorted_names[i][1]))
                        else:
                            print('Hue          Saturation',
                                  '  Value        name')
                            for i in range(0,len(sorted_names)):
                                print('%7.6e %7.6e %7.6e %s' %
                                      (sorted_names[i][0][0],
                                       sorted_names[i][0][1],
                                       sorted_names[i][0][2],
                                       sorted_names[i][1]))
                                
                        if len(selected)>0:
                            n=len(selected)
                            ncols=4
                            nrows=n//ncols
                            plot.rc('text',usetex=True)
                            plot.rc('font',family='serif')
                            self.fig,self.axes=plot.subplots(figsize=(8,6.4))
                            # Get height and width
                            X,Y=self.fig.get_dpi()*self.fig.get_size_inches()
                            h=Y/(nrows+1)
                            w=X/ncols
    
                            ax=self.axes
                            for i in range(0,n):
                                row=i%nrows
                                col=i//nrows
                                y=Y-(row*h)-h
                                xi_line=w*(col+0.05)
                                xf_line=w*(col+0.25)
                                xi_text=w*(col+0.3)
                                ax.text(xi_text,y,
                                        selected[i][3]+str(selected[i][0]),
                                        fontsize=(h*0.2),
                                        ha='left',va='center')
    
                                ax.hlines(y+h*0.1,xi_line,xf_line,
                                          color=selected[i][3],
                                          linewidth=(h*0.8))
    
                                ax.set_xlim(0,X)
                                ax.set_ylim(0,Y)
                                ax.set_axis_off()
                                
                                self.fig.subplots_adjust(left=0,right=1,
                                                         top=1,bottom=0,
                                                         hspace=0,wspace=0)
                            plot.savefig('o2graph_colors2.png')
                            print('Created file o2graph_colors2.png.')
                            import matplotlib
                            if (matplotlib.get_backend()!='Agg' and 
                                matplotlib.get_backend()!='agg'):
                                plot.show()
                            
                        finished=True
                        
                    if (cmd=='color-list') and (ix_next-ix)==2:
                        from matplotlib import colors as mcolors
                        print('Matplotlib colors:')
                        print(str_line)
                        base_dict=dict(mcolors.BASE_COLORS)
                        css4_dict=dict(**mcolors.CSS4_COLORS)
                        print(len(base_dict),'base colors:')
                        outs=''
                        ctr=0
                        for col in base_dict:
                            outs=outs+(col+' '+str(base_dict[col])).ljust(20)
                            if ctr%4==3:
                                outs=outs+'\n'
                            ctr=ctr+1
                        print(outs)
                        print(len(css4_dict),'CSS4 colors:')
                        outs=''
                        ctr=0
                        for col in css4_dict:
                            if ctr%3==0:
                                outs=outs+(col+' '+
                                           str(css4_dict[col])).ljust(26)
                            elif ctr%3==1:
                                outs=outs+(col+' '+
                                           str(css4_dict[col])).ljust(28)
                            else:
                                outs=outs+(col+' '+
                                           str(css4_dict[col])).ljust(26)
                                outs=outs+'\n'
                            ctr=ctr+1
                        print(outs)
                        print(' ')
                        outs=('O2graph also supports the (r,g,b) format '+
                              'the HTML format, and the XKCD colors. '+
                              'For (r,g,b) colors, '+
                              'the r, g, and b numbers should be from '+
                              '0.0 to 1.0. The HTML format is #RRGGBB '+
                              'where RR, GG, and BB are two-digit '+
                              'hexadecimal values.')
                        str_list=textwrap.wrap(outs,79)
                        for i in range (0,len(str_list)):
                            print(str_list[i])
                        finished=True
                        
                    if (cmd=='xkcd-color-list') and (ix_next-ix)==2:
                        from matplotlib import colors as mcolors
                        xkcd_dict=dict(**mcolors.XKCD_COLORS)
                        print('XKCD colors:')
                        print(str_line)
                        # These are commented out for now because
                        # o2graph has a hard time with spaces in
                        # color names
                        print(len(xkcd_dict),'XKCD colors:')
                        outs=''
                        ctr=0
                        for col in xkcd_dict:
                            if ctr%2==0:
                                outs=outs+(col+' '+
                                           str(xkcd_dict[col])).ljust(40)
                            else:
                                outs=outs+(col+' '+
                                           str(xkcd_dict[col])).ljust(39)
                                outs=outs+'\n'
                            ctr=ctr+1
                        print(outs)
                        finished=True

                    if (cmd=='marker-list') and (ix_next-ix)==2:
                        print('Matplotlib markers supported by O2graph:')
                        print(str_line)
                        outs='. point'.ljust(20)
                        outs=outs+', pixel'.ljust(20)
                        outs=outs+'o circle'.ljust(20)
                        outs=outs+'v triangle_down'.ljust(20)+'\n'
                        outs=outs+'^ triangle_up'.ljust(20)
                        outs=outs+'< triangle_left'.ljust(20)
                        outs=outs+'> triangle_right'.ljust(20)
                        outs=outs+'1 tri_down'.ljust(20)+'\n'
                        outs=outs+'2 tri_up'.ljust(20)
                        outs=outs+'3 tri_left'.ljust(20)
                        outs=outs+'4 tri_right'.ljust(20)
                        outs=outs+'8 octagon'.ljust(20)+'\n'
                        outs=outs+'s square'.ljust(20)
                        outs=outs+'p pentagon'.ljust(20)
                        outs=outs+'P plus (filled)'.ljust(20)
                        outs=outs+'* star'.ljust(20)+'\n'
                        outs=outs+'h hexagon1'.ljust(20)
                        outs=outs+'H hexagon2'.ljust(20)
                        outs=outs+'+ plus'.ljust(20)
                        outs=outs+'x x'.ljust(20)+'\n'
                        outs=outs+'X x (filled)'.ljust(20)
                        outs=outs+'D diamond'.ljust(20)
                        outs=outs+'d thin_diamond'.ljust(20)
                        outs=outs+'| vline'.ljust(20)+'\n'
                        outs=outs+'_ hline'.ljust(20)
                        outs=outs+'$...$ mathtext string'.ljust(20)
                        print(outs)
                        finished=True

                    if (cmd=='markers') and (ix_next-ix)==2:
                        mlist=[['.',"'.'",'point'],
                               [',',"','",'pixel'],
                               ['o',"'o'",'circle'],
                               ['v',"'v'",'down triangle'],
                               ['^',"'^'",'up triangle'],
                               ['<',"'<'",'left triangle'],
                               ['>',"'>'",'right triangle'],
                               ['1',"'1'",'down tri'],
                               ['2',"'2'",'up tri'],
                               ['3',"'3'",'left tri'],
                               ['4',"'4'",'right tri'],
                               ['8',"'8'",'octagon'],
                               ['s',"'s'",'square'],
                               ['p',"'p'",'pentagon'],
                               ['P',"'P'",'plus (filled)'],
                               ['*',"'*'",'star'],
                               ['h',"'h'",'hexagon 1'],
                               ['H',"'H'",'hexagon 2'],
                               ['+',"'+'",'plus'],
                               ['x',"'x'",'x'],
                               ['X',"'X'",'filled x'],
                               ['D',"'D'",'diamond'],
                               ['d',"'d'",'thin diamond'],
                               ['|',"'|'",'vertical line'],
                               ['_',"'_'",'horizontal line'],
                               [0,"0",'left tick'],
                               [1,"1",'right tick'],
                               [2,"2",'up tick'],
                               [3,"3",'down tick'],
                               [4,"4",'left caret'],
                               [5,"5",'right caret'],
                               [6,"6",'up caret'],
                               [7,"7",'down caret'],
                               [8,"8",'left shifted caret'],
                               [9,"9",'right shifted caret'],
                               [10,"10",'up shifted caret'],
                               [11,"11",'down shifted caret'],
                               ['$x^2$',"\$x^2\$",'math example']]
                        nmark=len(mlist)
                        ncols=2
                        nrows=(nmark+(nmark%2))/ncols
                        self.xlo=0
                        self.xhi=1
                        self.xset=True
                        self.fig_dict=('left_margin=0.01,top_margin=0.01,'+
                                       'right_margin=0.01,'+
                                       'bottom_margin=0.01,'+
                                       'fontsize=10,ticks_in=False,'+
                                       'rt_ticks=False')
                        self.canvas()
                        self.canvas_flag=True
                        self.axes.set_axis_off()
                        row_ctr=0
                        col_ctr=0
                        for entry in mlist:
                            if row_ctr>2:
                                plot.rc('text',usetex=False)
                                self.point(str((col_ctr+0.1)/(ncols)),
                                           str((nrows-row_ctr)/(nrows+1)),
                                           marker=entry[0],color='black',
                                           markersize=10)
                                self.text(str((col_ctr+0.25)/(ncols)),
                                          str((nrows-row_ctr)/(nrows+1)),
                                          entry[1],family='monospace',
                                          va='center',ha='center')
                                plot.rc('text',usetex=True)
                                self.text(str((col_ctr+0.37)/(ncols)),
                                          str((nrows-row_ctr)/(nrows+1)),
                                          entry[2].replace('_','\_'),
                                          va='center',ha='left')
                            row_ctr=row_ctr+1
                            if row_ctr>=nrows:
                                row_ctr=0
                                col_ctr=col_ctr+1
                        plot.savefig('o2graph_markers.png')
                        import matplotlib
                        if (matplotlib.get_backend()!='Agg' and 
                            matplotlib.get_backend()!='agg'):
                            plot.show()
                        finished=True
                        
                    # Handle the case of an acol command 
                    if match==False and finished==False:
                        self.gen_acol(o2scl_hdf,amp,cmd_name,
                                 strlist[ix+1:ix_next])

                    # If the user specified 'help set', then print
                    # the o2graph parameter documentation
                    if (cmd=='set' or cmd=='get') and (ix_next-ix)==2:
                        self.print_param_docs()

                    # If no arguments were given, then give a list of
                    # o2graph commands in addition to acol commands
                    if (ix_next-ix)==1:
                        print(str_line)
                        print('\nO2graph command-line options:\n')
                        for line in base_list:
                            strt='  -'+line[0]
                            while len(strt)<18:
                                strt=strt+' '
                            strt+=line[1]
                            print(strt)
                        print('\n'+str_line)
                        print('O2graph type-specific commands:\n')
                        extra_types.sort()
                        for typename in extra_types:
                            strt=typename+': '
                            first=True
                            for line in extra_list:
                                if line[0]==typename:
                                    if first==True:
                                        strt+=line[1]
                                        first=False
                                    else:
                                        strt+=', '+line[1]
                            str_list=textwrap.wrap(strt,77)
                            for i in range (0,len(str_list)):
                                if i==0:
                                    print(str_list[i])
                                else:
                                    print(' ',str_list[i])
                        print('\n'+str_line)
                        print('Additional o2graph help topics:',
                              'markers, cmaps, colors')

                elif cmd_name=='version':
                    
                    print('o2graph: A data table plotting and',
                          'processing program for O2scl.')
                    print(' Version '+version+'.')

                elif cmd_name=='plot':
                    
                    if self.verbose>2:
                        print('Process plot.')

                    self.plot(o2scl_hdf,amp,strlist[ix+1:ix_next])

                elif cmd_name=='rplot':
                    
                    if self.verbose>2:
                        print('Process rplot.')

                    self.rplot(o2scl_hdf,amp,strlist[ix+1:ix_next])

                elif cmd_name=='scatter':
                    
                    if self.verbose>2:
                        print('Process scatter.')

                    self.scatter(o2scl_hdf,amp,strlist[ix+1:ix_next])

                elif cmd_name=='histplot':
                    
                    if self.verbose>2:
                        print('Process histplot.')

                    self.histplot(o2scl_hdf,amp,strlist[ix+1:ix_next])

                elif cmd_name=='errorbar':
                    
                    if self.verbose>2:
                        print('Process errorbar.')

                    self.errorbar(o2scl_hdf,amp,strlist[ix+1:ix_next])

                elif cmd_name=='hist2dplot':
                    
                    if self.verbose>2:
                        print('Process hist2dplot.')
                        
                    self.hist2dplot(o2scl_hdf,amp,strlist[ix+1:ix_next])
                            
                elif cmd_name=='den-plot':
                    
                    if self.verbose>2:
                        print('Process den-plot.')

                    self.den_plot(o2scl_hdf,amp,strlist[ix+1:ix_next])
                
                elif cmd_name=='plot1':
                    
                    if self.verbose>2:
                        print('Process plot1.')
                        
                    self.plot1(o2scl_hdf,amp,strlist[ix+1:ix_next])
                            
                elif cmd_name=='plotv':
                    
                    if self.verbose>2:
                        print('Process plotv.')
                        
                    if ix_next-ix<2:
                        print('Not enough parameters for plotv option.')
                    else:
                        self.plotv(o2scl_hdf,amp,strlist[ix+1:ix_next])
                                                    
                elif cmd_name=='text':
                    
                    if self.verbose>2:
                        print('Process text.')
                        
                    if ix_next-ix<4:
                        print('Not enough parameters for text option.')
                    elif ix_next-ix<5:
                        self.text(strlist[ix+1],strlist[ix+2],strlist[ix+3])
                    else:
                        self.text(strlist[ix+1],strlist[ix+2],strlist[ix+3],
                                  **string_to_dict(strlist[ix+4]))
                        
                elif cmd_name=='ttext':
                    
                    if self.verbose>2:
                        print('Process ttext.')
                        
                    if ix_next-ix<4:
                        print('Not enough parameters for ttext option.')
                    elif ix_next-ix<5:
                        self.ttext(strlist[ix+1],strlist[ix+2],strlist[ix+3])
                    else:
                        self.ttext(strlist[ix+1],strlist[ix+2],strlist[ix+3],
                                   **string_to_dict(strlist[ix+4]))
                        
                elif cmd_name=='xlimits':
                    
                    if self.verbose>2:
                        print('Process xlimits.')
                        
                    if ix_next-ix<3:
                        print('Not enough parameters for xlimits option.')
                    else:
                        self.xlimits(float(strlist[ix+1]),float(strlist[ix+2]))
                        
                elif cmd_name=='ylimits':
                    
                    if self.verbose>2:
                        print('Process ylimits.')
                        
                    if ix_next-ix<3:
                        print('Not enough parameters for ylimits option.')
                    else:
                        self.ylimits(float(strlist[ix+1]),float(strlist[ix+2]))
                        
                elif cmd_name=='save':
                    if self.verbose>2:
                        
                        print('Process save.')
                    if ix_next-ix<2:
                        print('Not enough parameters for save option.')
                    else:
                        plot.savefig(strlist[ix+1])
                        
                elif cmd_name=='subplots':
                    
                    if self.verbose>2:
                        print('Process subplots.')
                        
                    if ix_next-ix<2:
                        print('Not enough parameters for subplots option.')
                    elif ix_next-ix<3:
                        self.subplots(int(strlist[ix+1]))
                    elif ix_next-ix<4:
                        self.subplots(int(strlist[ix+1]),int(strlist[ix+2]))
                    else:
                        self.subplots(int(strlist[ix+1]),int(strlist[ix+2]),
                                      **string_to_dict(strlist[ix+3]))
                        
                elif cmd_name=='selax':
                    
                    if self.verbose>2:
                        print('Process selax.')
                        
                    if ix_next-ix<2:
                        print('Not enough parameters for selax option.')
                    else:
                        self.selax(int(strlist[ix+1]))
                        
                elif cmd_name=='addcbar':
                    
                    if self.verbose>5:
                        print('Process addcbar.')
                        
                    if ix_next-ix<5:
                        print('Not enough parameters for selax option.')
                    elif ix_next-ix<6:
                        self.addcbar(float(strlist[ix+1]),
                                     float(strlist[ix+2]),
                                     float(strlist[ix+3]),
                                     float(strlist[ix+4]))
                    else:
                        self.addcbar(float(strlist[ix+1]),
                                     float(strlist[ix+2]),
                                     float(strlist[ix+3]),
                                     float(strlist[ix+4]),
                                     **string_to_dict(strlist[ix+5]))
                        
                elif cmd_name=='subadj':
                    
                    if self.verbose>2:
                        print('Process subadj.')

                    if ix_next-ix<2:
                        print('Not enough parameters for subadj option.')
                    else:
                        plot.subplots_adjust(**string_to_dict(strlist[ix+1]))
                        
                elif cmd_name=='xtitle':

                    if self.verbose>2:
                        print('Process xtitle.')

                    if ix_next-ix<2:
                        print('Not enough parameters for xtitle option.')
                    else:
                        self.xtitle(strlist[ix+1])
                        
                elif cmd_name=='ytitle':
                    
                    if self.verbose>2:
                        print('Process ytitle.')

                    if ix_next-ix<2:
                        print('Not enough parameters for ytitle option.')
                    else:
                        self.ytitle(strlist[ix+1])
                        
                elif cmd_name=='ztitle':
                    
                    if self.verbose>2:
                        print('Process ztitle.')

                    if ix_next-ix<2:
                        print('Not enough parameters for ztitle option.')
                    else:
                        self.ztitle(strlist[ix+1])
                        
                elif cmd_name=='line':
                    
                    if self.verbose>2:
                        print('Process line.')
                        
                    if ix_next-ix<5:
                        print('Not enough parameters for line option.')
                    elif ix_next-ix<6:
                        self.line(strlist[ix+1],strlist[ix+2],
                                  strlist[ix+3],strlist[ix+4])
                    else:
                        self.line(strlist[ix+1],strlist[ix+2],
                                  strlist[ix+3],strlist[ix+4],
                                  **string_to_dict(strlist[ix+5]))
                        
                elif cmd_name=='textbox':
                    
                    if self.verbose>2:
                        print('Process textbox.')
                        
                    if ix_next-ix<5:
                        print('Not enough parameters for textbox option.')
                    elif ix_next-ix<6:
                        self.textbox(strlist[ix+1],strlist[ix+2],
                                  strlist[ix+3],strlist[ix+4])
                    else:
                        self.textbox(strlist[ix+1],strlist[ix+2],
                                     strlist[ix+3],strlist[ix+4],
                                     **string_to_dict(strlist[ix+5]))
                        
                elif cmd_name=='arrow':
                    
                    if self.verbose>2:
                        print('Process arrow.')
                        
                    if ix_next-ix<6:
                        print('Not enough parameters for arrow option.')
                    elif ix_next-ix<7:
                        self.arrow(strlist[ix+1],strlist[ix+2],
                                   strlist[ix+3],strlist[ix+4],
                                   strlist[ix+5])
                    else:
                        self.arrow(strlist[ix+1],strlist[ix+2],
                                   strlist[ix+3],strlist[ix+4],
                                   strlist[ix+5],
                                   **string_to_dict(strlist[ix+6]))
                        
                elif cmd_name=='point':
                    
                    if self.verbose>2:
                        print('Process point.')
                        
                    if ix_next-ix<3:
                        print('Not enough parameters for point option.')
                    elif ix_next-ix<4:
                        self.point(strlist[ix+1],strlist[ix+2])
                    else:
                        self.point(strlist[ix+1],strlist[ix+2],
                                   **string_to_dict(strlist[ix+3]))
                        
                elif cmd_name=='python':
                    
                    if self.verbose>2:
                        print('Process python.')

                    print("The o2graph_plotter() object is named 'self'.")
                    print("Use 'import o2sclpy' and 'help(o2sclpy)' +"
                          "for more help on o2sclpy "+
                          "classes and functions.")
                    code.interact(local=locals())
                    
                elif cmd_name=='eval':
                    
                    if self.verbose>2:
                        print('Process eval.')

                    eval(strlist[ix+1],None,locals())
                    
                elif cmd_name=='image':
                    
                    if self.verbose>2:
                        print('Process image.')

                    import matplotlib.image as img
                    im = img.imread(strlist[ix+1])
                    default_plot(0.0,0.0,0.0,0.0)
                    plot.imshow(im)
                    plot.show()
                    
                elif cmd_name=='rect':
                    
                    if self.verbose>2:
                        print('Process rect.')
                        
                    if ix_next-ix<6:
                        print('Not enough parameters for rect option.')
                    elif ix_next-ix<7:
                        self.rect(strlist[ix+1],strlist[ix+2],
                                  strlist[ix+3],strlist[ix+4],
                                  strlist[ix+5])
                    else:
                        self.rect(strlist[ix+1],strlist[ix+2],
                                  strlist[ix+3],strlist[ix+4],
                                  strlist[ix+5],
                                  **string_to_dict(strlist[ix+6]))
                        
                elif cmd_name=='move-labels':
                    if self.verbose>2:
                        print('Process move-labels.')
                    self.move_labels()
                elif cmd_name=='show':
                    if self.verbose>2:
                        print('Process show.')
                    self.show()
                elif cmd_name=='move-labels':
                    if self.verbose>2:
                        print('Process move-labels.')
                    self.move_labels()
                elif cmd_name=='canvas':
                    if self.verbose>2:
                        print('Process canvas.')
                    self.canvas()
                elif cmd_name=='clf':
                    if self.verbose>2:
                        print('Process clf.')
                    plot.clf()
                    self.canvas_flag=False
                elif cmd_name=='backend':
                    if self.verbose>2:
                        print('Process backend in __init__.py.')
                elif cmd_name=='new-cmaps':
                    if self.verbose>2:
                        print('Process reds2.')
                    self.new_cmaps()
                else:
                    if self.verbose>2:
                        print('Process acol command '+cmd_name+'.')
                    self.gen_acol(o2scl_hdf,amp,cmd_name,
                                  strlist[ix+1:ix_next])
                    
                # Increment to the next option
                ix=ix_next
                
            if self.verbose>2:
                print('Going to next.')
                
        # End of function parse_string_list()
        return
    
