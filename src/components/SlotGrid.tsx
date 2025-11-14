"use client";

import { useState, useEffect } from 'react';

interface Slot {
  id: number;
  time: string;
  time_slot: string;
  is_available: boolean;
  remaining_capacity: number | null;
  total_capacity: number | null;
  last_checked: string;
}

interface SlotGridProps {
  location: string;
  date: string;
  onSlotClick?: (slot: Slot) => void;
}

export default function SlotGrid({ location, date, onSlotClick }: SlotGridProps) {
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  const fetchSlots = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        location,
        date,
        forceRefresh: forceRefresh.toString(),
      });

      const response = await fetch(`/api/slots/available?${params}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch slots');
      }

      setSlots(data.slots);
      setLastUpdate(data.timestamp);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSlots();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location, date]);

  const getSlotColor = (slot: Slot) => {
    if (!slot.is_available) {
      return 'bg-red-100 border-red-300 text-red-700 cursor-not-allowed';
    }
    if (slot.remaining_capacity !== null && slot.remaining_capacity <= 3) {
      return 'bg-yellow-100 border-yellow-300 text-yellow-700 hover:bg-yellow-200 cursor-pointer';
    }
    return 'bg-green-100 border-green-300 text-green-700 hover:bg-green-200 cursor-pointer';
  };

  const formatTime = (timeStr: string) => {
    // Convert "13:00:00" to "13:00"
    return timeStr.substring(0, 5);
  };

  const formatLastUpdate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  if (loading && slots.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 font-medium">Error loading slots</p>
        <p className="text-red-600 text-sm mt-1">{error}</p>
        <button
          onClick={() => fetchSlots()}
          className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">
            {location} - {date}
          </h3>
          {lastUpdate && (
            <p className="text-sm text-gray-500">
              Last updated: {formatLastUpdate(lastUpdate)}
            </p>
          )}
        </div>
        <button
          onClick={() => fetchSlots(true)}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
              Refreshing...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </>
          )}
        </button>
      </div>

      {/* Legend */}
      <div className="flex gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-100 border border-green-300 rounded"></div>
          <span>Available</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-100 border border-yellow-300 rounded"></div>
          <span>Limited (≤3 spots)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-100 border border-red-300 rounded"></div>
          <span>Unavailable</span>
        </div>
      </div>

      {/* Slot Grid */}
      {slots.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No slots found for this date
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {slots.map((slot) => (
            <button
              key={slot.id}
              onClick={() => slot.is_available && onSlotClick?.(slot)}
              disabled={!slot.is_available}
              className={`
                p-4 rounded-lg border-2 transition-all
                ${getSlotColor(slot)}
              `}
            >
              <div className="font-semibold text-lg">
                {formatTime(slot.time_slot)}
              </div>
              {slot.remaining_capacity !== null && (
                <div className="text-xs mt-1">
                  {slot.remaining_capacity} / {slot.total_capacity || '?'} spots
                </div>
              )}
              {!slot.is_available && (
                <div className="text-xs mt-1">Full</div>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Stats */}
      <div className="text-sm text-gray-600 pt-4 border-t">
        <span className="font-medium">
          {slots.filter(s => s.is_available).length} / {slots.length}
        </span>
        {' '}slots available
      </div>
    </div>
  );
}
