/**
 * Studio page.
 * Assembles all studio components into the three-panel layout.
 * Fetches current user on mount for the navbar.
 */

 import { useEffect, useState } from "react";
 import { authApi } from "../api/authApi";
 import { useStudioStore } from "../store/studioStore";
 import Navbar       from "../components/Layout/Navbar";
 import UploadPanel  from "../components/UploadPanel";
 import ImageCanvas  from "../components/ImageCanvas";
 import ObjectList   from "../components/ObjectList";
 import HotspotForm  from "../components/HotspotForm";
 
 export default function StudioPage() {
   const [email, setEmail] = useState("");
   const { toast, error, setError } = useStudioStore();
 
   // Fetch current user email for navbar
   useEffect(() => {
     authApi.me()
       .then(user => setEmail(user.email))
       .catch(() => {
         // Token invalid — authApi interceptor will redirect to login
       });
   }, []);
 
   // Auto-clear error after 4 seconds
   useEffect(() => {
     if (error) {
       const t = setTimeout(() => setError(null), 4000);
       return () => clearTimeout(t);
     }
   }, [error]);
 
   return (
     <div style={{
       display: "grid",
       gridTemplateRows: "56px 1fr",
       height: "100vh",
       overflow: "hidden",
     }}>
 
       {/* ── Navbar ── */}
       <Navbar email={email} />
 
       {/* ── Studio body ── */}
       <div style={{
         display: "grid",
         gridTemplateColumns: "260px 1fr 280px",
         overflow: "hidden",
       }}>
 
         {/* Left panel — upload + image list */}
         <aside style={{
           background: "var(--surface)",
           borderRight: "1px solid var(--border)",
           display: "flex",
           flexDirection: "column",
           overflow: "hidden",
         }}>
           <UploadPanel />
         </aside>
 
         {/* Center — image canvas */}
         <main style={{ overflow: "hidden" }}>
           <ImageCanvas />
         </main>
 
         {/* Right panel — objects + annotation form */}
         <aside style={{
           background: "var(--surface)",
           borderLeft: "1px solid var(--border)",
           display: "flex",
           flexDirection: "column",
           overflowY: "auto",
         }}>
           <ObjectList />
           <div className="divider" />
           <HotspotForm />
         </aside>
 
       </div>
 
       {/* ── Error banner ── */}
       {error && (
         <div style={{
           position: "fixed",
           top: "68px",
           left: "50%",
           transform: "translateX(-50%)",
           background: "rgba(229,83,83,0.12)",
           border: "1px solid rgba(229,83,83,0.35)",
           borderRadius: "8px",
           padding: "10px 20px",
           fontSize: "13px",
           color: "#e55353",
           zIndex: 50,
           backdropFilter: "blur(8px)",
           animation: "slideUp 0.3s ease",
           maxWidth: "500px",
           textAlign: "center",
         }}>
           {error}
         </div>
       )}
 
       {/* ── Toast notification ── */}
       {toast && (
         <div className="toast">
           <span style={{ fontSize: "16px" }}>{toast.icon}</span>
           {toast.msg}
         </div>
       )}
 
     </div>
   );
 }