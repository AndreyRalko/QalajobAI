type StatCardProps = {
  title: string;
  value: string;
  color?: string;
};

export default function StatCard({
  title,
  value,
  color = "text-cyan-400",
}: StatCardProps) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.02] p-6 backdrop-blur-xl">

      <p className="text-white/50 text-sm">
        {title}
      </p>

      <h3 className={`text-5xl font-black mt-3 ${color}`}>
        {value}
      </h3>

    </div>
  );
}