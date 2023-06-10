postgres:
	docker build -t pg -f ./postgres.dockerfile . && docker run -d --name csv -p 5433:5432 pg

psql:
	docker exec -it csv psql -U user -d test

server:
	python3 kurama/app.py