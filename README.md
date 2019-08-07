# MeerKAT @ IRIS

🚧 _Under construction_ 🚧

This repository contains instructions and example files for conducting reproducible radio data analysis with [CASA](https://casa.nrao.edu/) in a [Jupyter Notebook](https://jupyter.org/) using the [jupyter-casa kernel](https://github.com/aardk/jupyter-casa) on [IRIS](https://www.iris.ac.uk/) resources. It makes use of the [IDIA MeerKAT pipeline](https://github.com/idia-astro/pipelines/blob/master/README.md), a radio interferometric calibration pipeline designed to process MeerKAT data called processMeerKAT. For processMeerKAT usage, see the [IDIA Pipelines website](https://idia-pipelines.github.io/).

## Quick Start

#### 1. Clone this repository

```bash
git clone https://github.com/rainsworth/MeerKAT-IRIS.git
```

#### 2. Pull necessary Singularity containers

The [jupyter-casa](https://github.com/aardk/jupyter-casa) container allows you to use CASA tasks via a Jupyter notebook. 

```bash
singularity pull --name jupyter-casa.sif shub://aardk/jupyter-casa:@e858b080cdee724a34a76b47988e135d
```

Note: We also use the casameer-5.4.1.xvfb.simg Singularity container image to locally create the config file (in step #4), but it does not appear to be publicly available (see [here](https://idia-pipelines.github.io/docs/containers/)). Perhaps the casa-stable-5.3.0.simg will work? (Needs checking.) 


#### 3. Bash setup

The processMeerKAT pipeline can generate the general system error: Too many open files. You can see the current limits with (in bash): ```ulimit -a```. To increase the max system limits and avoid this error, set:
```bash
set: ulimit -n 4096
```
This setting is current terminal only, and you will need to reset every time you open a new terminal or screen or add it to your bashrc.

In order to use the `processMeerKAT.py` script, source the `setup.sh` file:

```bash
source pipelines/setup.sh
```

which will add the correct paths to your `$PATH` and `$PYTHONPATH` in order to correctly use the pipeline.

#### 4. Build the config file

```bash
pipelines/processMeerKAT/processMeerKAT.py -B -C myconfig.txt -l -M <MEASUREMENT SET> -c <CONTAINER>
```

processMeerKAT tag definitions (see [usage](https://idia-pipelines.github.io/docs/processMeerKAT/using-the-pipeline/)):
* `-B, --build` : Build config file using input MS.
* `-C path, --config path` : Path to config file.
* `-l, --local` : Build config file locally (i.e. without calling srun).
* `-M path, --MS path` : Path to measurement set.
* `-c path, --container path` : Use this container when calling scripts.

This command must be run in the directory containing the measurement set (.ms file) that the pipeline will be run on, so define full paths to processMeerKAT.py and the config file as necessary. This command generates the config file which defines several variables that are read by the pipeline while calibrating the data. The config file parameters are described by in-line comments in the config file itself wherever possible.

Note: We use the casameer-5.4.1.xvfb.simg Singularity container image to locally create the config file in this step, but it does not appear to be publicly available (see [here](https://idia-pipelines.github.io/docs/containers/)). Perhaps the casa-stable-5.3.0.simg will work? (Needs checking.)

#### 5. Edit path to data in config file

Ensure the path to the data in the config file will be correct for when it is used in the jupyter-casa container. For example:

```
[data]
vis = 'data/data.ms'
```

#### 6. Run the pipeline

For the standard use of the processMeerKAT pipeline, this step creates `submit_pipeline.sh`, which you can then run like ``./submit_pipeline.sh` to submit all pipeline jobs to the SLURM queue (see the [IDIA Pipelines website](https://idia-pipelines.github.io/docs/processMeerKAT/Quick-Start/)).

In this case we are running on [IRIS](), so do not need the `submit_pipeline.sh` or `.sbatch` files generated, however we will still take advantage of the bookkeeping this command establishes. 

```bash
pipelines/processMeerKAT/processMeerKAT.py -R -C myconfig.txt
```

processMeerKAT tag definitions (see [usage](https://idia-pipelines.github.io/docs/processMeerKAT/using-the-pipeline/)):
* ` -R, --run` : Run pipeline with input config file.
* `-C path, --config path` : Path to config file.

#### 7. Execute the pipeline within the containerised Jupyter notebook

```bash
singularity exec --cleanenv -H $PWD -B LOCAL/PATH/TO/DATA/:$PWD/data -B LOCAL/PATH/TO/PIPELINE/:$PWD/pipelines <CONTAINER IMAGE> <COMMAND SCRIPT TO EXECUTE>
```

Singularity tag definitions (see [usage](https://sylabs.io/guides/3.3/user-guide/cli/singularity_exec.html)):
* `exec` : Execute a command within container.
* `-e, --cleanenv` : Clean environment before running container.
* `-H path, --home path` : A home directory specification.
* `-B path, --bind path` : A user-bind path specification.

For example:

```bash
singularity exec --cleanenv -H $PWD -B /scratch/mightee/XMMLSS12_1539286252_tiny.ms:$PWD/data/XMMLSS12_1539286252_tiny.ms/ -B pipelines/:$PWD/pipelines jupyter-casa.simg './runjupyter_MeerKAT.sh'
```

## Directory Structure

This is how my directory looks for binding to the container:

```
MeerKAT-IRIS/
│   myconfig.txt
│   processMeerKAT_tutorial_clean.ipynb
│   README.md
│   runjupyter_MeerKAT.sh
│
└───data/
│   └───data.ms
│
└───logs/
│
│
└───pipelines/
    │   LICENSE
    │   README.md
    │   setup.sh
    │
    └───processMeerKAT/
        │   config_parser.py
        │   default_config.txt
        │   processMeerKAT.py
        │
        └───cal_scripts/
                __init__.py
                bookkeeping.py
                calc_refant.py
                fastplot.py
                flag_round_1.py
                flag_round_2.py
                get_fields.py
                partition.py
                plot_solutions.py
                quick_tclean.py
                setjy.py
                split.py
                validate_input.py
                xx_yy_apply.py
                xx_yy_solve.py
                xy_yx_apply.py
                xy_yx_solve.py
 
```

Unused files generated by processMeerKAT in top directory (need to disable this in processMeerKAT.py, but I just delete these for now): 
* `submit_pipeline.sh`
* `calc_refant.sbatch`
* `fastplot.sbatch`
* `flag_round_1.sbatch`
* `flag_round_2.sbatch`
* `get_fields.sbatch`
* `partition.sbatch`
* `plot_solutions.sbatch`
* `quick_tclean.sbatch`
* `setjy.sbatch`
* `split.sbatch`
* `validate_input.sbatch`
* `xx_yy_apply.sbatch`
* `xx_yy_solve.sbatch`
* `xy_yx_apply.sbatch`
* `xy_yx_solve.sbatch`

## Summary of steps for the MIGHTEE use-case on the IRIS high memory UI node

These are the steps I follow to run the processMeerKAT pipeline on the XMMLSS12_1539286252_tiny.ms dataset within a Jupyter notebook on the IRIS high memory UI node (same steps but slightly out of order from above). Note: the casameer-5.4.1.xvfb.simg Singularity container image does not appear to be publicly available (see [here](https://idia-pipelines.github.io/docs/containers/)).

1. In /scratch/mightee/ increase ulimit to avoid "Too many open files" error: ```ulimit -n 4096```
2. In /scratch/mightee/ clone [MeerKAT-IRIS](https://github.com/rainsworth/MeerKAT-IRIS): ```git clone https://github.com/rainsworth/MeerKAT-IRIS.git```
3. In /scratch/mightee/ source pipeline setup so it can find processMeerKAT modules: ```source MeerKAT-IRIS/pipelines/setup.sh```
4. In /scratch/mightee/ set up config file: ```MeerKAT-IRIS/pipelines/processMeerKAT/processMeerKAT.py -B -C MeerKAT-IRIS/myconfig.txt -l -M XMMLSS12_1539286252_tiny.ms -c casameer-5.4.1.xvfb.simg```
5. In /scratch/mightee/MeerKAT-IRIS/myconfig.txt edit path to data: ```vis = 'data/XMMLSS12_1539286252_tiny.ms'```
6. In /scratch/mightee/MeerKAT-IRIS/ run pipeline to setup bookkeeping (in future, need to remove sbatch generation from script): ```pipelines/processMeerKAT/processMeerKAT.py -R -C myconfig.txt```
7. In /scratch/mightee/MeerKAT-IRIS/ pull jupyter-casa container image: ```singularity pull --name jupyter-casa.simg shub://aardk/jupyter-casa:docker```
8. In /scratch/mightee/MeerKAT-IRIS/ execute container: ```singularity exec --cleanenv -H $PWD -B /scratch/mightee/XMMLSS12_1539286252_tiny.ms:$PWD/data/XMMLSS12_1539286252_tiny.ms/ -B pipelines/:$PWD/pipelines jupyter-casa.simg './runjupyter_MeerKAT.sh'```