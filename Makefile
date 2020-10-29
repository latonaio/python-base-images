docker-build-pylib-lite: build-python-package
	bash ./builders/docker-build-pylib-lite.sh

docker-push-pylib-lite: build-python-package
	bash ./builders/docker-build-pylib-lite.sh push

docker-build-l4t: build-python-package
	bash ./builders/docker-build-pylib-base.sh

docker-push-l4t: build-python-package
	bash ./builders/docker-build-pylib-base.sh push

docker-build-l4t-ds: build-python-package
	bash ./builders/docker-build-pylib-ds.sh

docker-push-l4t-ds: build-python-package
	bash ./builders/docker-build-pylib-ds.sh push

docker-build-l4t-ds-ffmpeg: build-python-package
	bash ./builders/docker-build-pylib-ds-ffmpeg.sh

docker-push-l4t-ds-ffmpeg: build-python-package
	bash ./builders/docker-build-pylib-ds-ffmpeg.sh push

docker-build-l4t-ds-opencv: build-python-package
	bash ./builders/docker-build-pylib-ds-opencv.sh 7.2

docker-push-l4t-ds-opencv: build-python-package
	bash ./builders/docker-build-pylib-ds-opencv.sh 7.2 true

docker-build-pylib-python3-amd: build-python-package
	bash ./builders/docker-build-pylib-python3-amd.sh

docker-push-pylib-python3-amd: build-python-package
	bash ./builders/docker-build-pylib-python3-amd.sh push

docker-build-pylib-python3: build-python-package
	bash ./builders/docker-build-pylib-python3.sh

docker-push-pylib-python3: build-python-package
	bash ./builders/docker-build-pylib-python3.sh push

################## packaging
build-python-package:
	python3 setup.py sdist
