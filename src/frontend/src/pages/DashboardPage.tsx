import { FileText, Layers3, ScanText, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchDocumentList, fetchDocumentStats } from "../lib/api";
import type { DocumentListItem, DocumentStatsResponse } from "../types";
import { DocumentsTable } from "../components/DocumentsTable";
import { KpiCard } from "../components/KpiCard";

interface DashboardPageProps {
  refreshKey: number;
}

interface DashboardState {
  stats: DocumentStatsResponse | null;
  recentDocuments: DocumentListItem[];
  loading: boolean;
  errorMessage: string | null;
}

export function DashboardPage({ refreshKey }: DashboardPageProps) {
  const [state, setState] = useState<DashboardState>({
    stats: null,
    recentDocuments: [],
    loading: true,
    errorMessage: null,
  });

  useEffect(() => {
    let isMounted = true;

    async function loadDashboard() {
      setState((currentState) => ({ ...currentState, loading: true, errorMessage: null }));

      try {
        const [stats, documents] = await Promise.all([fetchDocumentStats(), fetchDocumentList(1, 5)]);

        if (!isMounted) {
          return;
        }

        setState({
          stats,
          recentDocuments: documents.items,
          loading: false,
          errorMessage: null,
        });
      } catch (loadError) {
        if (!isMounted) {
          return;
        }

        setState({
          stats: null,
          recentDocuments: [],
          loading: false,
          errorMessage: loadError instanceof Error ? loadError.message : "Falha ao carregar o dashboard.",
        });
      }
    }

    loadDashboard();

    return () => {
      isMounted = false;
    };
  }, [refreshKey]);

  const totalDocuments = state.stats?.total ?? 0;
  const processedDocuments = state.stats?.por_status.done ?? 0;
  const queuedDocuments = state.stats?.por_status.queued ?? 0;
  const processingDocuments = state.stats?.por_status.processing ?? 0;
  const errorDocuments = state.stats?.por_status.error ?? 0;

  return (
    <div className="page-stack">
      <section className="hero-panel">
        <div>
          <p className="hero-panel__eyebrow">Resumo operacional</p>
          <h2>Visão consolidada da fila, do upload e do cache local</h2>
          <p>
            Esta tela reúne os números do backend e os documentos salvos no navegador para manter o operador orientado.
          </p>
        </div>

        <div className="hero-panel__badge">
          <Sparkles />
          <span>Dashboards em tempo quase real</span>
        </div>
      </section>

      {state.errorMessage ? <div className="feedback-box feedback-box--error">{state.errorMessage}</div> : null}

      {state.loading ? <div className="loading-box">Carregando indicadores...</div> : null}

      <section className="kpi-grid">
        <KpiCard
          label="Documentos recebidos"
          value={String(totalDocuments)}
          detail="Total registrado no backend"
          icon={Layers3}
          tone="blue"
        />
        <KpiCard
          label="Documentos processados"
          value={String(processedDocuments)}
          detail="Etapa concluída do OCR"
          icon={ScanText}
          tone="green"
        />
        <KpiCard
          label="Documentos na fila"
          value={String(queuedDocuments)}
          detail="Itens ainda aguardando OCR"
          icon={FileText}
          tone="violet"
        />
        <KpiCard
          label="Em processamento"
          value={String(processingDocuments)}
          detail="Pipeline em execução"
          icon={Sparkles}
          tone="amber"
        />
      </section>

      <section className="panel panel--compact">
        <div className="section-heading">
          <div>
            <h2>Falhas no fluxo</h2>
            <p>Quantidade de documentos que chegaram ao status de erro.</p>
          </div>
        </div>
        <div className="mini-metric">{errorDocuments}</div>
      </section>

      <DocumentsTable
        title="Últimos documentos do servidor"
        description="Registros retornados pelo backend com paginação inicial de cinco itens."
        items={state.recentDocuments}
        emptyMessage="Nenhum documento foi encontrado no backend ainda."
      />
    </div>
  );
}