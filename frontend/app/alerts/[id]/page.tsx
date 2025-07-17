'use client';

import useSWR from 'swr';
import { use } from 'react';
import AlertCard from '@/components/AlertCard';

interface AlertProps {
  title: string;
  summary: string;
  link: string;
  code?: string | null;
  source: string;
  published?: string;
}

interface AlertData {
  summary: string | AlertProps[]; // summary might still be a string when fetched
}

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function AlertDetails({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const { data, error } = useSWR<AlertData>(id ? `/api/alerts/${id}` : null, fetcher, {
    refreshInterval: 5000,
  });

  if (error) return <p>Error loading alert.</p>;
  if (!data) return <p>Loading...</p>;

  // Ensure summary is parsed before mapping
  let parsedSummary: AlertProps[] = [];
  try {
    parsedSummary = typeof data.summary === 'string'
      ? JSON.parse(data.summary)
      : data.summary;
  } catch {
    return <p>Failed to parse summary</p>;
  }

  return (
    <div className="max-w-3xl mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-6">Alert Details for {id}</h1>
      {parsedSummary.map((item, idx) => (
        <AlertCard key={idx} alert={item} />
      ))}
    </div>
  );
}
