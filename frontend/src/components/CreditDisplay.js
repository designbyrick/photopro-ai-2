import React from 'react';
import { Coins, Plus } from 'lucide-react';

function CreditDisplay({ credits, onPurchase }) {
  return (
    <div className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2">
      <Coins className="w-5 h-5 text-yellow-400" />
      <span className="text-white font-semibold">
        {credits} Credits
      </span>
      {onPurchase && (
        <button
          onClick={onPurchase}
          className="flex items-center space-x-1 text-white/80 hover:text-white transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span className="text-sm">Buy More</span>
        </button>
      )}
    </div>
  );
}

export default CreditDisplay;
