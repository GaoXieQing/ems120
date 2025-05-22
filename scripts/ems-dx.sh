#!/bin/bash
set -e
module load python/anaconda3/5.2.0
export PATH=/work/sph-gaoxq/.conda/envs/pytorch-tt/bin:$PATH #需要修改自己在HPC中的pytorch环境路径及名称
export CONDA_PREFIX=/work/sph-gaoxq/.conda/envs/pytorch-tt #需要修改自己在HPC中的pytorch环境路径及名称
python /work/sph-gaoxq/projects/ems120/ems-dx.py #修改为自己的文件路径