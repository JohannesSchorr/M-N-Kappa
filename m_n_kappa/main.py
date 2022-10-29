import material

"""
General Procedure
=================
1. Create Crossection
1.1 Material + Geometry --> Section 
1.2 Section + Section --> Crosssection

2. Loading 
- Define loading arrangement
- Define explicit load-case

3. Beam
- Crossection + beam-length + loading
--> Get load-deformation-curve

"""
concrete = material.Concrete(f_cm=68)

print(concrete.f_ck)
print(concrete.epsilon_c1, concrete.epsilon_cu1)
print(concrete.epsilon_c2, concrete.epsilon_cu2)
print(concrete.epsilon_c3, concrete.epsilon_cu3)

print(concrete.stress_strain)
