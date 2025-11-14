"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Timer } from 'lucide-react';

interface EnhancedRetryIntervalProps {
  value: number;
  onChange: (value: number) => void;
}

const presets = [
  { label: 'Fast', value: 30, description: 'Every 30 seconds' },
  { label: 'Normal', value: 60, description: 'Every 1 minute' },
  { label: 'Slow', value: 300, description: 'Every 5 minutes' },
];

export default function EnhancedRetryInterval({ value, onChange }: EnhancedRetryIntervalProps) {
  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Timer className="h-5 w-5" />
          <CardTitle>Retry Configuration</CardTitle>
        </div>
        <CardDescription>
          How often to retry if booking fails
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Presets */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Quick Presets</Label>
          <div className="grid grid-cols-3 gap-2">
            {presets.map((preset) => (
              <Button
                key={preset.value}
                variant={value === preset.value ? "default" : "outline"}
                onClick={() => onChange(preset.value)}
                className="h-auto py-3 flex flex-col items-start"
              >
                <span className="font-semibold">{preset.label}</span>
                <span className="text-xs opacity-70">{preset.description}</span>
              </Button>
            ))}
          </div>
        </div>

        {/* Custom Value */}
        <div className="space-y-2">
          <Label htmlFor="retry-interval" className="text-sm font-medium">
            Custom Interval (seconds)
          </Label>
          <div className="flex gap-2 items-center">
            <Input
              id="retry-interval"
              type="number"
              min="1"
              value={value}
              onChange={(e) => onChange(Math.max(1, parseInt(e.target.value) || 1))}
              className="max-w-[120px]"
            />
            <Badge variant="secondary">
              {formatDuration(value)}
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground">
            Minimum: 1 second • Recommended: 30-300 seconds
          </p>
        </div>

        {/* Info */}
        <div className="pt-4 border-t text-sm text-muted-foreground">
          <p>⚡ Lower intervals increase success chance but use more resources</p>
          <p className="mt-1">🎯 Slots unlock every hour at xx:00:00</p>
        </div>
      </CardContent>
    </Card>
  );
}
