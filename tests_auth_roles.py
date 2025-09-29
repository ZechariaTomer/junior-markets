
"""
Test suite: Auth & Roles (HR / Job Seeker)
------------------------------------------
How to run (in your local project virtualenv):

    pip install pytest requests
    # Optionally set BASE_URL (default: http://127.0.0.1:8000):
    #   set BASE_URL=http://127.0.0.1:8000     (Windows CMD)
    #   $env:BASE_URL="http://127.0.0.1:8000"  (PowerShell)
    #   export BASE_URL=http://127.0.0.1:8000  (Mac/Linux)

    pytest -q tests_auth_roles.py

Endpoints expected:
    POST /auth/signup {email, password, role}
    POST /auth/login  {username, password}  -> returns {access, refresh}
    GET  /api/hr/ping (Bearer access)       -> returns {"ok": true, "role": "HR"}
    GET  /api/js/ping (Bearer access)       -> returns {"ok": true, "role": "Job Seeker"}
"""

import os
import json
import time
import typing as t

import pytest
import requests


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

HR_EMAIL = os.getenv("HR_EMAIL", "hr1@example.com")
HR_PASS = os.getenv("HR_PASS", "Test12345")
JS_EMAIL = os.getenv("JS_EMAIL", "js1@example.com")
JS_PASS = os.getenv("JS_PASS", "Test12345")


def url(path: str) -> str:
    path = path.lstrip("/")
    return f"{BASE_URL}/{path}"


def signup(email: str, password: str, role: str) -> requests.Response:
    return requests.post(url("/auth/signup"), json={
        "email": email,
        "password": password,
        "role": role
    })


def login(username: str, password: str) -> dict:
    r = requests.post(url("/auth/login"), json={
        "username": username,
        "password": password
    })
    assert r.status_code in (200, 201), f"Login failed ({r.status_code}): {r.text}"
    data = r.json()
    assert "access" in data, f"Missing access token in response: {data}"
    return data


def auth_get(path: str, access: str) -> requests.Response:
    return requests.get(url(path), headers={
        "Authorization": f"Bearer {access}"
    })


@pytest.fixture(scope="session")
def hr_tokens():
    # Try signup; 201/200 = created; 409 = already exists (both acceptable)
    r = signup(HR_EMAIL, HR_PASS, "hr")
    assert r.status_code in (200, 201, 409), f"HR signup unexpected ({r.status_code}): {r.text}"
    return login(HR_EMAIL, HR_PASS)


@pytest.fixture(scope="session")
def js_tokens():
    r = signup(JS_EMAIL, JS_PASS, "job_seeker")
    assert r.status_code in (200, 201, 409), f"JS signup unexpected ({r.status_code}): {r.text}"
    return login(JS_EMAIL, JS_PASS)


def test_hr_ping_ok(hr_tokens):
    """HR token can access /api/hr/ping and role is HR"""
    access = hr_tokens["access"]
    r = auth_get("/api/hr/ping", access)
    assert r.status_code == 200, f"/api/hr/ping should be 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data.get("ok") is True, f"Expected ok=true, got: {data}"
    assert str(data.get("role")).lower() == "hr", f'Expected role "HR", got: {data.get("role")}'


def test_js_ping_ok(js_tokens):
    """JS token can access /api/js/ping and role is Job Seeker"""
    access = js_tokens["access"]
    r = auth_get("/api/js/ping", access)
    assert r.status_code == 200, f"/api/js/ping should be 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data.get("ok") is True, f"Expected ok=true, got: {data}"
    assert str(data.get("role")).lower().replace(" ", "") == "jobseeker", f'Expected role "Job Seeker", got: {data.get("role")}'


def test_hr_cannot_access_js_ping(hr_tokens):
    """HR token must be forbidden from /api/js/ping (403)"""
    access = hr_tokens["access"]
    r = auth_get("/api/js/ping", access)
    assert r.status_code == 403, f"HR should get 403 on /api/js/ping, got {r.status_code}: {r.text}"


def test_js_cannot_access_hr_ping(js_tokens):
    """JS token must be forbidden from /api/hr/ping (403)"""
    access = js_tokens["access"]
    r = auth_get("/api/hr/ping", access)
    assert r.status_code == 403, f"JS should get 403 on /api/hr/ping, got {r.status_code}: {r.text}"


def test_tokens_expire_and_refresh_optionally(js_tokens):
    """
    OPTIONAL: If your backend supports POST /auth/refresh, check refresh flow.
    This test is tolerant: it will be skipped if /auth/refresh is missing.
    """
    refresh = js_tokens.get("refresh")
    if not refresh:
        pytest.skip("No refresh token provided by backend; skipping refresh flow test.")
    rr = requests.post(url("/auth/refresh"), json={"refresh": refresh})
    if rr.status_code == 404:
        pytest.skip("/auth/refresh not found; skipping refresh flow test.")
    assert rr.status_code in (200, 201), f"Refresh failed ({rr.status_code}): {rr.text}"
    data = rr.json()
    assert "access" in data, f"Refresh response missing access: {data}"
