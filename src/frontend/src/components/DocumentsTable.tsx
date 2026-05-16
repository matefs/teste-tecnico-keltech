import type { DocumentListItem } from "../types";
import { StatusPill } from "./StatusPill";

interface DocumentsTableProps {
  title: string;
  description: string;
  items: DocumentListItem[];
  emptyMessage: string;
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

export function DocumentsTable({ title, description, items, emptyMessage }: DocumentsTableProps) {
  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
      </div>

      {items.length > 0 ? (
        <div className="table-wrap">
          <table className="document-table">
            <thead>
              <tr>
                <th>Documento</th>
                <th>Status</th>
                <th>Tamanho</th>
                <th>Data</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>
                    <div className="table-cell-title">{item.original_filename}</div>
                    <div className="table-cell-subtitle">{item.mime_type}</div>
                  </td>
                  <td>
                    <StatusPill status={item.status} />
                  </td>
                  <td>{formatFileSize(item.file_size)}</td>
                  <td>{formatDateTime(item.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">{emptyMessage}</div>
      )}
    </section>
  );
}