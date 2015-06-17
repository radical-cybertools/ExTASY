.. _intro:

Introduction
============

What is ExTASY ?
----------------

ExTASY is a tool to run multiple Molecular Dynamics simulations which can
be coupled to an Analysis stage. This forms a simulation-analysis loop which
can be made to iterate multiple times. It uses a pilot framework, namely
`Radical Pilot <http://radicalpilot.readthedocs.org/en/latest/>`_ to run a large
number of these ensembles concurrently on most of the commonly used supercomputers.
The complications of resource allocation, data management and task execution are
performed using Radical Pilot and handled by the ExTASY.

ExTASY provides a command line interface, that along with specific configuration files,
keeps the user's job minimal and free of the underlying execution methods and data management
that is resource specific.

The coupled simulation-analysis execution pattern (aka ExTASY pattern) currently supports two usecases:

    * **Gromacs** as the "Simulator" and **LSDMap** as the "Analyzer"
    * **AMBER** as the "Simulator" and **CoCo** as the "Analyzer"