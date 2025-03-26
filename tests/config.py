
def initialize_env_vars():
    import os
    os.environ["AUGURY_OAUTH2_INTERNAL_URL"] = 'test'
    os.environ["AUGURY_OAUTH2_URL"] = 'test'
    os.environ["OAUTH2_CLIENT_ID"] = 'test'
    os.environ["OAUTH2_CLIENT_SECRET"] = 'test'
