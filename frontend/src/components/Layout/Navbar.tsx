/**
 * Navbar component.
 * Displays logo, studio badge, current user email and sign out button.
 */

 import { authApi } from "../../api/authApi";

 interface NavbarProps {
   email: string;
 }
 
 export default function Navbar({ email }: NavbarProps) {
 
   const handleLogout = () => {
     authApi.logout();
   };
 
   // Get initials for avatar from email
   const initial = email ? email[0].toUpperCase() : "U";
 
   return (
     <nav style={{
       background: "var(--surface)",
       borderBottom: "1px solid var(--border)",
       display: "flex",
       alignItems: "center",
       padding: "0 24px",
       gap: "16px",
       height: "56px",
       position: "relative",
       zIndex: 10,
     }}>
 
       {/* Logo */}
       <div style={{
         fontFamily: "'Syne', sans-serif",
         fontSize: "18px",
         fontWeight: 800,
         color: "white",
         letterSpacing: "-0.5px",
         marginRight: "4px",
       }}>
         Photo<span style={{ color: "var(--blue)" }}>Contour</span>
       </div>
 
       {/* Studio badge */}
       <div style={{
         fontSize: "10px",
         background: "var(--blue-dim)",
         border: "1px solid rgba(47,128,237,0.3)",
         color: "var(--blue)",
         borderRadius: "4px",
         padding: "2px 8px",
         fontWeight: 600,
         letterSpacing: "0.08em",
         textTransform: "uppercase",
       }}>
         Studio
       </div>
 
       {/* Spacer */}
       <div style={{ flex: 1 }} />
 
       {/* User info */}
       <div style={{
         display: "flex",
         alignItems: "center",
         gap: "10px",
       }}>
 
         {/* Avatar */}
         <div style={{
           width: "28px",
           height: "28px",
           borderRadius: "50%",
           background: "var(--blue)",
           display: "flex",
           alignItems: "center",
           justifyContent: "center",
           fontSize: "12px",
           fontWeight: 700,
           color: "white",
           flexShrink: 0,
         }}>
           {initial}
         </div>
 
         {/* Email */}
         <span style={{
           fontSize: "13px",
           color: "var(--text)",
         }}>
           {email}
         </span>
       </div>
 
       {/* Sign out */}
       <button
         onClick={handleLogout}
         style={{
           fontSize: "12px",
           color: "var(--muted)",
           cursor: "pointer",
           padding: "5px 10px",
           border: "1px solid var(--border)",
           borderRadius: "6px",
           background: "transparent",
           fontFamily: "'DM Sans', sans-serif",
           transition: "all 0.2s",
         }}
         onMouseEnter={e => {
           (e.target as HTMLButtonElement).style.borderColor = "#e55353";
           (e.target as HTMLButtonElement).style.color = "#e55353";
         }}
         onMouseLeave={e => {
           (e.target as HTMLButtonElement).style.borderColor = "var(--border)";
           (e.target as HTMLButtonElement).style.color = "var(--muted)";
         }}
       >
         Sign out
       </button>
 
     </nav>
   );
 }