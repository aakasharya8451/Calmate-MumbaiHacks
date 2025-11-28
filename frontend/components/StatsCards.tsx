import React from 'react';
import { Users, UserPlus, Building2, TrendingUp } from 'lucide-react';

interface StatsCardsProps {
    totalEmployees: number;
    newJoinersCount: number;
}

export const StatsCards: React.FC<StatsCardsProps> = ({ totalEmployees, newJoinersCount }) => {
    const stats = [
        {
            label: 'Total Employees',
            value: totalEmployees,
            icon: Users,
            color: 'bg-blue-500',
            trend: '+12% from last month'
        },
        {
            label: 'New Joiners',
            value: newJoinersCount,
            icon: UserPlus,
            color: 'bg-green-500',
            trend: 'This Month'
        },
        {
            label: 'Active Rate',
            value: '94%', // Mock data
            icon: TrendingUp,
            color: 'bg-orange-500',
            trend: '+2% from last month'
        }
    ];

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, index) => {
                const Icon = stat.icon;
                return (
                    <div key={index} className="bg-white rounded-xl shadow-sm border p-6 transition-transform hover:scale-105">
                        <div className="flex items-center justify-between mb-4">
                            <div className={`p-3 rounded-lg ${stat.color} bg-opacity-10`}>
                                <Icon className={`w-6 h-6 ${stat.color.replace('bg-', 'text-')}`} />
                            </div>
                            <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full">
                                {stat.trend}
                            </span>
                        </div>
                        <h3 className="text-3xl font-bold text-gray-800 mb-1">{stat.value}</h3>
                        <p className="text-sm text-gray-500">{stat.label}</p>
                    </div>
                );
            })}
        </div>
    );
};
