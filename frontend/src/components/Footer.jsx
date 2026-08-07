export default function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-900 py-8">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6">
        <p className="text-sm text-slate-400">
          <span className="font-semibold text-slate-200">TruthLens AI</span> — verify before you share
        </p>
        <p className="text-xs text-slate-500">
          &copy; {new Date().getFullYear()} TruthLens AI. All rights reserved.
        </p>
      </div>
    </footer>
  )
}
