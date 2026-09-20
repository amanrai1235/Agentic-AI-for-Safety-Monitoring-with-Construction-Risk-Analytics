.PHONY: install seed api web build test demo clean

install:              ## install backend and frontend dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

seed:                 ## reset and seed the database with demo site data
	cd backend && python -m app.seed --reset

api:                  ## run the FastAPI server on :8000
	cd backend && uvicorn app.main:app --reload --port 8000

web:                  ## run the React dev server on :5173
	cd frontend && npm run dev

build:                ## build the React app so the API serves it on :8000
	cd frontend && npm run build

test:                 ## run the backend test suite
	cd backend && python -m pytest -q

demo:                 ## stream live site events into the running platform
	cd backend && python -m app.simulate --interval 5

clean:
	rm -f backend/buildsure.db
	rm -rf frontend/dist backend/.pytest_cache
	find . -name __pycache__ -type d -exec rm -rf {} +
