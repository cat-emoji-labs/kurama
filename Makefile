mongo:
	docker build -t mongodb . && docker run -d --name mongodb -p 27017:27017 mongodb

server:
	python3 kurama/app.py