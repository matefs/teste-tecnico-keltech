import type { CachedDocument } from "../types";
import { StatusPill } from "./StatusPill";

interface LocalDocumentsPanelProps {
  documents: CachedDocument[];
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatFileSize(value: number): string {
  if (value < 1024) {
    return `${value} B`;
  }

  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }

  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

export function LocalDocumentsPanel({ documents }: LocalDocumentsPanelProps) {
  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <h2>Documentos no navegador</h2>
          <p>Cache local usado para manter os uploads recentes visíveis no frontend.</p>
        </div>
        <div className="panel-badge">{documents.length} itens</div>
      </div>

      {documents.length > 0 ? (
        <div className="local-document-list">
          {documents.map((document) => (
            <article className="local-document-card" key={document.id}>
              <div className="local-document-card__header">
                <div>
                  <strong>{document.original_filename}</strong>
                  <p>{document.file_path}</p>
                </div>
                <StatusPill status={document.status} />
              </div>

              <div className="local-document-card__meta">
                <span>{formatFileSize(document.file_size)}</span>
                <span>{formatDateTime(document.cachedAt)}</span>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state">Nenhum documento foi salvo no localStorage ainda.</div>
      )}
    </section>
  );
}