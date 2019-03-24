User Manual of PI-REC
---------------
<p align="left">
		<img src="https://img.shields.io/badge/version-0.1-brightgreen.svg?style=flat-square"
			 alt="Version">
		<img src="https://img.shields.io/badge/status-release-gold.svg?style=flat-square"
			 alt="Status">
		<img src="https://img.shields.io/badge/platform-win | linux-lightgrey.svg?style=flat-square"
			 alt="Platform">
		<img src="https://img.shields.io/badge/PyTorch version-1.0-blue.svg?style=flat-square"
			 alt="PyTorch">
		<img src="https://img.shields.io/badge/License-CC BY·NC 4.0-green.svg?style=flat-square"
			 alt="License">
</p>

English | [中文版](#jump_zh)


## Introduction
#### We provide two ways in the project:
- **Basic command line mode** for batch test  
- **Drawing tool GUI mode** for creation

In short, each model has its own directory, which contains option file `config.yml` and model weights files `xxx.pth`.
We assume that you have finished the preparing steps in [README](README.md#usage).

## Check files
Make sure that your model dir like this (e.g. the `celeba model`):<br>
- `./models/celeba/config.yml` for the configuration
- `./models/celeba/G_Model_gen_xxxxxx.pth` for *2nd Generating Phase* of paper
- `./models/celeba/R_Model_gen_xxxxxx.pth` for *3rd Refinement Phase* of paper

If you cannot catch on *Xxxx Phase* above, read our paper thoroughly first.


## Command Line Mode
This mode is to show powerful reconstruction ability of PI-REC.
During this mode, PI-REC will automatically extract edges and color domains from GT.
So, just put the original GT validation dataset under the dir.

Phase | Command | Dataset loc | Description
-----|-------|------|-------
 2nd | python test.py -p models/celeba | `TEST_FLIST` in `config.yml` |  Reconstruct image using edge and color domain extracted from GT
 3rd | python refine.py -p models/celeba | `REFINE_FLIST` in `config.yml` |  Refine all the images (outputs from *2nd Phase*) 
 2+3 | python test_with_refine.py -p models/celeba | `TEST_FLIST` in `config.yml` |  Reconstruct and refine

- In the `config.yml` of the corresponding model, `TEST_FLIST` and `REFINE_FLIST` are most important config to define the testing dataset location as above.<br>
- Optional changeable configs: `DEBUG`, `INPUT_SIZE`, `SIGMA` and `KM`. Refer to the `config.yml` for details.

