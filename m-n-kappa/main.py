from . import material

concrete = material.Concrete(f_cm=68)

print(concrete.f_ck)
print(concrete.epsilon_c1, concrete.epsilon_cu1)
print(concrete.epsilon_c2, concrete.epsilon_cu2)
print(concrete.epsilon_c3, concrete.epsilon_cu3)

print(concrete.stress_strain)
