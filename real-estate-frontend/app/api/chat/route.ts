import { NextRequest, NextResponse } from "next/server";

// Backend URL - должен быть задан в переменных окружения
const BACKEND_URL = process.env.BACKEND_URL;

if (!BACKEND_URL) {
  throw new Error("BACKEND_URL environment variable is not set");
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    console.log(`[API Proxy] POST /api/chat -> ${BACKEND_URL}/chat`, body);

    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
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
    console.log(`[API Proxy] Backend response:`, data);

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
