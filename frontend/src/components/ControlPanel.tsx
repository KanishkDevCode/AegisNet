"use client";

import React, { useState } from 'react';
import { Shield, Play, Activity, ShieldAlert, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ControlPanelProps {
  onInitiate: (payloadSize: number, attackType: string) => void;
  isProcessing: boolean;
  hitlPending?: boolean;
}

const ATTACK_OPTIONS = [
  { value: 'normal', label: 'Normal Traffic', description: 'Benign network activity', color: 'text-green-400', bg: 'bg-green-500/10' },
  { value: 'ddos', label: 'DDoS Flood', description: 'Volumetric SYN/UDP flood attack', color: 'text-red-400', bg: 'bg-red-500/10' },
  { value: 'dos', label: 'DoS Slowloris', description: 'Connection exhaustion attack', color: 'text-orange-400', bg: 'bg-orange-500/10' },
  { value: 'bot', label: 'Botnet C2', description: 'Command & control beaconing', color: 'text-purple-400', bg: 'bg-purple-500/10' },
  { value: 'bruteforce', label: 'Bruteforce', description: 'SSH/FTP credential stuffing', color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
  { value: 'infiltration', label: 'Exfiltration', description: 'Stealthy data theft via tunnel', color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
  { value: 'web_attack', label: 'Web Attack', description: 'SQL injection / XSS payload', color: 'text-pink-400', bg: 'bg-pink-500/10' },
];

export default function ControlPanel({ onInitiate, isProcessing, hitlPending }: ControlPanelProps) {
  const [payloadSize, setPayloadSize] = useState<number>(50000);
  const [attackType, setAttackType] = useState<string>('normal');

  const isDisabled = isProcessing || hitlPending;
  const selectedAttack = ATTACK_OPTIONS.find(a => a.value === attackType);
  const isAttackMode = attackType !== 'normal';

  return (
    <div className="w-full h-full glass-panel p-6 flex flex-col">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-500/20 text-blue-400 rounded-lg">
          <Shield size={24} />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">AegisNet</h1>
          <p className="text-xs text-zinc-400">SOC Orchestrator</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-5 pr-2">
        <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider flex items-center gap-2">
          <Activity size={16} />
          Attack Scenario
        </h2>

        {/* Payload Size */}
        <div>
          <label className="block text-xs text-zinc-400 mb-1">Payload Size (Bytes)</label>
          <input
            type="number"
            value={payloadSize}
            onChange={(e) => setPayloadSize(Number(e.target.value))}
            disabled={isDisabled}
            className="w-full bg-black/50 border border-zinc-700 text-white rounded-md px-3 py-2 text-sm focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Target Vector */}
        <div>
          <label className="block text-xs text-zinc-400 mb-1">Target Vector</label>
          <select
            disabled={isDisabled}
            className="w-full bg-black/50 border border-zinc-700 text-white rounded-md px-3 py-2 text-sm focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option>Web-01 DMZ Ingress</option>
            <option>Phishing Email (Mail-01)</option>
          </select>
        </div>

        {/* Attack Type Selector */}
        <div>
          <label className="block text-xs text-zinc-400 mb-2 flex items-center gap-1.5">
            <Zap size={12} />
            Attack Vector
          </label>
          <div className="space-y-1">
            {ATTACK_OPTIONS.map((attack) => (
              <motion.button
                key={attack.value}
                whileHover={{ scale: isDisabled ? 1 : 1.01 }}
                whileTap={{ scale: isDisabled ? 1 : 0.99 }}
                onClick={() => !isDisabled && setAttackType(attack.value)}
                disabled={isDisabled}
                className={`w-full text-left px-3 py-1.5 rounded-lg border transition-all text-xs ${
                  attackType === attack.value
                    ? `${attack.bg} border-current ${attack.color} shadow-sm`
                    : 'border-zinc-800 text-zinc-500 hover:border-zinc-600 hover:text-zinc-300'
                } ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold">{attack.label}</span>
                  {attackType === attack.value && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className={`w-2 h-2 rounded-full ${attack.color === 'text-green-400' ? 'bg-green-400' : 'bg-current'}`}
                    />
                  )}
                </div>
                <p className="text-[10px] opacity-60 mt-0.5">{attack.description}</p>
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      {/* Action Button */}
      <div className="pt-4">
        <motion.button
          whileHover={{ scale: isDisabled ? 1 : 1.02 }}
          whileTap={{ scale: isDisabled ? 1 : 0.98 }}
          onClick={() => onInitiate(payloadSize, attackType)}
          disabled={isDisabled}
          className={`w-full py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors ${
            hitlPending
              ? 'bg-yellow-600/20 text-yellow-400 border border-yellow-600/40 cursor-not-allowed'
              : isProcessing
              ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
              : isAttackMode
              ? 'bg-red-600 hover:bg-red-500 text-white shadow-[0_0_20px_rgba(220,38,38,0.4)]'
              : 'bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_20px_rgba(37,99,235,0.4)]'
          }`}
        >
          {hitlPending ? (
            <span className="flex items-center gap-2">
              <ShieldAlert size={18} className="animate-pulse" />
              Awaiting HITL Approval
            </span>
          ) : isProcessing ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-zinc-500 border-t-transparent rounded-full animate-spin"></span>
              Swarm Active...
            </span>
          ) : isAttackMode ? (
            <>
              <Zap size={18} />
              Launch {selectedAttack?.label}
            </>
          ) : (
            <>
              <Play size={18} fill="currentColor" />
              Initiate Swarm
            </>
          )}
        </motion.button>
      </div>
    </div>
  );
}
