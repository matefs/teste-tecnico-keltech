import { useEffect, useState } from "react";
import { fetchDocumentList } from "../lib/api";
import { readCachedDocuments } from "../lib/storage";
import type { CachedDocument, DocumentListItem } from "../types";
import { DocumentsTable } from "../components/DocumentsTable";
import { LocalDocumentsPanel } from "../components/LocalDocumentsPanel";

interface DocumentsPageProps {
  refreshKey: number;
}

interface DocumentsState {
  serverDocuments: DocumentListItem[];
  localDocuments: CachedDocument[];
  loading: boolean;
  errorMessage: string | null;
}

export function DocumentsPage({ refreshKey }: DocumentsPageProps) {
  const [state, setState] = useState<DocumentsState>({
    serverDocuments: [],
    localDocuments: [],
    loading: true,
    errorMessage: null,
  });

  useEffect(() => {
    let isMounted = true;

    async function loadDocuments() {
      setState((currentState) => ({ ...currentState, loading: true, errorMessage: null }));

      try {
        const documents = await fetchDocumentList(1, 20);

        if (!isMounted) {
          return;
        }

        setState({
          serverDocuments: documents.items,
          localDocuments: readCachedDocuments(),
          loading: false,
          errorMessage: null,
        });
      } catch (loadError) {
        if (!isMounted) {
          return;
        }

        setState({
          serverDocuments: [],
          localDocuments: readCachedDocuments(),
          loading: false,
          errorMessage: loadError instanceof Error ? loadError.message : "Falha ao carregar documentos.",
        });
      }
    }

    loadDocuments();

    return () => {
      isMounted = false;
    };
  }, [refreshKey]);

  return (
    <div className="page-stack">
      <section className="hero-panel">
        <div>
          <p className="hero-panel__eyebrow">Documentos</p>
          <h2>Consulta do backend e do localStorage</h2>
          <p>
            Esta rota exibe tanto os documentos persistidos no servidor quanto os itens armazenados no navegador.
          </p>
        </div>
      </section>

      {state.errorMessage ? <div className="feedback-box feedback-box--error">{state.errorMessage}</div> : null}

      {state.loading ? <div className="loading-box">Carregando documentos...</div> : null}

      <DocumentsTable
        title="Documentos do servidor"
        description="Lista dos documentos recebidos pelo backend com os dados mais recentes." 
        items={state.serverDocuments}
        emptyMessage="O backend ainda não retornou documentos para esta consulta."
      />

      <LocalDocumentsPanel documents={state.localDocuments} />
    </div>
  );
}