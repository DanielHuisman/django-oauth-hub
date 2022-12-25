# Providers

OAuth clients can be configured in the database, for example using Django Admin.
Any OAuth compliant provider can be configured, but several templates are available for several providers.

- [Callback URLs](#callback-urls)
- [Available Providers](#available-providers)
- [Custom Providers](#custom-providers)

## Callback URLs
### Development
```
http://localhost:8000/oauth/<oauth_client_id>/callback
http://localhost:8000/oauth/<oauth_client_slug>/callback

# Examples
http://localhost:8000/oauth/1/callback
http://localhost:8000/oauth/cb8d7cc9-6c91-42b7-affc-4809231316f7/callback
http://localhost:8000/oauth/google/callback
```

### Production
```
https://example.com/oauth/<oauth_client_id>/callback
https://example.com/oauth/<oauth_client_slug>/callback

# Examples
https://example.com/oauth/1/callback
https://example.com/oauth/cb8d7cc9-6c91-42b7-affc-4809231316f7/callback
https://example.com/oauth/google/callback
```

## Available Providers
Templates are available for the providers listed below. The default slug is also listed.

- [Google](https://developers.google.com/identity/openid-connect/openid-connect) - `google`
- [Microsoft](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-protocols-oidc) - `microsoft`

## Custom Providers
TODO
