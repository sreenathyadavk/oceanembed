import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts';
import { DEPTHS, ProfilePoint } from '@/types/ocean';

interface Props {
  data: ProfilePoint[];
  depth: number;
  onDepthClick?: (depth: number) => void;
}

export default function ProfileChart({ data, depth, onDepthClick }: Props) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart 
        data={data} 
        layout="vertical" 
        margin={{ top: 20, right: 10, bottom: 5, left: -10 }}
        onClick={(e) => {
          if (e && e.activePayload && onDepthClick) {
             onDepthClick(e.activePayload[0].payload.depth);
          }
        }}
      >
        <CartesianGrid stroke="#E2E8F0" strokeDasharray="3 3" vertical={false} />
        
        <XAxis 
          type="number" 
          orientation="top" 
          domain={['auto', 'auto']} 
          axisLine={false} 
          tickLine={false} 
          tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} 
        />
        
        <YAxis 
          type="number" 
          dataKey="depth" 
          reversed 
          domain={[0, 1000]} 
          axisLine={false} 
          tickLine={false} 
          ticks={DEPTHS} 
          tick={{ fill: '#64748B', fontSize: 10, fontFamily: 'monospace' }} 
          width={35} 
        />
        
        <Tooltip 
          contentStyle={{ background: '#FFFFFF', border: '1px solid #E2E8F0', padding: '8px 12px', fontSize: 11, borderRadius: '6px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }} 
          formatter={(v: number, name: string) => {
            if (name === 'predicted') return [v.toFixed(2) + ' °C', 'OceanEmbed prediction'];
            if (name === 'glorys') return [v.toFixed(2) + ' °C', 'GLORYS reference'];
            return [v, name];
          }}
          labelStyle={{ color: '#0F172A', fontWeight: 600, fontSize: 11, fontFamily: 'monospace', marginBottom: '4px' }} 
          labelFormatter={l => `${l} m`}
          itemStyle={{ color: '#087EA4', fontWeight: 600, fontFamily: 'monospace' }} 
          cursor={{ stroke: '#CBD5E1', strokeWidth: 1, strokeDasharray: '3 3' }}
        />
        
        <ReferenceLine 
          y={depth} 
          stroke="#087EA4" 
          strokeDasharray="4 4" 
          strokeWidth={1.5} 
        />
        
        <Line 
          type="monotone"
          dataKey="predicted" 
          stroke="#087EA4" 
          strokeWidth={2} 
          dot={{ r: 2.5, fill: '#087EA4', strokeWidth: 0 }} 
          activeDot={{ r: 5, fill: '#087EA4', strokeWidth: 3, stroke: '#FFFFFF', cursor: 'pointer' }} 
          isAnimationActive={false}
        />
        <Line 
          type="monotone"
          dataKey="glorys" 
          stroke="#64748B" 
          strokeWidth={1.5} 
          dot={{ r: 0 }} 
          activeDot={{ r: 4, fill: '#64748B', strokeWidth: 0, cursor: 'default' }} 
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
