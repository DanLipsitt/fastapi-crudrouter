import pytest
import inspect
from fastapi.testclient import TestClient

from .implementations import *


def yield_test_client(app, impl):
    if impl.__name__ == "tortoise_implementation":
        from tortoise.contrib.test import initializer, finalizer

        initializer(["tests.implementations.tortoise_"])
        with TestClient(app) as c:
            yield c
        finalizer()

    else:
        with TestClient(app) as c:
            yield c


def label_func(*args):
    func, datasource = args[0]
    return f"{func.__name__}-{datasource.name}"


@pytest.fixture(params=implementations, ids=label_func, scope="class")
def client(request):
    impl, datasource = request.param

    datasource.clean()
    app, router, settings = impl(db_uri=datasource.uri)
    [app.include_router(router(**kwargs)) for kwargs in settings]
    yield from yield_test_client(app, impl)


@pytest.fixture(
    params=[
        sqlalchemy_implementation_custom_ids,
        databases_implementation_custom_ids,
        ormar_implementation_custom_ids,
        gino_implementation_custom_ids,
    ]
)
def custom_id_client(request):
    yield from yield_test_client(request.param(), request.param)


@pytest.fixture(
    params=[
        sqlalchemy_implementation_string_pk,
        databases_implementation_string_pk,
        ormar_implementation_string_pk,
        gino_implementation_string_pk,
    ],
    scope="function",
)
def string_pk_client(request):
    yield from yield_test_client(request.param(), request.param)


@pytest.fixture(
    params=[
        sqlalchemy_implementation_integrity_errors,
        ormar_implementation_integrity_errors,
        gino_implementation_integrity_errors,
    ],
    scope="function",
)
def integrity_errors_client(request):
    yield from yield_test_client(request.param(), request.param)
