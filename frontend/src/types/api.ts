/**
 * Shared TypeScript types matching backend Pydantic schemas exactly.
 */

// ── Auth ──────────────────────────────────────────────────────────────────
export interface UserCreate {
    email: string;
    password: string;
  }
  
  export interface UserLogin {
    email: string;
    password: string;
  }
  
  export interface Token {
    access_token: string;
    token_type: string;
  }
  
  export interface UserOut {
    id: number;
    email: string;
  }
  
  // ── Images ───────────────────────────────────────────────────────────────
  export interface ImageResponse {
    id: number;
    filename: string;
    filepath: string;
    width: number | null;
    height: number | null;
    created_at: string;
  }
  
  // ── Detection ────────────────────────────────────────────────────────────
  export interface BBox {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  }
  
  export interface DetectedObject {
    id: number;
    label: string;
    score: number;
    bbox: BBox;
    contour: number[][];
  }
  
  export interface DetectionResult {
    image_id: number;
    width: number | null;
    height: number | null;
    objects: DetectedObject[];
  }
  
  // ── Hotspot ───────────────────────────────────────────────────────────────
  export interface HotspotCreate {
    image_id: number;
    object_id: number;
    text: string;
    link: string;
    color?: string;
  }
  
  export interface SvgResponse {
    image_id: number;
    svg: string;
    preview_url: string;
  }