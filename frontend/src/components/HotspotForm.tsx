/**
 * Hotspot form component.
 * Allows the user to attach a description, link and color
 * to the selected detected object, then generate the SVG.
 */

 import { useStudioStore } from "../store/studioStore";
 import { hotspotApi } from "../api/hotspotApi";
 
 const COLORS = [
   "#2f80ed", // blue
   "#27c97a", // green
   "#f5a623", // orange
   "#e55353", // red
   "#a855f7", // purple
   "#e8f040", // yellow
 ];
 
 export default function HotspotForm() {
   const {
     activeImage,
     selectedObj,
     text,
     link,
     color,
     generating,
     setText,
     setLink,
     setColor,
     setGenerating,
     showToast,
     setError,
   } = useStudioStore();
 
   const canGenerate =
     selectedObj !== null &&
     text.trim().length > 0 &&
     link.trim().length > 0;
 
   const handleGenerate = async () => {
     if (!activeImage || !selectedObj) return;
     if (!text.trim()) {
       setError("Please enter a description.");
       return;
     }
     if (!link.trim()) {
       setError("Please enter a link URL.");
       return;
     }
 
     setGenerating(true);
     setError(null);
 
     try {
       await hotspotApi.generateAndDownload({
         image_id:  activeImage.id,
         object_id: selectedObj.id,
         text:      text.trim(),
         link:      link.trim(),
         color,
       });
       showToast("SVG downloaded successfully!", "⬇");
     } catch (err: unknown) {
       const msg =
         (err as { response?: { data?: { detail?: string } } })
           ?.response?.data?.detail ||
         "Failed to generate SVG. Please try again.";
       setError(msg);
       showToast(msg, "✕");
     } finally {
       setGenerating(false);
     }
   };
 
   return (
     <div>
 
       {/* ── Annotation section ── */}
       <div style={{ padding: "16px", borderBottom: "1px solid var(--border)" }}>
         <div className="panel-title">Annotation</div>
 
         {/* No object selected */}
         {!selectedObj ? (
           <div className="empty-state">
             <p>
               Select a detected object above to attach
               your description and link.
             </p>
           </div>
         ) : (
           <>
             {/* Selected object badge */}
             <div style={{
               display: "flex",
               alignItems: "center",
               gap: "8px",
               marginBottom: "16px",
               padding: "8px 10px",
               background: "var(--blue-dim)",
               borderRadius: "7px",
               border: "1px solid rgba(47,128,237,0.25)",
             }}>
               <div style={{
                 width: "6px", height: "6px",
                 borderRadius: "50%",
                 background: "var(--blue)",
                 boxShadow: "0 0 6px var(--blue)",
                 flexShrink: 0,
               }}/>
               <span style={{
                 fontSize: "12px",
                 fontWeight: 600,
                 color: "var(--text)",
                 textTransform: "capitalize",
                 flex: 1,
               }}>
                 {selectedObj.label}
               </span>
               <span style={{
                 fontSize: "10px",
                 color: "var(--muted)",
               }}>
                 {Math.round(selectedObj.score * 100)}% confidence
               </span>
             </div>
 
             {/* Description */}
             <div style={{ marginBottom: "14px" }}>
               <label className="form-label">Description</label>
               <textarea
                 className="form-textarea"
                 placeholder="Add a description for this object…"
                 value={text}
                 onChange={e => setText(e.target.value)}
               />
             </div>
 
             {/* Link URL */}
             <div style={{ marginBottom: "14px" }}>
               <label className="form-label">Link URL</label>
               <input
                 className="form-input"
                 type="url"
                 placeholder="https://example.com"
                 value={link}
                 onChange={e => setLink(e.target.value)}
               />
             </div>
 
             {/* Highlight color */}
             <div style={{ marginBottom: "4px" }}>
               <label className="form-label">Highlight Color</label>
               <div style={{
                 display: "flex",
                 gap: "8px",
                 alignItems: "center",
                 flexWrap: "wrap",
               }}>
                 {COLORS.map(c => (
                   <div
                     key={c}
                     onClick={() => setColor(c)}
                     style={{
                       width: "24px",
                       height: "24px",
                       borderRadius: "6px",
                       background: c,
                       cursor: "pointer",
                       transition: "transform 0.15s",
                       border: color === c
                         ? "2px solid white"
                         : "2px solid transparent",
                       transform: color === c ? "scale(1.15)" : "scale(1)",
                       flexShrink: 0,
                     }}
                     onMouseEnter={e => {
                       if (color !== c)
                         (e.currentTarget as HTMLDivElement).style.transform = "scale(1.1)";
                     }}
                     onMouseLeave={e => {
                       if (color !== c)
                         (e.currentTarget as HTMLDivElement).style.transform = "scale(1)";
                     }}
                   />
                 ))}
               </div>
             </div>
           </>
         )}
       </div>
 
       {/* ── Generate button ── */}
       <div style={{ padding: "16px" }}>
         <button
           className="btn-generate"
           disabled={!canGenerate || generating}
           onClick={handleGenerate}
         >
           {generating
             ? <span className="animate-pulse-slow">Generating SVG…</span>
             : <>⬇ Generate &amp; Download SVG</>
           }
         </button>
 
         {/* Helper text */}
         {!canGenerate && selectedObj && (
           <p style={{
             fontSize: "11px",
             color: "var(--muted)",
             textAlign: "center",
             marginTop: "8px",
           }}>
             Fill in description and link to continue
           </p>
         )}
 
         {/* No object selected helper */}
         {!selectedObj && (
           <p style={{
             fontSize: "11px",
             color: "var(--muted)",
             textAlign: "center",
             marginTop: "8px",
           }}>
             Detect and select an object first
           </p>
         )}
       </div>
 
     </div>
   );
 }