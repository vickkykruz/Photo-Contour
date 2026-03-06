/**
 * Image canvas component.
 * Displays the selected image and overlays detected object contours.
 */

 import { useRef, useState, useEffect } from "react";
 import { hotspotApi } from "../api/hotspotApi";
 import { useStudioStore } from "../store/studioStore";
 
 export default function ImageCanvas() {
   const imgRef = useRef<HTMLImageElement>(null);
   const [renderedSize, setRenderedSize] = useState({ w: 0, h: 0 });
 
   const {
     activeImage,
     detection,
     detecting,
     selectedObj,
     setDetection,
     setDetecting,
     showToast,
     setError,
   } = useStudioStore();
 
   // Track rendered image size for correct overlay scaling
   useEffect(() => {
     const updateSize = () => {
       if (imgRef.current) {
         const { width, height } = imgRef.current.getBoundingClientRect();
         setRenderedSize({ w: width, h: height });
       }
     };
     const observer = new ResizeObserver(updateSize);
     if (imgRef.current) observer.observe(imgRef.current);
     return () => observer.disconnect();
   }, [activeImage]);
 
   const handleDetect = async () => {
     if (!activeImage) return;
     setDetecting(true);
     setDetection(null);
     setError(null);
     try {
       const result = await hotspotApi.detect(activeImage.id);
       setDetection(result);
       if (result.objects.length === 0) {
         showToast("No objects detected. Try a clearer image.", "⚠");
       } else {
         showToast(`${result.objects.length} object${result.objects.length > 1 ? "s" : ""} detected`, "🔍");
       }
     } catch (err: unknown) {
       const msg =
         (err as { response?: { data?: { detail?: string } } })
           ?.response?.data?.detail ||
         "Detection failed. Please try again.";
       setError(msg);
       showToast(msg, "✕");
     } finally {
       setDetecting(false);
     }
   };
 
   // Build image URL with auth token
   const base  = import.meta.env.VITE_API_URL || "http://localhost:8000";
   const token = localStorage.getItem("access_token");
   const imgUrl = activeImage
     ? `${base}/images/${activeImage.id}/file?token=${token}`
     : null;
 
   // Natural image dimensions from detection result
   const natW = detection?.width  ?? activeImage?.width  ?? 1;
   const natH = detection?.height ?? activeImage?.height ?? 1;
 
   return (
     <div style={{
       display: "flex",
       flexDirection: "column",
       height: "100%",
       background: "#060a10",
       overflow: "hidden",
     }}>
 
       {/* ── Toolbar ── */}
       <div style={{
         padding: "10px 16px",
         borderBottom: "1px solid var(--border)",
         display: "flex",
         alignItems: "center",
         gap: "10px",
         background: "var(--surface)",
       }}>
         {activeImage ? (
           <>
             <span style={{
               fontSize: "11px",
               background: "var(--surface2)",
               border: "1px solid var(--border)",
               borderRadius: "4px",
               padding: "2px 8px",
               color: "var(--text)",
             }}>
               {activeImage.filename}
             </span>
             {activeImage.width && activeImage.height && (
               <span style={{ fontSize: "12px", color: "var(--muted)" }}>
                 {activeImage.width}×{activeImage.height} px
               </span>
             )}
           </>
         ) : (
           <span style={{ fontSize: "12px", color: "var(--muted)" }}>
             No image selected
           </span>
         )}
 
         <div style={{ flex: 1 }} />
 
         {activeImage && (
           <button
             className="btn-secondary"
             onClick={handleDetect}
             disabled={detecting}
           >
             {detecting
               ? <span className="animate-pulse-slow">Detecting…</span>
               : <>🔍 Detect Objects</>
             }
           </button>
         )}
       </div>
 
       {/* ── Viewport ── */}
       <div style={{
         flex: 1,
         display: "flex",
         alignItems: "center",
         justifyContent: "center",
         overflow: "hidden",
         position: "relative",
       }}>
         {activeImage && imgUrl ? (
           <div style={{
             position: "relative",
             borderRadius: "4px",
             overflow: "hidden",
             boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
             maxWidth: "90%",
             maxHeight: "90%",
           }}>
             {/* Image */}
             <img
               ref={imgRef}
               src={imgUrl}
               alt={activeImage.filename}
               style={{
                 display: "block",
                 maxWidth: "100%",
                 maxHeight: "calc(100vh - 200px)",
                 objectFit: "contain",
               }}
               onLoad={() => {
                 if (imgRef.current) {
                   const { width, height } = imgRef.current.getBoundingClientRect();
                   setRenderedSize({ w: width, h: height });
                 }
               }}
             />
 
             {/* SVG overlay — scales with rendered image */}
             {detection && renderedSize.w > 0 && (
               <svg
                 style={{
                   position: "absolute",
                   top: 0, left: 0,
                   pointerEvents: "none",
                 }}
                 width={renderedSize.w}
                 height={renderedSize.h}
                 viewBox={`0 0 ${renderedSize.w} ${renderedSize.h}`}
               >
                 {detection.objects.map(obj => {
                   const isSelected = selectedObj?.id === obj.id;
 
                   // Scale normalised contour points to rendered size
                   const points = obj.contour
                     .map(([x, y]) => `${x * renderedSize.w},${y * renderedSize.h}`)
                     .join(" ");
 
                   // Scale bbox to rendered size
                   const bx1 = obj.bbox.x1 * renderedSize.w;
                   const by1 = obj.bbox.y1 * renderedSize.h;
                   const bx2 = obj.bbox.x2 * renderedSize.w;
                   const by2 = obj.bbox.y2 * renderedSize.h;
                   const labelX = bx1;
                   const labelY = by1 > 18 ? by1 - 6 : by2 + 14;
 
                   return (
                     <g key={obj.id}>
                       {/* Contour polygon */}
                       <polygon
                         points={points}
                         fill={isSelected
                           ? "rgba(47,128,237,0.25)"
                           : "rgba(47,128,237,0.08)"}
                         stroke={isSelected ? "#2f80ed" : "rgba(47,128,237,0.4)"}
                         strokeWidth={isSelected ? 2 : 1}
                         className={isSelected ? "contour-anim" : ""}
                       />
 
                       {/* Label badge */}
                       <rect
                         x={labelX}
                         y={labelY - 11}
                         width={obj.label.length * 7 + 10}
                         height={14}
                         rx={3}
                         fill={isSelected ? "#2f80ed" : "rgba(47,128,237,0.5)"}
                       />
                       <text
                         x={labelX + 5}
                         y={labelY}
                         fontSize={9}
                         fill="white"
                         fontFamily="DM Sans, sans-serif"
                         fontWeight={600}
                       >
                         {obj.label}
                       </text>
                     </g>
                   );
                 })}
               </svg>
             )}
 
             {/* Selected object hint */}
             {selectedObj && (
               <div style={{
                 position: "absolute",
                 bottom: "12px",
                 left: "50%",
                 transform: "translateX(-50%)",
                 background: "rgba(8,12,20,0.85)",
                 border: "1px solid var(--border)",
                 borderRadius: "6px",
                 padding: "5px 12px",
                 fontSize: "11px",
                 color: "var(--muted)",
                 backdropFilter: "blur(8px)",
                 whiteSpace: "nowrap",
               }}>
                 ✦ Contour active:{" "}
                 <strong style={{ color: "var(--text)" }}>
                   {selectedObj.label}
                 </strong>
               </div>
             )}
           </div>
         ) : (
           // Empty state
           <div className="canvas-empty" style={{
             display: "flex",
             flexDirection: "column",
             alignItems: "center",
             gap: "12px",
             color: "var(--muted)",
             textAlign: "center",
           }}>
             <div style={{
               width: "64px", height: "64px", borderRadius: "16px",
               background: "var(--surface2)",
               border: "1px solid var(--border)",
               display: "flex", alignItems: "center",
               justifyContent: "center",
               fontSize: "28px", opacity: 0.6,
             }}>
               🖼
             </div>
             <div style={{
               fontFamily: "'Syne', sans-serif",
               fontSize: "18px",
               color: "var(--text)",
               opacity: 0.5,
             }}>
               No image selected
             </div>
             <p style={{ fontSize: "13px", maxWidth: "240px", lineHeight: 1.6 }}>
               Upload an image or select one from your library to get started
             </p>
           </div>
         )}
       </div>
 
       {/* ── Status bar ── */}
       <div style={{
         padding: "6px 16px",
         borderTop: "1px solid var(--border)",
         display: "flex",
         alignItems: "center",
         gap: "12px",
         background: "var(--surface)",
       }}>
         <div style={{
           width: "6px", height: "6px", borderRadius: "50%",
           background: "var(--green)",
           boxShadow: "0 0 6px var(--green)",
           flexShrink: 0,
         }}/>
         <span style={{ fontSize: "11px", color: "var(--muted)" }}>
           {detecting
             ? "Running YOLO detection…"
             : detection
               ? `${detection.objects.length} object${detection.objects.length !== 1 ? "s" : ""} detected · Select one from the right panel`
               : activeImage
                 ? "Image loaded · Click Detect Objects to begin"
                 : "Ready — upload or select an image"}
         </span>
       </div>
 
     </div>
   );
 }