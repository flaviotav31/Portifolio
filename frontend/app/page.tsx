import Link from "next/link";
import { BarChart2, Database, Code2, Server, ExternalLink, GitBranch } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center px-6 py-16">
      <div className="max-w-2xl w-full space-y-10">

        {/* Hero */}
        <div className="space-y-3">
          <p className="text-violet-400 text-sm font-medium tracking-wide uppercase">Data Engineer</p>
          <h1 className="text-4xl font-bold text-white">Flávio Tavares</h1>
          <p className="text-gray-400 text-lg leading-relaxed">
            Building end-to-end data pipelines, dimensional models, and REST APIs.
            Currently focused on AI labour market analytics in Alberta, Canada.
          </p>
          <div className="flex gap-4 pt-2">
            <a href="https://github.com/flaviotav31" target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm">
              <GitBranch size={16} /> GitHub
            </a>
            <a href="https://www.linkedin.com/in/fl%C3%A1vio-tavares-31080518b/" target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm">
              <ExternalLink size={16} /> LinkedIn
            </a>
          </div>
        </div>

        {/* Featured project */}
        <div className="border border-gray-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-white font-semibold text-lg">AI Talent Gap — Alberta</h2>
            <span className="text-xs bg-violet-500/20 text-violet-400 px-2 py-0.5 rounded-full">Featured</span>
          </div>
          <p className="text-gray-400 text-sm leading-relaxed">
            End-to-end data project analyzing the gap between AI talent demand and supply
            in Alberta (2023–2033). Built a full ETL pipeline, dimensional star schema,
            REST API, and this interactive dashboard.
          </p>
          <div className="flex flex-wrap gap-2">
            {["Python", "pandas", "FastAPI", "Next.js", "TypeScript", "Recharts", "Railway"].map((t) => (
              <span key={t} className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded-md">{t}</span>
            ))}
          </div>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <BarChart2 size={15} /> View Dashboard
          </Link>
        </div>

        {/* Skills */}
        <div className="grid grid-cols-2 gap-4">
          {[
            { icon: Database, label: "Data Engineering", items: "ETL · Star Schema · pandas" },
            { icon: Server, label: "Backend", items: "FastAPI · REST · Python" },
            { icon: Code2, label: "Frontend", items: "Next.js · TypeScript · Tailwind" },
            { icon: BarChart2, label: "Analytics", items: "Recharts · Dimensional Modeling" },
          ].map(({ icon: Icon, label, items }) => (
            <div key={label} className="bg-gray-900 rounded-xl p-4 flex items-start gap-3">
              <Icon size={18} className="text-violet-400 mt-0.5 shrink-0" />
              <div>
                <p className="text-white text-sm font-medium">{label}</p>
                <p className="text-gray-500 text-xs mt-0.5">{items}</p>
              </div>
            </div>
          ))}
        </div>

      </div>
    </main>
  );
}
