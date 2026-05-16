import { useEffect, useState } from "react";
import { fetchDocumentList } from "../lib/api";
import { readCachedDocuments } from "../lib/storage";
import type { CachedDocument, DocumentListItem } from "../types";
import { DocumentsTable } from "../components/DocumentsTable";
import { LocalDocumentsPanel } from "../components/LocalDocumentsPanel";
import { PaginationControls } from "../components/PaginationControls";

interface DocumentsPageProps {
  refreshKey: number;
}

interface DocumentsState {
  serverDocuments: DocumentListItem[];
  localDocuments: CachedDocument[];
  loading: boolean;
  errorMessage: string | null;
  totalDocuments: number;
  currentPage: number;
  perPage: number;
}

export function DocumentsPage({ refreshKey }: DocumentsPageProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const perPage = 10;
  const [state, setState] = useState<DocumentsState>({
    serverDocuments: [],
    localDocuments: [],
    loading: true,
    errorMessage: null,
    totalDocuments: 0,
    currentPage: 1,
    perPage,
  });

  useEffect(() => {
    let isMounted = true;

    async function loadDocuments() {
      setState((currentState) => ({ ...currentState, loading: true, errorMessage: null }));

      try {
        const documents = await fetchDocumentList(currentPage, perPage);

        if (!isMounted) {
          return;
        }

        setState({
          serverDocuments: documents.items,
          localDocuments: readCachedDocuments(),
          loading: false,
          errorMessage: null,
          totalDocuments: documents.total,
          currentPage: documents.page,
          perPage: documents.per_page,
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
          totalDocuments: 0,
          currentPage,
          perPage,
        });
      }
    }

    loadDocuments();

    return () => {
      isMounted = false;
    };
  }, [refreshKey, currentPage]);

  useEffect(() => {
    setCurrentPage(1);
  }, [refreshKey]);

  const totalPages = Math.ceil(state.totalDocuments / state.perPage);

  function handlePreviousPage() {
    setCurrentPage((page) => Math.max(1, page - 1));
  }

  function handleNextPage() {
    setCurrentPage((page) => page + 1);
  }

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
        description="Lista paginada dos documentos recebidos pelo backend."
        items={state.serverDocuments}
        emptyMessage="O backend ainda não retornou documentos para esta consulta."
      />

      <PaginationControls
        currentPage={state.currentPage}
        totalPages={totalPages}
        totalItems={state.totalDocuments}
        perPage={state.perPage}
        onPrevious={handlePreviousPage}
        onNext={handleNextPage}
      />

      <LocalDocumentsPanel documents={state.localDocuments} />
    </div>
  );
}