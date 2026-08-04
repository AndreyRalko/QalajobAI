export default function Topbar() {
  return (
    <div className="flex justify-between items-center mb-10">

      <div>

        <h1 className="text-5xl font-black">
          Welcome back 👋
        </h1>

        <p className="text-white/50 mt-2">
          Manage your career journey with AI.
        </p>

      </div>

      <div className="rounded-2xl bg-green-500/10 border border-green-500/20 px-5 py-3">

        <span className="text-green-400 font-bold">
          Profile Completion 85%
        </span>

      </div>

    </div>
  );
}