import { UploadPanel } from "../components/UploadPanel";
import type { DocumentUploadResponse } from "../types";

interface UploadPageProps {
  onUploaded: (document: DocumentUploadResponse) => void;
}

export function UploadPage({ onUploaded }: UploadPageProps) {
  return (
    <div className="page-stack">
      <section className="hero-panel">
        <div>
          <p className="hero-panel__eyebrow">Entrada de documentos</p>
          <h2>Envie arquivos PDF e PNG para a fila de OCR</h2>
          <p>
            O arquivo é validado no servidor, salvo no volume Docker e enfileirado imediatamente para o processamento.
          </p>
        </div>
      </section>

      <UploadPanel onUploaded={onUploaded} />
    </div>
  );
}