'use client';

import { useState, useEffect } from 'react';

export default function Home() {
  const [backendStatus, setBackendStatus] = useState('checking...');

  // Use environment variable if set, otherwise use empty string for relative URLs
  const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

  useEffect(() => {
    fetch(`${API_URL}/api/health`)
      .then((res) => res.json())
      .then((data) => {
        setBackendStatus(data.message || 'Error connecting');
      })
      .catch(() => {
        setBackendStatus('Failed to connect to backend');
      });
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Multi-Modal RAG System</h1>
        <p className="text-lg text-gray-400">
          Backend Status: <span className="font-semibold text-green-400">{backendStatus}</span>
        </p>
      </div>
    </main>
  );
}