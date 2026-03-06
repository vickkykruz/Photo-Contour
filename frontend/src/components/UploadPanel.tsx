/**
 * Upload panel component.
 * Handles image file upload and displays the user's image library.
 */

 import { useEffect, useRef } from "react";
 import { imageApi } from "../api/imageApi";
 import { useStudioStore } from "../store/studioStore";
 import type { ImageResponse } from "../types/api";
 
 export default function UploadPanel() {
   const fileInputRef = useRef<HTMLInputElement>(null);
 
   const {
     images,
     activeImage,
     setImages,
     addImage,
     setActiveImage,
     resetStudio,
     showToast,
     setError,
   } = useStudioStore();
 
   // Load image list on mount
   useEffect(() => {
     imageApi.list()
       .then(setImages)
       .catch(() => setError("Failed to load images."));
   }, []);
 
   const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
     const file = e.target.files?.[0];
     if (!file) return;
 
     // Basic client-side type check
     if (!file.type.startsWith("image/")) {
       setError("Please upload a valid image file.");
       return;
     }
 
     try {
       showToast("Uploading…", "📁");
       const uploaded = await imageApi.upload(file);
       addImage(uploaded);
       setActiveImage(uploaded);
       resetStudio();
       showToast(`${file.name} uploaded successfully`, "✓");
     } catch (err: unknown) {
       const msg =
         (err as { response?: { data?: { detail?: string } } })
           ?.response?.data?.detail ||
         "Upload failed. Please check your image and try again.";
       setError(msg);
       showToast(msg, "✕");
     }
 
     // Reset input so same file can be re-uploaded if needed
     if (fileInputRef.current) fileInputRef.current.value = "";
   };
 
   const handleSelectImage = (img: ImageResponse) => {
     if (activeImage?.id === img.id) return;
     setActiveImage(img);
     resetStudio();
   };
 
   return (
     <div style={{
       display: "flex",
       flexDirection: "column",
       overflow: "hidden",
       height: "100%",
     }}>
 
       {/* ── Upload zone ── */}
       <div style={{ padding: "16px", borderBottom: "1px solid var(--border)" }}>
         <div className="panel-title">Upload Image</div>
 
         <div
           onClick={() => fileInputRef.current?.click()}
           onDragOver={e => e.preventDefault()}
           onDrop={e => {
             e.preventDefault();
             const file = e.dataTransfer.files?.[0];
             if (file && fileInputRef.current) {
               const dt = new DataTransfer();
               dt.items.add(file);
               fileInputRef.current.files = dt.files;
               fileInputRef.current.dispatchEvent(new Event("change", { bubbles: true }));
             }
           }}
           style={{
             border: "1.5px dashed rgba(47,128,237,0.35)",
             borderRadius: "10px",
             padding: "24px 16px",
             textAlign: "center",
             cursor: "pointer",
             background: "var(--blue-dim)",
             transition: "all 0.2s",
           }}
           onMouseEnter={e => {
             (e.currentTarget as HTMLDivElement).style.borderColor = "var(--blue)";
             (e.currentTarget as HTMLDivElement).style.background = "rgba(47,128,237,0.2)";
           }}
           onMouseLeave={e => {
             (e.currentTarget as HTMLDivElement).style.borderColor = "rgba(47,128,237,0.35)";
             (e.currentTarget as HTMLDivElement).style.background = "var(--blue-dim)";
           }}
         >
           {/* Upload icon */}
           <div style={{
             width: "36px", height: "36px", borderRadius: "8px",
             background: "rgba(47,128,237,0.2)",
             border: "1px solid rgba(47,128,237,0.3)",
             display: "flex", alignItems: "center", justifyContent: "center",
             margin: "0 auto 10px", fontSize: "18px",
           }}>
             ↑
           </div>
           <div style={{ fontSize: "13px", fontWeight: 500, color: "var(--text)" }}>
             Drop image here or click to browse
           </div>
           <div style={{ fontSize: "11px", color: "var(--muted)", marginTop: "4px" }}>
             JPG, PNG · Max 10 MB · Min 300×300 px
           </div>
         </div>
 
         {/* Hidden file input */}
         <input
           ref={fileInputRef}
           type="file"
           accept="image/*"
           style={{ display: "none" }}
           onChange={handleFileChange}
         />
       </div>
 
       {/* ── Image list ── */}
       <div style={{
         padding: "16px",
         flex: 1,
         overflow: "hidden",
         display: "flex",
         flexDirection: "column",
       }}>
         <div className="panel-title">Your Images</div>
 
         {images.length === 0 ? (
           <div className="empty-state">
             <p>No images yet. Upload one to get started.</p>
           </div>
         ) : (
           <div style={{ overflowY: "auto", flex: 1 }}>
             {images.map(img => (
               <div
                 key={img.id}
                 onClick={() => handleSelectImage(img)}
                 style={{
                   display: "flex",
                   alignItems: "center",
                   gap: "10px",
                   padding: "8px 10px",
                   borderRadius: "8px",
                   cursor: "pointer",
                   transition: "background 0.15s",
                   marginBottom: "2px",
                   background: activeImage?.id === img.id
                     ? "var(--blue-dim)"
                     : "transparent",
                   outline: activeImage?.id === img.id
                     ? "1px solid rgba(47,128,237,0.3)"
                     : "none",
                 }}
                 onMouseEnter={e => {
                   if (activeImage?.id !== img.id)
                     (e.currentTarget as HTMLDivElement).style.background = "var(--surface2)";
                 }}
                 onMouseLeave={e => {
                   if (activeImage?.id !== img.id)
                     (e.currentTarget as HTMLDivElement).style.background = "transparent";
                 }}
               >
                 {/* Thumb */}
                 <div style={{
                   width: "36px", height: "36px", borderRadius: "6px",
                   background: "var(--surface2)",
                   border: "1px solid var(--border)",
                   display: "flex", alignItems: "center",
                   justifyContent: "center",
                   fontSize: "16px", flexShrink: 0,
                 }}>
                   🖼
                 </div>
 
                 {/* Info */}
                 <div style={{ minWidth: 0, flex: 1 }}>
                   <div style={{
                     fontSize: "12px", fontWeight: 500, color: "var(--text)",
                     whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                   }}>
                     {img.filename}
                   </div>
                   <div style={{ fontSize: "10px", color: "var(--muted)", marginTop: "2px" }}>
                     {img.width && img.height ? `${img.width}×${img.height} px` : "Processing…"}
                   </div>
                 </div>
               </div>
             ))}
           </div>
         )}
       </div>
     </div>
   );
 }