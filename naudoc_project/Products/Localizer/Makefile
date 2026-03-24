
mo:
	./zgettext.py -m

clean:
	rm -f *~ *.pyc
	rm -f locale/*~ locale/locale.pot.bak locale/*.mo
	rm -f help/*~
	rm -f tests/*~ tests/*.pyc
	rm -f ui/*~

test:
	python tests/test_language.py
	python tests/test_zgettext.py


binary: clean mo
	rm -f refresh.txt
