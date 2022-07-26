# M-N-Kappa

Implementation of the $M$-$N$-$\kappa$ method for computation of composite beams in python considering multi-line material models.

## Definitions

- $M$ describes the resistance moment of a crossection 
- $N$ is the internal shear-force applied with differing sign on the concrete-slab and the steel-girder
- $\kappa$ is the curvature over the crosssection. 
It is assumed that the curvature is uniformly distributed over the full height of the cross-section. 

The $M$-$\kappa$-Method allows to compute the deformation of composite beams assuming rigid shear connection. The $M$-$N$-$\kappa$-Method extends the method by the load-slip-behaviour of the shear connectors. 

## Features

- Easy to use interface
- strain-based design
- consideration of load-carrying behaviour of shear connectors

## Installation

```
pip install m-n-kappa
```

## Example

### Introduction

### Inputs

#### Geometries

#### Materials

#### Sections

#### Cross-section

### Computation 

Deformation

## Todo
- computation of single-span systems (no consideration of shear connectors)
- computation of single-span systems considering load-slip behaviour of shear connectors
- computation of multi-span systems
- Documentation
- Enhancement of performance writing several methods/classes in [Rust](https://www.rust-lang.org/)