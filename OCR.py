## Importing Necessary Items
import io
import logging

import click
import cv2
import numpy as np
import pytesseract as pt
from autocorrect import Speller
from wand.image import Image as wi


## CLI initialization & Input definition
@click.command()
@click.option(
    '--input',
    required=True,
    help=
    "type/paste the file path you wish to perform OCR.PDF, PNG, JPG, and JPEG are allowed."
)
@click.option('--output', required=True, help="Please name your output file.")
@click.option(
    '--verbose',
    required=False,
    help="Defaulted to False. to see detailed log, Enter the bool True")
## Main Function Definition
def ocr(input, output, verbose=False):
    ## Enable Logging if verbose is set to be True.
    ## Formatting goes : Time, category, message.
    if verbose == 'True':
        FORMAT = "%(asctime)s : %(levelname)s / %(message)s"
        logging.basicConfig(filename="OCR.log",
                            format=FORMAT,
                            level=logging.DEBUG)
        lg = logging.getLogger()

    ## "Disables" logging (Turns into critical mode) so none of the message is logged, if
    ## verbose is left False, or is manually entered "False".
    elif verbose == 'False':
        FORMAT = "%(asctime)s : %(levelname)s %(message)s"
        logging.basicConfig(filename="OCR.log",
                            format=FORMAT,
                            level=logging.CRITICAL)
        lg = logging.getLogger()
    ## If it is neither, raises an error, stops here.
    else:
        raise Exception(
            "verbose has to be a boolean variable, either True or False.")
    lg.info('Running OCR on {}...'.format(input))

    #### 1. GIVEN FILE IS A PDF:
    ## If a pdf is selected as a filetype, we will follow a different flow to a jpg or a png.
    if input.lower().endswith('.pdf'):  ##Proceed Only if filetype is pdf.
        lg.debug("Detected a PDF file, converting to image...")
        pdf = wi(filename=input, resolution=300)
        img = pdf.convert(
            "jpeg"
        )  ##Usage of Wand to convert pdf to jpeg (Multilayer for multi-page)
        ## Separation of Multilayer Image into multiple single-layer images, sorted in a list.
        parts = []
        for i in img.sequence:
            page = wi(image=i)
            parts.append(page.make_blob("jpeg"))
        #parts = [wi(image = i).make_blob("jpeg") for i in img.sequence]

        lg.debug("Conversion Completed, Proceeding to run OCR...")

        ## Pre-processing, text-conversion, and Post-Processing.
        out_text = []
        for j in parts:
            image = io.BytesIO(j)
            ## Pre-processing... Parameters were chosen based on a study : https://www.researchgate.net/publication/319288194_Selecting_Automatically_Pre-Processing_Methods_to_Improve_OCR_Performances
            ## Pre-processing Method Chosen : Grayscale + Gaussian Binarization
            image = cv2.imdecode(np.frombuffer(image.read(), np.uint8),
                                 1)  #cv2 conversion
            grayscaled = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  #Grayscaling
            image = cv2.adaptiveThreshold(grayscaled, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 17,
                                          32)  #Gaussian Binarization
            text = pt.image_to_string(
                image, lang="eng")  #Text recognition with tesseract.
            out_text.append(text)  #store into a list, page by page.
        lg.debug("OCR completed, writing into a {}.txt file...".format(output))

        ## Post-Processing & Storage in .txt file
        txt = open('{}.txt'.format(output), "w+")  #Creation of new file
        spell = Speller('en')  #calling & defining the autocorrect module
        for k in range(len(out_text)):
            txt.write(
                spell(out_text[k])
            )  #Page by Page, post-process'ed texts are added into the txt file.
        txt.close()  #Done
        lg.info("COMPLETED OCR ON {}".format(input))

        ## Complete message in CLI and finish.
        click.echo(
            "Completed! Check the directory of this .py file, you should see the .txt file!"
        )
        return None

    #### GIVEN FILE IS EITHER PNG, JPG or a JPEG
    ## Making sure we are dealing with the right filetype (png or jp(e)g.)
    elif not input.lower().endswith(
        ('.png', '.jpg', '.jpeg')
    ):  ##Elif not is used to error out unsupported. Thus passing this will mean that the passed file is indeed a png, jpg or a jpeg.
        raise Exception(
            "Filetype Not Supported!!, try with PDF, PNG, JPG, or JPEG to proceed."
        )

    lg.debug("Detected an image file, proceeding to OCR...")
    scan = cv2.imread(input)
    ## Preprocessing... Methods and Parameters were chosen based on a study : https://www.researchgate.net/publication/319288194_Selecting_Automatically_Pre-Processing_Methods_to_Improve_OCR_Performances
    ## Preprocessing Method Chosen : Grayscale + Gaussian Binarization
    grayscaled = cv2.cvtColor(scan, cv2.COLOR_BGR2GRAY)  #Grayscaling
    scan = cv2.adaptiveThreshold(grayscaled, 255,
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 17,
                                 32)  #Gaussian Binarization
    guess = pt.image_to_string(scan,
                               lang="eng")  #Text recognition with tesseract.

    ## Post-Processing & Storage in .txt file
    txt = open('{}.txt'.format(output), "w+")  #Creation of new file
    spell = Speller('en')  # calling & defining the autocorrect module
    txt.write(str(spell(guess)))  #storing the post-process'ed
    txt.close()
    lg.info("COMPLETED OCR ON {}".format(input))

    ## Complete message in CLI and finish.
    click.echo(
        "Completed! Check the directory of this .py file, you should see the txt file!"
    )
    return None


if __name__ == '__main__':
    ocr()
