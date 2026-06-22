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

function StatCard({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: number | string; color: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-4 flex items-center gap-4"
    >
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon size={20} />
      </div>
      <div>
        <p className="text-xs text-zinc-400 uppercase tracking-wider">{label}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
      </div>
    </motion.div>
  );
}

function DriftGauge({ value, status }: { value: number; status: string }) {
  const percentage = Math.min((value / 0.20) * 100, 100);
  let gaugeColor = '#22c55e';
  if (status === 'WARNING') gaugeColor = '#eab308';
  if (status === 'CRITICAL') gaugeColor = '#ef4444';

  return (
    <div className="glass-panel p-6 flex flex-col items-center justify-center">
      <p className="text-xs text-zinc-400 uppercase tracking-wider mb-4">Data Drift (Wasserstein)</p>
      <div className="relative w-32 h-32">
        <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
          <circle cx="60" cy="60" r="50" fill="none" stroke="#27272a" strokeWidth="10" />
          <circle
            cx="60" cy="60" r="50" fill="none"
            stroke={gaugeColor}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${percentage * 3.14} 314`}
            style={{ transition: 'stroke-dasharray 1s ease-in-out' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-white">{value.toFixed(4)}</span>
          <span className={`text-xs font-semibold ${status === 'OK' ? 'text-green-400' : status === 'WARNING' ? 'text-yellow-400' : 'text-red-400'}`}>
            {status}
          </span>
        </div>
      </div>
      <div className="flex gap-4 mt-4 text-[10px] text-zinc-500">
        <span><span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-1"></span>&lt;0.10</span>
        <span><span className="inline-block w-2 h-2 rounded-full bg-yellow-500 mr-1"></span>&lt;0.15</span>
        <span><span className="inline-block w-2 h-2 rounded-full bg-red-500 mr-1"></span>&gt;0.15</span>
      </div>
    </div>
  );
}

const customTooltipStyle = {
  backgroundColor: '#18181b',
  border: '1px solid #3f3f46',
  borderRadius: '8px',
  padding: '8px 12px',
  fontSize: '12px',
  color: '#e4e4e7',
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
      <div className="w-full h-full flex items-center justify-center text-zinc-500 font-mono text-sm">
        <Activity className="animate-pulse mr-2" size={16} />
        Connecting to AegisNet Telemetry...
      </div>
    );
  }

  return (
    <div className="w-full h-full overflow-y-auto p-1 space-y-4">
      {/* Stat Cards Row */}
      <div className="grid grid-cols-2 xl:grid-cols-5 gap-3">
        <StatCard icon={BarChart3} label="Total Scenarios" value={data.counters.total_scenarios} color="bg-blue-500/20 text-blue-400" />
        <StatCard icon={Shield} label="Containments" value={data.counters.containments} color="bg-green-500/20 text-green-400" />
        <StatCard icon={AlertTriangle} label="Threats Detected" value={data.counters.threats_detected} color="bg-red-500/20 text-red-400" />
        <StatCard icon={TrendingUp} label="Success Rate" value={data.counters.total_scenarios > 0 ? `${Math.round((data.counters.successful / data.counters.total_scenarios) * 100)}%` : '—'} color="bg-purple-500/20 text-purple-400" />
        <StatCard icon={Zap} label="Failed" value={data.counters.failed} color="bg-yellow-500/20 text-yellow-400" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Confidence Chart */}
        <div className="glass-panel p-4 lg:col-span-2">
          <p className="text-xs text-zinc-400 uppercase tracking-wider mb-3">Vision Model Confidence Over Time</p>
          {data.confidence_history.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={data.confidence_history}>
                <defs>
                  <linearGradient id="confGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#71717a' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#71717a' }} />
                <Tooltip contentStyle={customTooltipStyle} cursor={{ fill: '#27272a', opacity: 0.4 }} />
                <Area type="monotone" dataKey="value" stroke="#3b82f6" fill="url(#confGradient)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-zinc-600 text-sm italic h-[200px] flex items-center justify-center">No data yet. Run a scenario first.</p>
          )}
        </div>

        {/* Drift Gauge */}
        <DriftGauge value={data.current_drift} status={data.drift_status} />
      </div>

      {/* Latency Chart */}
      <div className="glass-panel p-4">
        <p className="text-xs text-zinc-400 uppercase tracking-wider mb-3">Phase Inference Latency (ms)</p>
        {data.latency_history.length > 0 ? (
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={data.latency_history}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#71717a' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#71717a' }} axisLine={false} tickLine={false} tickFormatter={(val) => `${(val / 1000).toFixed(0)}s`} />
              <Tooltip 
                contentStyle={customTooltipStyle} 
                formatter={(value: number) => [`${(value / 1000).toFixed(2)}s`, undefined]} 
                cursor={{ fill: '#27272a', opacity: 0.4 }}
              />
              <Legend iconType="circle" wrapperStyle={{ fontSize: '10px', paddingTop: '10px' }} />
              <Bar dataKey="phase1" stackId="a" fill="#3b82f6" name="P1 (Sensor)" maxBarSize={60} radius={[0, 0, 0, 0]} />
              <Bar dataKey="phase2" stackId="a" fill="#8b5cf6" name="P2 (Vision)" maxBarSize={60} radius={[0, 0, 0, 0]} />
              <Bar dataKey="phase3" stackId="a" fill="#f59e0b" name="P3 (LLM Brain)" maxBarSize={60} radius={[0, 0, 0, 0]} />
              <Bar dataKey="phase4" stackId="a" fill="#22c55e" name="P4 (DRL Firewall)" maxBarSize={60} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-zinc-600 text-sm italic h-[180px] flex items-center justify-center">No data yet. Run a scenario first.</p>
        )}
      </div>
    </div>
  );
}
