/**
 * App root.
 * Sets up React Router with protected and public routes.
 */

 import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
 import { authApi } from "./api/authApi";
 import LoginPage    from "./pages/LoginPage";
 import RegisterPage from "./pages/RegisterPage";
 import StudioPage   from "./pages/StudioPage";
 
 
 // ── Protected route wrapper ───────────────────────────────────────────────
 function ProtectedRoute({ children }: { children: React.ReactNode }) {
   if (!authApi.isAuthenticated()) {
     return <Navigate to="/login" replace />;
   }
   return <>{children}</>;
 }
 
 
 // ── App ───────────────────────────────────────────────────────────────────
 export default function App() {
   return (
     <BrowserRouter>
       <Routes>
 
         {/* Public routes */}
         <Route path="/login"    element={<LoginPage />} />
         <Route path="/register" element={<RegisterPage />} />
 
         {/* Protected routes */}
         <Route path="/studio" element={
           <ProtectedRoute>
             <StudioPage />
           </ProtectedRoute>
         }/>
 
         {/* Default redirect */}
         <Route path="*" element={
           <Navigate to={authApi.isAuthenticated() ? "/studio" : "/login"} replace />
         }/>
 
       </Routes>
     </BrowserRouter>
   );
 }