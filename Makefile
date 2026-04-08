.PHONY: dev build test clean install

dev:
	docker-compose up --build

build:
	docker-compose build

test:
	pytest backend/test_main.py -v

install:
	pip install -r requirements.txt
	cd frontend && npm install

train-baseline:
	python ml/baseline_model.py

train-bert:
	python ml/bert_model.py

evaluate:
	python ml/evaluate.py

backend:
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm start

clean:
	rm -rf ml/models/baseline.pkl ml/models/bert_finetuned/* ml/outputs/*
	rm -rf frontend/node_modules frontend/build
	docker-compose down --rmi all
