"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();
  const [dealId, setDealId] = useState("");

  const handleCreateDeal = () => {
    // Generate a simple UUID-like ID
    const newDealId = `deal-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
    router.push(`/deal/${newDealId}`);
  };

  const handleOpenDeal = () => {
    if (dealId.trim()) {
      router.push(`/deal/${dealId.trim()}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Globrix
          </h1>
          <p className="text-xl text-gray-600">
            AI-Powered Real Estate Deal Management
          </p>
        </div>

        {/* Actions */}
        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          {/* Create New Deal */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-3">
              Create New Deal
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Start a new real estate deal with AI assistance
            </p>
            <button
              onClick={handleCreateDeal}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Create New Deal
            </button>
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">or</span>
            </div>
          </div>

          {/* Open Existing Deal */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-3">
              Open Existing Deal
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Enter a deal ID to continue working on it
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={dealId}
                onChange={(e) => setDealId(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleOpenDeal()}
                placeholder="deal-abc-123..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleOpenDeal}
                disabled={!dealId.trim()}
                className="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
              >
                Open
              </button>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            icon="🤖"
            title="AI Assistant"
            description="Natural language interface for property search and deal management"
          />
          <FeatureCard
            icon="🏢"
            title="Dynamic UI"
            description="Adaptive interface that changes based on your needs"
          />
          <FeatureCard
            icon="📊"
            title="Smart Analytics"
            description="Automated insights and deal recommendations"
          />
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-gray-500">
          <p>Powered by Claude & LangGraph</p>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white rounded-lg p-6 text-center shadow-sm">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
