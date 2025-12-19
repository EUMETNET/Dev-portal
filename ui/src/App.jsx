import React, { useState, useEffect } from 'react';
import './App.css';
import 'primereact/resources/themes/lara-light-indigo/theme.css';
import 'primereact/resources/primereact.min.css';
import '/node_modules/primeflex/primeflex.css';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';

import Header from './components/Header';
import Footer from './components/Footer';

import { getAPIKey, deleteAPIKey, getRoutes } from './Services/apiService';
import { useAuth } from 'react-oidc-context';
import { toast } from 'react-toastify';

function App() {
  const auth = useAuth();
  const [infoMessage, setInfoMessage] = useState('');

  useEffect(() => {
    // send user back to Keycloak login screen if there is silentRenewError
    // e.g. when refresh token is expired it will throw silentRenewError
    const onSilentRenewError = () => {
      auth.signinRedirect();
    };

    auth.events.addSilentRenewError(onSilentRenewError);

    return () => {
      auth.events.removeSilentRenewError(onSilentRenewError);
    };
  }, [auth]);

  const handleGetAPIKey = async () => {
    try {
      const { data, isError } = await getAPIKey();
      if (!isError) {
        const apiKey = data.apiKey;
        setInfoMessage(`API key:\n ${apiKey}`);
      } else {
        showToaster(data?.message ?? 'Undefined error message');
      }
    } catch (error) {
      console.error(error);
      if (error.message === 'User is not logged in') {
        await auth.signinRedirect();
        console.log('User is not logged in');
      }
      showToaster('Unable to communicate with the API server');
    }
  };

  const handleDeleteApiKey = async () => {
    try {
      const { data, isError } = await deleteAPIKey();
      if (!isError) {
        setInfoMessage('API key deleted successfully');
      } else {
        showToaster(data?.message ?? 'Undefined error message');
      }
    } catch (error) {
      console.error(error);
      if (error.message === 'User is not logged in') {
        await auth.signinRedirect();
      }
      showToaster('Unable to communicate with the API server');
    }
  };

  const handleRoutes = async () => {
    try {
      const { data, isError } = await getRoutes();
      if (!isError) {
        const routes = data.routes;
        const listItems = routes.map((currElement, index) => {
          return { id: index, route: currElement };
        });
        setInfoMessage(generateTable(listItems));
      } else {
        showToaster(data?.message ?? 'Undefined error message');
      }
    } catch (error) {
      console.error(error);
      if (error.message === 'User is not logged in') {
        await auth.signinRedirect();
        console.log('User is not logged in');
      }
      showToaster('Unable to communicate with the API server');
    }
  };

  function generateTable(routes) {
    return (
      <DataTable value={routes} stripedRows emptyMessage="No routes available">
        <Column field="route" header="Available Routes"></Column>
      </DataTable>
    );
  }

  const logout = () => {
    auth.signoutRedirect();
    // use below one if user is wanted to log out only from dev portal but not from keycloak
    // of course prompted to login again once the IdP session expires
    //auth.removeUser();
    setInfoMessage();
  };

  function showToaster(error) {
    toast.error(error, {
      position: 'top-right',
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
      theme: 'dark',
    });
  }

  return (
    <div className="App">
      {/* <Auth /> */}
      <Header />
      
      {auth.isAuthenticated ? (
        <div className="content-container">
          {/* Button Group */}
          <div style={{ 
            display: 'flex', 
            gap: '16px', 
            flexWrap: 'wrap', 
            justifyContent: 'center',
            marginBottom: '40px'
          }}>
            <Button
              onClick={handleGetAPIKey}
              className="btn--yellow"
              label="Get API key"
              raised
            />
            <Button
              onClick={handleRoutes}
              className="btn--green"
              label="Show routes"
              raised
            />
            <Button
              onClick={handleDeleteApiKey}
              className="btn--red"
              label="Delete API key"
              raised
            />
            <Button
              onClick={logout}
              className="btn--orange"
              label="Logout"
              raised
            />
          </div>

          {/* Info Panel Card */}
          <div>
            <h3>Info Panel</h3>
            <Card>
              <div id="infoPanel">
                {infoMessage || 'Click a button above to get started'}
              </div>
            </Card>
          </div>
        </div>
      ) : (
        <div className="content-container">
          <div style={{ 
            textAlign: 'center', 
            padding: '60px 20px' 
          }}>
            <h3 style={{ marginBottom: '24px' }}>Welcome to Developer Portal</h3>
            <p style={{ 
              color: 'var(--color-sherpa200)', 
              marginBottom: '32px', 
              fontSize: '18px' 
            }}>
              Please log in to access your API keys and manage routes
            </p>
            <Button
              onClick={() => auth.signinRedirect()}
              className="btn--green"
              label="Login"
              raised
            />
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
}

export default App;