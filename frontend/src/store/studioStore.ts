/**
 * Zustand store for the Studio page.
 * Holds all shared state across UploadPanel, ImageCanvas,
 * ObjectList and HotspotForm.
 */

 import { create } from "zustand";
 import type {
   ImageResponse,
   DetectedObject,
   DetectionResult,
 } from "../types/api";
 
 
 interface StudioState {
 
   // ── Current image ────────────────────────────────────────────────────
   images:      ImageResponse[];
   activeImage: ImageResponse | null;
 
   // ── Detection ────────────────────────────────────────────────────────
   detection:   DetectionResult | null;
   detecting:   boolean;
 
   // ── Selected object ──────────────────────────────────────────────────
   selectedObj: DetectedObject | null;
 
   // ── Hotspot form ─────────────────────────────────────────────────────
   text:        string;
   link:        string;
   color:       string;
 
   // ── SVG generation ───────────────────────────────────────────────────
   generating:  boolean;
   svgPreview:  string | null;
 
   // ── UI feedback ──────────────────────────────────────────────────────
   toast:       { msg: string; icon: string } | null;
   error:       string | null;
 
   // ── Actions ──────────────────────────────────────────────────────────
   setImages:      (images: ImageResponse[]) => void;
   addImage:       (image: ImageResponse) => void;
   setActiveImage: (image: ImageResponse | null) => void;
   setDetection:   (result: DetectionResult | null) => void;
   setDetecting:   (val: boolean) => void;
   setSelectedObj: (obj: DetectedObject | null) => void;
   setText:        (val: string) => void;
   setLink:        (val: string) => void;
   setColor:       (val: string) => void;
   setGenerating:  (val: boolean) => void;
   setSvgPreview:  (val: string | null) => void;
   showToast:      (msg: string, icon?: string) => void;
   clearToast:     () => void;
   setError:       (msg: string | null) => void;
 
   // Reset detection + selection when switching images
   resetStudio:    () => void;
 }
 
 
 export const useStudioStore = create<StudioState>((set) => ({
 
   // ── Initial state ─────────────────────────────────────────────────────
   images:      [],
   activeImage: null,
   detection:   null,
   detecting:   false,
   selectedObj: null,
   text:        "",
   link:        "",
   color:       "#2f80ed",
   generating:  false,
   svgPreview:  null,
   toast:       null,
   error:       null,
 
   // ── Actions ───────────────────────────────────────────────────────────
   setImages:      (images) => set({ images }),
   addImage:       (image)  => set((s) => ({ images: [image, ...s.images] })),
   setActiveImage: (image)  => set({ activeImage: image }),
   setDetection:   (result) => set({ detection: result }),
   setDetecting:   (val)    => set({ detecting: val }),
   setSelectedObj: (obj)    => set({ selectedObj: obj }),
   setText:        (val)    => set({ text: val }),
   setLink:        (val)    => set({ link: val }),
   setColor:       (val)    => set({ color: val }),
   setGenerating:  (val)    => set({ generating: val }),
   setSvgPreview:  (val)    => set({ svgPreview: val }),
   setError:       (msg)    => set({ error: msg }),
 
   showToast: (msg, icon = "✓") => {
     set({ toast: { msg, icon } });
     setTimeout(() => set({ toast: null }), 3000);
   },
 
   clearToast: () => set({ toast: null }),
 
   resetStudio: () => set({
     detection:   null,
     detecting:   false,
     selectedObj: null,
     text:        "",
     link:        "",
     color:       "#2f80ed",
     generating:  false,
     svgPreview:  null,
     error:       null,
   }),
 
 }));