#!/bin/bash
# E0028 driver: real, then 999 surrogates, then tier-1 power; every stage resumes from its checkpoint.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$(dirname "$0")/../.."
python3 experiments/E0028_column_shift_llr_pages.py real
python3 experiments/E0028_column_shift_llr_pages.py surrogates --count 999
python3 experiments/E0028_column_shift_llr_pages.py power --plants 100
python3 experiments/E0028_column_shift_llr_pages.py report > /dev/null
echo ALLDONE >> results/E0028/run.log
