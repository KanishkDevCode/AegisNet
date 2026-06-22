"use client";

import React, { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface LogEntry {
  id: number;
  text: string;
  type: 'info' | 'warning' | 'error' | 'success';
}

interface StatusTerminalProps {
  logs: LogEntry[];
}

export default function StatusTerminal({ logs }: StatusTerminalProps) {
  const endRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="w-full h-full glass-panel flex flex-col overflow-hidden">
      <div className="bg-black/40 border-b border-zinc-800 px-4 py-2 flex items-center gap-2">
        <Terminal size={14} className="text-zinc-400" />
        <span className="text-xs font-mono text-zinc-400">LangGraph Execution Logs</span>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto font-mono text-sm space-y-2">
        <AnimatePresence>
          {logs.length === 0 && (
            <p className="text-zinc-600 italic">Waiting for swarm initiation...</p>
          )}
          {logs.map((log) => {
            let color = 'text-zinc-300';
            if (log.type === 'error') color = 'text-red-400';
            if (log.type === 'warning') color = 'text-yellow-400';
            if (log.type === 'success') color = 'text-green-400';
            if (log.type === 'info') color = 'text-blue-400';

            return (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                key={log.id}
                className={`${color} flex gap-2`}
              >
                <span className="text-zinc-600 select-none">{'>'}</span>
                <span>{log.text}</span>
              </motion.div>
            );
          })}
        </AnimatePresence>
        <div ref={endRef} />
      </div>
    </div>
  );
}
