.. ExTASY documentation master file, created by
   sphinx-quickstart on Fri Jan 23 12:42:20 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ExTASY's documentation!
==================================

Provides a command line interface to run multiple Molecular Dynamics (MD) simulations,
which can be coupled to an analysis tool. The coupled simulation-analysis execution
pattern (aka ExTASY pattern) currently supports two examples:

    (a) Gromacs as the "Simulator" and LSDMap as the "Analyzer"
    (b) AMBER as the "Simulator" and COCO as the "Analyzer"

Due to the plugin-based architecture, this execution pattern, will be expandable as to
support more Simulators and Analyzers.

.. toctree::
   :numbered:
   :maxdepth: 2

   pages/installation.rst
   pages/coam.rst
   pages/grlsd.rst
   pages/trouble.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

