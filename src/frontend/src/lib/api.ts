import type { DocumentListResponse, DocumentStatsResponse, DocumentUploadResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

function buildUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string; message?: string };
    return payload.detail ?? payload.message ?? response.statusText;
  } catch {
    return response.statusText || "Erro inesperado ao processar a requisição.";
  }
}

async function parseJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }

  return (await response.json()) as T;
}

export async function fetchDocumentStats(): Promise<DocumentStatsResponse> {
  const response = await fetch(buildUrl("/documentos/stats"));
  return parseJsonResponse<DocumentStatsResponse>(response);
}

export async function fetchDocumentList(page = 1, perPage = 20): Promise<DocumentListResponse> {
  const queryParameters = new URLSearchParams({ page: String(page), per_page: String(perPage) });
  const response = await fetch(buildUrl(`/documentos/?${queryParameters.toString()}`));
  return parseJsonResponse<DocumentListResponse>(response);
}

export async function uploadDocument(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(buildUrl("/documentos/"), {
    method: "POST",
    body: formData,
  });

  return parseJsonResponse<DocumentUploadResponse>(response);
}