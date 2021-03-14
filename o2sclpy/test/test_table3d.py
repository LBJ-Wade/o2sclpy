import o2sclpy
import copy
import numpy
import ctypes

def def_table3d(link):
    t3d=o2sclpy.table3d(link)
    ug_x=o2sclpy.uniform_grid_end_width.init(link,1,10,1)
    ug_y=o2sclpy.uniform_grid_end.init(link,1,6,12)
    t3d.set_xy_grid('x',ug_x,'y',ug_y)
    t3d.function_slice('(x-5)^2+(y-3)^2','z')
    return t3d

def subtest_basic(link):

    t3d=def_table3d(link)
    z=t3d.get_slice('z')
    assert z.to_numpy().shape==(z.size1(),z.size2()),'get_slice,etc.'
    xtmp=t3d.get_grid_x(5)
    ytmp=t3d.get_grid_y(5)
    ztmp=t3d.get(5,5,'z')
    assert (xtmp-5)**2+(ytmp-3)**2==ztmp,'get'
    nx=ctypes.c_size_t(0)
    ny=ctypes.c_size_t(0)
    t3d.get_size(nx,ny)
    print('herez',nx,ny)
    # Make sure summary() works
    t3d.summary()
    return

def subtest_hdf5(link):
    
    t3d1=def_table3d(link)

    # Write t3d1 to a file
    hf=o2sclpy.hdf_file(link)
    hf.open_or_create(b'temp.o2')
    o2sclpy.hdf_output_table3d(link,hf,t3d1,b'table3d')
    hf.close()

    # Open the file and read into t3d2
    hf.open(b'temp.o2',False,True)
    name=o2sclpy.std_string(link)
    t3d2=o2sclpy.table3d(link)
    o2sclpy.hdf_input_n_table3d(link,hf,t3d2,name)
    hf.close()
    assert name.to_bytes()==b'table3d','name after hdf_input()'
    assert t3d2.get_nx()==t3d1.get_nx(),"nlines after hdf_input()"
    return

def test_all():
    link=o2sclpy.linker()
    link.link_o2scl_o2graph()

    subtest_basic(link)
    subtest_hdf5(link)
    return
    
    
