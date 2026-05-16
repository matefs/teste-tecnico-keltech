import { useState, type FormEvent } from "react";
import { FileUp, UploadCloud, AlertTriangle, CheckCircle2 } from "lucide-react";
import type { DocumentUploadResponse } from "../types";
import { uploadDocument } from "../lib/api";

interface UploadPanelProps {
  onUploaded: (document: DocumentUploadResponse) => void;
}

export function UploadPanel({ onUploaded }: UploadPanelProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedFile) {
      setErrorMessage("Selecione um arquivo PDF ou PNG antes de enviar.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const response = await uploadDocument(selectedFile);
      onUploaded(response);
      setSuccessMessage(`Documento ${response.original_filename} enviado com sucesso.`);
      setSelectedFile(null);
    } catch (submissionError) {
      setErrorMessage(submissionError instanceof Error ? submissionError.message : "Falha ao enviar o documento.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="panel upload-panel">
      <div className="section-heading">
        <div>
          <h2>Enviar documento</h2>
          <p>Envie arquivos PDF ou PNG com até 25 MB para o pipeline de OCR.</p>
        </div>
        <UploadCloud className="section-heading__icon" />
      </div>

      <form className="upload-form" onSubmit={handleSubmit}>
        <label className="file-dropzone">
          <FileUp className="file-dropzone__icon" />
          <span className="file-dropzone__title">Clique para escolher um arquivo</span>
          <span className="file-dropzone__hint">Apenas PDF e PNG são aceitos no servidor.</span>
          <input
            type="file"
            accept=".pdf,.png,application/pdf,image/png"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
          />
        </label>

        {selectedFile ? (
          <div className="selected-file-box">
            <strong>{selectedFile.name}</strong>
            <span>{Math.max(1, Math.round(selectedFile.size / 1024))} KB</span>
          </div>
        ) : null}

        {errorMessage ? (
          <div className="feedback-box feedback-box--error">
            <AlertTriangle />
            <span>{errorMessage}</span>
          </div>
        ) : null}

        {successMessage ? (
          <div className="feedback-box feedback-box--success">
            <CheckCircle2 />
            <span>{successMessage}</span>
          </div>
        ) : null}

        <button className="primary-button" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Enviando..." : "Enviar documento"}
        </button>
      </form>
    </section>
  );
}