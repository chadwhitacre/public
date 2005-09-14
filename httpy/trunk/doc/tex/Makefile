# Makefile to process a file LaTeX with the Python LaTeX system.
#  Optionally processes reStructuredText files.

#
# Change the following to point to your Python source code.
#
PYTHON_SRC = /home/whit537/sandbox/Python-2.4.1


#
# Change these flags for your purposes.
#
HTMLFLAGS= --iconserver icons --html -s 0 --favicon icons/pyfav.gif \
--dir html

MKHOWTO = $(PYTHON_SRC)/Doc/tools/mkhowto


#
# Change this to the name of your source file (without extension).
#
SRC_NAME=manual


TARGETS = $(SRC_NAME).html

all: html

html:	$(TARGETS)


$(SRC_NAME).html: $(SRC_NAME).tex
	$(MKHOWTO) $(HTMLFLAGS) $(SRC_NAME).tex
	cp -r ../icons html/icons


clean:
	rm -f *~ *.aux *.idx *.ilg *.ind *.log *.toc *.bkm *.syn \
*.pla *.eps *.pdf *.ps *.lof *.l2h *.tex2 *.dvi
	rm -rf html