# The Neural Simulation Tool - NEST

This is a fork of NEST (version 3.1) in which the short-term-plasticity synapse named tsodyks3_synapse has been included. This version has been used in the context of the publication:

> Tiddia, G., Golosio, B., Fanti, V., & Paolucci, P. S. (2022). Simulations of working memory spiking networks driven by short-term plasticity. Frontiers in Integrative Neuroscience, 16, 972055. https://doi.org/10.3389/fnint.2022.972055

You can find the GitHub repository of the Working Memory spiking model [here](https://github.com/gmtiddia/working_memory_spiking_network).

The original NEST README can be found [here](NEST_README.md).

## Intalling this version

The installation has been tested on Ubuntu 21.10 and 22.04 by following these [installation instructions](https://nest-simulator.readthedocs.io/en/v3.1/installation/linux_install.html). The link refers to the advanced Ubuntu/Debian installation instructions of the NEST Documentation of the version 3.1 of NEST, from which this version is derived.

Currently, this version can not be installed using PPA or conda.


## Documentation

The Documentation to refer to is the [NEST Documentation v3.1](https://nest-simulator.readthedocs.io/en/v3.1/).

In the following is documented the new synapse model implemented in this version.

### The tsodyks3_synapse model

The tsodyks3_synapse model comes from a modification of the tsodyks2_synapse model, already existing in NEST. The documentation for the tsodyks2_synapse model can be found [here](https://nest-simulator.readthedocs.io/en/v3.1/models/tsodyks2_synapse.html).

The difference between these two models stems from the order of update of the STP variables *u* and *x* when a spike is emitted. These variables modulates the synaptic efficacy of a synapse following the equation $J^{(\text{mod})}=J^{(\text{abs})}ux$, with $J^{(\text{abs})}$ being the absolute synaptic efficacy.

Given a spike emitted at a time $t_s$, in tsodyks2_synapse the modulation is obtained by multiplying the absolute synaptic efficacy with the values of $u$ and $x$ before the spike emission, i.e., $J^{(\text{mod})}(t_s)=J^{(\text{abs})}u(t_s^{-})x(t_s^{-})$, where $t_s^{-}$ refers to the time immediately before the spike emission.

Given the same spike emitted at a time $t_s$, in tsodyks3_synapse the modulation is obtained by $J^{(\text{mod})}(t_s)=J^{(\text{abs})}u(t_s^{+})x(t_s^{-})$, where $t_s^{-}$ is the time immediately before the spike emission and $t_s^{+}$ is the time immediately after the spike emission.

More details on the implementation of the model and on the motivation of this changes are reported in the publication:

> Tiddia, G., Golosio, B., Fanti, V., & Paolucci, P. S. (2022). Simulations of working memory spiking networks driven by short-term plasticity. Frontiers in Integrative Neuroscience, 16, 972055. https://doi.org/10.3389/fnint.2022.972055


## License

NEST is open source software and is licensed under the [GNU General Public
License v2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) or
later.




