# Copyright (c) 2026 Brothertown Language
import os
import streamlit.components.v1 as components
from streamlit_oauth import OAuth2Component as BaseOAuth2Component

def get_fixed_authorize_button():
    """
    Creates a fixed version of the authorize_button component that points
    directly to index.html to avoid 'read error' (IsADirectoryError) in Streamlit.
    """
    # Locating the streamlit_oauth package path
    import streamlit_oauth
    package_dir = os.path.dirname(streamlit_oauth.__file__)
    build_dir = os.path.join(package_dir, "frontend", "dist")
    
    # In some Streamlit versions, providing the directory works, but if it fails
    # with IsADirectoryError, we might need a workaround.
    # However, declare_component 'path' MUST be a directory containing index.html.
    # The 'read error' usually happens when Streamlit tries to serve the root 
    # of the component path as a file.
    
    # WORKAROUND: In some cases, explicitly using index.html as a symlink or 
    # ensuring the path is recognized as a directory by Streamlit might help.
    # But since we can't change .venv, we just redeclare it here.
    # If it still fails, we might need to serve it ourselves via a custom route.
    
    return components.declare_component("authorize_button", path=build_dir)

_fixed_authorize_button = get_fixed_authorize_button()

class OAuth2Component(BaseOAuth2Component):
    def authorize_button(self, name, redirect_uri, scope, height=800, width=600, key=None, pkce=None, extras_params={}, icon=None, use_container_width=False, auto_click=False):
        import asyncio
        import streamlit as st
        from streamlit_oauth import _generate_state, _generate_pkce_pair, StreamlitOauthError
        
        # generate state based on key
        state = _generate_state(key)
        if pkce:
            code_verifier, code_challenge = _generate_pkce_pair(pkce, key)
            extras_params = {**extras_params, "code_challenge": code_challenge, "code_challenge_method": pkce}
        
        authorize_request = asyncio.run(self.client.get_authorization_url(
            redirect_uri=redirect_uri,
            scope=scope.split(" "),
            state=state,
            extras_params=extras_params
        ))
        
        # Use our FIXED component declaration
        result = _fixed_authorize_button(
            authorization_url=authorize_request,
            name=name,
            popup_height=height,
            popup_width=width,
            key=key,
            icon=icon,
            use_container_width=use_container_width,
            auto_click=auto_click,
        )
        
        if result:
            try:
                del st.session_state[f'state-{key}']
                del st.session_state[f'pkce-{key}']
            except:
                pass
            if 'error' in result:
                raise StreamlitOauthError(result)
            if 'state' in result and result['state'] != state:
                raise StreamlitOauthError(f"STATE {state} DOES NOT MATCH OR OUT OF DATE")
            if 'code' in result:
                args = {
                    'code': result['code'],
                    'redirect_uri': redirect_uri,
                }
                if pkce:
                    args['code_verifier'] = code_verifier

                result['token'] = asyncio.run(self.client.get_access_token(**args))
            if 'id_token' in result:
                import base64
                result['id_token'] = base64.b64decode(result['id_token'].split('.')[1] + '==')
        return result
