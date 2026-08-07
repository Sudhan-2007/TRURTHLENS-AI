import { Link } from 'react-router-dom'

const features = [
  {
    title: 'Detect',
    description:
      'Automatically flag suspicious claims across the web with AI-powered analysis.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="7" />
        <path d="m21 21-4.3-4.3" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: 'Verify',
    description:
      'Cross-check claims against trusted sources and get a clear confidence verdict.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="2">
        <path d="M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6l7-3z" strokeLinejoin="round" />
        <path d="m9 12 2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    title: 'Explain',
    description:
      'Understand why a claim was marked true, false, or unverifiable with clear reasoning.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="2">
        <path d="M21 12a8 8 0 0 1-8 8H4l2.5-2.5A8 8 0 1 1 21 12z" strokeLinejoin="round" />
        <path d="M9 10h6M9 14h3" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: 'Track',
    description:
      'Keep a personal history of everything you check and revisit verdicts anytime.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="2">
        <path d="M3 3v18h18" strokeLinecap="round" strokeLinejoin="round" />
        <path d="m7 14 4-4 3 3 5-6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
]

const steps = [
  { n: '1', title: 'Submit a claim', text: 'Paste a headline or statement you are unsure about.' },
  { n: '2', title: 'We analyze it', text: 'AI examines the claim against trusted sources.' },
  { n: '3', title: 'Get a verdict', text: 'Receive a clear, evidence-backed true / false verdict.' },
]

export default function Home() {
  return (
    <>
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-50 via-white to-slate-50">
        <div className="pointer-events-none absolute -top-24 right-0 h-72 w-72 rounded-full bg-blue-200/40 blur-3xl" />
        <div className="pointer-events-none absolute top-40 -left-20 h-64 w-64 rounded-full bg-indigo-200/40 blur-3xl" />

        <div className="relative mx-auto max-w-6xl px-4 py-24 text-center sm:px-6 sm:py-32">
          <span className="inline-flex items-center rounded-full border border-blue-200 bg-white px-3 py-1 text-xs font-semibold text-blue-700">
            AI-powered misinformation detection
          </span>
          <h1 className="mx-auto mt-6 max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl">
            Verify the truth before you{' '}
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              share it
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-500">
            TruthLens AI detects, verifies, explains, and tracks misinformation so you always
            know what to trust.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link to="/register" className="btn-primary px-6 py-3 text-base">
              Start verifying free
            </Link>
            <a href="#how-it-works" className="btn-secondary px-6 py-3 text-base">
              How it works
            </a>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f) => (
            <div
              key={f.title}
              className="card p-6 transition hover:-translate-y-1 hover:shadow-md"
            >
              <div className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                {f.icon}
              </div>
              <h3 className="mt-4 text-lg font-semibold text-slate-900">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-500">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="how-it-works" className="border-y border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <h2 className="text-center text-3xl font-bold tracking-tight text-slate-900">
            How it works
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-slate-500">
            Three simple steps between uncertainty and the truth.
          </p>
          <div className="mt-12 grid gap-8 sm:grid-cols-3">
            {steps.map((s, i) => (
              <div key={s.n} className="relative text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 text-lg font-bold text-white">
                  {s.n}
                </div>
                <h3 className="mt-4 text-lg font-semibold text-slate-900">{s.title}</h3>
                <p className="mt-2 text-sm text-slate-500">{s.text}</p>
                {i < steps.length - 1 && (
                  <div className="absolute top-6 hidden w-full border-t-2 border-dashed border-slate-200 sm:block" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-20 text-center sm:px-6">
        <h2 className="text-3xl font-bold tracking-tight text-slate-900">
          Ready to separate fact from fiction?
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-slate-500">
          Create your free account and start verifying claims today.
        </p>
        <Link to="/register" className="btn-primary mt-8 px-6 py-3 text-base">
          Create your account
        </Link>
      </section>
    </>
  )
}
