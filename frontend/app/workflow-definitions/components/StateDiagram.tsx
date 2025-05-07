'use client';

import React, { useCallback, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Position,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface State {
  id?: string;
  name: string;
  is_initial?: boolean;
  is_final?: boolean;
}

interface Transition {
  id?: string;
  name: string;
  from_state_id: string;
  to_state_id: string;
}

interface StateDiagramProps {
  states: State[];
  transitions: Transition[];
}

export default function StateDiagram({ states, transitions }: StateDiagramProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Create nodes from states
  const createNodes = useCallback(() => {
    return states.map((state, index) => {
      const stateId = state.id || index.toString();
      
      // Calculate position in a circular layout
      const radius = 200;
      const angle = (2 * Math.PI * index) / states.length;
      const x = radius * Math.cos(angle) + 300;
      const y = radius * Math.sin(angle) + 200;
      
      // Determine node style based on state type
      let style = {};
      let className = '';
      
      if (state.is_initial) {
        style = { ...style, borderColor: '#4CAF50', borderWidth: 2 };
        className = 'initial-state';
      }
      
      if (state.is_final) {
        style = { ...style, borderColor: '#F44336', borderWidth: 2 };
        className = state.is_initial ? 'initial-final-state' : 'final-state';
      }
      
      return {
        id: stateId,
        data: { label: state.name },
        position: { x, y },
        style,
        className,
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
      };
    });
  }, [states]);

  // Create edges from transitions
  const createEdges = useCallback(() => {
    return transitions.map((transition, index) => {
      const fromId = transition.from_state_id;
      const toId = transition.to_state_id;
      
      // Skip invalid transitions
      if (fromId === toId || !fromId || !toId) {
        return null;
      }
      
      return {
        id: transition.id || `e${index}`,
        source: fromId,
        target: toId,
        label: transition.name,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#555' },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: '#555',
        },
      };
    }).filter(Boolean) as Edge[];
  }, [transitions]);

  // Update nodes and edges when states or transitions change
  useEffect(() => {
    setNodes(createNodes());
  }, [states, createNodes]);

  useEffect(() => {
    setEdges(createEdges());
  }, [transitions, createEdges]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      fitView
      attributionPosition="bottom-left"
    >
      <Controls />
      <Background color="#f8f8f8" gap={16} />
      <style jsx global>{`
        .initial-state {
          background-color: #E8F5E9;
        }
        .final-state {
          background-color: #FFEBEE;
        }
        .initial-final-state {
          background: linear-gradient(135deg, #E8F5E9 50%, #FFEBEE 50%);
        }
      `}</style>
    </ReactFlow>
  );
}
