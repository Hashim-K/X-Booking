"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Stats {
  total_bookings: number;
  confirmed_bookings: number;
  failed_bookings: number;
  total_attempts: number;
  success_rate: number;
}

interface AccountStatsProps {
  accountId: number;
  compact?: boolean;
}

export default function AccountStats({ accountId, compact = false }: AccountStatsProps) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accountId]);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/accounts/${accountId}/stats`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch stats');
      }

      setStats(data.stats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-2">
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 text-sm">
        Error loading stats
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  if (compact) {
    return (
      <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
        <div>
          <span>Bookings:</span>
          <span className="ml-1 font-medium text-foreground">{stats.total_bookings}</span>
        </div>
        <div>
          <span>Success:</span>
          <span className="ml-1 font-medium text-foreground">{stats.success_rate}%</span>
        </div>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Account Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Total Bookings */}
          <Card className="bg-blue-50 dark:bg-blue-950">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Total Bookings</div>
              <div className="text-2xl font-bold">{stats.total_bookings}</div>
            </CardContent>
          </Card>

          {/* Confirmed */}
          <Card className="bg-green-50 dark:bg-green-950">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Confirmed</div>
              <div className="text-2xl font-bold text-green-600">{stats.confirmed_bookings}</div>
            </CardContent>
          </Card>

          {/* Failed */}
          <Card className="bg-red-50 dark:bg-red-950">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Failed</div>
              <div className="text-2xl font-bold text-red-600">{stats.failed_bookings}</div>
            </CardContent>
          </Card>

          {/* Success Rate */}
          <Card className="bg-purple-50 dark:bg-purple-950">
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground mb-1">Success Rate</div>
              <div className="text-2xl font-bold text-purple-600">{stats.success_rate}%</div>
            </CardContent>
          </Card>
        </div>

        {/* Additional Info */}
        <div className="mt-4 pt-4 border-t text-sm text-muted-foreground">
          <div>Total Attempts: <span className="font-medium text-foreground">{stats.total_attempts}</span></div>
        </div>
      </CardContent>
    </Card>
  );
}
