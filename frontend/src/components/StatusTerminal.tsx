"use client";

import React, { useEffect, useRef } from 'react';
import { Terminal, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface LogEntry {
  id: number;
  text: string;
  type: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
}

interface StatusTerminalProps {
  logs: LogEntry[];
  isProcessing?: boolean;
}

export default function StatusTerminal({ logs, isProcessing }: StatusTerminalProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="w-full h-full glass-panel flex flex-col overflow-hidden">
      <div className="bg-black/40 border-b border-zinc-800 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal size={14} className="text-zinc-400" />
          <span className="text-xs font-mono text-zinc-400">LangGraph Execution Logs</span>
        </div>
        {isProcessing && (
          <div className="flex items-center gap-1.5 text-blue-400">
            <Loader2 size={12} className="animate-spin" />
            <span className="text-xs font-mono">Processing...</span>
          </div>
        )}
      </div>

      <div className="flex-1 p-4 overflow-y-auto font-mono text-xs space-y-1.5">
        <AnimatePresence>
          {logs.length === 0 && !isProcessing && (
            <p className="text-zinc-600 italic text-sm">Waiting for swarm initiation...</p>
          )}
          {logs.map((log) => {
            let color = 'text-zinc-300';
            let prefix = '>';
            if (log.type === 'error') { color = 'text-red-400'; prefix = '!'; }
            if (log.type === 'warning') { color = 'text-yellow-400'; prefix = '~'; }
            if (log.type === 'success') { color = 'text-green-400'; prefix = '+'; }
            if (log.type === 'info') { color = 'text-blue-400'; prefix = '>'; }

            return (
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                key={log.id}
                className={`${color} flex gap-2 items-start`}
              >
                <span className="text-zinc-600 select-none flex-shrink-0">[{log.timestamp}]</span>
                <span className="text-zinc-600 select-none flex-shrink-0">{prefix}</span>
                <span className="break-all">{log.text}</span>
              </motion.div>
            );
          })}
        </AnimatePresence>
        <div ref={endRef} />
      </div>
    </div>
  );
}
