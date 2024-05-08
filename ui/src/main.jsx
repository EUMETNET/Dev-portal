import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'; 
import { AuthProvider } from 'react-oidc-context';

const oidcConfig = {
  authority: `${window.REACT_APP_KEYCLOAK_URL}realms/${window.REACT_APP_KEYCLOAK_REALM}`,
  client_id: window.REACT_APP_KEYCLOAK_CLIENTID,
  redirect_uri: window.location.origin,
  response_type: 'code',
  scope: 'openid',
  post_logout_redirect_uri: window.location.origin,
  automaticSilentRenew: true,
  loadUserInfo: false,
  silent_redirect_uri: window.location.origin,
  //userStore: window.sessionStorage is default
};

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider {...oidcConfig}>
      <App />
    </AuthProvider>
    <ToastContainer 
      position="top-right"
      autoClose={5000}
      hideProgressBar={false}
      newestOnTop={false}
      closeOnClick
      rtl={false}
      pauseOnFocusLoss
      draggable
      pauseOnHover
      theme="dark" 
    />
  </React.StrictMode>,
)
