# An XFEMM based switched reluctance generator calculator
You need XFEMM binaries built for your architecture with a replaced fpproc/main.cpp file as the default one doesn't output inductance.

##### compute_inductance.py
An XFEMM wrapper that changes the rotor position and runs XFEMM apps

##### srg_ode_solver.py
A script that sovles SRG ODEs to get the phase current as a function of the rotor angle

##### srg_optimizer.py
A PyGAD-based genetic algorithm script that optimizes SRG firing/generation angles for specified RPMs and voltage

#### SRG
![SRG](https://github.com/lastChance08/srg_calculator/blob/main/media/srg.png "SRG")
#### Inductance graph
![Inductance graph](https://github.com/lastChance08/srg_calculator/blob/main/media/L.png "Inductance graph")
#### Inductance derivative graph
![Inductance derivative graph](https://github.com/lastChance08/srg_calculator/blob/main/media/dLdTheta.png "Inductance derivative graph")
#### Phase current graph
![Phase current graph](https://github.com/lastChance08/srg_calculator/blob/main/media/i.png "Phase current graph")