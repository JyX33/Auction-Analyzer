import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatGold(copper: number): string {
  const gold = Math.floor(copper / 10000);
  const silver = Math.floor((copper % 10000) / 100);
  const remainingCopper = copper % 100;

  return `${gold}g ${silver}s ${remainingCopper}c`;
}

export function calculatePriceTrend(
  current: number,
  previous: number
): { percentage: number; direction: "up" | "down" | "stable" } {
  if (previous === 0) return { percentage: 0, direction: "stable" };
  
  const difference = current - previous;
  const percentage = Math.abs((difference / previous) * 100);
  
  if (difference > 0) return { percentage, direction: "up" };
  if (difference < 0) return { percentage, direction: "down" };
  return { percentage: 0, direction: "stable" };
}