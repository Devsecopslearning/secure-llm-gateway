import logging

API_KEY = "mysecretkey"
ALLOWED_ROLES = ["admin", "auditor"]

def check_api_key(key):
    return key == API_KEY

def check_role(role):
    return role in ALLOWED_ROLES

def log_query(user, prompt):
    logging.basicConfig(filename="query.log", level=logging.INFO)
    logging.info(f"{user} asked: {prompt}")