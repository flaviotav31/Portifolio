import type { LucideIcon } from "lucide-react";

interface Props {
  label: string;
  value: string;
  sub?: string;
  icon: LucideIcon;
  accent?: string;
}

export default function StatCard({ label, value, sub, icon: Icon, accent = "text-violet-400" }: Props) {
  return (
    <div className="bg-gray-900 rounded-2xl p-5 flex items-start gap-4">
      <div className={`mt-1 ${accent}`}>
        <Icon size={22} />
      </div>
      <div>
        <p className="text-gray-400 text-sm">{label}</p>
        <p className={`text-2xl font-bold ${accent}`}>{value}</p>
        {sub && <p className="text-gray-500 text-xs mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}
