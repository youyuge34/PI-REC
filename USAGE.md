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

*\*The codes of training for release are no completed yet, also waiting for release license of lab.* 
<br>   
**English | [中文版](#jump_zh)**


## Introduction
#### We provide two ways in the project:
1. **Basic command line mode** for batch test  
2. **Drawing tool GUI mode** for creation

In short, each model has its own directory, which contains option file `config.yml` and model weights files `xxx.pth`.
We assume that you have finished the preparing steps in [README](README.md#usage).

## Check files
Make sure that your model dir like this (e.g. the `celeba model`):<br>
- `./models/celeba/config.yml` for the configuration
- `./models/celeba/G_Model_gen_xxxxxx.pth` for *2nd Generating Phase* of paper
- `./models/celeba/R_Model_gen_xxxxxx.pth` for *3rd Refinement Phase* of paper

If you cannot catch on *Xxxx Phase* above, read our paper thoroughly first.

## Dataset for Test
For convenience, we provide a zip file containing test images of 4 datasets. It is mainly for **Command Line Mode** to do the reconstruction tests.<br>
1. Download --> [Google](https://drive.google.com/open?id=12TXQOWH_wcNGF9yiRDiBqRO0c1oOAWcs) | [Baidu](https://pan.baidu.com/s/1SdI0peZkY3_tnl9vVulF6A) (Extraction Code: rr8u) <br>
2. Unzip the file and make sure your path now is like: `./datasets/celeba/val`

## 1.Command Line Mode
This mode is to show powerful reconstruction ability of PI-REC.
During this mode, PI-REC will automatically extract edges and color domains from GT. 
So, just put the original GT validation dataset under the directory, like the testing datasets we provide above.

Phase | Command | Dataset loc | Description
-----|-------|------|-------
 *2nd* | python test.py -p models/celeba | `TEST_FLIST` in `config.yml` |  Reconstruct image using edge and color domain extracted from GT
 *3rd* | python refine.py -p models/celeba | `REFINE_FLIST` in `config.yml` |  Refine all the images (outputs from *2nd Phase*) 
 *2nd + 3rd* | python test_with_refine.py -p models/celeba | `TEST_FLIST` in `config.yml` |  Reconstruct and refine

- In the `config.yml` of the corresponding model, `TEST_FLIST` and `REFINE_FLIST` are most important option to define the testing dataset location.<br>
- Optional changeable options: `DEBUG`, `INPUT_SIZE`, `SIGMA` and `KM`. Refer to the `config.yml` for details.

## 2.Drawing GUI Mode
This mode is a simple interactive demo written by OpenCV and easygui, which has been shown before.

```bash
python tool_draw.py -p models/celeba -r
```

Command | Meaning
------|-------
`-p` or `--path` | The model dir path to load.
`-r` or `--refinement` | Load the *Refinement Phase* if added manually. (Need `R_Model_gen_xxx.pth`)
`-c` or `--canny` | *Hyperparameter:* sigma of canny (default=3)
`-k` or `--kmeans` | *Hyperparameter:* color cluster numbers of kmeans (default=3)

If everything is loaded successfully, a window shows as below:
 
<p align="center">
<img src="files/tool_1.png" width="640">
</p>

The drawing tool has three modes:
1. **Drawing from empty (not recommended)** <br> 
The drawing function in OpenCV is awful, which is not suitable for painting. The moving speed of mouse will affect the line quality. Drawing edge too fast or too slow will
both lead to the awful edges.

2. **Drawing from color domain and edge (Recommended).** <br>
We strongly recommend you to draw from this mode. We provide some anime edges and color domains drawn by myself in `./examples/getchu`. <br>
You can get more edges and color domains by yourself using the **Command Line Mode** above. The testing results contain extracted edges and color domains by default (`DEBUG: 1` in `config.yml`).

<p align="center">
<img src="files/mode2.gif">   
</p>

3. **Drawing from picture (Recommended too)**<br>
In this mode you need to choose a GT colorful image, then its edge and color domain will be auto-extracted, which is greatly convenient. <br>
For instance, just choose the image in the testing datasets. Optionally, use the command line parameter `-c` and `-k` to control
the sparsity of Canny and K-means (both default=3).

<p align="center">
<img src="files/mode3.gif">   
</p>

Four windows will show up, one for color domain, one for edge, one for output and a pane. Switch your typewriting into ENG first.

Key | Description
-----|------
Mouse `Left` | Draw
Mouse `Right` | Erase
Key `h` | Show the help message box.
Key `[` | To make the brush thickness smaller
Key `]` | To make the brush thickness larger
Key `g` | To reconstruct the image from edge and color domain
Key `u` | To refine the output only when `-r` is added in command line
Key `Alt` | To absorb mouse pointer color in color domain (the mouse must be moving at the same time)
Key `x` | To save the binary edge
Key `c` | To save the color domain
Key `s` | To save the output
Key `q` | To quit