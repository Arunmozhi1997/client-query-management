import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import os

st.set_page_config(page_title="Client Query Management")

DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "client_query_management"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "kovilvenni"),
}
def get_conn():
    conn = psycopg2.connect(
        host=DB["host"],
        port=DB["port"],
        dbname=DB["dbname"],
        user=DB["user"],
        password=DB["password"],
    )
    return conn

conn = get_conn()

def fetch_all(sql, params=None):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()

def exec_query(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
    conn.commit()

def hash_sha256(password: str) :
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_username(username: str):
    rows = fetch_all("SELECT * FROM users WHERE username = %s", (username,))
    return rows[0] if rows else None

def authenticate(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        return None
    if hash_sha256(password) == user["hashed_password"]:
        return user
    return None

def create_user(username: str, password: str, role: str):
    """
    Create a new user with SHA-256 hashed password.
    Returns (success: bool, message: str)
    """
    if role not in ("Client", "Support"):
        return False, "Invalid role"
    if not username or not password:
        return False, "Username and password are required"
    if get_user_by_username(username):
        return False, "Username already exists"
    hashed = hash_sha256(password)
    try:
        exec_query(
            "INSERT INTO users (username, hashed_password, role, created_at) VALUES (%s,%s,%s,NOW())",
            (username, hashed, role),
        )
        return True, "User created successfully"
    except Exception as e:
        return False, f"DB error: {e}"

st.title("Client Query Management")

st.sidebar.header("Account")

mode = st.sidebar.radio("Choose action", ["Login", "Register"])

if mode == "Register":
    st.sidebar.subheader("Create a new account")
    new_username = st.sidebar.text_input("Username (unique)", key="reg_user")
    new_password = st.sidebar.text_input("Password", type="password", key="reg_pass")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password", key="reg_pass2")
    new_role = st.sidebar.radio("Role", ("Client", "Support"), index=0, key="reg_role")
    if st.sidebar.button("Register"):
        if new_password != confirm_password:
            st.sidebar.error("Passwords do not match.")
        else:
            ok, msg = create_user(new_username.strip(), new_password, new_role)
            if ok:
                st.sidebar.success(msg)
                st.sidebar.info("Now switch to Login to sign in.")
            else:
                st.sidebar.error(msg)

else:  
    st.sidebar.subheader("Sign in")
    username = st.sidebar.text_input("Username", key="login_user")
    password = st.sidebar.text_input("Password", type="password", key="login_pass")
    if st.sidebar.button("Sign in"):
        user = authenticate(username.strip(), password)
        if user:
            st.session_state["user"] = user
            st.sidebar.success(f"Signed in as {user['username']} ({user['role']})")
        else:
            st.sidebar.error("Invalid username or password")

if "user" in st.session_state:
    with st.sidebar.expander("Account"):
        st.write(f"Signed in: *{st.session_state['user']['username']}*")
        st.write(f"Role: *{st.session_state['user']['role']}*")
        if st.button("Sign out"):
            st.session_state.pop("user", None)
            st.success("Signed out. Please refresh the page or reopen the app to sign in.")
            st.stop()

if "user" not in st.session_state:
    st.info("Please register or sign in from the sidebar.")
    st.stop()

user = st.session_state["user"]

def load_queries():
    try:
        rows = fetch_all("SELECT * FROM queries ORDER BY query_created_time DESC;")
        df = pd.DataFrame(rows)
        return df
    except Exception as e:
        st.error(f"Failed to fetch queries from DB: {e}")
        return pd.DataFrame()

st.subheader("All Queries")
df = load_queries()
if df.empty:
    st.write("No queries found.")
else:
    st.dataframe(df)

if user["role"] == "Client":
    st.markdown("### Create New Query")
    mail = st.text_input("Email", value=user["username"] + "@example.com", key="new_mail")
    mobile = st.text_input("Mobile Number", key="new_mobile")
    heading = st.text_input("Heading", key="new_heading")
    description = st.text_area("Description", key="new_desc")
    if st.button("Submit Query"):
        if not heading.strip():
            st.error("Heading is required.")
        else:
            try:
                exec_query(
                    "INSERT INTO queries (mail_id, mobile_number, query_heading, query_description, status, query_created_time) VALUES (%s,%s,%s,%s,'Open',NOW())",
                    (mail.strip() or None, mobile.strip() or None, heading.strip(), description.strip() or None),
                )
                st.success("Query submitted.")
            except Exception as e:
                st.error(f"Failed to submit query: {e}")

            df = load_queries()
            if df.empty:
                st.write("No queries found.")
            else:
                st.dataframe(df)
if user["role"] == "Support":
    st.markdown("### Close Query")
    qid = st.number_input("Query ID to close", min_value=1, step=1)
    if st.button("Close Query"):
        try:
            exec_query(
                "UPDATE queries SET status='Closed', query_closed_time=NOW() WHERE query_id = %s",
                (int(qid),),
            )
            st.success(f"Query {int(qid)} closed.")
        except Exception as e:
            st.error(f"Failed to close query: {e}")

        df = load_queries()
        if df.empty:
            st.write("No queries found.")
        else:
            st.dataframe(df)