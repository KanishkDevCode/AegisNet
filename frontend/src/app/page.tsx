"use client";

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Network, BarChart3, ShieldAlert, ShieldCheck, ShieldOff, X, AlertTriangle } from 'lucide-react';
import ControlPanel from '@/components/ControlPanel';
import NetworkCanvas from '@/components/NetworkCanvas';
import StatusTerminal from '@/components/StatusTerminal';
import MetricsDashboard from '@/components/MetricsDashboard';
import AfterActionReport from '@/components/AfterActionReport';

interface LogEntry {
  id: number;
  text: string;
  type: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
}

interface HITLData {
  taskId: string;
  malwareFamily: string;
  confidence: number;
  infectedServer: string;
  lateralMovementRisk: string;
}

type TabView = 'scenario' | 'metrics';

function getTimestamp() {
  return new Date().toLocaleTimeString('en-US', { hour12: false });
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabView>('scenario');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [infectedServer, setInfectedServer] = useState('');
  const [isolationPlan, setIsolationPlan] = useState('');
  const [hitlData, setHitlData] = useState<HITLData | null>(null);
  const [isApproving, setIsApproving] = useState(false);
  const [latestReport, setLatestReport] = useState<any>(null);
  const [isReportOpen, setIsReportOpen] = useState(false);

  const addLog = useCallback((text: string, type: 'info' | 'warning' | 'error' | 'success' = 'info') => {
    setLogs((prev) => [...prev, { id: Date.now() + Math.random(), text, type, timestamp: getTimestamp() }]);
  }, []);

  const initiateSwarm = async (payloadSize: number, attackType: string) => {
    setIsProcessing(true);
    setLogs([]);
    setInfectedServer('');
    setIsolationPlan('');
    setHitlData(null);

    const logMsg = attackType === 'normal' 
      ? `Initiating Swarm Orchestrator with payload size: ${payloadSize} bytes`
      : `Initiating ${attackType.toUpperCase()} Attack Vector (Payload: ${payloadSize} bytes)`;
    addLog(logMsg, 'info');

    try {
      const response = await axios.post('http://localhost:8000/api/scenarios', {
        network_payload: { bytes: payloadSize, protocol: 'TCP', attack_type: attackType }
      });

      const newTaskId = response.data.task_id;
      setTaskId(newTaskId);
      addLog(`Task queued. Task ID: ${newTaskId.slice(0, 8)}...`, 'success');
      addLog('Running Phase 1: CatBoost anomaly detection...', 'info');
    } catch (error) {
      addLog(`Failed to connect to API Gateway: ${error}`, 'error');
      setIsProcessing(false);
    }
  };

  const handleApprove = async () => {
    if (!hitlData) return;
    setIsApproving(true);
    addLog('[HITL] Human analyst APPROVED — executing Phase 4 DRL firewall isolation...', 'warning');
    try {
      await axios.post(`http://localhost:8000/api/scenarios/${hitlData.taskId}/approve`);
      setHitlData(null);
      setTaskId(hitlData.taskId);
      setIsProcessing(true);
    } catch (e) {
      addLog(`Approval failed: ${e}`, 'error');
    }
    setIsApproving(false);
  };

  const handleDeny = async () => {
    if (!hitlData) return;
    setIsApproving(true);
    addLog('[HITL] Human analyst DENIED — containment action blocked. Monitoring continues.', 'error');
    try {
      await axios.post(`http://localhost:8000/api/scenarios/${hitlData.taskId}/deny`);
      setHitlData(null);
      setTaskId(hitlData.taskId);
      setIsProcessing(true);
    } catch (e) {
      addLog(`Denial failed: ${e}`, 'error');
    }
    setIsApproving(false);
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (taskId && isProcessing) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`http://localhost:8000/api/scenarios/${taskId}`);
          const data = response.data;

          if (data.status === 'AWAITING_APPROVAL') {
            // Pause polling and show the HITL modal
            setIsProcessing(false);
            clearInterval(interval);
            const state = data.result;
            addLog(`[Phase 2] ViT Classification: ${state.malware_family} (Confidence: ${state.vision_confidence}%)`, 'warning');
            addLog(`[Phase 3] Infected Node: ${state.infected_server}`, 'error');
            addLog(`[Phase 3] LLM Risk: ${state.lateral_movement_risk}`, 'error');
            addLog(`[HITL] Confidence ${state.vision_confidence}% < 80% — HUMAN APPROVAL REQUIRED`, 'warning');
            if (state.infected_server) setInfectedServer(state.infected_server);
            setHitlData({
              taskId,
              malwareFamily: state.malware_family,
              confidence: state.vision_confidence,
              infectedServer: state.infected_server,
              lateralMovementRisk: state.lateral_movement_risk,
            });
            setTaskId(null);

          } else if (data.status === 'SUCCESS' || data.status === 'DENIED') {
            setIsProcessing(false);
            clearInterval(interval);
            const finalState = data.result;

            if (data.status === 'SUCCESS') {
              addLog(`[Phase 1] Threat Detected: ${finalState.threat_detected}`, 'warning');
              if (finalState.threat_detected) {
                if (!hitlData) {
                  // Only log these again if we didn't already log them during AWAITING_APPROVAL
                  addLog(`[Phase 2] Malware Family: ${finalState.malware_family} (Confidence: ${finalState.vision_confidence}%)`, 'warning');
                  if (finalState.infected_server) {
                    setInfectedServer(finalState.infected_server);
                    addLog(`[Phase 3] Infected Node: ${finalState.infected_server}`, 'error');
                    addLog(`[Phase 3] LLM Risk Assessment: ${finalState.lateral_movement_risk}`, 'error');
                  }
                }
                if (finalState.isolation_plan) {
                  setIsolationPlan(finalState.isolation_plan);
                  addLog(`[Phase 4] DRL Agent Action: ${finalState.isolation_plan}`, 'success');
                  addLog('STATUS: INFECTION CONTAINED.', 'success');
                }
                if (finalState.soar_webhook && Object.keys(finalState.soar_webhook).length > 0) {
                  addLog(`[SOAR] Enterprise webhook generated: ${finalState.soar_webhook.event_type}`, 'info');
                }
                if (finalState.phase_latencies && Object.keys(finalState.phase_latencies).length > 0) {
                  const lat = finalState.phase_latencies;
                  addLog(`[METRICS] P1: ${lat.phase1 || 0}ms | P2: ${lat.phase2 || 0}ms | P3: ${lat.phase3 || 0}ms | P4: ${lat.phase4 || 0}ms`, 'info');
                }
                
                // Show the After-Action Report modal
                setLatestReport(finalState);
                setIsReportOpen(true);
              }
            } else {
              // DENIED
              addLog(`[Phase 4] DRL Agent: ${finalState.isolation_plan}`, 'error');
              addLog('STATUS: MONITORING ACTIVE. No automated action taken.', 'warning');
            }
            setTaskId(null);

          } else if (data.status === 'FAILURE') {
            setIsProcessing(false);
            clearInterval(interval);
            addLog(`Task failed: ${data.result}`, 'error');
            setTaskId(null);
          }
        } catch (error) {
          addLog(`Polling error: ${error}`, 'error');
          setIsProcessing(false);
          clearInterval(interval);
          setTaskId(null);
        }
      }, 2000);
    }

    return () => clearInterval(interval);
  }, [taskId, isProcessing]);

  const confidenceColor = hitlData
    ? hitlData.confidence >= 80 ? 'text-green-400' : hitlData.confidence >= 50 ? 'text-yellow-400' : 'text-red-400'
    : '';

  return (
    <div className="w-screen h-screen overflow-hidden flex gap-4 p-4 box-border relative bg-[#09090b]">

      {/* After-Action Report Modal */}
      <AnimatePresence>
        {isReportOpen && latestReport && (
          <AfterActionReport reportData={latestReport} onClose={() => setIsReportOpen(false)} />
        )}
      </AnimatePresence>

      {/* HITL Approval Modal */}
      <AnimatePresence>
        {hitlData && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.85, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.85, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              className="glass-panel w-full max-w-lg mx-4 overflow-hidden"
            >
              {/* Modal Header */}
              <div className="bg-yellow-500/10 border-b border-yellow-500/30 px-6 py-4 flex items-center gap-3">
                <div className="p-2 bg-yellow-500/20 rounded-lg">
                  <AlertTriangle size={20} className="text-yellow-400" />
                </div>
                <div>
                  <h2 className="text-white font-bold text-lg">Human Approval Required</h2>
                  <p className="text-yellow-400/80 text-xs">HITL Matrix — Low Confidence Detection</p>
                </div>
              </div>

              {/* Modal Body */}
              <div className="p-6 space-y-4">
                <p className="text-zinc-400 text-sm">
                  The AI confidence score is below the 80% auto-approval threshold.
                  A human SOC analyst must review and approve the isolation action.
                </p>

                {/* Threat Details Grid */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-black/40 rounded-lg p-3 border border-zinc-800">
                    <p className="text-zinc-500 text-xs mb-1">Malware Family</p>
                    <p className="text-white font-mono font-semibold text-sm">{hitlData.malwareFamily}</p>
                  </div>
                  <div className="bg-black/40 rounded-lg p-3 border border-zinc-800">
                    <p className="text-zinc-500 text-xs mb-1">ViT Confidence</p>
                    <p className={`font-mono font-bold text-lg ${confidenceColor}`}>{hitlData.confidence.toFixed(1)}%</p>
                  </div>
                  <div className="bg-black/40 rounded-lg p-3 border border-zinc-800">
                    <p className="text-zinc-500 text-xs mb-1">Infected Node</p>
                    <p className="text-red-400 font-mono font-semibold text-sm">{hitlData.infectedServer || 'Unknown'}</p>
                  </div>
                  <div className="bg-black/40 rounded-lg p-3 border border-zinc-800">
                    <p className="text-zinc-500 text-xs mb-1">Proposed Action</p>
                    <p className="text-purple-400 font-mono text-xs">DRL Firewall Isolation</p>
                  </div>
                </div>

                {/* LLM Risk Assessment */}
                <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-3">
                  <p className="text-zinc-500 text-xs mb-1">LLM Risk Assessment</p>
                  <p className="text-zinc-300 text-xs leading-relaxed">{hitlData.lateralMovementRisk || 'High risk of lateral movement. Immediate isolation recommended.'}</p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-2">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleDeny}
                    disabled={isApproving}
                    className="flex-1 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 transition-colors disabled:opacity-50"
                  >
                    <ShieldOff size={16} />
                    Deny Action
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleApprove}
                    disabled={isApproving}
                    className="flex-1 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 bg-green-600 hover:bg-green-500 text-white shadow-[0_0_20px_rgba(34,197,94,0.3)] transition-colors disabled:opacity-50"
                  >
                    {isApproving ? (
                      <span className="w-4 h-4 border-2 border-white/50 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <ShieldCheck size={16} />
                    )}
                    Approve Isolation
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Left Sidebar */}
      <div className="w-80 flex-shrink-0 flex flex-col gap-4 h-full overflow-hidden">
        <div className="flex-1 overflow-hidden min-h-0">
          <ControlPanel onInitiate={initiateSwarm} isProcessing={isProcessing} hitlPending={!!hitlData} />
        </div>
        
        {/* Navigation Tabs and View AAR Button */}
        <div className="flex flex-col gap-2 mt-4">
          <div className="flex bg-black/40 border border-white/10 rounded-xl overflow-hidden p-1 gap-1">
            <button
              onClick={() => setActiveTab('scenario')}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-2 text-[10px] sm:text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${activeTab === 'scenario' ? 'bg-purple-600 text-white shadow-lg' : 'text-zinc-500 hover:text-white hover:bg-white/5'}`}
            >
              <Network size={14} />
              Scenario
            </button>
            <button
              onClick={() => setActiveTab('metrics')}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-2 text-[10px] sm:text-xs font-bold uppercase tracking-wider rounded-lg transition-all ${activeTab === 'metrics' ? 'bg-purple-600 text-white shadow-lg' : 'text-zinc-500 hover:text-white hover:bg-white/5'}`}
            >
              <BarChart3 size={14} />
              MLOps
            </button>
          </div>

          {latestReport && (
            <button
              onClick={() => setIsReportOpen(true)}
              className="w-full py-3 px-6 bg-zinc-800 border border-zinc-600 hover:bg-zinc-700 text-white rounded-xl text-xs font-bold uppercase tracking-wider transition-colors shadow-lg flex items-center justify-center gap-2"
            >
              View Last AAR
            </button>
          )}
        </div>

        {/* HITL Pending Badge */}
        <AnimatePresence>
          {hitlData && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="glass-panel p-3 border border-yellow-500/40 bg-yellow-500/5 flex items-center gap-3"
            >
              <ShieldAlert size={18} className="text-yellow-400 flex-shrink-0 animate-pulse" />
              <div>
                <p className="text-yellow-400 text-xs font-bold">HITL PENDING</p>
                <p className="text-zinc-400 text-xs">Analyst action required</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col gap-4 min-w-0">
        <AnimatePresence mode="wait">
          {activeTab === 'scenario' ? (
            <motion.div
              key="scenario"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="flex-1 flex flex-col gap-4"
            >
              <div className="flex-1 relative">
                <NetworkCanvas infectedServer={infectedServer} isolationPlan={isolationPlan} />
              </div>
              <div className="h-64 flex-shrink-0">
                <StatusTerminal logs={logs} isProcessing={isProcessing} />
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="metrics"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="flex-1"
            >
              <MetricsDashboard />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
