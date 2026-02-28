interface BankIconProps {
  institutionName: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function BankIcon({ institutionName, size = 'md' }: BankIconProps) {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
  };

  const getBankLogo = (name: string): JSX.Element => {
    const nameLower = name.toLowerCase();

    // Chase - Blue octagon
    if (nameLower.includes('chase')) {
      return (
        <div className={`${sizeClasses[size]} bg-[#117ACA] rounded-lg flex items-center justify-center shadow-sm p-1.5`}>
          <svg viewBox="0 0 100 100" className="w-full h-full">
            <polygon points="50,0 100,0 100,50" fill="white" />
            <polygon points="0,50 0,100 50,100" fill="white" />
            <polygon points="0,0 0,50 50,0" fill="white" />
            <polygon points="50,100 100,100 100,50" fill="white" />
          </svg>
        </div>
      );
    }

    // American Express - Blue box with white text
    if (nameLower.includes('amex') || nameLower.includes('american express')) {
      return (
        <div className={`${sizeClasses[size]} bg-[#006FCF] rounded-lg flex items-center justify-center shadow-sm`}>
          <span className="text-white font-bold" style={{ fontSize: size === 'sm' ? '9px' : size === 'md' ? '11px' : '13px', letterSpacing: '-0.5px' }}>
            AMEX
          </span>
        </div>
      );
    }

    // Ally Bank - Purple with white text
    if (nameLower.includes('ally')) {
      return (
        <div className={`${sizeClasses[size]} bg-[#6B1E82] rounded-lg flex items-center justify-center shadow-sm`}>
          <span className="text-white font-bold lowercase" style={{ fontSize: size === 'sm' ? '11px' : size === 'md' ? '14px' : '16px' }}>
            ally
          </span>
        </div>
      );
    }

    // Citizens Bank - Green
    if (nameLower.includes('citizens')) {
      return (
        <div className={`${sizeClasses[size]} bg-[#24A047] rounded-lg flex items-center justify-center shadow-sm p-2`}>
          <svg viewBox="0 0 100 100" className="w-full h-full">
            <circle cx="50" cy="50" r="45" fill="none" stroke="white" strokeWidth="8"/>
            <path d="M50 15 L50 85 M15 50 L85 50" stroke="white" strokeWidth="8"/>
          </svg>
        </div>
      );
    }

    // Bank of America - Red flag
    if (nameLower.includes('bank of america') || nameLower.includes('boa')) {
      return (
        <div className={`${sizeClasses[size]} bg-white rounded-lg flex items-center justify-center shadow-sm overflow-hidden`}>
          <svg viewBox="0 0 100 100" className="w-full h-full">
            <rect x="0" y="0" width="100" height="33" fill="#E31837"/>
            <rect x="0" y="33" width="100" height="34" fill="#012169"/>
            <rect x="0" y="67" width="100" height="33" fill="#E31837"/>
          </svg>
        </div>
      );
    }

    // Wells Fargo - Yellow/Gold stagecoach theme
    if (nameLower.includes('wells fargo')) {
      return (
        <div className={`${sizeClasses[size]} bg-[#D71E28] rounded-lg flex items-center justify-center shadow-sm`}>
          <span className="text-[#FFCD41] font-bold" style={{ fontSize: size === 'sm' ? '8px' : size === 'md' ? '10px' : '12px' }}>
            WF
          </span>
        </div>
      );
    }

    // Capital One - Red/Blue
    if (nameLower.includes('capital one')) {
      return (
        <div className={`${sizeClasses[size]} bg-[#004879] rounded-lg flex items-center justify-center shadow-sm`}>
          <span className="text-white font-bold" style={{ fontSize: size === 'sm' ? '8px' : size === 'md' ? '10px' : '12px' }}>
            C1
          </span>
        </div>
      );
    }

    // Discover - Orange
    if (nameLower.includes('discover')) {
      return (
        <div className={`${sizeClasses[size]} bg-[#FF6000] rounded-lg flex items-center justify-center shadow-sm`}>
          <span className="text-white font-bold" style={{ fontSize: size === 'sm' ? '7px' : size === 'md' ? '9px' : '11px' }}>
            DISCOVER
          </span>
        </div>
      );
    }

    // Citi - Blue and red arc
    if (nameLower.includes('citi')) {
      return (
        <div className={`${sizeClasses[size]} bg-white rounded-lg flex items-center justify-center shadow-sm border border-gray-200`}>
          <div className="relative w-full h-full flex items-center justify-center">
            <span className="text-[#056DAE] font-bold" style={{ fontSize: size === 'sm' ? '11px' : size === 'md' ? '14px' : '16px' }}>
              citi
            </span>
            <svg viewBox="0 0 40 40" className="absolute top-0 right-0 w-1/3 h-1/3">
              <path d="M35 5 Q40 5 40 10" fill="none" stroke="#ED1C24" strokeWidth="3"/>
            </svg>
          </div>
        </div>
      );
    }

    // Default fallback with initials
    const getInitials = (name: string): string => {
      const words = name.split(' ');
      if (words.length >= 2) {
        return (words[0][0] + words[1][0]).toUpperCase();
      }
      return name.substring(0, 2).toUpperCase();
    };

    const getBankColor = (name: string): string => {
      const firstLetter = name.charAt(0).toUpperCase();
      const charCode = firstLetter.charCodeAt(0);
      const colors = [
        'bg-blue-600', 'bg-green-600', 'bg-purple-600', 'bg-red-600',
        'bg-yellow-600', 'bg-indigo-600', 'bg-pink-600', 'bg-teal-600'
      ];
      return colors[charCode % colors.length];
    };

    const initials = getInitials(name);
    const bgColor = getBankColor(name);

    return (
      <div className={`${sizeClasses[size]} ${bgColor} rounded-lg flex items-center justify-center shadow-sm`}>
        <span className={`text-white font-semibold ${size === 'sm' ? 'text-xs' : size === 'md' ? 'text-sm' : 'text-base'}`}>
          {initials}
        </span>
      </div>
    );
  };

  return getBankLogo(institutionName);
}
