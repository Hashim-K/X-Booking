"use client";

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

interface Booking {
  id: number;
  booking_date: string;
  time_slot: string;
  location: string;
  sub_location: string | null;
  status: 'pending' | 'confirmed' | 'failed' | 'cancelled';
  booking_reference: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

interface BookingHistoryProps {
  accountId?: number;
}

export default function BookingHistory({ 
  accountId
}: BookingHistoryProps) {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterDate, setFilterDate] = useState<string>('');

  useEffect(() => {
    fetchBookings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accountId, filterStatus, filterDate]);

  const fetchBookings = async () => {
    setLoading(true);
    setError(null);

    try {
      let url = accountId 
        ? `/api/accounts/${accountId}/bookings`
        : '/api/bookings';

      const params = new URLSearchParams();
      if (filterStatus !== 'all') params.append('status', filterStatus);
      if (filterDate) params.append('date', filterDate);

      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await fetch(url);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch bookings');
      }

      setBookings(data.bookings || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelBooking = async (bookingId: number) => {
    if (!confirm('Are you sure you want to cancel this booking?')) {
      return;
    }

    try {
      const response = await fetch(`/api/bookings/${bookingId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to cancel booking');
      }

      fetchBookings();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to cancel booking');
    }
  };

  const getStatusColor = (status: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      case 'confirmed':
        return 'default';
      case 'pending':
        return 'secondary';
      case 'failed':
        return 'destructive';
      case 'cancelled':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString();
  };

  const formatTime = (timeStr: string) => {
    // Convert "13:00:00" to "13:00"
    return timeStr.substring(0, 5);
  };

  if (loading && bookings.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header & Filters */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <h3 className="text-lg font-semibold">Booking History</h3>
        <div className="flex gap-2">
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="confirmed">Confirmed</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
            </SelectContent>
          </Select>
          <Input
            type="date"
            value={filterDate}
            onChange={(e) => setFilterDate(e.target.value)}
            className="w-[180px]"
          />
        </div>
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">Error: {error}</p>
            <Button
              onClick={fetchBookings}
              variant="ghost"
              className="mt-2 text-sm"
            >
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Bookings Table */}
      {bookings.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            No bookings found
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Reference</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {bookings.map((booking) => (
                  <TableRow key={booking.id}>
                    <TableCell>{formatDate(booking.booking_date)}</TableCell>
                    <TableCell className="font-mono">{formatTime(booking.time_slot)}</TableCell>
                    <TableCell>
                      <div>
                        <span className="font-medium">{booking.location}</span>
                        {booking.sub_location && (
                          <span className="ml-1 text-sm text-muted-foreground">
                            ({booking.sub_location})
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusColor(booking.status)}>
                        {booking.status.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {booking.booking_reference || '-'}
                    </TableCell>
                    <TableCell>
                      {booking.status === 'confirmed' && (
                        <Button
                          onClick={() => handleCancelBooking(booking.id)}
                          variant="destructive"
                          size="sm"
                        >
                          Cancel
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Summary */}
      <div className="text-sm text-muted-foreground pt-4 border-t">
        <span className="font-medium">{bookings.length}</span> booking(s) found
        {filterStatus !== 'all' && (
          <span> • Filtered by: <span className="font-medium">{filterStatus}</span></span>
        )}
      </div>
    </div>
  );
}
