export type DocumentStatus = "queued" | "processing" | "done" | "error";

export interface DocumentUploadResponse {
  id: string;
  status: DocumentStatus;
  original_filename: string;
  file_path: string;
  mime_type: string;
  file_size: number;
  created_at: string;
}

export interface DocumentListItem {
  id: string;
  status: DocumentStatus;
  original_filename: string;
  mime_type: string;
  file_size: number;
  created_at: string;
}

export interface DocumentListResponse {
  total: number;
  page: number;
  per_page: number;
  items: DocumentListItem[];
}

export interface DocumentStatsResponse {
  total: number;
  por_status: Record<string, number>;
}

export type UserRole = "operador" | "gestor" | "admin";

export interface SessionData {
  username: string;
  displayName: string;
  role: UserRole;
  accessToken: string;
  authenticatedAt: string;
}

export interface CachedDocument extends DocumentUploadResponse {
  cachedAt: string;
}

export type AppRoute = "dashboard" | "upload" | "documents";