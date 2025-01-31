interface WowMoneyIconProps {
  type: 'gold' | 'silver' | 'copper';
  className?: string;
}

export function WowMoneyIcon({ type, className = '' }: WowMoneyIconProps) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 14 14"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {type === 'gold' && (
        <circle cx="7" cy="7" r="6" fill="#FFD700" stroke="#B8860B" strokeWidth="1" />
      )}
      {type === 'silver' && (
        <circle cx="7" cy="7" r="6" fill="#C0C0C0" stroke="#808080" strokeWidth="1" />
      )}
      {type === 'copper' && (
        <circle cx="7" cy="7" r="6" fill="#B87333" stroke="#8B4513" strokeWidth="1" />
      )}
    </svg>
  );
}