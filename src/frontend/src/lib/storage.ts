import { DEFAULT_LOGIN_CREDENTIALS } from "./auth";
import type { CachedDocument, DocumentUploadResponse, SessionData } from "../types";

const SESSION_STORAGE_KEY = "keltech:session";
const DOCUMENTS_STORAGE_KEY = "keltech:documents";

function parseJson<T>(value: string | null): T | null {
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as T;
  } catch {
    return null;
  }
}

export function getDefaultLoginCredentials() {
  return DEFAULT_LOGIN_CREDENTIALS;
}

export function readSession(): SessionData | null {
  if (typeof window === "undefined") {
    return null;
  }

  return parseJson<SessionData>(window.localStorage.getItem(SESSION_STORAGE_KEY));
}

export function saveSession(session: SessionData): void {
  window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  window.localStorage.removeItem(SESSION_STORAGE_KEY);
}

export function readCachedDocuments(): CachedDocument[] {
  if (typeof window === "undefined") {
    return [];
  }

  return parseJson<CachedDocument[]>(window.localStorage.getItem(DOCUMENTS_STORAGE_KEY)) ?? [];
}

export function saveCachedDocument(document: DocumentUploadResponse): CachedDocument {
  const cachedDocument: CachedDocument = {
    ...document,
    cachedAt: new Date().toISOString(),
  };

  const cachedDocuments = readCachedDocuments().filter((currentDocument) => currentDocument.id !== document.id);
  const nextDocuments = [cachedDocument, ...cachedDocuments].slice(0, 100);

  window.localStorage.setItem(DOCUMENTS_STORAGE_KEY, JSON.stringify(nextDocuments));

  return cachedDocument;
}

export function clearCachedDocuments(): void {
  window.localStorage.removeItem(DOCUMENTS_STORAGE_KEY);
}

export function getCachedDocumentCount(): number {
  return readCachedDocuments().length;
}