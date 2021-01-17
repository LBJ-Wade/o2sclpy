import o2sclpy

l=o2sclpy.linker()
l.get_library_settings()
l.link_o2scl_o2graph(True)

# Create neutron and proton
neut=o2sclpy.fermion(l.o2scl_part)
neut.g=2.0
neut.m=939.6/197.33

prot=o2sclpy.fermion(l.o2scl_part)
prot.g=2.0
prot.m=938.4/197.33

# Create an object
sk=o2sclpy.eos_had_skyrme(l.o2scl_eos)

