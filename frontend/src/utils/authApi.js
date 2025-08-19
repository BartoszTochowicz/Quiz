import axios from 'axios';
import Cookies from 'js-cookie';

const authApi = axios.create({
    baseURL: "http://localhost:5000", //replace with your BaseURL
    headers: {
        'Content-Type': 'application/json', // change according header type accordingly
    }
});

// Add a request interceptor to include tokens in the headers of outgoing requests
authApi.interceptors.request.use(
    (config) => {
        const accessToken = localStorage.getItem('access_token'); // get stored access token
        if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`; // set in header
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
  );

authApi.interceptors.response.use(
(response) => {
    return response;
},
async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        const csrfToken = Cookies.get('csrf_refresh_token'); // get CSRF token from cookies
        if (csrfToken) {
            console.log('Access token expired, trying to refresh...');
            try {
                const response = await axios.get("http://localhost:5000/api/v1/auth/refresh",{
                    withCredentials: true, // include cookies in the request
                    headers: {
                        'X-CSRF-Token': csrfToken, // set CSRF token in header
                    }
                });
                // don't use axious instance that already configured for refresh token authApi call
                const newAccessToken = response.data.access_token;
                localStorage.setItem('access_token', newAccessToken);  //set new access token
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                return axios(originalRequest); //recall authApi with new token
            } catch (error) {
                console.error('Token refresh failed:', error);
            // Handle token refresh failure
            // mostly logout the user and re-authenticate by login again
            }
        }
    }
    return Promise.reject(error);
}
);

export default authApi;