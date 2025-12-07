"use client";

import React, { use } from "react";
import { DealRenderer } from "@/lib/deal-renderer";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { useDealState } from "@/lib/hooks/useDealState";

interface DealPageProps {
  params: Promise<{ id: string }>;
}

export default function DealPage({ params }: DealPageProps) {
  const { id } = use(params);
  const { data, isLoading, error, refetch } = useDealState(id);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mb-4 mx-auto"></div>
          <p className="text-gray-600">Loading deal...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="max-w-md p-6 bg-red-50 border border-red-200 rounded-lg">
          <h2 className="text-lg font-semibold text-red-900 mb-2">
            Error Loading Deal
          </h2>
          <p className="text-red-700">{error.message}</p>
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Deal: {id}
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Real Estate Deal Management
              </p>
            </div>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
            >
              Refresh
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {data && <DealRenderer blocks={data.blocks} />}
        </main>
      </div>

      {/* Chat Sidebar */}
      <aside className="w-96 flex-shrink-0">
        <ChatPanel dealId={id} onUpdate={() => refetch()} />
      </aside>
    </div>
  );
}
