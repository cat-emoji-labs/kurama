mongo:
	docker build -t mongodb -f ./mongodb.dockerfile . && docker run -d --name mongodb -p 27017:27017 mongodb

pg:
	docker build -t pg -f ./postgres.dockerfile . && docker run -d --name csv -p 5433:5432 pg

psql:
	docker exec -it csv psql -U user -d test

server:
	python3 kurama/app.py