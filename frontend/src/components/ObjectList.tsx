/**
 * Object list component.
 * Displays detected objects and allows the user to select one
 * to attach an annotation to.
 */

 import { useStudioStore } from "../store/studioStore";
 import type { DetectedObject } from "../types/api";
 
 export default function ObjectList() {
   const {
     activeImage,
     detection,
     detecting,
     selectedObj,
     setSelectedObj,
     setText,
     setLink,
     setColor,
     setSvgPreview,
   } = useStudioStore();
 
   const handleSelect = (obj: DetectedObject) => {
     // Reset annotation fields when switching objects
     if (selectedObj?.id !== obj.id) {
       setText("");
       setLink("");
       setColor("#2f80ed");
       setSvgPreview(null);
     }
     setSelectedObj(obj);
   };
 
   // Score to color — green above 80%, yellow above 50%, red below
   const scoreColor = (score: number) => {
     if (score >= 0.8) return "#27c97a";
     if (score >= 0.5) return "#f5a623";
     return "#e55353";
   };
 
   return (
     <div style={{ padding: "16px" }}>
       <div className="panel-title">Detected Objects</div>
 
       {/* No image selected */}
       {!activeImage && (
         <div className="empty-state">
           <p>Select an image first, then run detection.</p>
         </div>
       )}
 
       {/* Image selected but not detected yet */}
       {activeImage && !detection && !detecting && (
         <div className="empty-state">
           <p>
             Click{" "}
             <strong style={{ color: "var(--text)" }}>
               "Detect Objects"
             </strong>{" "}
             to run AI detection on this image.
           </p>
         </div>
       )}
 
       {/* Detecting in progress */}
       {detecting && (
         <div className="empty-state">
           <div style={{
             width: "20px", height: "20px",
             border: "2px solid var(--border)",
             borderTopColor: "var(--blue)",
             borderRadius: "50%",
             marginBottom: "8px",
           }}
             className="animate-spin-slow"
           />
           <p className="animate-pulse-slow">Running YOLO detection…</p>
         </div>
       )}
 
       {/* No objects found */}
       {detection && detection.objects.length === 0 && (
         <div className="empty-state">
           <p>
             No objects detected. Try uploading a clearer,
             well-focused image.
           </p>
         </div>
       )}
 
       {/* Object list */}
       {detection && detection.objects.length > 0 && (
         <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
           {detection.objects.map(obj => {
             const isSelected = selectedObj?.id === obj.id;
             return (
               <div
                 key={obj.id}
                 onClick={() => handleSelect(obj)}
                 style={{
                   display: "flex",
                   alignItems: "center",
                   gap: "10px",
                   padding: "9px 12px",
                   borderRadius: "8px",
                   cursor: "pointer",
                   transition: "all 0.15s",
                   border: isSelected
                     ? "1px solid rgba(47,128,237,0.4)"
                     : "1px solid transparent",
                   background: isSelected
                     ? "var(--blue-dim)"
                     : "transparent",
                 }}
                 onMouseEnter={e => {
                   if (!isSelected)
                     (e.currentTarget as HTMLDivElement).style.background = "var(--surface2)";
                 }}
                 onMouseLeave={e => {
                   if (!isSelected)
                     (e.currentTarget as HTMLDivElement).style.background = "transparent";
                 }}
               >
                 {/* Status dot */}
                 <div style={{
                   width: "8px", height: "8px",
                   borderRadius: "50%",
                   flexShrink: 0,
                   background: isSelected ? "var(--blue)" : "var(--muted)",
                   boxShadow: isSelected ? "0 0 6px var(--blue)" : "none",
                   transition: "all 0.15s",
                 }}/>
 
                 {/* Label */}
                 <span style={{
                   fontSize: "13px",
                   fontWeight: 500,
                   flex: 1,
                   color: "var(--text)",
                   textTransform: "capitalize",
                 }}>
                   {obj.label}
                 </span>
 
                 {/* Confidence score */}
                 <span style={{
                   fontSize: "10px",
                   fontWeight: 500,
                   background: isSelected
                     ? "rgba(47,128,237,0.2)"
                     : "var(--surface2)",
                   color: isSelected
                     ? "var(--blue)"
                     : scoreColor(obj.score),
                   borderRadius: "4px",
                   padding: "2px 6px",
                   flexShrink: 0,
                 }}>
                   {Math.round(obj.score * 100)}%
                 </span>
               </div>
             );
           })}
         </div>
       )}
     </div>
   );
 }