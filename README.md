# M-N-Kappa

Implementation of the $M$-$N$-$\kappa$ method for computation of composite beams considering multi-line material models in python.

## Definitions

- $M$: resistance moment of a cross-section 
- $N$: internal shear-force applied with differing sign on the concrete-slab and the steel-girder
- $\kappa$: the curvature over the cross-section. 

It is assumed that the curvature $\kappa$ is uniformly distributed over the full height of the cross-section. 

The $M$-$\kappa$-Method allows to compute the deformation of composite beams assuming rigid shear connection. The $M$-$N$-$\kappa$-Method extends the method by the load-slip-behaviour of the shear connectors. 

## Features

- Easy to use interface
- strain-based design
- consideration of load-slip behaviour of shear connectors

## Documentation

- Getting started
- Examples
- Users' guide
- Theory guide
- API

## Todo
- computation of single-span systems considering load-slip behaviour of shear connectors + testing + validation 
- computation of multi-span systems
- Documentation
- Publication on GitHub and pypi
- (Presentation of results (i.e. in Jupyter Notebooks, Altair, Plotly, etc.))
- (Enhancement of performance writing several methods/classes in [Rust](https://www.rust-lang.org/))