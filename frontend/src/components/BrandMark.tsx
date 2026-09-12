export default function BrandMark({ light = false }: { light?: boolean }) {
  return (
    <div className="flex items-center gap-3" data-testid="brand-mark">
      <img
        src="https://upload.wikimedia.org/wikipedia/commons/5/5d/Logo_Ministry_of_AYUSH.png"
        alt="Official Emblem of Ministry of Ayush, Government of India"
        className="h-11 w-auto object-contain"
        data-testid="ministry-ayush-logo"
      />
      <div className="border-l border-current/20 pl-3">
        <p className={`font-mono text-[10px] font-semibold uppercase tracking-[0.18em] ${light ? "text-amber-200" : "text-amber-700"}`} data-testid="brand-ministry-label">Ministry of Ayush</p>
        <p className={`text-xl font-bold tracking-tight ${light ? "text-white" : "text-[#0B3C2A]"}`} data-testid="brand-name">SAMANVAYA</p>
      </div>
    </div>
  );
}