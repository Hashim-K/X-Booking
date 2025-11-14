"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Calendar } from '@/components/ui/calendar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CalendarIcon } from 'lucide-react';
import { format, addDays } from 'date-fns';

interface EnhancedCalendarProps {
  selectedDate: Date;
  onDateChange: (date: Date) => void;
}

export default function EnhancedCalendar({ selectedDate, onDateChange }: EnhancedCalendarProps) {
  const today = new Date();
  const maxDate = addDays(today, 168); // 7 days for fitness, adjust based on location

  const quickDates = [
    { label: 'Today', date: today },
    { label: 'Tomorrow', date: addDays(today, 1) },
    { label: '+3 Days', date: addDays(today, 3) },
    { label: '+7 Days', date: addDays(today, 7) },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <CalendarIcon className="h-5 w-5" />
          <CardTitle>Select Date</CardTitle>
        </div>
        <CardDescription>
          Choose your booking date
          {selectedDate && (
            <Badge variant="outline" className="ml-2">
              {format(selectedDate, 'MMM dd, yyyy')}
            </Badge>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Quick Select */}
        <div className="space-y-2">
          <div className="text-sm font-medium">Quick Select</div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {quickDates.map((quick) => (
              <Button
                key={quick.label}
                variant={
                  format(selectedDate, 'yyyy-MM-dd') === format(quick.date, 'yyyy-MM-dd')
                    ? "default"
                    : "outline"
                }
                size="sm"
                onClick={() => onDateChange(quick.date)}
              >
                {quick.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Calendar */}
        <div className="flex justify-center">
          <Calendar
            mode="single"
            selected={selectedDate}
            onSelect={(date) => date && onDateChange(date)}
            disabled={(date) => date < today || date > maxDate}
            className="rounded-md border"
          />
        </div>

        {/* Info */}
        <div className="text-xs text-muted-foreground space-y-1">
          <p>📅 Fitness: Available 7 days (168h) in advance</p>
          <p>📅 X1/X3: Available 3 days (72h) in advance</p>
        </div>
      </CardContent>
    </Card>
  );
}
