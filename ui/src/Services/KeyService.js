import axios from "axios"

export const keyApi = {
    getApiKey
  }
  
  function getApiKey(token) {
    debugger
    return instance.get('/getapikey', {
      headers: { 'Authorization': bearerAuth(token)}
    })

    // instance.get('/getapikey', { headers: { 'Authorization': bearerAuth(token)}})
    // .then((response) => {return response.data})
    // .catch((error) => {return error})
  }
  
  // -- Axios
  const instance = axios.create({
    //baseURL: config.url.API_BASE_URL,
    baseURL: process.env.REACT_APP_BACKEND_URL,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  })
  
  instance.interceptors.response.use(response => {
    return response
  }, function (error) {
    if (error.response.status === 404) {
      return { status: error.response.status }
    }
    return Promise.reject(error.response)
  })
  
  // -- Helper functions
  
  function bearerAuth(token) {
    return `Bearer ${token}`
  }