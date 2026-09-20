import requests
import streamlit as st


BASE_URL = "http://127.0.0.1:8000"


# =========================================
# Authentication
# =========================================

def login_user(email, password):

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def register_user(name, email, password):

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def refresh_access_token(refresh_token):

    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={
            "refresh_token": refresh_token
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# =========================================
# Authentication Header
# =========================================

def get_auth_headers():

    access_token = st.session_state.get(
        "access_token"
    )

    return {
        "Authorization": f"Bearer {access_token}"
    }


# =========================================
# Document APIs
# =========================================

def upload_document(uploaded_file):

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file,
            "application/pdf"
        )
    }

    response = requests.post(
        f"{BASE_URL}/upload",
        files=files,
        headers=get_auth_headers(),
        timeout=60
    )

    response.raise_for_status()

    return response.json()


def get_documents():

    response = requests.get(
        f"{BASE_URL}/documents",
        headers=get_auth_headers(),
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def delete_document(filename):

    response = requests.delete(
        f"{BASE_URL}/document/{filename}",
        headers=get_auth_headers(),
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def get_document_url(filename):

    return f"{BASE_URL}/document/{filename}"


# =========================================
# RAG / Ask API
# =========================================

def ask_question(question):

    response = requests.post(
        f"{BASE_URL}/ask",
        json={
            "question": question
        },
        headers=get_auth_headers(),
        timeout=60
    )

    response.raise_for_status()

    return response.json()