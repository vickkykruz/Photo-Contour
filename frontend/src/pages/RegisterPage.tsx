/**
 * Register page.
 * Handles new user registration and redirects to studio on success.
 */

 import { useState } from "react";
 import { useNavigate, Link } from "react-router-dom";
 import { authApi } from "../api/authApi";
 
 export default function RegisterPage() {
   const navigate = useNavigate();
 
   const [email,    setEmail]    = useState("");
   const [password, setPassword] = useState("");
   const [confirm,  setConfirm]  = useState("");
   const [error,    setError]    = useState<string | null>(null);
   const [loading,  setLoading]  = useState(false);
 
   const handleRegister = async () => {
     if (!email || !password || !confirm) {
       setError("Please fill in all fields.");
       return;
     }
     if (password !== confirm) {
       setError("Passwords do not match.");
       return;
     }
     if (password.length < 8) {
       setError("Password must be at least 8 characters.");
       return;
     }
     setError(null);
     setLoading(true);
     try {
       await authApi.register({ email, password });
       // Auto login after register
       await authApi.login({ email, password });
       navigate("/studio");
     } catch (err: unknown) {
       const msg =
         (err as { response?: { data?: { detail?: string } } })
           ?.response?.data?.detail || "Registration failed. Please try again.";
       setError(msg);
     } finally {
       setLoading(false);
     }
   };
 
   const handleKeyDown = (e: React.KeyboardEvent) => {
     if (e.key === "Enter") handleRegister();
   };
 
   return (
     <div style={{
       minHeight: "100vh",
       display: "grid",
       gridTemplateColumns: "1fr 1fr",
     }}>
 
       {/* ── Brand panel ── */}
       <div style={{
         background: "linear-gradient(135deg, #0b1220 0%, #0d1a30 100%)",
         display: "flex",
         flexDirection: "column",
         justifyContent: "center",
         alignItems: "center",
         padding: "60px",
         position: "relative",
         overflow: "hidden",
       }}>
 
         {/* Grid background */}
         <div style={{
           position: "absolute", inset: 0,
           backgroundImage: `
             linear-gradient(rgba(47,128,237,0.04) 1px, transparent 1px),
             linear-gradient(90deg, rgba(47,128,237,0.04) 1px, transparent 1px)
           `,
           backgroundSize: "40px 40px",
         }}/>
 
         {/* Glow */}
         <div style={{
           position: "absolute", inset: 0,
           background: "radial-gradient(ellipse 60% 50% at 30% 60%, rgba(47,128,237,0.12) 0%, transparent 70%)",
         }}/>
 
         {/* Logo */}
         <div style={{
           fontFamily: "'Syne', sans-serif",
           fontSize: "42px",
           fontWeight: 800,
           letterSpacing: "-1px",
           color: "white",
           position: "relative",
           zIndex: 1,
           marginBottom: "12px",
         }}>
           Photo<span style={{ color: "var(--blue)" }}>Contour</span>
         </div>
 
         {/* Tagline */}
         <div style={{
           fontSize: "15px",
           color: "var(--muted)",
           position: "relative",
           zIndex: 1,
           maxWidth: "320px",
           textAlign: "center",
           lineHeight: 1.6,
         }}>
           One image. One click. Infinite interactivity.
           AI detects objects so you can tell their story.
         </div>
 
         {/* Features list */}
         <div style={{
           position: "relative",
           zIndex: 1,
           marginTop: "48px",
           display: "flex",
           flexDirection: "column",
           gap: "12px",
         }}>
           {[
             "✦ AI-powered object detection",
             "✦ Self-contained SVG output",
             "✦ Works on any browser",
           ].map(f => (
             <div key={f} style={{
               display: "inline-flex",
               alignItems: "center",
               gap: "6px",
               background: "var(--blue-dim)",
               border: "1px solid rgba(47,128,237,0.3)",
               borderRadius: "20px",
               padding: "8px 18px",
               fontSize: "13px",
               color: "var(--blue)",
               fontWeight: 500,
             }}>
               {f}
             </div>
           ))}
         </div>
 
       </div>
 
       {/* ── Form panel ── */}
       <div style={{
         background: "var(--bg)",
         display: "flex",
         alignItems: "center",
         justifyContent: "center",
         padding: "60px",
       }}>
         <div style={{ width: "100%", maxWidth: "400px" }}>
 
           {/* Title */}
           <div style={{
             fontFamily: "'Syne', sans-serif",
             fontSize: "28px",
             fontWeight: 700,
             color: "white",
             marginBottom: "6px",
           }}>
             Create account
           </div>
           <div style={{
             fontSize: "14px",
             color: "var(--muted)",
             marginBottom: "36px",
           }}>
             Start creating interactive images for free
           </div>
 
           {/* Error */}
           {error && (
             <div style={{
               background: "rgba(229,83,83,0.1)",
               border: "1px solid rgba(229,83,83,0.3)",
               borderRadius: "8px",
               padding: "10px 14px",
               fontSize: "13px",
               color: "#e55353",
               marginBottom: "20px",
             }}>
               {error}
             </div>
           )}
 
           {/* Email */}
           <div style={{ marginBottom: "18px" }}>
             <label style={{
               display: "block",
               fontSize: "12px",
               fontWeight: 500,
               color: "var(--muted)",
               textTransform: "uppercase",
               letterSpacing: "0.06em",
               marginBottom: "8px",
             }}>
               Email address
             </label>
             <input
               className="auth-input"
               type="email"
               placeholder="you@example.com"
               value={email}
               onChange={e => setEmail(e.target.value)}
               onKeyDown={handleKeyDown}
             />
           </div>
 
           {/* Password */}
           <div style={{ marginBottom: "18px" }}>
             <label style={{
               display: "block",
               fontSize: "12px",
               fontWeight: 500,
               color: "var(--muted)",
               textTransform: "uppercase",
               letterSpacing: "0.06em",
               marginBottom: "8px",
             }}>
               Password
             </label>
             <input
               className="auth-input"
               type="password"
               placeholder="Min. 8 characters"
               value={password}
               onChange={e => setPassword(e.target.value)}
               onKeyDown={handleKeyDown}
             />
           </div>
 
           {/* Confirm password */}
           <div style={{ marginBottom: "24px" }}>
             <label style={{
               display: "block",
               fontSize: "12px",
               fontWeight: 500,
               color: "var(--muted)",
               textTransform: "uppercase",
               letterSpacing: "0.06em",
               marginBottom: "8px",
             }}>
               Confirm password
             </label>
             <input
               className="auth-input"
               type="password"
               placeholder="••••••••"
               value={confirm}
               onChange={e => setConfirm(e.target.value)}
               onKeyDown={handleKeyDown}
             />
           </div>
 
           {/* Submit */}
           <button
             className="btn-primary"
             onClick={handleRegister}
             disabled={loading}
           >
             {loading
               ? <span className="animate-pulse-slow">Creating account…</span>
               : "Create account"
             }
           </button>
 
           {/* Switch to login */}
           <div style={{
             textAlign: "center",
             marginTop: "24px",
             fontSize: "13px",
             color: "var(--muted)",
           }}>
             Already have an account?{" "}
             <Link to="/login" style={{
               color: "var(--blue)",
               fontWeight: 500,
               textDecoration: "none",
             }}>
               Sign in
             </Link>
           </div>
 
         </div>
       </div>
     </div>
   );
 }