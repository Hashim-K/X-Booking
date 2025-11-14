'use client';

import StatusBar from '@/components/StatusBar';
import AccountSwitcher from '@/components/AccountSwitcher';
import BookingHistory from '@/components/BookingHistory';
import AccountStats from '@/components/AccountStats';
import EnhancedCalendar from '@/components/EnhancedCalendar';
import EnhancedTimeSelector from '@/components/EnhancedTimeSelector';
import EnhancedRetryInterval from '@/components/EnhancedRetryInterval';
import LocationSelector from '@/components/LocationSelector';
import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export default function Home() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [selectedTimes, setSelectedTimes] = useState<string[]>([]);
  const [retryInterval, setRetryInterval] = useState<number>(300);
  const [location, setLocation] = useState<string>('Fitness');
  const [status, setStatus] = useState<string>('');
  const [isBooking, setIsBooking] = useState<boolean>(false);
  const [selectedAccountId, setSelectedAccountId] = useState<number | undefined>(undefined);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const attemptBooking = async () => {
    try {
      const response = await fetch('/api/book', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          date: selectedDate,
          times: selectedTimes,
          interval: retryInterval,
          location: location,
        }),
      });

      if (response.ok) {
        setStatus('Booking completed!');
        setIsBooking(false);
        return true;
      }
      console.log(response);
      return false;
    } catch (error) {
      setStatus(`Error: ${error}`);
      setIsBooking(false);
      console.log(error);
      return false;
    }
  };

  const handleStartBooking = async () => {
    if (selectedTimes.length === 0) {
      setStatus('Please select at least one time slot');
      return;
    }

    setIsBooking(true);
    setStatus('Starting booking process...');

    if (!(await attemptBooking())) {
      setStatus(`No available slots, retrying in ${retryInterval} seconds...`);
      retryTimeoutRef.current = setTimeout(handleStartBooking, retryInterval * 1000);
    }
  };

  const handleStopBooking = () => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }
    setStatus('Booking stopped');
    setIsBooking(false);
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">
          Multi-Account Fitness Slot Booking
        </h1>
        <p className="text-center text-muted-foreground">
          Bot-sniping system with priority-based booking
        </p>
      </div>

      <Tabs defaultValue="single" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="single">Single Booking</TabsTrigger>
          <TabsTrigger value="multi">Multi-Booking</TabsTrigger>
          <TabsTrigger value="accounts">Accounts</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        {/* Single Booking Tab - Manual/Sniping */}
        <TabsContent value="single" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Account Selection */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle>Active Account</CardTitle>
                </CardHeader>
                <CardContent>
                  <AccountSwitcher
                    currentAccountId={selectedAccountId}
                    onAccountChange={(account) => setSelectedAccountId(account.id)}
                    showStats={false}
                  />
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Booking Configuration */}
            <div className="lg:col-span-2 space-y-6">
              <EnhancedCalendar 
                selectedDate={selectedDate} 
                onDateChange={setSelectedDate} 
              />

              <LocationSelector 
                value={location}
                onChange={setLocation}
              />

              <EnhancedTimeSelector 
                selectedTimes={selectedTimes}
                onTimesChange={setSelectedTimes}
              />

              <EnhancedRetryInterval 
                value={retryInterval} 
                onChange={setRetryInterval} 
              />

              <div className="flex gap-4">
                <Button
                  onClick={handleStartBooking}
                  disabled={isBooking}
                  className="flex-1"
                  size="lg"
                >
                  {isBooking ? 'Booking...' : 'Start Booking'}
                </Button>
                <Button
                  onClick={handleStopBooking}
                  disabled={!isBooking}
                  variant="destructive"
                  className="flex-1"
                  size="lg"
                >
                  Stop Retrying
                </Button>
              </div>

              <StatusBar status={status} />
            </div>
          </div>
        </TabsContent>

        {/* Multi-Booking Tab - Advanced Operations */}
        <TabsContent value="multi" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Multi-Booking Configuration</CardTitle>
              <p className="text-sm text-muted-foreground mt-2">
                Configure priority-based booking across multiple accounts with divide & conquer strategy
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Priority Configuration */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Location Priority</h3>
                <p className="text-sm text-muted-foreground">
                  Locations will be attempted in this order until successful
                </p>
                <div className="flex gap-2 items-center">
                  <Badge variant="default">1. X1</Badge>
                  <span className="text-muted-foreground">→</span>
                  <Badge variant="secondary">2. X3</Badge>
                  <span className="text-muted-foreground">→</span>
                  <Badge variant="outline">3. Fitness</Badge>
                </div>
              </div>

              {/* Account Selection */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Account Allocation</h3>
                <p className="text-sm text-muted-foreground">
                  Select accounts to participate in multi-booking sniping
                </p>
                <AccountSwitcher
                  currentAccountId={selectedAccountId}
                  onAccountChange={(account) => setSelectedAccountId(account.id)}
                  showStats={true}
                />
              </div>

              {/* Consecutive Hours */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Consecutive Hours</h3>
                <p className="text-sm text-muted-foreground">
                  Number of consecutive hours to book (3 hours = 3 slots)
                </p>
                <div className="flex gap-2">
                  {[1, 2, 3].map((hours) => (
                    <Button
                      key={hours}
                      variant={selectedTimes.length === hours ? "default" : "outline"}
                      onClick={() => setSelectedTimes(Array(hours).fill('').map((_, i) => `${13 + i}:00`))}
                    >
                      {hours} {hours === 1 ? 'Hour' : 'Hours'}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Start Time */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Start Time</h3>
                <EnhancedCalendar 
                  selectedDate={selectedDate} 
                  onDateChange={setSelectedDate} 
                />
              </div>

              {/* Sub-location Strategy */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Sub-location Strategy</h3>
                <p className="text-sm text-muted-foreground">
                  Divide & Conquer: Split accounts across X1-A, X1-B, X3-A, X3-B
                </p>
                <div className="grid grid-cols-2 gap-2">
                  <Badge variant="outline">Auto-allocate accounts</Badge>
                  <Badge variant="outline">Maximize coverage</Badge>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4 border-t">
                <Button className="flex-1" size="lg">
                  Start Multi-Booking Snipe
                </Button>
                <Button variant="outline" size="lg">
                  Schedule for Unlock Time
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Account Management Tab */}
        <TabsContent value="accounts" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <AccountSwitcher
                currentAccountId={selectedAccountId}
                onAccountChange={(account) => setSelectedAccountId(account.id)}
                showStats={true}
              />
            </div>
            <div>
              {selectedAccountId && (
                <AccountStats accountId={selectedAccountId} />
              )}
            </div>
          </div>
        </TabsContent>

        {/* Booking History Tab */}
        <TabsContent value="history">
          <BookingHistory accountId={selectedAccountId} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
