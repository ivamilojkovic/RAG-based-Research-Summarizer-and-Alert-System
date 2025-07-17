// components/AlertCard.tsx

import React from 'react';

export interface AlertProps {
  title: string;
  summary: string;
  link: string;
  code?: string | null;
  source: string;
  published?: string;
}

const AlertCard: React.FC<{ alert: AlertProps }> = ({ alert }) => {
  return (
    <div className="p-4 border rounded-lg shadow-sm mb-4 bg-white">
      <h2 className="text-xl font-semibold mb-2">{alert.title}</h2>
      <p className="mb-2 text-gray-800">{alert.summary}</p>
      <p className="text-sm text-gray-500 mb-1">Source: {alert.source}</p>
      {alert.published && <p className="text-sm text-gray-500 mb-1">Published: {alert.published}</p>}
      <div className="mt-2 space-x-4">
        <a
          href={alert.link}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          Read Paper
        </a>
        {alert.code && (
          <a
            href={alert.code}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            Code
          </a>
        )}
      </div>
    </div>
  );
};

export default AlertCard;
