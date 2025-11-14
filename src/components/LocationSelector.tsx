"use client";

import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { MapPin } from 'lucide-react';

interface LocationSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const locations = [
  { value: 'Fitness', label: 'Fitness', description: '168h advance booking' },
  { value: 'X1', label: 'X1', description: '72h advance booking' },
  { value: 'X3', label: 'X3', description: '72h advance booking' },
];

export default function LocationSelector({ value, onChange }: LocationSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <MapPin className="h-5 w-5" />
          <CardTitle>Location</CardTitle>
        </div>
        <CardDescription>Select your preferred booking location</CardDescription>
      </CardHeader>
      <CardContent>
        <ToggleGroup type="single" value={value} onValueChange={onChange} className="justify-start">
          {locations.map((location) => (
            <ToggleGroupItem
              key={location.value}
              value={location.value}
              aria-label={`Select ${location.label}`}
              className="flex-col h-auto py-3 px-6 data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
            >
              <div className="font-semibold">{location.label}</div>
              <div className="text-xs opacity-70">{location.description}</div>
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </CardContent>
    </Card>
  );
}
