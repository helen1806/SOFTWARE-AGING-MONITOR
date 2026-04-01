import os
from functools import wraps
from flask import session, redirect, url_for, abort
from supabase import create_client, Client


from dotenv import load_dotenv
load_dotenv()
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def get_current_user_id():
    """Return the Supabase user UUID from the Flask session, or None."""
    return session.get('user_id')


def login_required(f):
    """Decorator that redirects to /login if no user is in session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_user_id():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def sign_up(email: str, password: str):
    """
    Register a new user with Supabase.
    Returns (user, error_message).
    """
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            return res.user, None
        return None, "Sign up failed. Please try again."
    except Exception as e:
        return None, str(e)


def sign_in(email: str, password: str):
    """
    Sign in an existing user.
    Returns (session_data, error_message).
    """
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user and res.session:
            return res, None
        return None, "Invalid email or password."
    except Exception as e:
        return None, "Invalid email or password."


def sign_out(access_token: str):
    """Sign out from Supabase (invalidates the token server-side)."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass  # Even if this fails, we clear the Flask session