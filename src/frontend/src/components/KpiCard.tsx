import type { LucideIcon } from "lucide-react";

interface KpiCardProps {
  label: string;
  value: string;
  detail: string;
  icon: LucideIcon;
  tone: "blue" | "green" | "amber" | "violet";
}

export function KpiCard({ label, value, detail, icon: Icon, tone }: KpiCardProps) {
  return (
    <article className={`kpi-card kpi-card--${tone}`}>
      <div className="kpi-card__icon-wrapper">
        <Icon className="kpi-card__icon" />
      </div>
      <div>
        <p className="kpi-card__label">{label}</p>
        <strong className="kpi-card__value">{value}</strong>
        <p className="kpi-card__detail">{detail}</p>
      </div>
    </article>
  );
}