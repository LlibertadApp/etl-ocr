install:
	cp ./.env.sample .env
	npm install
	python3 -m pip install -t ./vendor -r lambda/SaveImageToS3/requirements.txt

deploy:
	npm run deploy