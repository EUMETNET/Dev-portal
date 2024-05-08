import React, { useState, useEffect } from 'react';
import './App.css';
import "primereact/resources/themes/lara-light-indigo/theme.css";
import "primereact/resources/primereact.min.css";
import '/node_modules/primeflex/primeflex.css'
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { DataTable } from "primereact/datatable";
import {Column} from 'primereact/column';

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
      const { data, isError} = await getAPIKey()
      if (!isError) {
        const apiKey = data.apiKey;
        setInfoMessage(`API key: ${apiKey}`)
      } else {
        showToaster(data?.message ?? "Undefined error message");
      }
    } catch (error) {
      console.error(error)
      if (error.message === 'User is not logged in') {
        await auth.signinRedirect();
        console.log('User is not logged in')
      }
      showToaster("Unable to communicate with the API server");
    }
  }

  const  handleDeleteApiKey = async () => {
    try {
      const { data, isError} = await deleteAPIKey();
      if (!isError) {
        setInfoMessage('API key deleted successfully')
      } else {
        showToaster(data?.message ?? "Undefined error message");
      }
    } catch (error) {
      console.error(error)
      if (error.message === 'User is not logged in') {
        await auth.signinRedirect();
      }
      showToaster("Unable to communicate with the API server");
    } 
  }

  const handleRoutes = async () => {
    try {
      const { data, isError} = await getRoutes()
      if (!isError) {
        const routes = data.routes;
        const listItems = routes.map((currElement, index) => {
          return {id:index, route:currElement}
        });
        setInfoMessage(generateTable(listItems));
      } else {
        showToaster(data?.message ?? "Undefined error message");
      }
    } catch (error) {
      console.error(error)
      if (error.message === 'User is not logged in') {
        await auth.signinRedirect();
        console.log('User is not logged in')
      }
      showToaster("Unable to communicate with the API server");
    }
  };

  function generateTable(routes) {
    return(
    <DataTable value={routes}>
    <Column field="route" header="Routes"></Column>
    </DataTable>);
  }

  const logout = () => {
    auth.signoutRedirect();
    // use below one if user is wanted to log out only from dev portal but not from keycloak
    // of course prompted to login again once the IdP session expires
    //auth.removeUser();
    setInfoMessage();
  }

  function showToaster(error) {
    toast.error(error, {
      position: "top-right",
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
      theme: "dark",
      })
  }

  return (
    <div className="App">
      {/* <Auth /> */}
      <div className='grid'>
        <div className='col-12'>
          <h1>Developer Portal prototype</h1>
        </div>
        <div className='col-12'>
          <h1 id='app-header-2'>Secured with Keycloak</h1>
        </div>
      </div>
      <div className="grid">
        <div className="col">
          {auth.isAuthenticated 
            ? (
              <>
                <Button onClick={() => { handleGetAPIKey() }} className='m-1' label='Get API key' severity="success" />
                <Button onClick={() => { handleRoutes() }} className="m-1" label='Show routes' severity="info" />
                <Button onClick={() => { handleDeleteApiKey() }} className="m-1" label='Delete API key' severity="danger" />
                <Button onClick={() => { logout() }} className="m-1" label='Logout' severity="danger" />
              </>
            )
            : (
              <Button onClick={() => { auth.signinRedirect() }} className='m-1' label='Login' severity="success" />
            )
          } 
        </div>
      </div>

      {auth.isAuthenticated && (
        <div className='grid'>
          <div className='col-2'></div>
          <div className='col-8'>
            <h3>Info Pane</h3>
            <Card>
              {infoMessage}
            </Card>
          </div>
          <div className='col-2'></div>
        </div>
      )}

    </div>
  );
}

export default App;
