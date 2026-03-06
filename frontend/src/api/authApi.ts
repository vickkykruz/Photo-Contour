/**
 * Authentication API calls.
 * Handles register, login, logout and current user retrieval.
 */

 import client from "./client";
 import { UserCreate, UserLogin, Token, UserOut } from "../types/api";
 
 
 export const authApi = {
 
   async register(data: UserCreate): Promise<UserOut> {
     const response = await client.post<UserOut>("/auth/register", data);
     return response.data;
   },
 
   async login(data: UserLogin): Promise<Token> {
     const response = await client.post<Token>("/auth/login", data);
     // Store token immediately after login
     localStorage.setItem("access_token", response.data.access_token);
     return response.data;
   },
 
   async me(): Promise<UserOut> {
     const response = await client.get<UserOut>("/auth/me");
     return response.data;
   },
 
   logout(): void {
     localStorage.removeItem("access_token");
     window.location.href = "/login";
   },
 
   isAuthenticated(): boolean {
     return !!localStorage.getItem("access_token");
   },
 
 };