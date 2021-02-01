"""
  -------------------------------------------------------------------

  Copyright (C) 2020-2021, Andrew W. Steiner

  This file is part of O2scl.

  O2scl is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  (at your option) any later version.

  O2scl is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with O2scl. If not, see <http://www.gnu.org/licenses/>.
  -------------------------------------------------------------------
"""

import ctypes
from abc import abstractmethod
from o2sclpy.utils import force_bytes


class table:
    """
    Python interface for class :ref:`table<> <o2scl:table<>>`.
    """

    _ptr=0
    _link=0

    def __init__(self,link):
        """
        Init function for class table<> .
        """

        f=link.o2scl.o2scl_create_table__
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._link=link
        return

    def __del__(self):
        """
        Delete function for class table<> .
        """

        f=self._link.o2scl.o2scl_free_table__
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    def set(self,col,row,val):
        """
        Wrapper for table<>::set() .
        wrapper for :ref:`o2sclp:table<>::set()`.
        """
        col_=ctypes.c_char_p(force_bytes(col))
        func=self._link.o2scl.o2scl_table___set
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_double]
        func(self._ptr,col_,row,val)
        return

    def get(self,col,row):
        """
        Wrapper for table<>::get() .
        wrapper for :ref:`o2sclp:table<>::get()`.
        """
        col_=ctypes.c_char_p(force_bytes(col))
        func=self._link.o2scl.o2scl_table___get
        func.restype=ctypes.c_double
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t]
        ret=func(self._ptr,col_,row)
        return ret

    def get_ncolumns(self):
        """
        Wrapper for table<>::get_ncolumns() .
        wrapper for :ref:`o2sclp:table<>::get_ncolumns()`.
        """
        func=self._link.o2scl.o2scl_table___get_ncolumns
        func.restype=ctypes.c_size_t
        func.argtypes=[ctypes.c_void_p]
        ret=func(self._ptr,)
        return ret

    def get_nlines(self):
        """
        Wrapper for table<>::get_nlines() .
        wrapper for :ref:`o2sclp:table<>::get_nlines()`.
        """
        func=self._link.o2scl.o2scl_table___get_nlines
        func.restype=ctypes.c_size_t
        func.argtypes=[ctypes.c_void_p]
        ret=func(self._ptr,)
        return ret

    def set_nlines(self,lines):
        """
        Wrapper for table<>::set_nlines() .
        wrapper for :ref:`o2sclp:table<>::set_nlines()`.
        """
        func=self._link.o2scl.o2scl_table___set_nlines
        func.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
        func(self._ptr,lines)
        return

    def new_column(self,col):
        """
        Wrapper for table<>::new_column() .
        wrapper for :ref:`o2sclp:table<>::new_column()`.
        """
        col_=ctypes.c_char_p(force_bytes(col))
        func=self._link.o2scl.o2scl_table___new_column
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
        func(self._ptr,col_)
        return

    def get_column_name(self,icol):
        """
        Wrapper for table<>::get_column_name() .
        wrapper for :ref:`o2sclp:table<>::get_column_name()`.
        """
        func=self._link.o2scl.o2scl_table___get_column_name
        func.restype=ctypes.c_char_p
        func.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
        ret=func(self._ptr,icol)
        return ret

    def clear(self):
        """
        Wrapper for table<>::clear() .
        wrapper for :ref:`o2sclp:table<>::clear()`.
        """
        func=self._link.o2scl.o2scl_table___clear
        func.argtypes=[ctypes.c_void_p]
        func(self._ptr,)
        return

    def clear_data(self):
        """
        Wrapper for table<>::clear_data() .
        wrapper for :ref:`o2sclp:table<>::clear_data()`.
        """
        func=self._link.o2scl.o2scl_table___clear_data
        func.argtypes=[ctypes.c_void_p]
        func(self._ptr,)
        return

    def clear_table(self):
        """
        Wrapper for table<>::clear_table() .
        wrapper for :ref:`o2sclp:table<>::clear_table()`.
        """
        func=self._link.o2scl.o2scl_table___clear_table
        func.argtypes=[ctypes.c_void_p]
        func(self._ptr,)
        return

    def clear_constants(self):
        """
        Wrapper for table<>::clear_constants() .
        wrapper for :ref:`o2sclp:table<>::clear_constants()`.
        """
        func=self._link.o2scl.o2scl_table___clear_constants
        func.argtypes=[ctypes.c_void_p]
        func(self._ptr,)
        return

class table_units(table):
    """
    Python interface for class :ref:`table_units<> <o2scl:table_units<>>`.
    """

    def __init__(self,link):
        """
        Init function for class table_units<> .
        """

        f=link.o2scl.o2scl_create_table_units__
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._link=link
        return

    def __del__(self):
        """
        Delete function for class table_units<> .
        """

        f=self._link.o2scl.o2scl_free_table_units__
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    def get_unit(self,col):
        """
        Wrapper for table_units<>::get_unit() .
        wrapper for :ref:`o2sclp:table_units<>::get_unit()`.
        """
        col_=ctypes.c_char_p(force_bytes(col))
        func=self._link.o2scl.o2scl_table_units___get_unit
        func.restype=ctypes.c_char_p
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
        ret=func(self._ptr,col_)
        return ret

    def set_unit(self,col,unit):
        """
        Wrapper for table_units<>::set_unit() .
        wrapper for :ref:`o2sclp:table_units<>::set_unit()`.
        """
        col_=ctypes.c_char_p(force_bytes(col))
        unit_=ctypes.c_char_p(force_bytes(unit))
        func=self._link.o2scl.o2scl_table_units___set_unit
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p]
        func(self._ptr,col_,unit_)
        return

    def convert_to_unit(self,col,unit,err_on_fail):
        """
        Wrapper for table_units<>::convert_to_unit() .
        wrapper for :ref:`o2sclp:table_units<>::convert_to_unit()`.
        """
        col_=ctypes.c_char_p(force_bytes(col))
        unit_=ctypes.c_char_p(force_bytes(unit))
        func=self._link.o2scl.o2scl_table_units___convert_to_unit
        func.restype=ctypes.c_int
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_bool]
        ret=func(self._ptr,col_,unit_,err_on_fail)
        return ret

    def clear_table(self):
        """
        Wrapper for table_units<>::clear_table() .
        wrapper for :ref:`o2sclp:table_units<>::clear_table()`.
        """
        func=self._link.o2scl.o2scl_table_units___clear_table
        func.argtypes=[ctypes.c_void_p]
        func(self._ptr,)
        return

class table3d:
    """
    Python interface for class :ref:`table3d <o2scl:table3d>`.
    """

    _ptr=0
    _link=0

    def __init__(self,link):
        """
        Init function for class table3d .
        """

        f=link.o2scl.o2scl_create_table3d
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._link=link
        return

    def __del__(self):
        """
        Delete function for class table3d .
        """

        f=self._link.o2scl.o2scl_free_table3d
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    def set(self,ix,iy,name,val):
        """
        Wrapper for table3d::set() .
        wrapper for :ref:`o2sclp:table3d::set()`.
        """
        name_=ctypes.c_char_p(force_bytes(name))
        func=self._link.o2scl.o2scl_table3d_set
        func.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_char_p,ctypes.c_double]
        func(self._ptr,ix,iy,name_,val)
        return

    def get(self,ix,iy,name):
        """
        Wrapper for table3d::get() .
        wrapper for :ref:`o2sclp:table3d::get()`.
        """
        name_=ctypes.c_char_p(force_bytes(name))
        func=self._link.o2scl.o2scl_table3d_get
        func.restype=ctypes.c_double
        func.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_char_p]
        ret=func(self._ptr,ix,iy,name_)
        return ret

    def new_slice(self,slice):
        """
        Wrapper for table3d::new_slice() .
        wrapper for :ref:`o2sclp:table3d::new_slice()`.
        """
        slice_=ctypes.c_char_p(force_bytes(slice))
        func=self._link.o2scl.o2scl_table3d_new_slice
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
        func(self._ptr,slice_)
        return

    def get_nx(self):
        """
        Wrapper for table3d::get_nx() .
        wrapper for :ref:`o2sclp:table3d::get_nx()`.
        """
        func=self._link.o2scl.o2scl_table3d_get_nx
        func.restype=ctypes.c_size_t
        func.argtypes=[ctypes.c_void_p]
        ret=func(self._ptr,)
        return ret

    def get_ny(self):
        """
        Wrapper for table3d::get_ny() .
        wrapper for :ref:`o2sclp:table3d::get_ny()`.
        """
        func=self._link.o2scl.o2scl_table3d_get_ny
        func.restype=ctypes.c_size_t
        func.argtypes=[ctypes.c_void_p]
        ret=func(self._ptr,)
        return ret

    def get_nslices(self):
        """
        Wrapper for table3d::get_nslices() .
        wrapper for :ref:`o2sclp:table3d::get_nslices()`.
        """
        func=self._link.o2scl.o2scl_table3d_get_nslices
        func.restype=ctypes.c_size_t
        func.argtypes=[ctypes.c_void_p]
        ret=func(self._ptr,)
        return ret

class tensor:
    """
    Python interface for class :ref:`tensor<> <o2scl:tensor<>>`.
    """

    _ptr=0
    _link=0

    def __init__(self,link):
        """
        Init function for class tensor<> .
        """

        f=link.o2scl.o2scl_create_tensor__
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._link=link
        return

    def __del__(self):
        """
        Delete function for class tensor<> .
        """

        f=self._link.o2scl.o2scl_free_tensor__
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    def clear(self):
        """
        Wrapper for tensor<>::clear() .
        wrapper for :ref:`o2sclp:tensor<>::clear()`.
        """
        func=self._link.o2scl.o2scl_tensor___clear
        func.argtypes=[ctypes.c_void_p]
        func(self._ptr,)
        return

class find_constants:
    """
    Python interface for class :ref:`find_constants <o2scl:find_constants>`.
    """

    _ptr=0
    _link=0

    def __init__(self,link):
        """
        Init function for class find_constants .
        """

        f=link.o2scl.o2scl_create_find_constants
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._link=link
        return

    def __del__(self):
        """
        Delete function for class find_constants .
        """

        f=self._link.o2scl.o2scl_free_find_constants
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    def find_print(self,name,unit,prec,verbose):
        """
        Wrapper for find_constants::find_print() .
        wrapper for :ref:`o2sclp:find_constants::find_print()`.
        """
        name_=ctypes.c_char_p(force_bytes(name))
        unit_=ctypes.c_char_p(force_bytes(unit))
        func=self._link.o2scl.o2scl_find_constants_find_print
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_size_t,ctypes.c_int]
        func(self._ptr,name_,unit_,prec,verbose)
        return

    def find_unique(self,name,unit):
        """
        Wrapper for find_constants::find_unique() .
        wrapper for :ref:`o2sclp:find_constants::find_unique()`.
        """
        name_=ctypes.c_char_p(force_bytes(name))
        unit_=ctypes.c_char_p(force_bytes(unit))
        func=self._link.o2scl.o2scl_find_constants_find_unique
        func.restype=ctypes.c_double
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p]
        ret=func(self._ptr,name_,unit_)
        return ret

class convert_units:
    """
    Python interface for class :ref:`convert_units<> <o2scl:convert_units<>>`.
    """

    _ptr=0
    _link=0

    def __init__(self,link):
        """
        Init function for class convert_units<> .
        """

        f=link.o2scl.o2scl_create_convert_units__
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._link=link
        return

    def __del__(self):
        """
        Delete function for class convert_units<> .
        """

        f=self._link.o2scl.o2scl_free_convert_units__
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    @property
    def verbose(self):
        """
        Getter function for convert_units<>::verbose .
        """
        func=self._link.o2scl.o2scl_convert_units___get_verbose
        func.restype=ctypes.c_int
        func.argtypes=[ctypes.c_void_p]
        return func(self._ptr)

    @verbose.setter
    def verbose(self,value):
        """
        Setter function for convert_units<>::verbose .
        """
        func=self._link.o2scl.o2scl_convert_units___set_verbose
        func.argtypes=[ctypes.c_void_p,ctypes.c_int]
        func(self._ptr,value)
        return

    @property
    def use_gnu_units(self):
        """
        Getter function for convert_units<>::use_gnu_units .
        """
        func=self._link.o2scl.o2scl_convert_units___get_use_gnu_units
        func.restype=ctypes.c_bool
        func.argtypes=[ctypes.c_void_p]
        return func(self._ptr)

    @use_gnu_units.setter
    def use_gnu_units(self,value):
        """
        Setter function for convert_units<>::use_gnu_units .
        """
        func=self._link.o2scl.o2scl_convert_units___set_use_gnu_units
        func.argtypes=[ctypes.c_void_p,ctypes.c_bool]
        func(self._ptr,value)
        return

    @property
    def err_on_fail(self):
        """
        Getter function for convert_units<>::err_on_fail .
        """
        func=self._link.o2scl.o2scl_convert_units___get_err_on_fail
        func.restype=ctypes.c_bool
        func.argtypes=[ctypes.c_void_p]
        return func(self._ptr)

    @err_on_fail.setter
    def err_on_fail(self,value):
        """
        Setter function for convert_units<>::err_on_fail .
        """
        func=self._link.o2scl.o2scl_convert_units___set_err_on_fail
        func.argtypes=[ctypes.c_void_p,ctypes.c_bool]
        func(self._ptr,value)
        return

    @property
    def combine_two_conv(self):
        """
        Getter function for convert_units<>::combine_two_conv .
        """
        func=self._link.o2scl.o2scl_convert_units___get_combine_two_conv
        func.restype=ctypes.c_bool
        func.argtypes=[ctypes.c_void_p]
        return func(self._ptr)

    @combine_two_conv.setter
    def combine_two_conv(self,value):
        """
        Setter function for convert_units<>::combine_two_conv .
        """
        func=self._link.o2scl.o2scl_convert_units___set_combine_two_conv
        func.argtypes=[ctypes.c_void_p,ctypes.c_bool]
        func(self._ptr,value)
        return

    def get_units_cmd_string(self,units_cmd_string):
        """
        Getter function for convert_units<>::units_cmd_string .
        """
        func=self._link.o2scl.o2scl_convert_units___get_units_cmd_string
        func.restype=ctypes.c_char_p
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
        func(self._ptr,units_cmd_string._ptr)
        return

    def set_units_cmd_string(self,value):
        """
        Setter function for convert_units<>::units_cmd_string .
        """
        func=self._link.o2scl.o2scl_convert_units___set_units_cmd_string
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
        func(self._ptr,value._ptr)
        return

    def convert(self,frm,to,val):
        """
        Wrapper for convert_units<>::convert() .
        wrapper for :ref:`o2sclp:convert_units<>::convert()`.
        """
        frm_=ctypes.c_char_p(force_bytes(frm))
        to_=ctypes.c_char_p(force_bytes(to))
        func=self._link.o2scl.o2scl_convert_units___convert
        func.restype=ctypes.c_double
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_double]
        ret=func(self._ptr,frm_,to_,val)
        return ret

    def convert_ret(self,frm,to,val,converted):
        """
        Wrapper for convert_units<>::convert_ret() .
        wrapper for :ref:`o2sclp:convert_units<>::convert_ret()`.
        """
        frm_=ctypes.c_char_p(force_bytes(frm))
        to_=ctypes.c_char_p(force_bytes(to))
        func=self._link.o2scl.o2scl_convert_units___convert_ret
        func.restype=ctypes.c_int
        func.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_double,ctypes.c_double]
        ret=func(self._ptr,frm_,to_,val,converted)
        return ret

    def print_cache(self):
        """
        Wrapper for convert_units<>::print_cache() .
        wrapper for :ref:`o2sclp:convert_units<>::print_cache()`.
        """
        func=self._link.o2scl.o2scl_convert_units___print_cache
        func.argtypes=[ctypes.c_void_p]
        func(self._ptr,)
        return

class shared_ptr_table_units(table_units):

    _s_ptr=0
    _ptr=0
    _link=0

    def __init__(self,link):
        """
        Init function for sp table_units<> .
        """

        self._s_ptr=0
        self._ptr=0
        self._link=link
        return

    def __del__(self):
        """
        Delete function for sp table_units<> .
        """

        f=self._link.o2scl.o2scl_free_shared_ptr_table_units__
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    def __set_ptr(self):
        """
        Set pointer function for sp table_units<> .
        """

        f=self._link.o2scl.o2scl_shared_ptr_table_units___ptr
        f.argtypes=[ctypes.c_void_p]
        f.restype=ctypes.c_void_p
        self._ptr=f(self._s_ptr)
        return

