# smoke_test.py
import importlib
import os
import sys
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import declarative_base
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from typing import get_type_hints
from faker import Faker

# === CONFIG ===
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = "sqlite:///:memory:"  # Non-destructive in-memory DB
FAKE = Faker()

# === SETUP DATABASE ===
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.rollback()  # never commit
    finally:
        session.close()

# === UTILITY: import all modules ===
def import_all_modules(base_dir):
    sys.path.insert(0, base_dir)
    modules = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                mod_path = os.path.relpath(os.path.join(root, file), base_dir) \
                    .replace(os.sep, ".").rsplit(".py", 1)[0]
                try:
                    modules.append(importlib.import_module(mod_path))
                except Exception as e:
                    print(f"Failed to import {mod_path}: {e}")
    return modules

# === UTILITY: find FastAPI instance ===
def find_fastapi_app(modules):
    for mod in modules:
        for attr in dir(mod):
            obj = getattr(mod, attr)
            try:
                from fastapi import FastAPI
                if isinstance(obj, FastAPI):
                    return obj
            except Exception:
                continue
    return None

# === UTILITY: find SQLAlchemy models ===
def find_models(modules):
    models = []
    for mod in modules:
        for attr in dir(mod):
            obj = getattr(mod, attr)
            try:
                if hasattr(obj, "__table__") and hasattr(obj, "__mapper__"):
                    models.append(obj)
            except Exception:
                continue
    return models

# === GENERATE DUMMY DATA ===
def generate_dummy_data(model_cls):
    data = {}
    hints = get_type_hints(model_cls)
    for field, typ in hints.items():
        if typ == int:
            data[field] = FAKE.random_int()
        elif typ == str:
            data[field] = FAKE.word()
        elif typ == float:
            data[field] = round(FAKE.pyfloat(left_digits=2, right_digits=2),2)
        elif typ == bool:
            data[field] = FAKE.boolean()
        else:
            data[field] = None
    return data

# === MAIN TEST FUNCTION ===
def run_smoke_test():
    modules = import_all_modules(PROJECT_DIR)
    app = find_fastapi_app(modules)
    if not app:
        print("No FastAPI app found.")
        return

    client = TestClient(app)
    models = find_models(modules)

    results = {"routes": [], "models": []}

    # === TEST MODELS: simulate creation ===
    with session_scope() as session:
        for model in models:
            try:
                dummy = generate_dummy_data(model)
                obj = model(**dummy)
                session.add(obj)
                session.flush()  # simulate insertion
                results["models"].append({"model": model.__name__, "status": "PASS"})
            except Exception as e:
                results["models"].append({"model": model.__name__, "status": "FAIL", "error": str(e)})

    # === TEST ROUTES: simulate requests ===
    for route in app.routes:
        if hasattr(route, "methods"):
            method = list(route.methods)[0]
            url = route.path
            try:
                if method in ["POST", "PUT", "PATCH", "DELETE"]:
                    # simulate non-destructive request
                    response = client.request(method, url, json={})
                else:  # GET or others
                    response = client.request(method, url)
                results["routes"].append({
                    "path": url,
                    "method": method,
                    "status_code": response.status_code
                })
            except Exception as e:
                results["routes"].append({
                    "path": url,
                    "method": method,
                    "error": str(e)
                })

    # === OUTPUT JSON REPORT ===
    report_file = os.path.join(PROJECT_DIR, "smoke_test_report.json")
    with open(report_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Smoke test completed! Report saved to {report_file}")

# === RUN ===
if __name__ == "__main__":
    run_smoke_test()
