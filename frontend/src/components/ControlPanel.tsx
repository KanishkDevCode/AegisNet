"use client";

import React, { useState } from 'react';
import { Shield, Play, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

interface ControlPanelProps {
  onInitiate: (payloadSize: number) => void;
  isProcessing: boolean;
}

export default function ControlPanel({ onInitiate, isProcessing }: ControlPanelProps) {
  const [payloadSize, setPayloadSize] = useState<number>(50000);

  return (
    <div className="w-full h-full glass-panel p-6 flex flex-col">
      <div className="flex items-center gap-3 mb-8">
        <div className="p-2 bg-blue-500/20 text-blue-400 rounded-lg">
          <Shield size={24} />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">AegisNet</h1>
          <p className="text-xs text-zinc-400">SOC Orchestrator</p>
        </div>
      </div>

      <div className="flex-1">
        <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Activity size={16} />
          Attack Scenario
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-zinc-400 mb-1">Payload Size (Bytes)</label>
            <input 
              type="number" 
              value={payloadSize}
              onChange={(e) => setPayloadSize(Number(e.target.value))}
              className="w-full bg-black/50 border border-zinc-700 text-white rounded-md px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-xs text-zinc-400 mb-1">Target Vector</label>
            <select className="w-full bg-black/50 border border-zinc-700 text-white rounded-md px-3 py-2 text-sm focus:outline-none focus:border-blue-500">
              <option>Web-01 DMZ Ingress</option>
              <option>Phishing Email (Mail-01)</option>
            </select>
          </div>
        </div>
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => onInitiate(payloadSize)}
        disabled={isProcessing}
        className={`w-full py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors ${
          isProcessing 
            ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed' 
            : 'bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_20px_rgba(37,99,235,0.4)]'
        }`}
      >
        {isProcessing ? (
          <span className="flex items-center gap-2">
            <span className="w-4 h-4 border-2 border-zinc-500 border-t-transparent rounded-full animate-spin"></span>
            Swarm Active...
          </span>
        ) : (
          <>
            <Play size={18} fill="currentColor" />
            Initiate Swarm
          </>
        )}
      </motion.button>
    </div>
  );
}
