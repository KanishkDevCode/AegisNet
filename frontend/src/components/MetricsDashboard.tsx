"use client";

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart3, Activity, AlertTriangle, Shield, TrendingUp, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, Legend
} from 'recharts';

interface MetricsData {
  counters: {
    total_scenarios: number;
    successful: number;
    failed: number;
    threats_detected: number;
    containments: number;
  };
  confidence_history: Array<{ label: string; value: number }>;
  latency_history: Array<{ label: string; phase1: number; phase2: number; phase3: number; phase4: number }>;
  drift_history: Array<{ label: string; value: number; status: string }>;
  current_drift: number;
  drift_status: string;
}

function StatCard({ icon: Icon, label, value, color, glowColor }: { icon: React.ElementType; label: string; value: number | string; color: string; glowColor: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5, boxShadow: `0 10px 30px -10px ${glowColor}` }}
      className="relative overflow-hidden rounded-xl bg-black/40 backdrop-blur-xl border border-white/10 p-5 flex flex-col gap-3 group transition-all"
    >
      <div className="absolute top-0 left-0 w-full h-1 opacity-0 group-hover:opacity-100 transition-opacity" style={{ background: glowColor }} />
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-xl bg-gradient-to-br ${color} shadow-lg ring-1 ring-white/10`}>
          <Icon size={22} className="text-white drop-shadow-md" />
        </div>
        <div className="flex-1">
          <p className="text-[10px] text-zinc-400 font-semibold uppercase tracking-[0.2em] mb-1">{label}</p>
          <p className="text-3xl font-black text-white tracking-tight">{value}</p>
        </div>
      </div>
    </motion.div>
  );
}

function DriftGauge({ value, status }: { value: number; status: string }) {
  const percentage = Math.min((value / 0.20) * 100, 100);
  let gaugeColor = '#22c55e';
  let glowClass = 'drop-shadow-[0_0_8px_rgba(34,197,94,0.8)]';
  
  if (status === 'WARNING') {
    gaugeColor = '#eab308';
    glowClass = 'drop-shadow-[0_0_8px_rgba(234,179,8,0.8)]';
  }
  if (status === 'CRITICAL') {
    gaugeColor = '#ef4444';
    glowClass = 'drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]';
  }

  return (
    <motion.div 
      whileHover={{ scale: 1.02 }}
      className="rounded-xl bg-black/40 backdrop-blur-xl border border-white/10 p-6 flex flex-col items-center justify-center relative overflow-hidden"
    >
      <div className="absolute -top-24 -right-24 w-48 h-48 bg-white/5 rounded-full blur-3xl" />
      <p className="text-[10px] font-semibold text-zinc-400 uppercase tracking-[0.2em] mb-4">Data Drift (Wasserstein)</p>
      <div className="relative w-36 h-36">
        <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={gaugeColor} />
              <stop offset="100%" stopColor={status === 'OK' ? '#10b981' : status === 'WARNING' ? '#ca8a04' : '#b91c1c'} />
            </linearGradient>
          </defs>
          <circle cx="60" cy="60" r="50" fill="none" stroke="#18181b" strokeWidth="8" />
          <circle
            cx="60" cy="60" r="50" fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${percentage * 3.14} 314`}
            className={`transition-all duration-1000 ease-out ${glowClass}`}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-black text-white tracking-tighter">{value.toFixed(4)}</span>
          <span className={`text-xs font-bold tracking-widest mt-1 ${status === 'OK' ? 'text-green-400' : status === 'WARNING' ? 'text-yellow-400' : 'text-red-400'}`}>
            {status}
          </span>
        </div>
      </div>
      <div className="flex justify-center gap-4 mt-6 px-4 py-2 bg-black/30 rounded-full border border-white/5 text-[10px] text-zinc-400 font-medium">
        <span className="flex items-center"><span className="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5 shadow-[0_0_5px_#22c55e]"></span>&lt;0.10</span>
        <span className="flex items-center"><span className="w-1.5 h-1.5 rounded-full bg-yellow-500 mr-1.5 shadow-[0_0_5px_#eab308]"></span>&lt;0.15</span>
        <span className="flex items-center"><span className="w-1.5 h-1.5 rounded-full bg-red-500 mr-1.5 shadow-[0_0_5px_#ef4444]"></span>&gt;0.15</span>
      </div>
    </motion.div>
  );
}

const customTooltipStyle = {
  backgroundColor: 'rgba(9, 9, 11, 0.9)',
  backdropFilter: 'blur(8px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '12px',
  padding: '12px 16px',
  fontSize: '13px',
  color: '#fafafa',
  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
};

export default function MetricsDashboard() {
  const [data, setData] = useState<MetricsData | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/metrics');
        setData(res.data);
      } catch {
        // API not reachable yet
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 3000);
    return () => clearInterval(interval);
  }, []);

  if (!data) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center text-zinc-500 font-mono text-sm gap-4">
        <div className="w-12 h-12 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
        Connecting to AegisNet Telemetry...
      </div>
    );
  }

  return (
    <div className="w-full h-full overflow-y-auto p-1 space-y-5 pb-10">
      {/* Stat Cards Row */}
      <div className="grid grid-cols-2 xl:grid-cols-5 gap-4">
        <StatCard icon={BarChart3} label="Total Scenarios" value={data.counters.total_scenarios} color="from-blue-600 to-blue-400" glowColor="rgba(59,130,246,0.5)" />
        <StatCard icon={Shield} label="Containments" value={data.counters.containments} color="from-emerald-600 to-emerald-400" glowColor="rgba(16,185,129,0.5)" />
        <StatCard icon={AlertTriangle} label="Threats Detected" value={data.counters.threats_detected} color="from-rose-600 to-rose-400" glowColor="rgba(225,29,72,0.5)" />
        <StatCard icon={TrendingUp} label="Success Rate" value={data.counters.total_scenarios > 0 ? `${Math.round((data.counters.successful / data.counters.total_scenarios) * 100)}%` : '—'} color="from-indigo-600 to-indigo-400" glowColor="rgba(79,70,229,0.5)" />
        <StatCard icon={Zap} label="Failed Tasks" value={data.counters.failed} color="from-amber-600 to-amber-400" glowColor="rgba(217,119,6,0.5)" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Confidence Chart */}
        <motion.div whileHover={{ scale: 1.01 }} className="rounded-xl bg-black/40 backdrop-blur-xl border border-white/10 p-5 lg:col-span-2 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-32 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
          <h3 className="text-sm font-bold text-white tracking-wide mb-1">Vision Model Confidence</h3>
          <p className="text-[10px] text-zinc-400 font-semibold uppercase tracking-[0.1em] mb-6">Historical prediction accuracy over scenario runs</p>
          
          {data.confidence_history.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={data.confidence_history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="confGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.6} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#a1a1aa' }} axisLine={false} tickLine={false} dy={10} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#a1a1aa' }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={customTooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
                <Area type="monotone" dataKey="value" stroke="#60a5fa" fill="url(#confGradient)" strokeWidth={3} activeDot={{ r: 6, fill: '#fff', stroke: '#3b82f6', strokeWidth: 2 }} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[220px] flex flex-col items-center justify-center text-zinc-500 text-sm">
              <Activity className="opacity-20 mb-2" size={32} />
              <p>No telemetry data. Run a scenario to populate.</p>
            </div>
          )}
        </motion.div>

        {/* Drift Gauge */}
        <DriftGauge value={data.current_drift} status={data.drift_status} />
      </div>

      {/* Latency Chart */}
      <motion.div whileHover={{ scale: 1.005 }} className="rounded-xl bg-black/40 backdrop-blur-xl border border-white/10 p-5 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />
        <h3 className="text-sm font-bold text-white tracking-wide mb-1">Agentic Phase Latency</h3>
        <p className="text-[10px] text-zinc-400 font-semibold uppercase tracking-[0.1em] mb-6">Inference time across all Swarm components</p>
        
        {data.latency_history.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.latency_history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }} barGap={2} barSize={12}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#a1a1aa' }} axisLine={false} tickLine={false} dy={10} />
              <YAxis tick={{ fontSize: 11, fill: '#a1a1aa' }} axisLine={false} tickLine={false} tickFormatter={(val) => `${(val / 1000).toFixed(1)}s`} />
              <Tooltip 
                contentStyle={customTooltipStyle} 
                formatter={(value) => [`${(Number(value ?? 0) / 1000).toFixed(2)}s`, undefined as never]} 
                cursor={{ fill: 'rgba(255,255,255,0.02)' }}
              />
              <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', fontWeight: 500, color: '#e4e4e7', paddingTop: '20px' }} />
              <Bar dataKey="phase1" fill="#3b82f6" name="P1 (CatBoost)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="phase2" fill="#8b5cf6" name="P2 (Vision)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="phase3" fill="#f59e0b" name="P3 (LLM Brain)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="phase4" fill="#10b981" name="P4 (DRL Firewall)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[220px] flex flex-col items-center justify-center text-zinc-500 text-sm">
            <BarChart3 className="opacity-20 mb-2" size={32} />
            <p>Awaiting latency metrics from swarm pipeline...</p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
