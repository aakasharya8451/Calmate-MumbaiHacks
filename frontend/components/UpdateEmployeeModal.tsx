import React, { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';
import { Button } from './Button';
import { Input } from './Input';
import { User } from '../types';

interface UpdateEmployeeModalProps {
    user: User;
    isOpen: boolean;
    onClose: () => void;
    onSave: (updatedUser: User) => Promise<void>;
}

export const UpdateEmployeeModal: React.FC<UpdateEmployeeModalProps> = ({ user, isOpen, onClose, onSave }) => {
    const [formData, setFormData] = useState<User>(user);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setFormData(user);
    }, [user]);

    if (!isOpen) return null;

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await onSave(formData);
            onClose();
        } catch (error) {
            console.error('Failed to update user', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl relative max-h-[90vh] overflow-y-auto">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
                >
                    <X size={24} />
                </button>

                <div className="p-6 border-b">
                    <h2 className="text-2xl font-bold text-gray-800">Update Employee</h2>
                    <p className="text-sm text-gray-500">Edit the details below to update the employee record.</p>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <Input
                            label="Full Name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                        />
                        <Input
                            label="Email Address"
                            name="email"
                            type="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                        <Input
                            label="Phone Number"
                            name="phone_number"
                            value={formData.phone_number}
                            onChange={handleChange}
                        />
                        <Input
                            label="Date of Birth"
                            name="dob"
                            type="date"
                            value={formData.dob || ''}
                            onChange={handleChange}
                        />
                        <Input
                            label="Department"
                            name="department"
                            value={formData.department}
                            onChange={handleChange}
                        />
                        <Input
                            label="Branch"
                            name="branch"
                            value={formData.branch}
                            onChange={handleChange}
                        />
                        <div className="md:col-span-2">
                            <Input
                                label="Context / Notes"
                                name="context"
                                value={formData.context || ''}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-4 border-t">
                        <Button type="button" variant="ghost" onClick={onClose} disabled={loading}>
                            Cancel
                        </Button>
                        <Button type="submit" isLoading={loading}>
                            <Save size={18} className="mr-2" />
                            Save Changes
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
};
