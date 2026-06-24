"use strict";
"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Activity, Eye, Brain, ShieldAlert, Zap, Server, Network } from 'lucide-react';

interface AfterActionReportProps {
  reportData: any;
  onClose: () => void;
}

export default function AfterActionReport({ reportData, onClose }: AfterActionReportProps) {
  if (!reportData) return null;

  const isThreat = reportData.threat_detected;
  const attackType = reportData.network_payload?.attack_type || 'Normal Traffic';
  const confidence = reportData.vision_confidence || 0;
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="absolute inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md p-6"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className="w-full max-w-4xl max-h-[90vh] glass-panel border border-white/10 rounded-2xl shadow-2xl shadow-green-900/20 flex flex-col relative overflow-hidden"
      >
        {/* Background Glowing Orb */}
        <div className={`absolute -top-32 -left-32 w-64 h-64 rounded-full blur-3xl pointer-events-none ${isThreat ? 'bg-red-500/10' : 'bg-green-500/10'}`} />

        {/* Header Section */}
        <div className={`p-8 border-b ${isThreat ? 'border-red-500/20 bg-red-500/5' : 'border-green-500/20 bg-green-500/5'} flex items-center justify-between`}>
          <div className="flex items-center gap-4">
            <div className={`p-4 rounded-2xl ${isThreat ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
              {isThreat ? <ShieldAlert size={32} /> : <ShieldCheck size={32} />}
            </div>
            <div>
              <p className={`text-xs font-bold uppercase tracking-[0.2em] mb-1 ${isThreat ? 'text-red-400' : 'text-green-400'}`}>
                {isThreat ? 'Threat Contained' : 'Scenario Completed'}
              </p>
              <h1 className="text-3xl font-black text-white tracking-tight">After-Action Report (AAR)</h1>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-zinc-500 font-mono mb-1">Incident ID</p>
            <p className="text-sm font-mono text-zinc-300 bg-black/40 px-3 py-1 rounded-md border border-white/10">
              {reportData.task_id || Math.random().toString(36).substring(7).toUpperCase()}
            </p>
          </div>
        </div>

        {/* Body Content */}
        <div className="p-8 space-y-6 flex-1 overflow-y-auto">
          
          {/* Top Metrics Row */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-black/40 rounded-xl border border-white/5 p-4 relative overflow-hidden">
              <Zap size={16} className="text-blue-400 absolute top-4 right-4 opacity-20" />
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold mb-1">Attack Vector</p>
              <p className="text-lg font-bold text-white capitalize">{attackType.replace('-', ' ')}</p>
            </div>
            <div className="bg-black/40 rounded-xl border border-white/5 p-4 relative overflow-hidden">
              <Server size={16} className="text-red-400 absolute top-4 right-4 opacity-20" />
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold mb-1">Target Node</p>
              <p className="text-lg font-bold text-white">{reportData.infected_server || 'None'}</p>
            </div>
            <div className="bg-black/40 rounded-xl border border-white/5 p-4 relative overflow-hidden">
              <Activity size={16} className="text-purple-400 absolute top-4 right-4 opacity-20" />
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold mb-1">Resolution Time</p>
              <p className="text-lg font-bold text-white">
                {(((reportData.phase_latencies?.phase1 || 0) + (reportData.phase_latencies?.phase2 || 0) + (reportData.phase_latencies?.phase3 || 0) + (reportData.phase_latencies?.phase4 || 0)) / 1000).toFixed(2)}s
              </p>
            </div>
          </div>

          {/* AI Executive Summary */}
          {isThreat && (
            <div className="bg-black/40 border border-purple-500/20 rounded-xl p-5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl pointer-events-none" />
              <h2 className="text-sm font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-2 mb-3">
                <Brain size={16} className="text-purple-400" />
                AI Executive Summary
              </h2>
              <p className="text-sm text-zinc-300 leading-relaxed font-serif">
                AegisNet Swarm Orchestrator detected a highly suspicious <strong className="text-white">{attackType.replace('-', ' ')}</strong> targeting <strong className="text-white">{reportData.infected_server || 'the network'}</strong>. 
                Vision analysis confirmed the payload matches the <strong className="text-purple-300">{reportData.malware_family || 'unknown'}</strong> malware family with {confidence.toFixed(1)}% confidence. 
                GraphRAG context evaluation identified lateral movement risks, and the DRL Zero-Trust Firewall successfully isolated the threat by executing: <strong className="text-green-400 font-mono text-xs ml-1 bg-green-500/10 px-1 py-0.5 rounded">{reportData.isolation_plan}</strong>.
              </p>
            </div>
          )}

          {/* Detailed Pipeline Breakdown */}
          {isThreat && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-2 mb-4">
                <Network size={16} className="text-blue-500" /> 
                Swarm Pipeline Execution
              </h2>

              <div className="grid grid-cols-2 gap-4">
                {/* Phase 1 & 2 */}
                <div className="space-y-4">
                  <div className="bg-black/40 border border-white/5 rounded-xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="bg-blue-500/20 p-1.5 rounded-md"><Activity size={14} className="text-blue-400" /></div>
                      <p className="text-sm font-bold text-white">Phase 1: CatBoost Sensor</p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3">
                      <p className="text-xs text-zinc-400 mb-1">Pattern Detected</p>
                      <p className="text-sm font-mono text-zinc-200">{attackType}</p>
                    </div>
                  </div>

                  <div className="bg-black/40 border border-white/5 rounded-xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="bg-purple-500/20 p-1.5 rounded-md"><Eye size={14} className="text-purple-400" /></div>
                      <p className="text-sm font-bold text-white">Phase 2: Vision Transformer</p>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-zinc-400 mb-1">Malware Family</p>
                        <p className="text-sm font-mono text-zinc-200">{reportData.malware_family || 'N/A'}</p>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-zinc-400 mb-1">Confidence</p>
                        <p className={`text-sm font-bold font-mono ${confidence > 90 ? 'text-green-400' : 'text-yellow-400'}`}>
                          {confidence.toFixed(2)}%
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Phase 3 & 4 */}
                <div className="space-y-4">
                  <div className="bg-black/40 border border-white/5 rounded-xl p-5 h-full flex flex-col">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="bg-yellow-500/20 p-1.5 rounded-md"><Brain size={14} className="text-yellow-400" /></div>
                      <p className="text-sm font-bold text-white">Phase 3: GraphRAG LLM Brain</p>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3 flex-1">
                      <p className="text-xs text-zinc-400 mb-2">Lateral Movement Risk Assessment</p>
                      <p className="text-xs text-zinc-300 leading-relaxed font-serif italic border-l-2 border-yellow-500/50 pl-3">
                        {reportData.lateral_movement_risk}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* DRL Firewall Action */}
              <div className="mt-4 bg-gradient-to-r from-green-900/40 to-emerald-900/20 border border-green-500/30 rounded-xl p-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/10 rounded-full blur-2xl" />
                <div className="flex items-center gap-3 mb-4 relative z-10">
                  <div className="bg-green-500/20 p-2 rounded-lg">
                    <ShieldCheck size={20} className="text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-white">Phase 4: DRL Zero-Trust Firewall</p>
                    <p className="text-xs text-green-400">Threat Auto-Contained</p>
                  </div>
                </div>
                <div className="bg-black/50 border border-green-500/20 rounded-lg p-4 font-mono text-sm text-green-300 shadow-inner relative z-10">
                  {">"} {reportData.isolation_plan}
                </div>
              </div>
            </div>
          )}

        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t border-white/5 bg-black/20 flex justify-end">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onClose}
            className="px-8 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-bold transition-colors shadow-lg shadow-black/50 border border-white/10"
          >
            Acknowledge & Close Report
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  );
}
