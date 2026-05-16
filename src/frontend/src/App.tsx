import { useEffect, useState } from "react";
import { AppShell } from "./components/AppShell";
import { LoginScreen } from "./components/LoginScreen";
import { DashboardPage } from "./pages/DashboardPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { UploadPage } from "./pages/UploadPage";
import { clearSession, getCachedDocumentCount, readSession, saveCachedDocument, saveSession } from "./lib/storage";
import type { AppRoute, DocumentUploadResponse, SessionData } from "./types";

function normalizeRoute(pathname: string): AppRoute {
  const normalizedPath = pathname.replace(/\/+$/, "") || "/";

  if (normalizedPath === "/upload") {
    return "upload";
  }

  if (normalizedPath === "/documentos") {
    return "documents";
  }

  return "dashboard";
}

function routeToPath(route: AppRoute): string {
  if (route === "upload") {
    return "/upload";
  }

  if (route === "documents") {
    return "/documentos";
  }

  return "/";
}

function pushRoute(route: AppRoute): void {
  window.history.pushState({}, "", routeToPath(route));
}

export default function App() {
  const [session, setSession] = useState<SessionData | null>(() => readSession());
  const [route, setRoute] = useState<AppRoute>(() => normalizeRoute(window.location.pathname));
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const handlePopState = () => {
      setRoute(normalizeRoute(window.location.pathname));
    };

    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  useEffect(() => {
    if (session) {
      saveSession(session);
      return;
    }

    clearSession();
  }, [session]);

  function handleAuthenticated(nextSession: SessionData) {
    setSession(nextSession);
    pushRoute("dashboard");
    setRoute("dashboard");
  }

  function handleNavigate(nextRoute: AppRoute) {
    pushRoute(nextRoute);
    setRoute(nextRoute);
  }

  function handleLogout() {
    clearSession();
    setSession(null);
    pushRoute("dashboard");
    setRoute("dashboard");
  }

  function handleUploadedDocument(document: DocumentUploadResponse) {
    saveCachedDocument(document);
    setRefreshKey((currentValue) => currentValue + 1);
    setRoute("documents");
    pushRoute("documents");
  }

  if (!session) {
    return <LoginScreen onAuthenticated={handleAuthenticated} />;
  }

  let pageContent = <DashboardPage refreshKey={refreshKey} />;

  if (route === "upload") {
    pageContent = <UploadPage onUploaded={handleUploadedDocument} />;
  } else if (route === "documents") {
    pageContent = <DocumentsPage refreshKey={refreshKey} />;
  }

  return (
    <AppShell session={session} currentRoute={route} onNavigate={handleNavigate} onLogout={handleLogout}>
      <div className="page-slot">
        <div className="page-slot__meta">Documentos salvos no navegador: {getCachedDocumentCount()}</div>
        {pageContent}
      </div>
    </AppShell>
  );
}