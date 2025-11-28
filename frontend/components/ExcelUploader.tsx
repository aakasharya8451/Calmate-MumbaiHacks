import React, { useRef, useState } from 'react';
import * as XLSX from 'xlsx';
import { Upload, X, FileSpreadsheet, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from './Button';
import { User, ExcelRow } from '../types';
import { supabase } from '../lib/supabase';

interface ExcelUploaderProps {
  onSuccess: () => void;
  onClose: () => void;
}

export const ExcelUploader: React.FC<ExcelUploaderProps> = ({ onSuccess, onClose }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<User[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadStats, setUploadStats] = useState<{ success: number; failed: number } | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.match(/\.(xlsx|csv)$/)) {
        setError('Please select a valid Excel (.xlsx) or CSV file.');
        return;
      }
      setFile(selectedFile);
      setError(null);
      parseFile(selectedFile);
    }
  };

  const parseFile = async (f: File) => {
    try {
      const data = await f.arrayBuffer();
      const workbook = XLSX.read(data);
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json<ExcelRow>(worksheet);

      // Transform and validate
      const users: User[] = jsonData.map((row) => {
        let dob = row.dob;
        // Handle Excel Serial Date
        if (typeof dob === 'number') {
           const date = new Date((dob - (25567 + 2)) * 86400 * 1000);
           dob = date.toISOString().split('T')[0];
        }

        return {
          name: row.name || '',
          email: row.email || '',
          phone_number: String(row.phone_number || ''),
          branch: row.branch || '',
          department: row.department || '',
          context: row.context || '',
          dob: String(dob || ''),
        };
      }).filter(u => u.name && u.email); // Basic filter

      if (users.length === 0) {
        setError("No valid rows found. Check column headers: name, email, phone_number, etc.");
      } else {
        setPreview(users.slice(0, 5)); // Show first 5 as preview
      }
    } catch (err) {
      setError("Failed to parse file. Ensure it is a valid Excel file.");
      console.error(err);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsProcessing(true);
    setUploadStats(null);
    setError(null);

    try {
      // Re-parse to get all data (in case we only previewed a slice, though we parsed all above)
      // For efficiency, we already parsed. Let's just re-read the buffer if we needed to, but we can store the parsed data in state if it's not huge.
      // For this demo, let's re-parse to be safe or assuming 'preview' was just a subset.
      
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data);
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<ExcelRow>(sheet);
      
      const validUsers: User[] = rows.map((row) => {
         let dob = row.dob;
         if (typeof dob === 'number') {
           const date = new Date((dob - (25567 + 2)) * 86400 * 1000);
           dob = date.toISOString().split('T')[0];
         }
         return {
          name: row.name,
          email: row.email,
          phone_number: String(row.phone_number || ''),
          branch: row.branch,
          department: row.department,
          context: row.context,
          dob: String(dob || '')
         }
      }).filter(u => u.email && u.name);

      // Bulk insert in chunks
      const CHUNK_SIZE = 100;
      let successCount = 0;
      let failCount = 0;

      for (let i = 0; i < validUsers.length; i += CHUNK_SIZE) {
        const chunk = validUsers.slice(i, i + CHUNK_SIZE);
        const { error: insertError } = await supabase.from('users').insert(chunk);
        
        if (insertError) {
          console.error('Batch error:', insertError);
          failCount += chunk.length;
        } else {
          successCount += chunk.length;
        }
      }

      setUploadStats({ success: successCount, failed: failCount });
      if (successCount > 0) {
        setTimeout(() => {
            onSuccess();
        }, 1500);
      }
    } catch (err) {
      setError("An unexpected error occurred during upload.");
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg p-6 relative">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <X size={24} />
        </button>

        <h2 className="text-2xl font-bold text-gray-800 mb-2">Import Users</h2>
        <p className="text-gray-500 mb-6 text-sm">
          Upload an .xlsx or .csv file. Required columns: name, email, phone_number, branch, department, context, dob.
        </p>

        {!file ? (
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-10 flex flex-col items-center justify-center cursor-pointer hover:border-primary hover:bg-primary-light transition-all group"
          >
            <Upload className="text-gray-400 group-hover:text-primary mb-3" size={48} />
            <p className="text-gray-600 font-medium group-hover:text-primary">Click to select file</p>
            <p className="text-gray-400 text-xs mt-1">XLSX or CSV</p>
            <input 
              ref={fileInputRef}
              type="file" 
              accept=".xlsx,.csv" 
              className="hidden"
              onChange={handleFileSelect}
            />
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between bg-gray-50 p-3 rounded-lg border">
              <div className="flex items-center gap-3">
                <FileSpreadsheet className="text-primary" />
                <div>
                  <p className="font-medium text-sm text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
              <button 
                onClick={() => { setFile(null); setPreview([]); setError(null); setUploadStats(null); }}
                className="text-red-500 hover:text-red-700 text-sm font-medium"
              >
                Change
              </button>
            </div>

            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm flex items-start gap-2">
                <AlertCircle size={16} className="mt-0.5" />
                {error}
              </div>
            )}

            {preview.length > 0 && !uploadStats && (
              <div className="border rounded-lg overflow-hidden">
                <div className="bg-gray-100 px-3 py-2 text-xs font-semibold text-gray-600">
                  Preview (First {preview.length} rows)
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-xs text-left">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2">Name</th>
                        <th className="px-3 py-2">Email</th>
                        <th className="px-3 py-2">Branch</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {preview.map((row, i) => (
                        <tr key={i}>
                          <td className="px-3 py-2">{row.name}</td>
                          <td className="px-3 py-2">{row.email}</td>
                          <td className="px-3 py-2">{row.branch}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {uploadStats && (
              <div className={`p-4 rounded-lg flex flex-col items-center justify-center gap-2 ${uploadStats.failed === 0 ? 'bg-green-50 text-green-700' : 'bg-orange-50 text-orange-700'}`}>
                {uploadStats.failed === 0 ? <CheckCircle size={32} /> : <AlertCircle size={32} />}
                <p className="font-semibold">
                  Processed: {uploadStats.success + uploadStats.failed}
                </p>
                <p className="text-sm">
                  Success: {uploadStats.success} | Failed: {uploadStats.failed}
                </p>
                {uploadStats.failed > 0 && <p className="text-xs mt-2">Check console for error details.</p>}
              </div>
            )}

            <div className="flex justify-end gap-3 pt-4">
               <Button variant="ghost" onClick={onClose} disabled={isProcessing}>Cancel</Button>
               {!uploadStats && (
                 <Button onClick={handleUpload} isLoading={isProcessing} disabled={!!error || preview.length === 0}>
                   Import Data
                 </Button>
               )}
               {uploadStats && (
                 <Button onClick={onSuccess}>Done</Button>
               )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};