import os
import streamlit_authenticator as stauth
import streamlit as streamlit


def init_aws_session():
    # AWS Profile
    import boto3
    aws_profile = os.getenv('AWS_PROFILE', None)
    if aws_profile:
        boto3.setup_default_session(profile_name=aws_profile)
    # AWS AccessKey from Environment Variables 
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', None)
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', None)
    aws_region = os.getenv('REGION', None)
    if aws_access_key_id and aws_secret_access_key and aws_region:
        boto3.setup_default_session(
            aws_access_key_id=aws_access_key_id, 
            aws_secret_access_key=aws_secret_access_key
            )

def load_auth_config():
    import yaml
    from yaml import SafeLoader
    with open('.streamlit/auth_conf.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    stauth.Hasher.hash_passwords(config['credentials'])
    authenticator = stauth.Authenticate(
        '.streamlit/auth_conf.yaml',
        # config['credentials'],
        # config['cookie']['name'],
        # config['cookie']['key'],
        # config['cookie']['expiry_days']
    )
    return authenticator

def signin_authentication(authenticator, st):
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)
    if st.session_state['authentication_status']:
        authenticator.logout()
    elif st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] is None:
        st.warning('Please enter your username and password')
    return authenticator

def get_authen_decorator(st):
    def is_authen(roles):
        def wrapper(func):
            def wrapped_func(*args, **kwargs):
                if 'authentication_status' in st.session_state and st.session_state['authentication_status']:
                    for require_role in roles:
                        if require_role in st.session_state['roles']:
                            return func(*args, **kwargs)
                    st.error("You do not have the required role to access this page.")
                else:
                    st.warning("Please log in to access this page.")
            return wrapped_func
        return wrapper
    
    return is_authen