import { useEffect, useRef } from "react";

export default function AntigravityCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches || window.innerWidth < 768) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    let frame = 0;
    let width = 0;
    let height = 0;
    const pointer = { x: -1000, y: -1000 };
    const dots = Array.from({ length: 75 }, (_, index) => ({
      x: (index * 79) % 960,
      y: (index * 47) % 520,
      phase: index * 0.6,
    }));
    const resize = () => {
      width = canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      height = canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      context.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
    };
    const move = (event: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      pointer.x = event.clientX - rect.left;
      pointer.y = event.clientY - rect.top;
    };
    const draw = (time: number) => {
      const scale = window.devicePixelRatio;
      context.clearRect(0, 0, width / scale, height / scale);
      dots.forEach((dot, index) => {
        const baseX = (dot.x / 960) * (width / scale);
        const baseY = (dot.y / 520) * (height / scale);
        const dx = baseX - pointer.x;
        const dy = baseY - pointer.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const force = Math.max(0, 1 - distance / 150);
        const x = baseX + (dx / Math.max(distance, 1)) * force * 16;
        const y = baseY + (dy / Math.max(distance, 1)) * force * 16 + Math.sin(time / 1200 + dot.phase) * 2;
        context.beginPath();
        context.arc(x, y, index % 5 === 0 ? 2.4 : 1.3, 0, Math.PI * 2);
        context.fillStyle = index % 5 === 0 ? "rgba(217,119,6,.38)" : "rgba(255,255,255,.24)";
        context.fill();
      });
      frame = requestAnimationFrame(draw);
    };
    resize();
    window.addEventListener("resize", resize);
    canvas.addEventListener("mousemove", move);
    frame = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
      canvas.removeEventListener("mousemove", move);
    };
  }, []);

  return <canvas ref={canvasRef} aria-hidden="true" className="pointer-events-none absolute inset-0 h-full w-full opacity-80" />;
}