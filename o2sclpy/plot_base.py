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
import numpy

import matplotlib.pyplot as plot

# To create new color maps
from matplotlib.colors import LinearSegmentedColormap

# For rectangles
import matplotlib.patches as patches

from o2sclpy.utils import parse_arguments, string_to_dict
from o2sclpy.utils import force_bytes, default_plot, get_str_array

class plot_base:
    """
    A base class for plotting classes :py:class:`o2sclpy.plotter` and
    :py:class:`o2sclpy.o2graph_plotter` . The principal purpose
    of this class is just to provide some additional simplification
    to python code which makes plots using matplotlib.
    """

    last_image=0
    """
    The last image object created (used for addcbar)
    """
    axes=0
    """ 
    Axis object
    """
    axis_list=[]
    """
    2D array of axis objects when subplots is used
    """
    fig=0
    """ 
    Figure object
    """
    canvas_flag=False
    """
    If True, then the figure and axes objects have been created
    (default False)
    """
    
    # Quantities modified by set/get
    
    logx=False
    """
    If True, then use a logarithmic x axis (default False)
    """
    logy=False
    """
    If True, then use a logarithmic y axis (default False)
    """
    logz=False
    """
    If True, then use a logarithmic z axis (default False)
    """
    ztitle=''
    """
    Title for z axis (default '')
    """
    xlo=0
    """
    Lower limit for x axis (default 0)
    """
    xhi=0
    """
    Upper limit for x axis (default 0)
    """
    xset=False
    """ 
    If True, then the x axis limits have been set (default False)
    """
    ylo=0
    """
    Lower limit for y axis (default 0)
    """
    yhi=0
    """
    Upper limit for y axis (default 0)
    """
    yset=False
    """ 
    If True, then the y axis limits have been set (default False)
    """
    zlo=0
    """
    Lower limit for z axis (default 0)
    """
    zhi=0
    """
    Upper limit for z axis (default 0)
    """
    zset=False
    """ 
    If True, then the z axis limits have been set (default False)
    """
    verbose=1
    """
    Verbosity parameter (default 1)
    """
    colbar=False
    """
    If True, then include a color legend for density plots (default False)
    """
    left_margin=0.14
    """
    Left plot margin (default 0.14)
    """
    right_margin=0.04
    """
    Right plot margin (default 0.04)
    """
    top_margin=0.04
    """
    Top plot margin (default 0.04)
    """
    bottom_margin=0.12
    """
    Bottom plot margin (default 0.12)
    """
    font=16
    """
    Font size for :py:func:`o2sclpy.plot_base.text()`,
    :py:func:`o2sclpy.plot_base.ttext()`, and axis titles (default
    16). Axis labels are set by this size times 0.8 .
    """
    fig_dict=''
    """
    A dictionary which refers to the figure and axis defaults for
    :py:func:`o2sclpy.default_plot()`. The default value is
    ``('fig_size_x=6.0,fig_size_y=6.0,ticks_in=False,'+
    'rt_ticks=False,left_margin=0.14,right_margin=0.04,'+
    'bottom_margin=0.12,top_margin=0.04,fontsize=16')`` . The x and y
    sizes of the figure object are in fig_size_x and fig_size_y. The
    value ticks_in refers to whether or not the ticks are inside or
    outside the plot. The value of rt_ticks refers to whether or not
    tick marks are plotted on the right and top sides of the plot. The
    font size parameter is multiplied by 0.8 and then used for the
    axis labels.
    """
    ticks_in=False
    """
    If true, move the ticks inside (default False)
    """
    rt_ticks=False
    """
    If true, include ticks on right side and top (default False)
    """
    yt_resolution=(512,512)
    """
    Resolution for yt rendering (default (512,512))
    """
    yt_focus=[0.5,0.5,0.5]
    """
    yt camera focus (default [0.5,0.5,0.5])
    """
    yt_position=[1.5,0.6,0.7]
    """
    yt camera position (default [1.5,0.6,0.7])
    """
    yt_path=''
    """
    yt animation path (default '')
    """
    yt_tf=0
    """
    The yt transfer function
    """
    yt_sigma_clip=4.0
    """
    The sigma_clip parameter for yt (default 4.0)
    """
    new_cmaps_defined=False
    """
    True if new colormaps were defined with 'new-cmaps'
    """
    yt_volume_data=[]
    """
    Current list of data objects for volume sources
    """
    yt_volume_bbox=[]
    """
    Current list of bbox arrays for volume sources
    """
    yt_vols=[]
    """
    Current list of volume source objects
    """
    yt_data_sources=[]
    """
    Current list of yt data source objects
    """
    
    def yt_unique_keyname(self,prefix):
        if self.yt_scene==0:
            return(prefix)
        current=prefix
        unique=False
        count=1
        while unique==False:
            unique=True
            if count>1:
                current=prefix+str(count)
            for key, value in self.yt_scene.sources.items():
                if key==current:
                    unique=False
            if unique==False:
                count=count+1
        if self.verbose>0 and count>1:
            print('Key name',prefix,'changed to unique name',current)
        # End of function plot_base::yt_unique_keyname()
        return(current)
    
    def new_cmaps(self):
        """
        Add a few new colormaps
        """
        # A white to red colormap
        cdict={'red': ((0.0,1.0,1.0),(1.0,1.0,1.0)),
               'green': ((0.0,1.0,1.0),(1.0,0.0,0.0)),
               'blue': ((0.0,1.0,1.0),(1.0,0.0,0.0))}
        reds2=LinearSegmentedColormap('reds2',cdict)
        plot.register_cmap(cmap=reds2)
        # A new version of the ``jet`` colormap which starts with
        # white instead of blue. In order, the index colors are white,
        # blue, green, yellow, orange, and red
        cdict={'red': ((0.0,1.0,1.0),(0.2,0.0,0.0),
                       (0.4,0.0,0.0),(0.6,1.0,1.0),
                       (0.8,1.0,1.0),(1.0,1.0,1.0)),
               'green': ((0.0,1.0,1.0),(0.2,0.0,0.0),
                         (0.4,0.5,0.5),(0.6,1.0,1.0),
                         (0.8,0.6,0.6),(1.0,0.0,0.0)),
               'blue': ((0.0,1.0,1.0),(0.2,1.0,1.0),
                        (0.4,0.0,0.0),(0.6,0.0,0.0),
                        (0.8,0.0,0.0),(1.0,0.0,0.0))}
        jet2=LinearSegmentedColormap('jet2',cdict)
        plot.register_cmap(cmap=jet2)
        # A new version of the ``pastel`` colormap which starts with
        # white instead of blue. In order, the index colors are white,
        # blue, green, yellow, orange, and red
        cdict={'red': ((0.0,1.0,1.0),(0.2,0.3,0.3),
                       (0.4,0.3,0.3),(0.6,1.0,1.0),
                       (0.8,1.0,1.0),(1.0,1.0,1.0)),
               'green': ((0.0,1.0,1.0),(0.2,0.3,0.3),
                         (0.4,0.5,0.5),(0.6,1.0,1.0),
                         (0.8,0.6,0.6),(1.0,0.3,0.3)),
               'blue': ((0.0,1.0,1.0),(0.2,1.0,1.0),
                        (0.4,0.3,0.3),(0.6,0.3,0.3),
                        (0.8,0.3,0.3),(1.0,0.3,0.3))}
        pastel2=LinearSegmentedColormap('pastel2',cdict)
        plot.register_cmap(cmap=pastel2)
        # A white to green colormap
        cdict={'red': ((0.0,1.0,1.0),(1.0,0.0,0.0)),
               'green': ((0.0,1.0,1.0),(1.0,1.0,1.0)),
               'blue': ((0.0,1.0,1.0),(1.0,0.0,0.0))}
        greens2=LinearSegmentedColormap('greens2',cdict)
        plot.register_cmap(cmap=greens2)
        # A white to blue colormap
        cdict={'red': ((0.0,1.0,1.0),(1.0,0.0,0.0)),
               'green': ((0.0,1.0,1.0),(1.0,0.0,0.0)),
               'blue': ((0.0,1.0,1.0),(1.0,1.0,1.0))}
        blues2=LinearSegmentedColormap('blues2',cdict)
        plot.register_cmap(cmap=blues2)
        new_cmaps_defined=True
        # End of function plot_base::new_cmaps()
        return
        
    def set(self,name,value):
        """
        Set the value of parameter named ``name`` to value ``value``
        """
        if name=='logx':
            if value=='False' or value=='0':
                self.logx=False
            else:
                self.logx=True
        elif name=='logy':
            if value=='False' or value=='0':
                self.logy=False
            else:
                self.logy=True
        elif name=='logz':
            if value=='False' or value=='0':
                self.logz=False
            else:
                self.logz=True
        elif name=='xlo':
            if value[0]=='(':
                self.xlo=float(eval(value))
            else:
                self.xlo=float(value)
            self.xset=True
        elif name=='xhi':
            if value[0]=='(':
                self.xhi=float(eval(value))
            else:
                self.xhi=float(value)
            self.xset=True
        elif name=='xset':
            if value=='False' or value=='0':
                self.xset=False
            else:
                self.xset=True
        elif name=='ylo':
            if value[0]=='(':
                self.ylo=float(eval(value))
            else:
                self.ylo=float(value)
            self.yset=True
        elif name=='yhi':
            if value[0]=='(':
                self.yhi=float(eval(value))
            else:
                self.yhi=float(value)
            self.yset=True
        elif name=='yset':
            if value=='False' or value=='0':
                self.xset=False
            else:
                self.xset=True
        elif name=='zlo':
            if value[0]=='(':
                self.zlo=float(eval(value))
            else:
                self.zlo=float(value)
            self.zset=True
        elif name=='zhi':
            if value[0]=='(':
                self.zhi=float(eval(value))
            else:
                self.zhi=float(value)
            self.zset=True
        elif name=='zset':
            if value=='False' or value=='0':
                self.zset=False
            else:
                self.zset=True
        elif name=='verbose':
            self.verbose=int(value)
        elif name=='colbar':
            if value=='False' or value=='0':
                self.colbar=False
            else:
                self.colbar=True
        elif name=='font':
            self.font=float(value)
        elif name=='fig_dict':
            self.fig_dict=value
        elif name=='yt_resolution':
            left_paren=value.find('(')
            right_paren=value.find(')')
            value=value[left_paren+1:right_paren]
            value=value.split(',')
            self.yt_resolution=(float(value[0]),float(value[1]))
        elif name=='yt_focus':
            left_brace=value.find('[')
            right_brace=value.find(']')
            value=value[left_brace+1:right_brace]
            value=value.split(',')
            self.yt_focus=[float(value[0]),float(value[1]),
                           float(value[2])]
        elif name=='yt_sigma_clip':
            self.yt_sigma_clip=float(value)
        elif name=='yt_position':
            left_brace=value.find('[')
            right_brace=value.find(']')
            value=value[left_brace+1:right_brace]
            value=value.split(',')
            self.yt_position=[float(value[0]),float(value[1]),
                              float(value[2])]
        elif name=='yt_path':
            self.yt_path=value
        else:
            print('No variable named',name)
            
        if self.verbose>0:
            print('Set',name,'to',value)
            
        # End of function plot_base::set()
        return

    def yt_def_vol(self):
        """
        Create a default yt volume source for rendering other objects
        """
        import yt
        from yt.visualization.volume_rendering.api \
            import VolumeSource

        if self.verbose>0:
            print('No volume object, adding yt volume.')
            
        self.yt_tf=yt.ColorTransferFunction((0,1),grey_opacity=False)
        self.yt_tf.add_gaussian(2,0,[0,0,0,0])
            
        arr=numpy.zeros(shape=(2,2,2))
        bbox=numpy.array([[0.0,1.0],[0.0,1.0],[0.0,1.0]])
        ds=yt.load_uniform_grid(dict(density=arr),
                                arr.shape,bbox=bbox)
        vol=VolumeSource(ds,field='density')
        vol.log_field=False
            
        vol.set_transfer_function(self.yt_tf)
        if self.yt_created_scene==False:
            self.yt_create_scene()

        kname=self.yt_unique_keyname('o2graph_vol')
        self.yt_scene.add_source(vol,keyname=kname)
                            
        if self.yt_created_camera==False:
            self.yt_create_camera(ds)
            
        # End of function plot_base::yt_def_vol()
        return
            
    def get(self,name):
        """
        Output the value of parameter named ``name``
        """
        if name=='colbar':
            print('The value of colbar is',self.colbar,'.')
        if name=='logx':
            print('The value of logx is',self.logx,'.')
        if name=='logy':
            print('The value of logy is',self.logy,'.')
        if name=='logz':
            print('The value of logz is',self.logz,'.')
        if name=='verbose':
            print('The value of verbose is',self.verbose,'.')
        if name=='xhi':
            print('The value of xhi is',self.xhi,'.')
        if name=='xlo':
            print('The value of xlo is',self.xlo,'.')
        if name=='xset':
            print('The value of xset is',self.xset,'.')
        if name=='yhi':
            print('The value of yhi is',self.yhi,'.')
        if name=='ylo':
            print('The value of ylo is',self.ylo,'.')
        if name=='yset':
            print('The value of yset is',self.yset,'.')
        if name=='zhi':
            print('The value of zhi is',self.zhi,'.')
        if name=='zlo':
            print('The value of zlo is',self.zlo,'.')
        if name=='zset':
            print('The value of zset is',self.zset,'.')
        if name=='fig_dict':
            print('The value of fig_dict is',self.fig_dict,'.')
        if name=='yt_axis':
            print('The value of yt_axis is',self.yt_axis,'.')
        if name=='yt_axis_color':
            print('The value of yt_axis_color is',self.yt_axis_color,'.')
        if name=='yt_axis_labels_flat':
            print('The value of yt_axis_labels_flat is',
                  self.yt_axis_labels_flat,'.')
        if name=='yt_axis_resolution':
            print('The value of yt_axis_resolution is',
                  self.yt_axis_resolution,'.')
        if name=='yt_focus':
            print('The value of yt_focus is',self.yt_focus,'.')
        if name=='yt_sigma_clip':
            print('The value of yt_sigma_clip is',self.yt_sigma_clip,'.')
        if name=='yt_position':
            print('The value of yt_position is',self.yt_position,'.')
        if name=='yt_path':
            print('The value of yt_path is',self.yt_path,'.')
        # End of function plot_base::get()
        return

    def reset_xlimits(self):
        """
        Reset x axis limits
        """
        self.xset=False
        # End of function plot_base::reset_xlimits()
        return

    def xlimits(self,xlo,xhi):
        """
        Set the x-axis limits
        """
        self.xlo=xlo
        self.xhi=xhi
        self.xset=True
        if self.canvas_flag==True:
            self.axes.set_xlim(self.xlo,self.xhi)
        # End of function plot_base::xlimits()
        return

    def reset_ylimits(self):
        """
        Reset y axis limits
        """
        self.yset=False
        # End of function plot_base::reset_ylimits()
        return

    def ylimits(self,ylo,yhi):
        """
        Set the y-axis limits
        """
        self.ylo=ylo
        self.yhi=yhi
        self.yset=True
        if self.canvas_flag==True:
            self.axes.set_ylim(self.ylo,self.yhi)
        # End of function plot_base::ylimits()
        return

    def reset_zlimits(self):
        """
        Reset z axis limits
        """
        self.zset=False
        # End of function plot_base::reset_zlimits()
        return

    def zlimits(self,zlo,zhi):
        """
        Set the z-axis limits
        """
        self.zlo=zlo
        self.zhi=zhi
        self.zset=True
        #if self.canvas_flag==True:
        #plot.zlim([zlo,zhi])
        # End of function plot_base::zlimits()
        return

    def line(self,x1,y1,x2,y2,**kwargs):
        """
        Plot a line from :math:`(x_1,y_1)` to :math:`(x_2,y_2)`
        """
        if self.verbose>2:
            print('Line',x1,y1,x2,y1)
        if self.canvas_flag==False:
            self.canvas()
        self.axes.plot([float(eval(x1)),float(eval(x2))],
                       [float(eval(y1)),float(eval(y2))],**kwargs)
        # End of function plot_base::line()
        return

    def arrow(self,x1,y1,x2,y2,arrowprops,**kwargs):
        """
        Plot an arrow from :math:`(x_1,y_1)` to :math:`(x_2,y_2)`
        """
        if self.verbose>2:
            print('Arrow',x1,y1,x2,y1,arrowprops)
        if self.canvas_flag==False:
            self.canvas()
        self.axes.annotate("",xy=(float(eval(x2)),float(eval(y2))),
                           xycoords='data',
                           xytext=(float(eval(x1)),float(eval(y1))),
                           textcoords='data',
                           arrowprops=string_to_dict(arrowprops))
        # End of function plot_base::arrow()
        return

    def point(self,xval,yval,**kwargs):
        """
        Plot a point at location (xval,yval)
        """
        if self.verbose>2:
            print('point',xval,yval,kwargs)
        if self.canvas_flag==False:
            self.canvas()
        self.axes.plot([float(eval(xval))],[float(eval(yval))],**kwargs)
        if self.xset==True:
            self.axes.set_xlim(self.xlo,self.xhi)
        if self.yset==True:
            self.axes.set_ylim(self.ylo,self.yhi)
        # End of function plot_base::point()
        return

    def rect(self,x1,y1,x2,y2,angle,**kwargs):
        """
        Plot a rectangle from :math:`(x_1,y_1)` to :math:`(x_2,y_2)`
        """
        if self.verbose>2:
            print('Rect',x1,y1,x2,y1)
        if self.canvas_flag==False:
            self.canvas()
        fx1=float(eval(x1))
        fx2=float(eval(x2))
        fy1=float(eval(y1))
        fy2=float(eval(y2))
        left=fx1
        if fx2<fx1:
            left=fx2
        lower=fy1
        if fy2<fy1:
            lower=fy2
        w=abs(fx1-fx2)
        h=abs(fy1-fy2)
        if self.canvas_flag==False:
            self.canvas()
        r=patches.Rectangle((left,lower),w,h,angle,**kwargs)
        self.axes.add_patch(r)
        # End of function plot_base::rect()
        return

    def show(self):
        """
        Call the ``matplotlib`` show function.
        """
        plot.show()
        # End of function plot_base::show()
        return

    def save(self,filename):
        """
        Save plot to file named ``filename``. If the verbose parameter is
        greater than zero, then this function prints the filename to
        the screen.
        """
        if self.verbose>0:
            print('Saving as',filename,'.')
        plot.savefig(filename)
        # End of function plot_base::save()
        return

    def ttext(self,tx,ty,textstr,**kwargs):
        """
        Plot text in the native coordinate system using a transAxes
        transformation. This function uses the class font size and and
        centering in the horizontal and vertical directions by
        default. A figure and axes are created using 
        :py:func:`o2sclpy.plot_base.canvas()`,
        if they
        have not been created already. If ``tx`` and ``ty`` are strings, then
        they are passed through the ``eval()`` function and converted to
        floating-point numbers.
        """
        if self.canvas_flag==False:
            self.canvas()
            
        ha_present=False
        for key in kwargs:
            if key=='ha' or key=='horizontalalignment':
                ha_present=True
        if ha_present==False:
            kwargs=dict(kwargs,ha='center')
            
        va_present=False
        for key in kwargs:
            if key=='va' or key=='verticalalignment':
                va_present=True
        if va_present==False:
            kwargs=dict(kwargs,va='center')

        fontsize_present=False
        for key in kwargs:
            if key=='fontsize':
                fontsize_present=True
        if fontsize_present==False:
            kwargs=dict(kwargs,fontsize=self.font)

        transform_present=False
        for key in kwargs:
            if key=='transform':
                transform_present=True
        if transform_present==False:
            kwargs=dict(kwargs,transform=self.axes.transAxes)

        if isinstance(tx,str):
            tx=float(eval(tx))
        if isinstance(ty,str):
            ty=float(eval(ty))

        self.axes.text(tx,ty,textstr,**kwargs)

        # End of function plot_base::ttext()
        return

    def text(self,tx,ty,textstr,**kwargs):
        """Plot text in the axis coordinate system transforming using the
        class font size and and centering in the horizontal and
        vertical directions by default. A figure and axes are created
        using :py:func:`o2sclpy.plot_base.canvas()`, if they have not
        been created already. If ``tx`` and ``ty`` are strings, then
        they are passed through the ``eval()`` function and converted
        to floating-point numbers.
        """
        if self.canvas_flag==False:
            self.canvas()
            
        ha_present=False
        for key in kwargs:
            if key=='ha' or key=='horizontalalignment':
                ha_present=True
        if ha_present==False:
            kwargs=dict(kwargs,ha='center')
            
        va_present=False
        for key in kwargs:
            if key=='va' or key=='verticalalignment':
                va_present=True
        if va_present==False:
            kwargs=dict(kwargs,va='center')

        fontsize_present=False
        for key in kwargs:
            if key=='fontsize':
                fontsize_present=True
        if fontsize_present==False:
            kwargs=dict(kwargs,fontsize=self.font)

        if isinstance(tx,str):
            tx=float(eval(tx))
        if isinstance(ty,str):
            ty=float(eval(ty))

        self.axes.text(tx,ty,textstr,**kwargs)
        
        # End of function plot_base::text()
        return

    def textbox(self,tx,ty,str,boxprops,**kwargs):
        """
        Plot text in the axis coordinate system with a box
        """
        if self.canvas_flag==False:
            self.canvas()
            
        ha_present=False
        for key in kwargs:
            if key=='ha':
                ha_present=True
        if ha_present==False:
            kwargs=dict(kwargs,ha='center')
            
        va_present=False
        for key in kwargs:
            if key=='va':
                va_present=True
        if va_present==False:
            kwargs=dict(kwargs,va='center')

        self.axes.text(float(eval(tx)),float(eval(ty)),str,
                       fontsize=self.font,
                       transform=self.axes.transAxes,
                       bbox=string_to_dict(boxprops),**kwargs)
        # End of function plot_base::textbox()
        return

    def subplots(self,nr,nc=1,**kwargs):
        plot.rc('text',usetex=True)
        plot.rc('font',family='serif')
        plot.rcParams['lines.linewidth']=0.5
        dct=string_to_dict(self.fig_dict)
        if not('fig_size_x' in dct):
            dct['fig_size_x']=6.0
        if not('fig_size_y' in dct):
            dct['fig_size_y']=6.0
        self.fig,axis_temp=plot.subplots(nrows=nr,ncols=nc,
                                         figsize=(dct["fig_size_x"],
                                                  dct["fig_size_y"]))
        if nr==1 and nc==1:
            self.axis_list.append(axis_temp)
        elif nr==1:
            for i in range(0,nc):
                self.axis_list.append(axis_temp[i])
        elif nc==1:
            for i in range(0,nr):
                self.axis_list.append(axis_temp[i])
        else:
            for i in range(0,nr):
                for j in range(0,nc):
                    self.axis_list.append(axis_temp[i][j])
        for i in range(0,len(self.axis_list)):
            self.axis_list[i].minorticks_on()
            self.axis_list[i].tick_params('both',length=12,width=1,
                                          which='major')
            self.axis_list[i].tick_params('both',length=5,width=1,
                                          which='minor')
            self.axis_list[i].tick_params(labelsize=self.font*0.8)
        self.canvas_flag=True
        # End of function plot_base::subplots()
        return

    def xtitle(self,args,scale=0.6,font=30,color=(1,1,1,1),
               keyname='o2graph_x_title'):
        """
        Add a title for the x-axis

        yt-mode: <text> [x loc] [y loc] [z loc]
        """
        if self.yt_scene!=0:
            if (self.xset==False or self.yset==False or
                self.zset==False):
                print('Cannot place xtitle before limits set.')
                return
            xval=0.5
            yval=-0.1
            zval=-0.1
            if len(args)>2:
                xval=(float(eval(args[1]))-self.xlo)/(self.xhi-self.xlo)
            if len(args)>3:
                yval=(float(eval(args[2]))-self.ylo)/(self.yhi-self.ylo)
            if len(args)>4:
                zval=(float(eval(args[3]))-self.zlo)/(self.zhi-self.zlo)
            kname=self.yt_unique_keyname(keyname)
            self.yt_text_to_scene([xval,yval,zval],
                                  args[0],scale=scale,font=font,keyname=kname)
        elif args[0]!='' and args[0]!='none':
            if self.canvas_flag==False:
                self.canvas()
            self.axes.set_xlabel(args[0],fontsize=self.font)
        # End of function plot_base::xtitle()
        return
            
    def ytitle(self,args,scale=0.6,font=30,color=(1,1,1,1),
               keyname='o2graph_y_title'):
        """
        Add a title for the y-axis

        yt-mode: <text> [x loc] [y loc] [z loc]
        """
        if self.yt_scene!=0:
            if (self.xset==False or self.yset==False or
                self.zset==False):
                print('Cannot place ytitle before limits set.')
                return
            xval=-0.1
            yval=0.5
            zval=-0.1
            if len(args)>2:
                xval=(float(eval(args[1]))-self.xlo)/(self.xhi-self.xlo)
            if len(args)>3:
                yval=(float(eval(args[2]))-self.ylo)/(self.yhi-self.ylo)
            if len(args)>4:
                zval=(float(eval(args[3]))-self.zlo)/(self.zhi-self.zlo)
            kname=self.yt_unique_keyname(keyname)
            self.yt_text_to_scene([xval,yval,zval],
                                  args[0],scale=scale,font=font,keyname=kname)
        elif args[0]!='' and args[0]!='none':
            if self.canvas_flag==False:
                self.canvas()
            self.axes.set_ylabel(args[0],fontsize=self.font)
        # End of function plot_base::ytitle()
        return
        
    def ztitle(self,args,scale=0.6,font=30,color=(1,1,1,1),
               keyname='o2graph_z_title'):
        """
        Add a title for the z-axis

        yt-mode: <text> [x loc] [y loc] [z loc]
        """
        if self.yt_scene!=0:
            if (self.xset==False or self.yset==False or
                self.zset==False):
                print('Cannot place ztitle before limits set.')
                return
            xval=-0.1
            yval=-0.1
            zval=0.5
            if len(args)>2:
                xval=(float(eval(args[1]))-self.xlo)/(self.xhi-self.xlo)
            if len(args)>3:
                yval=(float(eval(args[2]))-self.ylo)/(self.yhi-self.ylo)
            if len(args)>4:
                zval=(float(eval(args[3]))-self.zlo)/(self.zhi-self.zlo)
            kname=self.yt_unique_keyname(keyname)
            self.yt_text_to_scene([xval,yval,zval],
                                  args[0],scale=scale,font=font,
                                  keyname=kname)
        else:
            print('No yt scene has been created for ztitle.')
        # End of function plot_base::ztitle()
        return
    
    def selax(self,nr,nc=0):
        nr_temp=len(self.axis_list)
        try:
            nc_temp=len(self.axis_list[0])
        except:
            nc_temp=1
        if nc_temp==1:
            self.axes=self.axis_list[nr]
        else:
            self.axes=self.axis_list[nr][nc]
        # End of function plot_base::selax()
        return

    def addcbar(self,left,bottom,width,height,**kwargs):
        axis_temp=self.fig.add_axes([left,bottom,width,height])
        self.axis_list.append(axis_temp)
        self.axes=axis_temp
        cbar=self.fig.colorbar(self.last_image,cax=self.axes,**kwargs)
        cbar.ax.tick_params(labelsize=self.font*0.8)
        # End of function plot_base::addcbar()
        return

    def canvas(self):
        """
        This function creates a default figure using default_plot()
        and axis object using the xtitle and ytitle for the
        axis titles and xlo, xhi, ylo, and yhi for the axis limits.
        """
        if self.verbose>2:
            print('Canvas')
            
        dct=string_to_dict(self.fig_dict)
        (self.fig,self.axes)=default_plot(**dct)
        
        # Plot limits
        if self.xset==True:
            self.axes.set_xlim(self.xlo,self.xhi)
        if self.yset==True:
            self.axes.set_ylim(self.ylo,self.yhi)
        self.canvas_flag=True
        # End of function plot_base::canvas()
        return

    def move_labels(self):
        """
        Move tick labels
        """
        for label in self.axes.get_xticklabels():
            t=label.get_position()
            t2=t[0],t[1]-0.01
            label.set_position(t2)
            label.set_fontsize(16)
        for label in self.axes.get_yticklabels():
            t=label.get_position()
            t2=t[0]-0.01,t[1]
            label.set_position(t2)
            label.set_fontsize(16)
        # End of function plot_base::move_labels()
        return
