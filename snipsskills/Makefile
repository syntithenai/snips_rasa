test:
	current=`pwd`; \
	for skillRepo in snips_skill_maths snips_skill_spelling snips_skill_monitorcontrol snips_skill_usb_power ; do \
		echo $$skillRepo; \
		echo "\n"; \
		cd "$$current/$$skillRepo" ; \
		python3 setup.py test ;\
	done
	

format:
	current=`pwd`; \
	for skillRepo in snips_skill_maths snips_skill_spelling snips_skill_monitorcontrol snips_skill_usb_power ; do \
		echo $$skillRepo; \
		echo "\n"; \
		cd "$$current/$$skillRepo" ; \
		pip3 install pycodestyle ; \
		pip3 install autopep8 ; \
		autopep8 --in-place --recursive --exclude='src,temp' .  ; \
		pycodestyle --exclude='src,temp' . ; \
	done
	

install:
	current=`pwd`; \
	for skillRepo in snips_skill_maths snips_skill_spelling snips_skill_monitorcontrol snips_skill_usb_power ; do \
		echo $$skillRepo; \
		echo "\n"; \
		cd "$$current/$$skillRepo" ; \
		rm -fr build ; \
		rm -fr dist ; \
		rm -fr *.egg-info ; \
		rm -fr **/*.pyc ; \
		python3 setup.py install --user ; \
		python3 setup.py develop --user ; \
		pip install --upgrade ./ ; \
	done
	snips-install-assistant snips-assistant-basics/assistantproj_GwB7NQG39.zip
	snips&
	sleep 10
	cd snips-assistant-basics/
	snipsskills install
	
run:
	cd snips-assistant-basics/
	snipsskills run


pypi:
	current=`pwd`; \
	for skillRepo in snips_skill_maths snips_skill_spelling snips_skill_monitorcontrol snips_skill_usb_power ; do \
		echo $$skillRepo; \
		echo "\n"; \
		cd "$$current/$$skillRepo" ; \
		rm -fr build ; \
		rm -fr dist ; \
		rm -fr *.egg-info ; \
		rm -fr **/*.pyc ; \
		python3 setup.py install --user ; \
		python3 setup.py develop --user ; \
		python3 setup.py sdist ; \
		python3 setup.py bdist_wheel --universal ; \
		twine upload dist/* ; \
	done

clean:
	current=`pwd`; \
	for skillRepo in snips_skill_maths snips_skill_spelling snips_skill_monitorcontrol snips_skill_usb_power ; do \
		echo $$skillRepo; \
		echo "\n"; \
		cd "$$current/$$skillRepo" ; \
		rm -fr build ; \
		rm -fr dist ; \
		rm -fr *.egg-info ; \
		rm -fr **/*.pyc ; \
	done
