"use client";

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Trash2 } from 'lucide-react';

interface Account {
  id: number;
  netid: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Stats {
  total_bookings: number;
  confirmed_bookings: number;
  failed_bookings: number;
  total_attempts: number;
  success_rate: number;
}

interface AccountSwitcherProps {
  currentAccountId?: number;
  onAccountChange?: (account: Account) => void;
  showStats?: boolean;
}

export default function AccountSwitcher({ 
  currentAccountId, 
  onAccountChange,
  showStats = false 
}: AccountSwitcherProps) {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [accountStats, setAccountStats] = useState<Record<number, Stats>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchAccounts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (currentAccountId && accounts.length > 0) {
      const account = accounts.find(a => a.id === currentAccountId);
      if (account) {
        setSelectedAccount(account);
      }
    }
  }, [currentAccountId, accounts]);

  const fetchAccounts = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/accounts?isActive=true');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch accounts');
      }

      setAccounts(data.accounts);

      // Fetch stats if needed
      if (showStats) {
        for (const account of data.accounts) {
          fetchAccountStats(account.id);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const fetchAccountStats = async (accountId: number) => {
    try {
      const response = await fetch(`/api/accounts/${accountId}/stats`);
      const data = await response.json();

      if (response.ok) {
        setAccountStats(prev => ({
          ...prev,
          [accountId]: data.stats
        }));
      }
    } catch (err) {
      console.error(`Failed to fetch stats for account ${accountId}:`, err);
    }
  };

  const handleAccountSelect = (account: Account) => {
    setSelectedAccount(account);
    onAccountChange?.(account);
  };

  const handleAddAccount = async (netid: string, password: string) => {
    try {
      const response = await fetch('/api/accounts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ netid, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to add account');
      }

      setShowAddForm(false);
      fetchAccounts();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to add account');
    }
  };

  const handleDeleteAccount = async (accountId: number) => {
    if (!confirm('Are you sure you want to delete this account?')) {
      return;
    }

    try {
      const response = await fetch(`/api/accounts/${accountId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to delete account');
      }

      fetchAccounts();
      if (selectedAccount?.id === accountId) {
        setSelectedAccount(null);
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete account');
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-10 bg-muted rounded"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive">
        <CardContent className="pt-6">
          <p className="text-destructive">Error: {error}</p>
          <Button
            onClick={fetchAccounts}
            variant="ghost"
            className="mt-2 text-sm"
          >
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Accounts</h3>
        <Button
          onClick={() => setShowAddForm(!showAddForm)}
          variant={showAddForm ? "outline" : "default"}
        >
          {showAddForm ? 'Cancel' : '+ Add Account'}
        </Button>
      </div>

      {/* Add Account Form */}
      {showAddForm && (
        <AddAccountForm
          onSubmit={handleAddAccount}
          onCancel={() => setShowAddForm(false)}
        />
      )}

      {/* Account List */}
      {accounts.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            No accounts found. Add one to get started.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3">
          {accounts.map((account) => {
            const isSelected = selectedAccount?.id === account.id;
            const stats = accountStats[account.id];

            return (
              <Card
                key={account.id}
                className={`cursor-pointer transition-all ${
                  isSelected ? 'border-primary border-2' : 'hover:border-primary/50'
                }`}
                onClick={() => handleAccountSelect(account)}
              >
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold text-lg">{account.netid}</h4>
                        {isSelected && (
                          <Badge>Active</Badge>
                        )}
                      </div>
                      
                      {showStats && stats && (
                        <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                          <div>
                            <span>Bookings:</span>
                            <span className="ml-1 font-medium text-foreground">{stats.total_bookings}</span>
                          </div>
                          <div>
                            <span>Success Rate:</span>
                            <span className="ml-1 font-medium text-foreground">{stats.success_rate}%</span>
                          </div>
                        </div>
                      )}
                    </div>

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteAccount(account.id);
                      }}
                      className="ml-4 text-destructive hover:text-destructive hover:bg-destructive/10"
                      title="Delete account"
                    >
                      <Trash2 className="h-5 w-5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

interface AddAccountFormProps {
  onSubmit: (netid: string, password: string) => void;
  onCancel: () => void;
}

function AddAccountForm({ onSubmit, onCancel }: AddAccountFormProps) {
  const [netid, setNetid] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (netid && password) {
      onSubmit(netid, password);
      setNetid('');
      setPassword('');
    }
  };

  return (
    <Card className="border-primary">
      <CardHeader>
        <CardTitle>Add New Account</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="netid">NetID</Label>
            <Input
              id="netid"
              type="text"
              value={netid}
              onChange={(e) => setNetid(e.target.value)}
              placeholder="Enter NetID"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>
          <div className="flex gap-2">
            <Button type="submit" className="flex-1">
              Add Account
            </Button>
            <Button type="button" onClick={onCancel} variant="outline">
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
