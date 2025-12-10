import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Color Palette Constants for reference
export const COLORS = {
  primary: "#C0392B", // Crimson
  secondary: "#00796B", // Deep Teal
  success: "#388E3C", // Modern Green
  indigo: "#3949AB", // Voice Button
  background: "#F5F7FA", // Soft gray/white
};

// Typography & Layout Constants
export const LAYOUT_CONTAINER = "max-w-md mx-auto min-h-screen bg-[#F5F7FA] flex flex-col font-sans text-gray-800";
export const TEXT_HERO = "text-3xl font-bold tracking-tight text-[#00796B]";
export const TEXT_TITLE = "text-xl font-bold text-[#00796B] flex items-center gap-2";
export const TEXT_SUBTITLE = "text-lg font-semibold text-gray-700";
export const TEXT_BODY = "text-base font-medium text-gray-600 leading-relaxed";
export const TEXT_CAPTION = "text-xs font-semibold uppercase tracking-wider text-gray-500";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'success' | 'voice';
  size?: 'sm' | 'default' | 'lg' | 'full';
}

export const ModernButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'default', ...props }, ref) => {
    
    const variants = {
      primary: "bg-[#00796B] text-white hover:bg-[#00695C] shadow-md active:scale-[0.98]",
      success: "bg-[#388E3C] text-white hover:bg-[#2E7D32] shadow-md active:scale-[0.98]",
      voice: "bg-[#3949AB] text-white hover:bg-[#303F9F] shadow-md active:scale-[0.98]", // Indigo
      secondary: "bg-white text-[#00796B] border border-gray-200 hover:bg-gray-50 shadow-sm",
      outline: "bg-transparent border-2 border-[#00796B] text-[#00796B]",
      ghost: "bg-transparent text-gray-600 hover:bg-gray-100",
    };

    const sizes = {
      sm: "py-2 px-4 text-sm rounded-lg",
      default: "py-3 px-6 text-base rounded-xl",
      lg: "py-4 px-8 text-lg rounded-xl font-bold",
      full: "w-full py-4 text-lg rounded-xl font-bold",
    };

    return (
      <button
        ref={ref}
        className={cn(
          "transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    );
  }
);
ModernButton.displayName = "ModernButton";

export const ModernCard = ({ className, children, active = false, ...props }: React.HTMLAttributes<HTMLDivElement> & { active?: boolean }) => {
  return (
    <div 
      className={cn(
        "bg-white rounded-2xl p-5 shadow-sm border border-gray-100 transition-all",
        active && "ring-2 ring-[#00796B] shadow-md",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const ModernInput = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "w-full bg-white border border-gray-200 rounded-xl py-4 px-5 text-lg font-medium text-gray-900 placeholder:text-gray-400 focus:border-[#00796B] focus:outline-none focus:ring-2 focus:ring-[#00796B]/20 transition-all",
          className
        )}
        {...props}
      />
    );
  }
);
ModernInput.displayName = "ModernInput";

export const ModernSelect = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
    ({ className, ...props }, ref) => {
      return (
        <div className="relative">
          <select
            ref={ref}
            className={cn(
                "w-full bg-white border border-gray-200 rounded-xl py-4 px-5 text-lg font-medium text-gray-900 placeholder:text-gray-400 focus:border-[#00796B] focus:outline-none focus:ring-2 focus:ring-[#00796B]/20 transition-all appearance-none",
              className
            )}
            {...props}
          />
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500">
            <svg className="fill-current h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
          </div>
        </div>
      );
    }
  );
  ModernSelect.displayName = "ModernSelect";

// Compatibility exports for existing code (if any remains)
export const ChunkyButton = ModernButton;
export const ChunkyCard = ModernCard;
export const ChunkyInput = ModernInput;
export const ChunkySelect = ModernSelect;
