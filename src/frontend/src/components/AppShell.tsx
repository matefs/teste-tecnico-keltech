import { FileText, LayoutDashboard, LogOut, UploadCloud } from "lucide-react";
import type { ReactNode } from "react";
import type { AppRoute, SessionData } from "../types";

interface AppShellProps {
  session: SessionData;
  currentRoute: AppRoute;
  onNavigate: (route: AppRoute) => void;
  onLogout: () => void;
  children: ReactNode;
}

const NAVIGATION_ITEMS: Array<{ label: string; route: AppRoute; icon: typeof LayoutDashboard }> = [
  { label: "Dashboard", route: "dashboard", icon: LayoutDashboard },
  { label: "Upload", route: "upload", icon: UploadCloud },
  { label: "Documentos", route: "documents", icon: FileText },
];

export function AppShell({ session, currentRoute, onNavigate, onLogout, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <div className="sidebar__logo">K</div>
          <div>
            <strong>Keltech</strong>
            <span>Document Management</span>
          </div>
        </div>

        <nav className="sidebar__nav">
          {NAVIGATION_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = currentRoute === item.route;

            return (
              <button
                key={item.route}
                className={`sidebar__nav-item ${isActive ? "sidebar__nav-item--active" : ""}`}
                type="button"
                onClick={() => onNavigate(item.route)}
              >
                <Icon />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar__footer">
          <div className="sidebar__session">
            <span>Logado como</span>
            <strong>{session.displayName}</strong>
            <small>{session.role}</small>
          </div>

          <button className="secondary-button" type="button" onClick={onLogout}>
            <LogOut />
            Sair
          </button>
        </div>
      </aside>

      <div className="content-area">
        <header className="topbar">
          <div>
            <p className="topbar__eyebrow">Operação de documentos</p>
            <h1>Monitoramento de upload e processamento</h1>
          </div>
          <div className="topbar__session-badge">Sessão ativa</div>
        </header>

        <main className="page-content">{children}</main>
      </div>
    </div>
  );
}