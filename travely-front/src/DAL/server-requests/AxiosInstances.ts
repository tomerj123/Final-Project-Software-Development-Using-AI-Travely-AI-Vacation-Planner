import axios from 'axios';

// you will need to add .env with `REACT_APP_ENDPOINT` etc

export const backendServiceInstance = axios.create({
    baseURL: 'http://127.0.0.1:8000',
});
