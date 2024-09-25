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
      <DataTable value={routes}>
        <Column field="route" header="Routes"></Column>
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
      <div className="grid">
        <div className="col-12">
          {auth.isAuthenticated ? (
            <>
              <Button
                onClick={() => {
                  handleGetAPIKey();
                }}
                className="m-1 md:px-0 py-2 col-10 md:col-2 xl:col-1 btn--yellow"
                label="Get API key"
                raised
              />
              <Button
                onClick={() => {
                  handleRoutes();
                }}
                className="m-1 md:px-0 py-2 col-10 md:col-2 xl:col-1 btn--green"
                label="Show routes"
                raised
              />
              <Button
                onClick={() => {
                  handleDeleteApiKey();
                }}
                className="m-1 md:px-0 py-2 col-10 md:col-2 xl:col-1 btn--red"
                label="Delete API key"
                raised
              />
              <Button
                onClick={() => {
                  logout();
                }}
                className="m-1 md:px-0 py-2 col-10 md:col-2 xl:col-1 btn--orange"
                label="Logout"
                raised
              />
              <div className="col-12 mt-2 mb-0 md:mt-3">
                <h3>Info Pane</h3>
              </div>
              <div className="mt-0 flex justify-content-center flex-wrap">
                <Card
                  className="md:px-0 col-10 md:col-8 xl:col-8"
                  style={{ overflowX: 'auto', whiteSpace: 'pre-line' }}
                >
                  {infoMessage}
                </Card>
              </div>
            </>
          ) : (
            <Button
              onClick={() => {
                auth.signinRedirect();
              }}
              className="m-1 md:px-0 py-2 col-10 md:col-2 xl:col-1 btn--green"
              label="Login"
              raised
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
