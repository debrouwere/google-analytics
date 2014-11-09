# None

Convenience functions for authenticating with Google and asking for authorization with Google, with  `authenticate` at its core. 
`authenticate` will do what it says on the tin, but unlike  the basic `googleanalytics.oauth.authenticate`, it also tries  to get existing credentials from the keyring, from environment variables, it prompts for information when required and so on.


