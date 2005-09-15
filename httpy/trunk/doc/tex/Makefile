# Makefile to create documentation using the Python LaTeX system.

PYTHON_SRC = /home/whit537/sandbox/Python-2.4.1
MKHOWTO    = $(PYTHON_SRC)/Doc/tools/mkhowto \
				--iconserver icons \
				--split 0 \
				--favicon icons/pyfav.gif \
				--dir ../html \
				--logging \
				--numeric


html:
	rm -rf ../html
	$(MKHOWTO) manual.tex
	cp -r ../icons ../html/
	rm -rf ../html/icons/.svn


clean:
	rm -f *~ *.aux *.idx *.ilg *.ind *.log *.toc *.bkm *.syn \
			*.pla *.eps *.pdf *.ps *.lof *.l2h *.tex2 *.dvi
