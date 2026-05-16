interface PaginationControlsProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  perPage: number;
  onPrevious: () => void;
  onNext: () => void;
}

export function PaginationControls({
  currentPage,
  totalPages,
  totalItems,
  perPage,
  onPrevious,
  onNext,
}: PaginationControlsProps) {
  const isFirstPage = currentPage <= 1;
  const isLastPage = currentPage >= totalPages;

  return (
    <div className="pagination-bar">
      <div className="pagination-bar__summary">
        <strong>Página {currentPage} de {Math.max(totalPages, 1)}</strong>
        <span>{totalItems} documentos no total · {perPage} por página</span>
      </div>

      <div className="pagination-bar__actions">
        <button className="secondary-button" type="button" onClick={onPrevious} disabled={isFirstPage}>
          Anterior
        </button>
        <button className="secondary-button" type="button" onClick={onNext} disabled={isLastPage || totalPages === 0}>
          Próxima
        </button>
      </div>
    </div>
  );
}