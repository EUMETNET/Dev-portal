# Ui
first in the project directory you need to install all packages
### `npm install`

In the project directory, you can run:

### `npm run start`

Runs the app in the development mode.\
Open [http://localhost:3002](http://localhost:3002) to view it in your browser.


You can adjust the default `/public/env-config.js` as per needs. 

```javascript
window.REACT_APP_KEYCLOAK_URL="http://localhost:8080";
window.REACT_APP_LOGOUT_URL="http://localhost:3002";
window.REACT_APP_KEYCLOAK_REALM="meteogate";
window.REACT_APP_KEYCLOAK_CLIENTID="frontend";
window.REACT_APP_BACKEND_URL="http://localhost:8082";
```