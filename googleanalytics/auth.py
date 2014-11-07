import os
import utils
import oauth

# cascade through all options to get the identity
def get_identity(prompt=False, client=None, name=None, prefix=None, suffix=None):
    environment_keys = {
        "client_id": utils.affix(prefix, 'GOOGLE_ANALYTICS_CLIENT_ID', suffix), 
        "client_secret": utils.affix(prefix, 'GOOGLE_ANALYTICS_CLIENT_SECRET', suffix), 
        "refresh_token": utils.affix(prefix, 'GOOGLE_ANALYTICS_REFRESH_TOKEN', suffix), 
    }

    if client:
        identity = client
    elif name:
        identity = utils.keyring.get(name)

    if identity:
        client_id = identity['client_id']
        client_secret = identity['client_secret']
        refresh_token = identity.get('access_token')
        refresh_token = identity.get('refresh_token')
        name = name or identity.get('name', client_id)
    elif os.environ.get(environment_keys['client_id']):
        client_id = os.environ.get(environment_keys['client_id'])
        client_secret = os.environ.get(environment_keys['client_secret'])
        access_token = os.environ.get(environment_keys['access_token'])
        refresh_token = os.environ.get(environment_keys['refresh_token'])
        name = name or prefix or suffix or client_id
    
    if not (client_id and client_secret):
        if prompt:
            name = raw_input('Human-readable account name: ')
            client_id = raw_input('Client ID: ')
            client_secret = raw_input('Client secret: ')
        else:
            raise ValueError("""No Google Analytics identity found.
                Please provide a `client` dictionary, a `name` that maps to a client id 
                or existing login information in the keychain, or put authentication 
                information in GOOGLE_ANALYTICS_CLIENT_ID and GOOGLE_ANALYTICS_CLIENT_SECRET
                environment variables.""")

    return dict(
        name=name, 
        client_id=client_id, 
        client_secret=client_secret, 
        refresh_token=refresh_token
        )

def navigate(accounts, account=None, webproperty=None, profile=None):
    scope = accounts

    if account:
        scope = scope[account]

    if webproperty:
        if account:
            scope = scope.webproperties[webproperty]
        else:
            raise ValueError()

    if profile:
        if account and webproperty:
            scope = scope.profiles[profile]
        else:
            raise ValueError()

    return scope    

def authenticate(account=None, webproperty=None, profile=None, 
    prompt=False, client=None, name=None, prefix=None, suffix=None):
    
    identity = get_identity(
        prompt=prompt, 
        client=client, 
        name=name, 
        prefix=prefix, 
        suffix=suffix
        )
    client_id = identity['client_id']
    client_secret = identity['client_secret']
    access_token = identity.get('access_token')
    refresh_token = identity.get('refresh_token')

    if refresh_token:
        accounts = oauth.authenticate(client_id, client_secret, access_token, refresh_token)
    else:
        raise ValueError("""Cannot authenticate without client_id, 
            client_secret and either access_token or refresh_token.""")

    scope = navigate(accounts, account=account, webproperty=webproperty, profile=profile)
    return scope
