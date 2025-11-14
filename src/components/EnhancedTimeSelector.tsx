"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Clock, X } from 'lucide-react';
import { useState } from 'react';

interface EnhancedTimeSelectorProps {
  selectedTimes: string[];
  onTimesChange: (times: string[]) => void;
}

const timeSlots = [
  '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
  '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
  '18:00', '19:00', '20:00', '21:00', '22:00'
];

export default function EnhancedTimeSelector({ selectedTimes, onTimesChange }: EnhancedTimeSelectorProps) {
  const [quickSelect, setQuickSelect] = useState<number>(3);

  const isSelected = (time: string) => selectedTimes.includes(time);

  const toggleTime = (time: string) => {
    if (isSelected(time)) {
      onTimesChange(selectedTimes.filter(t => t !== time));
    } else {
      onTimesChange([...selectedTimes, time].sort());
    }
  };

  const selectConsecutive = (startTime: string, hours: number) => {
    const startIndex = timeSlots.indexOf(startTime);
    if (startIndex === -1) return;
    
    const consecutive = timeSlots.slice(startIndex, startIndex + hours);
    onTimesChange(consecutive);
  };

  const clearAll = () => {
    onTimesChange([]);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            <CardTitle>Time Slots</CardTitle>
          </div>
          {selectedTimes.length > 0 && (
            <Button variant="ghost" size="sm" onClick={clearAll}>
              <X className="h-4 w-4 mr-1" />
              Clear All
            </Button>
          )}
        </div>
        <CardDescription>
          Select time slots for booking • {selectedTimes.length} slot{selectedTimes.length !== 1 ? 's' : ''} selected
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Quick Select */}
        <div className="space-y-2">
          <div className="text-sm font-medium">Quick Select Consecutive Hours</div>
          <div className="flex gap-2">
            {[1, 2, 3].map((hours) => (
              <Button
                key={hours}
                variant={quickSelect === hours ? "default" : "outline"}
                size="sm"
                onClick={() => setQuickSelect(hours)}
              >
                {hours}h
              </Button>
            ))}
          </div>
        </div>

        {/* Time Grid */}
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
          {timeSlots.map((time) => {
            const selected = isSelected(time);
            return (
              <Button
                key={time}
                variant={selected ? "default" : "outline"}
                className="h-auto py-3"
                onClick={() => {
                  if (quickSelect === 1) {
                    toggleTime(time);
                  } else {
                    selectConsecutive(time, quickSelect);
                  }
                }}
              >
                <div className="flex flex-col items-center">
                  <span className="font-mono font-semibold">{time}</span>
                  {selected && (
                    <Badge variant="secondary" className="mt-1 text-[10px] h-4">
                      {selectedTimes.indexOf(time) + 1}
                    </Badge>
                  )}
                </div>
              </Button>
            );
          })}
        </div>

        {/* Selected Times Summary */}
        {selectedTimes.length > 0 && (
          <div className="pt-4 border-t">
            <div className="text-sm font-medium mb-2">Selected Times</div>
            <div className="flex flex-wrap gap-2">
              {selectedTimes.map((time) => (
                <Badge key={time} variant="default" className="gap-1">
                  {time}
                  <button
                    onClick={() => toggleTime(time)}
                    className="ml-1 hover:bg-primary-foreground/20 rounded-sm"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
