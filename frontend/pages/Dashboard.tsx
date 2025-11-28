import React, { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { User, AuthSession, SortConfig } from '../types';
import { Button } from '../components/Button';
import { ExcelUploader } from '../components/ExcelUploader';
import { Sidebar } from '../components/Sidebar';
import { StatsCards } from '../components/StatsCards';
import { UpdateEmployeeModal } from '../components/UpdateEmployeeModal';
import {
  Search,
  Plus,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Calendar,
  Briefcase,
  Pencil,
  Trash2
} from 'lucide-react';
import { authService } from '../services/authService';

interface DashboardProps {
  session: AuthSession;
}

const PAGE_SIZE = 10;

export const Dashboard: React.FC<DashboardProps> = ({ session }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [sort, setSort] = useState<SortConfig>({ key: 'created_at', direction: 'desc' });
  const [showUpload, setShowUpload] = useState(false);

  // New State
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [newJoinersCount, setNewJoinersCount] = useState(0);

  const fetchStats = async () => {
    try {
      const now = new Date();
      const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString();

      const { count, error } = await supabase
        .from('users')
        .select('*', { count: 'exact', head: true })
        .gte('created_at', firstDayOfMonth);

      if (error) throw error;
      setNewJoinersCount(count || 0);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const from = (page - 1) * PAGE_SIZE;
      const to = from + PAGE_SIZE - 1;

      let query = supabase
        .from('users')
        .select('*', { count: 'exact' });

      // Apply Search
      if (searchQuery) {
        query = query.or(`name.ilike.%${searchQuery}%,email.ilike.%${searchQuery}%`);
      }

      // Apply Sort
      query = query.order(sort.key, { ascending: sort.direction === 'asc' });

      // Apply Pagination
      query = query.range(from, to);

      const { data, error, count } = await query;

      if (error) throw error;

      setUsers(data || []);
      setTotalCount(count || 0);
    } catch (err) {
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    // Debounce search
    const timer = setTimeout(() => {
      fetchUsers();
    }, 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, searchQuery, sort]);

  const handleSort = (key: keyof User) => {
    setSort(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const handleUpdateClick = (user: User) => {
    setSelectedUser(user);
    setShowUpdateModal(true);
  };

  const handleSaveUpdate = async (updatedUser: User) => {
    if (!updatedUser.id) return;

    try {
      const { error } = await supabase
        .from('users')
        .update({
          name: updatedUser.name,
          email: updatedUser.email,
          phone_number: updatedUser.phone_number,
          branch: updatedUser.branch,
          department: updatedUser.department,
          dob: updatedUser.dob,
          context: updatedUser.context
        })
        .eq('id', updatedUser.id);

      if (error) throw error;

      // Refresh list
      fetchUsers();
    } catch (error) {
      console.error('Error updating user:', error);
      throw error;
    }
  };

  const handleDeleteClick = async (userId: string) => {
    if (window.confirm('Are you sure you want to delete this employee? This action cannot be undone.')) {
      try {
        const { error } = await supabase
          .from('users')
          .delete()
          .eq('id', userId);

        if (error) throw error;

        // Refresh list
        fetchUsers();
        fetchStats();
      } catch (error) {
        console.error('Error deleting user:', error);
        alert('Failed to delete user');
      }
    }
  };

  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onLogout={authService.logout}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header (Mobile only or simplified) */}
        <header className="bg-white border-b md:hidden sticky top-0 z-30">
          <div className="px-4 h-16 flex justify-between items-center">
            <span className="font-bold text-lg">Admin Portal</span>
            {/* Mobile menu button could go here */}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">

            {/* Stats Cards */}
            <StatsCards totalEmployees={totalCount} newJoinersCount={newJoinersCount} />

            {/* Actions Bar */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <div className="relative w-full sm:w-96">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Search by name or email..."
                  className="w-full pl-10 pr-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Button onClick={() => setShowUpload(true)}>
                <Plus size={20} />
                Upload Excel
              </Button>
            </div>

            {/* Table Container */}
            <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {[
                        { key: 'id', label: 'ID' },
                        { key: 'name', label: 'User' },
                        { key: 'email', label: 'Email' },
                        { key: 'phone_number', label: 'Phone' },
                        { key: 'department', label: 'Department' },
                        { key: 'branch', label: 'Branch' },
                        { key: 'dob', label: 'Date of Birth' },
                        { key: 'created_at', label: 'Joined' },
                      ].map((col) => (
                        <th
                          key={col.key}
                          onClick={() => handleSort(col.key as keyof User)}
                          className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                        >
                          <div className="flex items-center gap-2">
                            {col.label}
                            {sort.key === col.key ? (
                              sort.direction === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                            ) : <ArrowUpDown size={14} className="opacity-30" />}
                          </div>
                        </th>
                      ))}
                      <th className="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {loading ? (
                      Array.from({ length: 5 }).map((_, i) => (
                        <tr key={i} className="animate-pulse">
                          <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-16"></div></td>
                          <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-32"></div></td>
                          <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-32"></div></td>
                          <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-24"></div></td>
                          <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-24"></div></td>
                          <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-20"></div></td>
                          <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-24"></div></td>
                          <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-24"></div></td>
                          <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-16"></div></td>
                        </tr>
                      ))
                    ) : users.length === 0 ? (
                      <tr>
                        <td colSpan={9} className="px-6 py-12 text-center text-gray-500">
                          No users found. Try searching or uploading an Excel file.
                        </td>
                      </tr>
                    ) : (
                      users.map((user, index) => (
                        <tr key={user.id || index} className="hover:bg-green-50 transition-colors group">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono text-xs">
                            {user.id ? `${String(user.id).slice(0, 8)}...` : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="flex-shrink-0 h-10 w-10 bg-primary-light text-primary rounded-full flex items-center justify-center font-bold">
                                {(user.name || '?').charAt(0).toUpperCase()}
                              </div>
                              <div className="ml-4">
                                <div className="text-sm font-medium text-gray-900 group-hover:text-primary-dark transition-colors">{user.name || 'Unknown User'}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {user.email || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {user.phone_number || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              <Briefcase size={12} className="mr-1" />
                              {user.department || '-'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {user.branch || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <div className="flex items-center">
                              <Calendar size={14} className="mr-2 text-gray-400" />
                              {user.dob || '-'}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end gap-2">
                              <button
                                onClick={() => handleUpdateClick(user)}
                                className="text-blue-600 hover:text-blue-900 p-1 hover:bg-blue-50 rounded"
                                title="Edit"
                              >
                                <Pencil size={16} />
                              </button>
                              <button
                                onClick={() => user.id && handleDeleteClick(user.id)}
                                className="text-red-600 hover:text-red-900 p-1 hover:bg-red-50 rounded"
                                title="Delete"
                              >
                                <Trash2 size={16} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="bg-white px-4 py-3 border-t border-gray-200 flex items-center justify-between sm:px-6">
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Showing <span className="font-medium">{Math.min(totalCount, (page - 1) * PAGE_SIZE + 1)}</span> to <span className="font-medium">{Math.min(totalCount, page * PAGE_SIZE)}</span> of <span className="font-medium">{totalCount}</span> results
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                      <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        <ChevronLeft size={20} />
                      </button>
                      <button
                        className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-primary hover:bg-gray-50"
                      >
                        {page}
                      </button>
                      <button
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page >= totalPages}
                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        <ChevronRight size={20} />
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Upload Modal */}
        {showUpload && (
          <ExcelUploader
            onClose={() => setShowUpload(false)}
            onSuccess={() => {
              setShowUpload(false);
              fetchUsers();
            }}
          />
        )}

        {/* Update Modal */}
        {selectedUser && (
          <UpdateEmployeeModal
            user={selectedUser}
            isOpen={showUpdateModal}
            onClose={() => {
              setShowUpdateModal(false);
              setSelectedUser(null);
            }}
            onSave={handleSaveUpdate}
          />
        )}
      </div>
    </div>
  );
};