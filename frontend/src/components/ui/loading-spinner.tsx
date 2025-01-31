import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingSpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: number;
}

export function LoadingSpinner({ size = 24, className, ...props }: LoadingSpinnerProps) {
  return (
    <div className={cn("animate-spin", className)} {...props}>
      <Loader2 size={size} />
    </div>
  );
}