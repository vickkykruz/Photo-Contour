/**
 * Axios client configuration.
 * Sets base URL and attaches JWT token to every request automatically.
 */

 import axios from "axios";

 const client = axios.create({
   baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
   headers: {
     "Content-Type": "application/json",
   },
 });
 
 // Attach token to every request if it exists
 client.interceptors.request.use((config) => {
   const token = localStorage.getItem("access_token");
   if (token) {
     config.headers.Authorization = `Bearer ${token}`;
   }
   return config;
 });
 
 // Handle 401 globally — clear token and redirect to login
 client.interceptors.response.use(
   (response) => response,
   (error) => {
     if (error.response?.status === 401) {
       localStorage.removeItem("access_token");
       window.location.href = "/login";
     }
     return Promise.reject(error);
   }
 );
 
 export default client;
 ```
 
 ---
 
 Then create a `.env` file in the `frontend/` root (not inside `src/`) with this:
 ```
 VITE_API_URL=http://localhost:8000