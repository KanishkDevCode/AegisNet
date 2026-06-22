"use client";

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Network, BarChart3 } from 'lucide-react';
import ControlPanel from '@/components/ControlPanel';
import NetworkCanvas from '@/components/NetworkCanvas';
import StatusTerminal from '@/components/StatusTerminal';
import MetricsDashboard from '@/components/MetricsDashboard';

interface LogEntry {
  id: number;
  text: string;
  type: 'info' | 'warning' | 'error' | 'success';
}

type TabView = 'scenario' | 'metrics';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabView>('scenario');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [infectedServer, setInfectedServer] = useState('');
  const [isolationPlan, setIsolationPlan] = useState('');

  const addLog = (text: string, type: 'info' | 'warning' | 'error' | 'success' = 'info') => {
    setLogs((prev) => [...prev, { id: Date.now() + Math.random(), text, type }]);
  };

  const initiateSwarm = async (payloadSize: number) => {
    setIsProcessing(true);
    setLogs([]);
    setInfectedServer('');
    setIsolationPlan('');
    
    addLog(`Initiating Swarm Orchestrator with payload size: ${payloadSize} bytes`, 'info');

    try {
      const response = await axios.post('http://localhost:8000/api/scenarios', {
        network_payload: { bytes: payloadSize, protocol: 'TCP' }
      });
      
      const newTaskId = response.data.task_id;
      setTaskId(newTaskId);
      addLog(`Task queued successfully. Task ID: ${newTaskId}`, 'success');
      addLog('Polling for LangGraph state updates...', 'warning');
      
    } catch (error) {
      addLog(`Failed to connect to API Gateway: ${error}`, 'error');
      setIsProcessing(false);
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (taskId && isProcessing) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`http://localhost:8000/api/scenarios/${taskId}`);
          const data = response.data;

          if (data.status === 'SUCCESS') {
            setIsProcessing(false);
            const finalState = data.result;
            
            addLog(`[Phase 1] Threat Detected: ${finalState.threat_detected}`, 'warning');
            addLog(`[Phase 2] Malware Family: ${finalState.malware_family} (Confidence: ${finalState.vision_confidence}%)`, 'warning');
            
            if (finalState.infected_server) {
              setInfectedServer(finalState.infected_server);
              addLog(`[Phase 3] Infected Node: ${finalState.infected_server}`, 'error');
              addLog(`[Phase 3] LLM Risk Assessment: ${finalState.lateral_movement_risk}`, 'error');
            }

            if (finalState.isolation_plan) {
              setIsolationPlan(finalState.isolation_plan);
              addLog(`[Phase 4] DRL Agent Action: ${finalState.isolation_plan}`, 'success');
              addLog('STATUS: INFECTION CONTAINED.', 'success');
            }

            // Show SOAR webhook if present
            if (finalState.soar_webhook && Object.keys(finalState.soar_webhook).length > 0) {
              addLog(`[SOAR] Enterprise webhook generated → ${finalState.soar_webhook.event_type}`, 'info');
            }

            // Show latencies if present
            if (finalState.phase_latencies && Object.keys(finalState.phase_latencies).length > 0) {
              const lat = finalState.phase_latencies;
              addLog(`[METRICS] Latencies → P1: ${lat.phase1 || 0}ms | P2: ${lat.phase2 || 0}ms | P3: ${lat.phase3 || 0}ms | P4: ${lat.phase4 || 0}ms`, 'info');
            }
            
            setTaskId(null);
          } else if (data.status === 'FAILURE') {
            setIsProcessing(false);
            addLog(`Task failed: ${data.result}`, 'error');
            setTaskId(null);
          }
        } catch (error) {
           addLog(`Polling error: ${error}`, 'error');
           setIsProcessing(false);
           setTaskId(null);
        }
      }, 2000);
    }

    return () => clearInterval(interval);
  }, [taskId, isProcessing]);

  return (
    <div className="w-screen h-screen flex gap-4 p-4 box-border">
      {/* Left Sidebar */}
      <div className="w-80 flex-shrink-0 flex flex-col gap-4">
        <ControlPanel onInitiate={initiateSwarm} isProcessing={isProcessing} />
        
        {/* Tab Switcher */}
        <div className="glass-panel p-2 flex gap-2">
          <button
            onClick={() => setActiveTab('scenario')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'scenario'
                ? 'bg-blue-600 text-white shadow-[0_0_12px_rgba(37,99,235,0.3)]'
                : 'text-zinc-400 hover:text-white hover:bg-zinc-800'
            }`}
          >
            <Network size={14} />
            Scenario
          </button>
          <button
            onClick={() => setActiveTab('metrics')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'metrics'
                ? 'bg-purple-600 text-white shadow-[0_0_12px_rgba(147,51,234,0.3)]'
                : 'text-zinc-400 hover:text-white hover:bg-zinc-800'
            }`}
          >
            <BarChart3 size={14} />
            MLOps
          </button>
        </div>
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
              {/* Network Canvas */}
              <div className="flex-1 relative">
                <NetworkCanvas infectedServer={infectedServer} isolationPlan={isolationPlan} />
              </div>

              {/* Terminal */}
              <div className="h-64 flex-shrink-0">
                <StatusTerminal logs={logs} />
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
