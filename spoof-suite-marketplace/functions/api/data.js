// Cloudflare Pages Function for API endpoints
export async function onRequest(context) {
  const { request, env } = context;
  
  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };

  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    // Sample data for your marketplace
    const data = {
      credit_cards: 247,
      debit_cards: 128,
      plaid_logs: 67,
      fullz_count: 43,
      notifications: [
        "✓ All systems operational - Marketplace running smoothly",
        "• 247 credit cards available - Quality verified",
        "• 128 debit cards in stock - High balance selection",
        "• Banking logs active - Live account access available",
        "• Identity profiles ready - Complete data packages",
        "→ 24/7 marketplace access - Always fresh inventory"
      ],
      bins: [
        {"bin": "424242", "type": "Credit", "bank": "Chase Bank", "country": "USA"},
        {"bin": "411111", "type": "Credit", "bank": "Bank of America", "country": "USA"},
        {"bin": "555555", "type": "Credit", "bank": "Mastercard", "country": "USA"},
        {"bin": "400012", "type": "Debit", "bank": "Wells Fargo", "country": "USA"}
      ]
    };

    return new Response(JSON.stringify(data), {
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }
}
