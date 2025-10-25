export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-12">
      <div className="max-w-4xl w-full grid md:grid-cols-2 gap-8 items-center">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl">Private Knowledge Assistant</h1>
          <p className="text-slate-600 text-lg">
            Secure retrieval and generation across your enterprise documents.
          </p>
          <div className="h-48 rounded-3xl bg-gradient-to-tr from-amber-200 via-orange-100 to-sky-100 shadow-glow" />
        </div>
        <div className="bg-white/90 backdrop-blur rounded-3xl p-8 shadow-xl fade-up">
          {children}
        </div>
      </div>
    </div>
  );
}
