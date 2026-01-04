import { NextRequest, NextResponse } from "next/server";

// Backend URL - должен быть задан в переменных окружения
const BACKEND_URL = process.env.BACKEND_URL;

if (!BACKEND_URL) {
  throw new Error("BACKEND_URL environment variable is not set");
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: dealId } = await params;

  try {
    console.log(`[API Proxy] GET /api/deal/${dealId}/state -> ${BACKEND_URL}/api/deal/${dealId}/state`);

    const response = await fetch(`${BACKEND_URL}/api/deal/${dealId}/state`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    console.log(`[API Proxy] Backend response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[API Proxy] Backend error:`, errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log(`[API Proxy] Deal state blocks:`, data.blocks?.length || 0);

    return NextResponse.json(data);
  } catch (error) {
    console.error("[API Proxy] Error:", error);

    const errorMessage = error instanceof Error ? error.message : "Unknown error";

    return NextResponse.json(
      { error: "Failed to connect to backend", details: errorMessage },
      { status: 502 }
    );
  }
}
