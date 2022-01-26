build:
	docker build . \
		--tag artsy/ops-util

push:
	docker login
	docker push artsy/ops-util:latest
