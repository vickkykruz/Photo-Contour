/**
 * Hotspot API calls.
 * Handles object detection, SVG generation and download.
 */

 import client from "./client";
 import type { DetectionResult, HotspotCreate, SvgResponse } from "../types/api";
 
 
 export const hotspotApi = {
 
   async detect(imageId: number): Promise<DetectionResult> {
     const response = await client.post<DetectionResult>(
       `/hotspots/detect/${imageId}`
     );
     return response.data;
   },
 
   async generateSvg(data: HotspotCreate): Promise<SvgResponse> {
     const response = await client.post<SvgResponse>(
       "/hotspots/generate-svg",
       data
     );
     return response.data;
   },
 
   downloadSvg(
     imageId: number,
     objectId: number,
     text: string,
     link: string
   ): void {
     const base = import.meta.env.VITE_API_URL || "http://localhost:8000";
     const params = new URLSearchParams({ text, link });
     const url = `${base}/hotspots/${imageId}/${objectId}/download-svg?${params}`;
 
     // Trigger browser download
     const anchor = document.createElement("a");
     anchor.href = url;
     anchor.download = `photo_contour_${imageId}_${objectId}.svg`;
     document.body.appendChild(anchor);
     anchor.click();
     document.body.removeChild(anchor);
   },
 
   async generateAndDownload(data: HotspotCreate): Promise<void> {
     const response = await client.post<SvgResponse>(
       "/hotspots/generate-svg",
       data,
       { responseType: "text" }
     );
 
     // Build blob from SVG string and trigger download
     const blob = new Blob([response.data as unknown as string], {
       type: "image/svg+xml",
     });
     const url  = URL.createObjectURL(blob);
     const anchor = document.createElement("a");
     anchor.href = url;
     anchor.download = `photo_contour_${data.image_id}_${data.object_id}.svg`;
     document.body.appendChild(anchor);
     anchor.click();
     document.body.removeChild(anchor);
     URL.revokeObjectURL(url);
   },
 
 };