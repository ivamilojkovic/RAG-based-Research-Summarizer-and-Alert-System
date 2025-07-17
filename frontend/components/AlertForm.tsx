'use client'

import { useRouter } from 'next/navigation';
import React, { useState } from 'react'

const AlertForm = () => {
    const [query, setQuery] = useState('');
    const [period, setPeriod] = useState(7);
    const router = useRouter();
  
    const createAlert = async () => {
      await fetch('/api/alerts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, period })
      });
      router.push('/alerts');
    };
  
    return (
      <div className="max-w-2xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Create Research Alert</h1>
        <input
          className="w-full p-2 border mb-4"
          placeholder="Enter your query..."
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <div className="mb-4">
          {[7, 14, 30].map(days => (
            <label key={days} className="mr-4">
              <input
                type="radio"
                name="period"
                value={days}
                checked={period === days}
                onChange={() => setPeriod(days)}
              />{' '}
              Last {days} days
            </label>
          ))}
        </div>
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded"
          onClick={createAlert}
        >
          Create Alert
        </button>
      </div>
    );
}

export default AlertForm