/**
 * Image API calls.
 * Handles upload, list and retrieval of images.
 */

 import client from "./client";
 import type { ImageResponse } from "../types/api";
 
 
 export const imageApi = {
 
   async upload(file: File): Promise<ImageResponse> {
     const formData = new FormData();
     formData.append("file", file);
 
     const response = await client.post<ImageResponse>("/images/", formData, {
       headers: {
         "Content-Type": "multipart/form-data",
       },
     });
     return response.data;
   },
 
   async list(): Promise<ImageResponse[]> {
     const response = await client.get<ImageResponse[]>("/images/");
     return response.data;
   },
 
   async getById(imageId: number): Promise<ImageResponse> {
     const response = await client.get<ImageResponse>(`/images/${imageId}`);
     return response.data;
   },
 
   getFileUrl(imageId: number): string {
     const base = import.meta.env.VITE_API_URL || "http://localhost:8000";
     const token = localStorage.getItem("access_token");
     return `${base}/images/${imageId}/file?token=${token}`;
   },
 
 };