# Makefile to create documentation using the Python LaTeX system.

PYTHON_SRC = /home/whit537/shelf/Python-2.4.2
MKHOWTO    = $(PYTHON_SRC)/Doc/tools/mkhowto \
				--iconserver icons \
				--split 4 \
				--link 2 \
				--favicon icons/zeta.ico \
				--dir ../html \
				--logging \
				--up-link "http://www.zetadev.com/software/httpy/" \
				--up-title "httpy homepage" \
				--address "<a href=\"http://www.zetadev.com/software/httpy/\">httpy is Zeta software</a>" \
#				--numeric \
#				--style style.css

default: html clean

html:
	rm -rf ../html
	$(MKHOWTO) httpy.tex
	cp -r ../icons ../html/
	rm -rf ../html/icons/.svn


clean:
	rm -f *~ *.aux *.idx *.ilg *.ind *.log *.toc *.bkm *.syn \
			*.pla *.eps *.pdf *.ps *.lof *.l2h *.tex2 *.dvi
