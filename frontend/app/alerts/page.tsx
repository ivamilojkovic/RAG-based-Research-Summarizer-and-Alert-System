'use client'

import { useRouter } from 'next/navigation';
import useSWR from 'swr';

interface Alert {
  id: string
  query: string
  period: number
  status: string;
}

const fetcher = (url: string) => fetch(url).then(res => res.json());

const AlertsPage = () => {
  const { data: alerts, mutate } = useSWR('/api/alerts', fetcher);
  const router = useRouter();

  const deleteAlert = async (id: string) => {
    await fetch(`/api/alerts/${id}`, { method: 'DELETE' });
    mutate();
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">My Alerts</h1>
      <table className="w-full border">
        <thead>
          <tr>
            <th className="p-2 border">Query</th>
            <th className="p-2 border">Period (days)</th>
            <th className="p-2 border">Status</th>
            <th className="p-2 border">Actions</th>
          </tr>
        </thead>
        <tbody>
          {alerts?.map((alert: Alert) => (
            <tr key={alert.id}>
              <td className="p-2 border">{alert.query}</td>
              <td className="p-2 border">{alert.period}</td>
              <td className="p-2 border capitalize">{alert.status}</td>
              <td className="p-2 border">
                <button
                  className="text-blue-500 mr-2"
                  onClick={() => router.push(`/alerts/${alert.id}`)}
                >
                  View
                </button>
                <button
                  className="text-red-500"
                  onClick={() => deleteAlert(alert.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AlertsPage;