export default function BrandMark({ light = false, testIdPrefix = "brand" }: { light?: boolean; testIdPrefix?: string }) {
  return (
    <div className="flex items-center gap-3" data-testid={`${testIdPrefix}-mark`}>
      <img
        src="https://upload.wikimedia.org/wikipedia/commons/5/5d/Logo_Ministry_of_AYUSH.png"
        alt="Official Emblem of Ministry of Ayush, Government of India"
        className="h-11 w-[175px] shrink-0 object-contain object-left sm:h-14 sm:w-[245px]"
        data-testid={`${testIdPrefix}-ministry-logo`}
      />
      <div className="hidden border-l border-current/20 pl-3 md:block">
        <p className={`font-mono text-[10px] font-semibold uppercase tracking-[0.18em] ${light ? "text-amber-200" : "text-amber-700"}`} data-testid={`${testIdPrefix}-ministry-label`}>Ministry of Ayush</p>
        <p className={`text-xl font-bold tracking-tight ${light ? "text-white" : "text-[#0B3C2A]"}`} data-testid={`${testIdPrefix}-name`}>SAMANVAYA</p>
      </div>
    </div>
  );
}