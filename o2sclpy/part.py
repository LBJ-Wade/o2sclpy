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

class part:

    _ptr=0
    _dll=0

    def __init__(self,dll):
        """
        Init function for class part .
        """

        f=dll.o2scl_create_part
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class part .
        """

        f=self._dll.o2scl_free_part
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    @property
    def g(self):
        """
        Getter function for part::g .
        """
        f=self._dll.o2scl_part_get_g
        f.restype=ctypes.c_double
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @g.setter
    def g(self,value):
        """
        Setter function for part::g .
        """
        f=self._dll.o2scl_part_set_g
        f.argtypes=[ctypes.c_void_p,ctypes.c_double]
        self._g=f(self._ptr,value)
        return

    @property
    def m(self):
        """
        Getter function for part::m .
        """
        f=self._dll.o2scl_part_get_m
        f.restype=ctypes.c_double
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @m.setter
    def m(self,value):
        """
        Setter function for part::m .
        """
        f=self._dll.o2scl_part_set_m
        f.argtypes=[ctypes.c_void_p,ctypes.c_double]
        self._m=f(self._ptr,value)
        return

    @property
    def ms(self):
        """
        Getter function for part::ms .
        """
        f=self._dll.o2scl_part_get_ms
        f.restype=ctypes.c_double
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @ms.setter
    def ms(self,value):
        """
        Setter function for part::ms .
        """
        f=self._dll.o2scl_part_set_ms
        f.argtypes=[ctypes.c_void_p,ctypes.c_double]
        self._ms=f(self._ptr,value)
        return

    @property
    def mu(self):
        """
        Getter function for part::mu .
        """
        f=self._dll.o2scl_part_get_mu
        f.restype=ctypes.c_double
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @mu.setter
    def mu(self,value):
        """
        Setter function for part::mu .
        """
        f=self._dll.o2scl_part_set_mu
        f.argtypes=[ctypes.c_void_p,ctypes.c_double]
        self._mu=f(self._ptr,value)
        return

    @property
    def nu(self):
        """
        Getter function for part::nu .
        """
        f=self._dll.o2scl_part_get_nu
        f.restype=ctypes.c_double
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @nu.setter
    def nu(self,value):
        """
        Setter function for part::nu .
        """
        f=self._dll.o2scl_part_set_nu
        f.argtypes=[ctypes.c_void_p,ctypes.c_double]
        self._nu=f(self._ptr,value)
        return

    @property
    def ed(self):
        """
        Getter function for part::ed .
        """
        f=self._dll.o2scl_part_get_ed
        f.restype=ctypes.c_double
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @ed.setter
    def ed(self,value):
        """
        Setter function for part::ed .
        """
        f=self._dll.o2scl_part_set_ed
        f.argtypes=[ctypes.c_void_p,ctypes.c_double]
        self._ed=f(self._ptr,value)
        return

    @property
    def pr(self):
        """
        Getter function for part::pr .
        """
        f=self._dll.o2scl_part_get_pr
        f.restype=ctypes.c_double
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @pr.setter
    def pr(self,value):
        """
        Setter function for part::pr .
        """
        f=self._dll.o2scl_part_set_pr
        f.argtypes=[ctypes.c_void_p,ctypes.c_double]
        self._pr=f(self._ptr,value)
        return

    @property
    def en(self):
        """
        Getter function for part::en .
        """
        f=self._dll.o2scl_part_get_en
        f.restype=ctypes.c_double
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @en.setter
    def en(self,value):
        """
        Setter function for part::en .
        """
        f=self._dll.o2scl_part_set_en
        f.argtypes=[ctypes.c_void_p,ctypes.c_double]
        self._en=f(self._ptr,value)
        return

    @property
    def inc_rest_mass(self):
        """
        Getter function for part::inc_rest_mass .
        """
        f=self._dll.o2scl_part_get_inc_rest_mass
        f.restype=ctypes.c_bool
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @inc_rest_mass.setter
    def inc_rest_mass(self,value):
        """
        Setter function for part::inc_rest_mass .
        """
        f=self._dll.o2scl_part_set_inc_rest_mass
        f.argtypes=[ctypes.c_void_p,ctypes.c_bool]
        self._inc_rest_mass=f(self._ptr,value)
        return

    @property
    def non_interacting(self):
        """
        Getter function for part::non_interacting .
        """
        f=self._dll.o2scl_part_get_non_interacting
        f.restype=ctypes.c_bool
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @non_interacting.setter
    def non_interacting(self,value):
        """
        Setter function for part::non_interacting .
        """
        f=self._dll.o2scl_part_set_non_interacting
        f.argtypes=[ctypes.c_void_p,ctypes.c_bool]
        self._non_interacting=f(self._ptr,value)
        return

class fermion(part):

    def __init__(self,dll):
        """
        Init function for class fermion .
        """

        f=dll.o2scl_create_fermion
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class fermion .
        """

        f=self._dll.o2scl_free_fermion
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    @property
    def kf(self):
        """
        Getter function for fermion::kf .
        """
        f=self._dll.o2scl_fermion_get_kf
        f.restype=ctypes.c_double
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @kf.setter
    def kf(self,value):
        """
        Setter function for fermion::kf .
        """
        f=self._dll.o2scl_fermion_set_kf
        f.argtypes=[ctypes.c_void_p,ctypes.c_double]
        self._kf=f(self._ptr,value)
        return

    @property
    def delta(self):
        """
        Getter function for fermion::delta .
        """
        f=self._dll.o2scl_fermion_get_delta
        f.restype=ctypes.c_double
        f.argtypes=[ctypes.c_void_p]
        return f(self._ptr)

    @delta.setter
    def delta(self,value):
        """
        Setter function for fermion::delta .
        """
        f=self._dll.o2scl_fermion_set_delta
        f.argtypes=[ctypes.c_void_p,ctypes.c_double]
        self._delta=f(self._ptr,value)
        return

class fermion_zerot:

    _ptr=0
    _dll=0

    def __init__(self,dll):
        """
        Init function for class fermion_zerot .
        """

        f=dll.o2scl_create_fermion_zerot
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class fermion_zerot .
        """

        f=self._dll.o2scl_free_fermion_zerot
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    def kf_from_density(self,f):
        """
        Wrapper for fermion_zerot::kf_from_density() .
        """
        func=self._dll.o2scl_fermion_zerot_kf_from_density
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
        func(self._ptr,f._ptr)
        return

    def energy_density_zerot(self,f):
        """
        Wrapper for fermion_zerot::energy_density_zerot() .
        """
        func=self._dll.o2scl_fermion_zerot_energy_density_zerot
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
        func(self._ptr,f._ptr)
        return

    def pressure_zerot(self,f):
        """
        Wrapper for fermion_zerot::pressure_zerot() .
        """
        func=self._dll.o2scl_fermion_zerot_pressure_zerot
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
        func(self._ptr,f._ptr)
        return

    def calc_mu_zerot(self,f):
        """
        Wrapper for fermion_zerot::calc_mu_zerot() .
        """
        func=self._dll.o2scl_fermion_zerot_calc_mu_zerot
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
        func(self._ptr,f._ptr)
        return

    def calc_density_zerot(self,f):
        """
        Wrapper for fermion_zerot::calc_density_zerot() .
        """
        func=self._dll.o2scl_fermion_zerot_calc_density_zerot
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
        func(self._ptr,f._ptr)
        return

class fermion_rel(fermion_zerot):

    def __init__(self,dll):
        """
        Init function for class fermion_rel .
        """

        f=dll.o2scl_create_fermion_rel
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class fermion_rel .
        """

        f=self._dll.o2scl_free_fermion_rel
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

    def calc_mu_deg(self,f,T,prec):
        """
        Wrapper for fermion_rel::calc_mu_deg() .
        """
        func=self._dll.o2scl_fermion_rel_calc_mu_deg
        func.restype=ctypes.c_bool
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double,ctypes.c_double]
        ret=func(self._ptr,f._ptr,T,prec)
        return ret

    def calc_mu_ndeg(self,f,T,prec,inc_antip):
        """
        Wrapper for fermion_rel::calc_mu_ndeg() .
        """
        func=self._dll.o2scl_fermion_rel_calc_mu_ndeg
        func.restype=ctypes.c_bool
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double,ctypes.c_double,ctypes.c_bool]
        ret=func(self._ptr,f._ptr,T,prec,inc_antip)
        return ret

    def massless_calc_mu(self,f,T):
        """
        Wrapper for fermion_rel::massless_calc_mu() .
        """
        func=self._dll.o2scl_fermion_rel_massless_calc_mu
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double]
        func(self._ptr,f._ptr,T)
        return

    def massless_pair_mu(self,f,T):
        """
        Wrapper for fermion_rel::massless_pair_mu() .
        """
        func=self._dll.o2scl_fermion_rel_massless_pair_mu
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double]
        func(self._ptr,f._ptr,T)
        return

    def massless_calc_density(self,f,T):
        """
        Wrapper for fermion_rel::massless_calc_density() .
        """
        func=self._dll.o2scl_fermion_rel_massless_calc_density
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double]
        func(self._ptr,f._ptr,T)
        return

    def massless_pair_density(self,f,T):
        """
        Wrapper for fermion_rel::massless_pair_density() .
        """
        func=self._dll.o2scl_fermion_rel_massless_pair_density
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double]
        func(self._ptr,f._ptr,T)
        return

    def nu_from_n(self,f,T):
        """
        Wrapper for fermion_rel::nu_from_n() .
        """
        func=self._dll.o2scl_fermion_rel_nu_from_n
        func.restype=ctypes.c_int
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double]
        ret=func(self._ptr,f._ptr,T)
        return ret

    def calc_density(self,f,T):
        """
        Wrapper for fermion_rel::calc_density() .
        """
        func=self._dll.o2scl_fermion_rel_calc_density
        func.restype=ctypes.c_int
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double]
        ret=func(self._ptr,f._ptr,T)
        return ret

    def pair_density(self,f,T):
        """
        Wrapper for fermion_rel::pair_density() .
        """
        func=self._dll.o2scl_fermion_rel_pair_density
        func.restype=ctypes.c_int
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double]
        ret=func(self._ptr,f._ptr,T)
        return ret

    def calc_mu(self,f,T):
        """
        Wrapper for fermion_rel::calc_mu() .
        """
        func=self._dll.o2scl_fermion_rel_calc_mu
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double]
        func(self._ptr,f._ptr,T)
        return

    def pair_mu(self,f,T):
        """
        Wrapper for fermion_rel::pair_mu() .
        """
        func=self._dll.o2scl_fermion_rel_pair_mu
        func.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_double]
        func(self._ptr,f._ptr,T)
        return

class fermion_nonrel:

    _ptr=0
    _dll=0

    def __init__(self,dll):
        """
        Init function for class fermion_nonrel .
        """

        f=dll.o2scl_create_fermion_nonrel
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class fermion_nonrel .
        """

        f=self._dll.o2scl_free_fermion_nonrel
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

class fermion_deriv_nr:

    _ptr=0
    _dll=0

    def __init__(self,dll):
        """
        Init function for class fermion_deriv_nr .
        """

        f=dll.o2scl_create_fermion_deriv_nr
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class fermion_deriv_nr .
        """

        f=self._dll.o2scl_free_fermion_deriv_nr
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

class fermion_deriv_rel:

    _ptr=0
    _dll=0

    def __init__(self,dll):
        """
        Init function for class fermion_deriv_rel .
        """

        f=dll.o2scl_create_fermion_deriv_rel
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class fermion_deriv_rel .
        """

        f=self._dll.o2scl_free_fermion_deriv_rel
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

class boson_rel:

    _ptr=0
    _dll=0

    def __init__(self,dll):
        """
        Init function for class boson_rel .
        """

        f=dll.o2scl_create_boson_rel
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class boson_rel .
        """

        f=self._dll.o2scl_free_boson_rel
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

class classical_thermo:

    _ptr=0
    _dll=0

    def __init__(self,dll):
        """
        Init function for class classical_thermo .
        """

        f=dll.o2scl_create_classical_thermo
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class classical_thermo .
        """

        f=self._dll.o2scl_free_classical_thermo
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

class classical_deriv_thermo:

    _ptr=0
    _dll=0

    def __init__(self,dll):
        """
        Init function for class classical_deriv_thermo .
        """

        f=dll.o2scl_create_classical_deriv_thermo
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class classical_deriv_thermo .
        """

        f=self._dll.o2scl_free_classical_deriv_thermo
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

class fermion_mag_zerot:

    _ptr=0
    _dll=0

    def __init__(self,dll):
        """
        Init function for class fermion_mag_zerot .
        """

        f=dll.o2scl_create_fermion_mag_zerot
        f.restype=ctypes.c_void_p
        f.argtypes=[]
        self._ptr=f()
        self._dll=dll
        return

    def __del__(self):
        """
        Delete function for class fermion_mag_zerot .
        """

        f=self._dll.o2scl_free_fermion_mag_zerot
        f.argtypes=[ctypes.c_void_p]
        f(self._ptr)
        return

