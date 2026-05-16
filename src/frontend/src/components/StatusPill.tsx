import type { DocumentStatus } from "../types";

interface StatusPillProps {
  status: DocumentStatus;
}

const STATUS_LABELS: Record<DocumentStatus, string> = {
  queued: "Na fila",
  processing: "Processando",
  done: "Processado",
  error: "Erro",
};

export function StatusPill({ status }: StatusPillProps) {
  return <span className={`status-pill status-pill--${status}`}>{STATUS_LABELS[status]}</span>;
}