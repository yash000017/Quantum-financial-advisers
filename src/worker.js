const GONE_PATHS = new Set([
  "/first-time-buyer",
  "/first-time-buyer.html",
  "/remortgaging",
  "/remortgaging.html",
  "/life-insurance",
  "/life-insurance.html",
  "/income-protection",
  "/income-protection.html",
  "/private-medical-insurance",
  "/private-medical-insurance.html",
  "/critical-illness-insurance",
  "/critical-illness-insurance.html",
  "/buildings-contents-insurance",
  "/buildings-contents-insurance.html",
  "/total-wealth-planning",
  "/total-wealth-planning.html",
  "/savings-and-investments",
  "/savings-and-investments.html",
  "/pensions-advice",
  "/pensions-advice.html",
  "/equity-release",
  "/equity-release.html",
  "/wills-and-trust",
  "/wills-and-trust.html",
  "/estate-planning",
  "/estate-planning.html",
  "/incapacity-planning",
  "/incapacity-planning.html",
  "/faqs",
  "/faqs.html",
]);

const SECURITY_HEADERS = {
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "X-Frame-Options": "SAMEORIGIN",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
};

function cacheControlFor(pathname) {
  if (pathname.startsWith("/assets/")) {
    return "public, max-age=31536000, immutable";
  }
  if (/\.(?:woff2|webp|png|jpg|jpeg|ico|svg)$/i.test(pathname)) {
    return "public, max-age=31536000, immutable";
  }
  if (pathname.endsWith(".css") || pathname.endsWith(".js") || pathname.endsWith(".webmanifest")) {
    return "public, max-age=604800";
  }
  return "public, max-age=300";
}

function pathnameOf(request) {
  const url = new URL(request.url);
  return url.pathname.replace(/\/+$/, "") || "/";
}

export default {
  async fetch(request, env) {
    const pathname = pathnameOf(request);

    if (GONE_PATHS.has(pathname)) {
      const gonePage = await env.ASSETS.fetch(new URL("/410.html", request.url));
      const headers = new Headers(gonePage.headers);
      for (const [name, value] of Object.entries(SECURITY_HEADERS)) {
        headers.set(name, value);
      }
      return new Response(gonePage.body, {
        status: 410,
        statusText: "Gone",
        headers,
      });
    }

    const asset = await env.ASSETS.fetch(request);
    const headers = new Headers(asset.headers);
    for (const [name, value] of Object.entries(SECURITY_HEADERS)) {
      headers.set(name, value);
    }
    headers.set("Cache-Control", cacheControlFor(pathname));
    return new Response(asset.body, {
      status: asset.status,
      statusText: asset.statusText,
      headers,
    });
  },
};
