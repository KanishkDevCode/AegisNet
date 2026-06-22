"use client";

import React, { useMemo } from 'react';
import ReactFlow, { Background, Controls, Node, Edge, BackgroundVariant } from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes: Node[] = [
  { id: '1', position: { x: 350, y: 50 }, data: { label: 'Web-01 (DMZ)' }, style: { background: '#18181b', color: '#fff', border: '1px solid #3f3f46', borderRadius: '8px', padding: '10px' } },
  { id: '2', position: { x: 200, y: 150 }, data: { label: 'App-01' }, style: { background: '#18181b', color: '#fff', border: '1px solid #3f3f46', borderRadius: '8px', padding: '10px' } },
  { id: '3', position: { x: 500, y: 150 }, data: { label: 'Mail-01' }, style: { background: '#18181b', color: '#fff', border: '1px solid #3f3f46', borderRadius: '8px', padding: '10px' } },
  { id: '4', position: { x: 350, y: 250 }, data: { label: 'DB-Primary' }, style: { background: '#18181b', color: '#fff', border: '1px solid #3f3f46', borderRadius: '8px', padding: '10px' } },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#3b82f6', strokeWidth: 2 } },
  { id: 'e1-3', source: '1', target: '3', animated: true, style: { stroke: '#3b82f6', strokeWidth: 2 } },
  { id: 'e2-4', source: '2', target: '4', animated: true, style: { stroke: '#3b82f6', strokeWidth: 2 } },
];

interface NetworkCanvasProps {
  infectedServer: string;
  isolationPlan: string;
}

export default function NetworkCanvas({ infectedServer, isolationPlan }: NetworkCanvasProps) {
  const nodes = useMemo(() => {
    return initialNodes.map((n) => {
      let bgColor = '#18181b';
      let borderColor = '#3f3f46';
      
      // If server is infected
      if (infectedServer && n.data.label.includes(infectedServer)) {
        bgColor = '#450a0a'; // dark red
        borderColor = '#ef4444'; // bright red
      } 
      
      // If server is isolated by DRL Agent
      if (isolationPlan && isolationPlan.includes(n.data.label.split(' ')[0])) {
        bgColor = '#052e16'; // dark green
        borderColor = '#22c55e'; // bright green
      }

      return {
        ...n,
        style: { ...n.style, background: bgColor, border: `2px solid ${borderColor}` }
      };
    });
  }, [infectedServer, isolationPlan]);

  return (
    <div className="w-full h-full glass-panel overflow-hidden relative">
      <div className="absolute top-4 left-4 z-10 text-xs text-zinc-400 font-mono">
        <div className="flex items-center gap-2 mb-1"><div className="w-2 h-2 rounded-full bg-blue-500"></div> Normal</div>
        <div className="flex items-center gap-2 mb-1"><div className="w-2 h-2 rounded-full bg-red-500"></div> Infected</div>
        <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-green-500"></div> Isolated</div>
      </div>
      <ReactFlow nodes={nodes} edges={initialEdges} fitView attributionPosition="bottom-right">
        <Background color="#3f3f46" variant={BackgroundVariant.Dots} gap={16} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
