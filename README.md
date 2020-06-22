# Coding Challenge - OCR Machine

This document aims to further explain and clarify what the workflow and configuration was/is.

The full task description can be found below.

Also, the main Project zipped folder containing the `.py` file as well as `.toml` file for package management can be found below as well.

[coding_test.pdf](coding_test.pdf)

[OCR.py](OCR.py)

[pyproject.toml](pyproject.toml)

# Coding Environemnt

PC environment : iMac, MacOS 10.13.6 

Used Python IDE here was [Pycharm](https://www.jetbrains.com/pycharm/) by JetBrains, as they have very easy setup for a virtual environment build, including the usage of Poetry.

Things done (mostly in order):

- Poetry Install and Venv configuration
- Connection of Venv and Pycharm IDE
- Installment of homebrew for outside-python packages

# Basic Flow of the Code:

The flow of the code goes as follows:

- Import necessary packages
    - io
    - numpy
    - pytesseract
    - cv2
    - click
    - wand
    - logging
    - autocorrect
- Activating and Setup the Click module to operate with CLI

    Options:

    - Input (path)
    - Output (filename)
    - verbose (log bool)
- Definition of Main Function
    1. **Activation of logging if required**
    2. **PDF OCR Process if detected a pdf:**
    2a. Conversion to Multi-layer jpg
    2b. Splitting of Multi-layer to several single layer
    2c. Pre-processing
    2d.  Making Guess with Tesseract
    2e. Post-Processing 
    2f. Write to a txt
    3. **Errors out if PDF, PNG, JPG, or JPEG not detected**
    4. **OCR process for ordinary image file:**
    4a. Pre-processing
    ****4b. Making Guess with Tesseract
    ****4c. Post-Processing
    ****4d. Write to a txt

# Pytesseract and TesseractOCR engine

pytesseract was install through `poetry`, and the tesseract engine by itself was installed through `brew`.  Versions are `0.3.4` , and `4.1.1` respectively.

Pytesseract served its main purpose of performing the OCR, essentially maiking a "guess" to a pre-processed data (more on pre-processing below).  The only used command from this package is:

```python
pytesseract.image_to_string(target, lang = 'eng)
```

It is defaulted to English anyways, but since we have a problem with constraint "English only", it shouldn't hurt to specify.

# OpenCV

## Reading/Loading Images

all of the reading and loading of the photos or converted photos were done through the OpenCV module, using the following command.

```python
cv2.imread(target_path)
```

## Pre-Processing

OpenCV has also contributed in pre-processing of the work. According to the [research](https://www.researchgate.net/publication/319288194_Selecting_Automatically_Pre-Processing_Methods_to_Improve_OCR_Performances), over 90% of the work were improved through a Binarization Preprocessing, or so-called thresholding. Also, Gaussian Adaptive Thresholding are know to well serve the purpose, thus the main pre-processing method being used was:

```python
cv2.adaptiveThreshold(grayscaledImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,x, c)
```

 

the gray-scaled images were obtained through:

```python
cv2.cvtColor(targetImage, cv2.COLOR_BGR2GRAY)
```

### Finding the right parameters

The problem was the combination of parameters `x` and `c` . As I have never experienced OCR development or OpenCV in my life, I struggled to find a "sweetspot" of the parameter combination. Thus, I have done a exhaustive&random search on another piece of code (sample also uploaded here) to determine the most suitable pair of `x` and `c`, on multiple image samples. The result I got with this search was `17` and `32` , respectively.

The flow of the search was the following:

1. Load the sample images
2. choose an arbitrary number of loops(around 30-50% of exhaustive), and randomly select acceptable `x` and `c`.
3. Pre-process on the parameters `x` and `c` , and then perform the tesseract OCR.
4. to evaluate the wellness of the OCR: 
**(Hypothesis: if an OCR went accurately, one should obtain a sentence with words that make sense. ↔  words should be accurately read.)**
4a. load an open-source most used 18k word dictionary, convert into a word list.
4b. for each word in OCR'ed result, if the word is found in the dictionary, add 1 point.
4c. list the total scores of each attempts.
5. Return the index and the pair of parameters with the highest score. (i.e. return the pair of parameters containing more "known" words.)

for most of the samples i used, they have shown a consistent parameters around late 10s for `x` and late20s/early 30s for `c`.

There are great chances that the parameters for pre-processing or even methods of pre-processing are suboptimal. for example, the second sample file (82251504.png) has yielded a terrible score overall. There are definitely ways to improve the accuracy through smart selection of preprocessing methods.

# Autocorrect & Speller

## Post-Processing

For a post-processing measure, I have tried implementing several modules from `TextBlob`, `SymSpell`, and `Pyspellchecker`, but I have failed to obtain an even decent result. With the default configuration, they have changed the right words into a wrong one, changing rwos without reason, etc. They were simply unusable, with my knowledge of these packages.

However, `Autocorrect` was bringing me some good luck. For small errors, the `Speller` submodule consistently fixed them without issues. They also run fast. 

The issue I noticed and has space for improvement in the future would be the following  things:

1. **"-" separated words**: Often for longer words, they are forced to have the "-" in te line break. This will be recognized as two words in all the post-processing modules i have tried.
2. **Names/Original words**: The names can be recognized to be similar to a known word, and can be swapped .
3. **links & sensitive characters**: links can be considered a "wrong" line of letters and may be replaced. However this is crucially bad since if any letter is swapped from the link it will be an invalid one.
4. **Non-characters**: Charts and graphs, symbols and pictures are often mistakenly recognized.

# Other Modules Used Worth Mentioning

## Click

For a first time CLI build, Click ended up to be a very intuitive package. I have used to make the following options.

- Path of INPUT, type = `str` , required.

```python
@click.option('--input',required=True)
```

- Name of OUTPUT, type = `str` , required

```python
@click.option('--output', required=True)
```

- Verbose Logging, type = `boolean`, not required, default = `False`

```python
@click.option('--verbose', required=False)
```

and `click.echo` command was used to display messages in the command line.

## yapf

Stands for 'yet another python formatter`, makes the script readable. I do personally dislike the outcome, seems less legible to me. the code used to convert in shell is:

```bash
yapf target.py
```

## isort

Re-orders and cleans the package imports. Mostly did nothing to my code. Again a shell command directly manipulating the file, the code is:

```bash
isort target.py
```
